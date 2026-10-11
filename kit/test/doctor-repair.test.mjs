import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { chmod, lstat, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { acquireDoctorLock } from '../dist/doctor/lock.js';
import { mutate } from '../dist/doctor/mutate.js';
import { planMissingTool } from '../dist/doctor/fixers/missing-omp-tool.js';
import { INSTALL_FILES } from '../dist/install.js';
import { exitCodeForFailure } from '../src/cli/exit.mjs';
import { doctorFixture, repoRoot, snapshot } from './doctor-support.mjs';
import { runCli } from './cli-support.mjs';

const REPAIR_IDS = 'fm-logs-mode-too-open,fm-hooks-global-link-broken,fm-plugins-omp-tool-missing';
const FIXTURE_ROOT = join(repoRoot, 'kit/test/doctor_fixtures');
const TEMPLATE_ROOT = join(repoRoot, 'kit/templates');

function digest(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function runRepair(args, fixture) {
  const doctorDir = join(fixture.home, '.local/state/classifier/doctor');
  return runCli(['repair', ...args], {
    home: fixture.home,
    cwd: fixture.repo,
    env: {
      CI: '1',
      JEV_STATE_DIR: fixture.stateDir,
      JEV_DOCTOR_DIR: doctorDir,
      NO_COLOR: '1',
      PATH: '',
    },
  });
}

function runFixtureScript(fixtureName, scriptName, values) {
  const result = spawnSync('/bin/sh', [join(FIXTURE_ROOT, fixtureName, scriptName)], {
    encoding: 'utf8',
    env: { PATH: process.env.PATH ?? '/usr/bin:/bin', ...values },
  });
  assert.equal(result.status, 0, `${scriptName} failed: ${result.stderr}${result.stdout}`);
}

function runGit(repo, args) {
  const result = spawnSync('git', args, {
    cwd: repo,
    encoding: 'utf8',
    env: { PATH: process.env.PATH ?? '/usr/bin:/bin', GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: '/dev/null' },
  });
  assert.equal(result.status, 0, `git ${args.join(' ')} failed: ${result.stderr}`);
}

async function fileState(path) {
  try {
    const [bytes, metadata] = await Promise.all([readFile(path), lstat(path)]);
    return { exists: true, sha256: digest(bytes), mode: metadata.mode & 0o777 };
  } catch (error) {
    if (error?.code === 'ENOENT') return { exists: false };
    throw error;
  }
}

async function makeRepairFixture(label) {
  const fixture = await doctorFixture(label, { tier: 'deep' });
  const doctorDir = join(fixture.home, 'doctor-state');
  const inventory = {
    schema_version: 'test-fixture.v1',
    surfaces: [{
      id: 'fixture-global-hook',
      expect: 'on',
      group: 'global',
      repo: '.omp/hooks/post/fixture-hook.ts',
      hookfile: 'fixture-hook.ts',
    }],
  };
  const inventoryPath = join(fixture.repo, 'work/jev-inventory/expected.json');
  await writeFile(inventoryPath, `${JSON.stringify(inventory)}\n`);
  fixture.inventory = inventory;

  const sourceRelative = '.omp/hooks/post/fixture-hook.ts';
  const source = join(fixture.repo, sourceRelative);
  const target = join(fixture.home, '.omp/agent/hooks/post/fixture-hook.ts');
  await mkdir(dirname(source), { recursive: true });
  await mkdir(dirname(target), { recursive: true });
  await writeFile(source, 'export const fixtureHook = true;\n', { mode: 0o644 });
  await writeFile(target, await readFile(source), { mode: 0o644 });
  runGit(fixture.repo, ['init', '--quiet', '--initial-branch=main']);
  runGit(fixture.repo, ['-c', 'user.name=Doctor Fixture', '-c', 'user.email=fixture@example.invalid', 'add', sourceRelative, 'work/jev-inventory/expected.json']);
  runGit(fixture.repo, ['-c', 'user.name=Doctor Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '--quiet', '-m', 'fixture source']);

  const manifestFiles = {};
  for (const [destination, template] of Object.entries(INSTALL_FILES)) {
    const templatePath = resolve(TEMPLATE_ROOT, template);
    const bytes = await readFile(templatePath);
    const installedPath = join(fixture.repo, '.omp', destination);
    await mkdir(dirname(installedPath), { recursive: true });
    await writeFile(installedPath, bytes, { mode: 0o644 });
    manifestFiles[destination] = digest(bytes);
  }
  await writeFile(join(fixture.repo, '.omp/jev-kit-manifest.json'), `${JSON.stringify({ version: 1, files: manifestFiles }, null, 2)}\n`, { mode: 0o644 });

  const logPath = join(fixture.stateDir, 'gate-observe.jsonl');
  await writeFile(logPath, `${JSON.stringify({ ts: '2026-10-06T12:00:00.000Z', status: 'fixture' })}\n`, { mode: 0o600 });
  await chmod(logPath, 0o600);

  runFixtureScript('fm-logs-mode-too-open', 'corrupt.sh', { TARGET: logPath });
  runFixtureScript('fm-hooks-global-link-broken', 'corrupt.sh', { SOURCE: source, TARGET: target });
  const toolPath = join(fixture.repo, '.omp/tools/jev-gate.ts');
  runFixtureScript('fm-plugins-omp-tool-missing', 'corrupt.sh', { TARGET: toolPath });

  return { ...fixture, doctorDir, inventory, source, target, logPath, toolPath };
}

function lifecycleEnv(fixture) {
  return {
    HOME: fixture.home,
    JEV_STATE_DIR: fixture.stateDir,
    JEV_DOCTOR_DIR: fixture.doctorDir,
  };
}

test('repair defaults to a zero-write plan and names apply plus rollback commands', async () => {
  const fixture = await doctorFixture('classifier-repair-plan', { tier: 'deep' });
  const log = join(fixture.stateDir, 'mode-check.jsonl');
  await writeFile(log, '');
  await chmod(log, 0o644);
  const before = await snapshot(fixture.home);
  const beforeMode = (await lstat(log)).mode & 0o777;

  const result = runRepair(['--json', '--only', 'fm-logs-mode-too-open'], fixture);

  assert.equal(result.status, 0, result.stderr || result.stdout);
  const envelope = JSON.parse(result.stdout);
  assert.equal(envelope.schema, 'classifier.repair.v1');
  assert.equal(envelope.status, 'OK');
  assert.equal(envelope.data.mode, 'plan');
  const commands = JSON.stringify(envelope.data);
  assert.ok(commands.includes('--apply'));
  assert.ok(commands.includes('undo latest'));
  assert.deepEqual(await snapshot(fixture.home), before);
  assert.equal(((await lstat(log)).mode & 0o777), beforeMode);
});

test('unknown repair option typo returns usage status and exact corrected command', async () => {
  const fixture = await doctorFixture('classifier-repair-option-typo', { tier: 'deep' });

  const result = runRepair(['--jso'], fixture);

  assert.equal(result.status, 64, result.stderr || result.stdout);
  assert.ok(result.stderr.includes("error: unknown option '--jso'"), result.stderr);
  assert.ok(result.stderr.includes('did you mean: classifier repair --json'), result.stderr);
});

test('apply repairs, doctor verifies clean, and undo restores the byte-identical corrupted state', async () => {
  const fixture = await makeRepairFixture('classifier-repair-lifecycle');
  const before = await snapshot(fixture.home);
  const corruptedState = {
    log: await fileState(fixture.logPath),
    hook: await fileState(fixture.target),
    missingTool: await fileState(fixture.toolPath),
  };

  const planned = runCli(['repair', '--only', REPAIR_IDS, '--robot'], {
    home: fixture.home,
    cwd: fixture.repo,
    env: lifecycleEnv(fixture),
  });
  assert.equal(planned.status, 0, `${planned.stderr}${planned.stdout}`);
  const plan = JSON.parse(planned.stdout).data;
  assert.equal(plan.mode, 'plan');
  assert.equal(plan.actions_taken, 0);
  assert.equal(plan.actions.length, 3);
  assert.deepEqual(await snapshot(fixture.home), before);
  assert.deepEqual({
    log: await fileState(fixture.logPath),
    hook: await fileState(fixture.target),
    missingTool: await fileState(fixture.toolPath),
  }, corruptedState);

  const applied = runCli(['repair', '--apply', '--only', REPAIR_IDS, '--robot'], {
    home: fixture.home,
    cwd: fixture.repo,
    env: lifecycleEnv(fixture),
  });
  assert.equal(applied.status, 0, `${applied.stderr}${applied.stdout}`);
  assert.equal(JSON.parse(applied.stdout).data.actions_taken, 3);
  runFixtureScript('fm-logs-mode-too-open', 'assert.sh', { TARGET: fixture.logPath });
  runFixtureScript('fm-hooks-global-link-broken', 'assert.sh', { SOURCE: fixture.source, TARGET: fixture.target });
  const template = resolve(TEMPLATE_ROOT, INSTALL_FILES['tools/jev-gate.ts']);
  runFixtureScript('fm-plugins-omp-tool-missing', 'assert.sh', {
    TARGET: fixture.toolPath,
    EXPECTED_TEMPLATE: template,
  });

  const repeated = runCli(['repair', '--apply', '--only', REPAIR_IDS, '--robot'], {
    home: fixture.home,
    cwd: fixture.repo,
    env: lifecycleEnv(fixture),
  });
  assert.equal(repeated.status, 0, `${repeated.stderr}${repeated.stdout}`);
  assert.equal(JSON.parse(repeated.stdout).data.actions_taken, 0);

  const verified = runCli(['doctor', '--deep', '--only', REPAIR_IDS, '--json'], {
    home: fixture.home,
    cwd: fixture.repo,
    env: lifecycleEnv(fixture),
  });
  assert.equal(verified.status, 0, `${verified.stderr}${verified.stdout}`);
  assert.deepEqual(JSON.parse(verified.stdout).findings, []);

  const undone = runCli(['repair', 'undo', 'latest', '--robot'], {
    home: fixture.home,
    cwd: fixture.repo,
    env: lifecycleEnv(fixture),
  });
  assert.equal(undone.status, 0, `${undone.stderr}${undone.stdout}`);
  assert.equal(JSON.parse(undone.stdout).data.actions_taken, 3);
  assert.deepEqual({
    log: await fileState(fixture.logPath),
    hook: await fileState(fixture.target),
    missingTool: await fileState(fixture.toolPath),
  }, corruptedState);

  const undoneAgain = runCli(['repair', 'undo', 'latest', '--robot'], {
    home: fixture.home,
    cwd: fixture.repo,
    env: lifecycleEnv(fixture),
  });
  assert.equal(undoneAgain.status, 0, `${undoneAgain.stderr}${undoneAgain.stdout}`);
  assert.equal(JSON.parse(undoneAgain.stdout).data.actions_taken, 0);
});

test('a models.yml write refuses with exit 4 and no backup or action row', async () => {
  const fixture = await doctorFixture('classifier-repair-protected-models');
  const target = join(fixture.home, '.omp/agent/models.yml');
  await mkdir(dirname(target), { recursive: true });
  const bytes = Buffer.from('provider: operator-owned\n');
  await writeFile(target, bytes, { mode: 0o600 });
  const before = await fileState(target);
  const doctorDir = join(fixture.home, 'doctor-state');

  await assert.rejects(mutate({
    root: fixture.home,
    doctorDir,
    target: '.omp/agent/models.yml',
    writeScopes: ['.omp/agent/models.yml'],
    operation: 'write',
    content: 'replacement\n',
    mode: 0o600,
    expectedBeforeSha256: digest(bytes),
    expectedBeforeMode: 0o600,
  }), (error) => error.code === 'REFUSED');
  assert.deepEqual(await fileState(target), before);
  assert.equal(exitCodeForFailure({ reason: 'refused-unsafe' }), 4);
  await assert.rejects(lstat(join(doctorDir, 'runs')), { code: 'ENOENT' });
  assert.deepEqual(await readdir(doctorDir), ['lock.free']);
});

test('a missing-tool repair refuses an edited source template', async () => {
  const fixture = await doctorFixture('classifier-repair-edited-template');
  const template = resolve(TEMPLATE_ROOT, INSTALL_FILES['tools/jev-gate.ts']);
  const templateBytes = await readFile(template);
  const target = join(fixture.repo, '.omp/tools/jev-gate.ts');
  await mkdir(dirname(target), { recursive: true });
  await writeFile(join(fixture.repo, '.omp/jev-kit-manifest.json'), JSON.stringify({
    version: 1,
    files: { 'tools/jev-gate.ts': digest(templateBytes) },
  }));
  const overrideRoot = join(fixture.home, 'edited-templates');
  const editedTemplate = join(overrideRoot, INSTALL_FILES['tools/jev-gate.ts']);
  await mkdir(dirname(editedTemplate), { recursive: true });
  await writeFile(editedTemplate, Buffer.concat([templateBytes, Buffer.from('\n// edited after install\n')]));
  await assert.rejects(planMissingTool({
    id: 'fm-plugins-omp-tool-missing',
    evidence: { file: '.omp/tools/jev-gate.ts' },
  }, {
    home: fixture.home,
    repo: fixture.repo,
    stateDir: fixture.stateDir,
    doctorDir: join(fixture.home, 'doctor-state'),
    templateRoot: overrideRoot,
  }), (error) => error.code === 'REFUSED');
  await assert.rejects(lstat(target), { code: 'ENOENT' });
  await assert.rejects(lstat(join(fixture.home, 'doctor-state')), { code: 'ENOENT' });
});

test('a concurrent apply refuses with exit 5 and the live lock owner pid', async () => {
  const fixture = await doctorFixture('classifier-repair-concurrent-apply');
  const doctorDir = join(fixture.home, 'doctor-state');
  const logPath = join(fixture.stateDir, 'gate-observe.jsonl');
  await writeFile(logPath, '\n', { mode: 0o644 });
  await chmod(logPath, 0o644);
  const lock = await acquireDoctorLock(doctorDir);
  try {
    const result = runCli(['repair', '--apply', '--only', 'fm-logs-mode-too-open', '--robot'], {
      home: fixture.home,
      cwd: fixture.repo,
      env: lifecycleEnv({ ...fixture, doctorDir }),
    });
    assert.equal(result.status, 5, `${result.stderr}${result.stdout}`);
    assert.equal(exitCodeForFailure({ reason: 'transport' }), 5);
    assert.ok(result.stdout.includes(`pid ${process.pid}`), result.stdout);
    assert.equal((await fileState(logPath)).mode, 0o644);
    await assert.rejects(lstat(join(doctorDir, 'runs')), { code: 'ENOENT' });
  } finally {
    await lock.release();
  }
});

test('installer uninstall removes managed files only through quarantine', async () => {
  const source = await readFile(join(repoRoot, 'kit/src/install.ts'), 'utf8');
  assert.ok(source.includes('operation: "quarantine"'), 'uninstall must quarantine managed files');
  assert.equal(source.includes('unlink('), false, 'uninstall must not unlink managed paths directly');
});

test('doctor mutation calls stay behind mutate.ts', async () => {
  const root = join(repoRoot, 'kit/src/doctor');
  const paths = [];
  async function collect(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) await collect(path);
      else if (entry.name.endsWith('.ts') || entry.name.endsWith('.mjs')) paths.push(path);
    }
  }
  await collect(root);
  const forbidden = ['writeFile(', 'unlink(', 'rm('];
  for (const path of paths) {
    if (path === join(root, 'mutate.ts')) continue;
    const source = await readFile(path, 'utf8');
    for (const call of forbidden) assert.equal(source.includes(call), false, `${path} contains ${call}`);
  }
});
