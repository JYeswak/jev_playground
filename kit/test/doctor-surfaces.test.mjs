import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { chmod, copyFile, link, mkdir, mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectors as surfaceDetectors, surfacePaths } from '../src/doctor/detectors/surfaces.mjs';
import { detectors as driftDetectors } from '../src/doctor/detectors/drift.mjs';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const scratchRoot = join(repoRoot, 'var/agent-tmp');
async function fixture(label) {
  await mkdir(scratchRoot, { recursive: true });
  const dir = await mkdtemp(join(scratchRoot, `${label}.${process.pid}.`));
  await writeFile(join(dir, '.owner'), `pid=${process.pid}\nlabel=${label}\nrepo=jev\ncreated=${new Date().toISOString()}\n`);
  return dir;
}
const base = (repo, overrides = {}) => ({
  repo, home: '/fixture/home', stateDir: '/fixture/state', inventory: null,
  now: Date.parse('2026-10-06T12:00:00Z'), tier: 'default', online: false, env: {},
  exec: async () => { throw new Error('unexpected command execution'); },
  fetch: async () => { throw new Error('unexpected network access'); },
  ...overrides,
});
const detector = (detectors, id) => detectors.find((item) => item.id === id);

test('the OMP discovery surface enumerates all six install tools plus hook and extensions', () => {
  assert.equal(surfacePaths.tools.length, 6);
  assert.ok(surfacePaths.tools.includes('.omp/tools/jev-rerank.ts'));
  assert.ok(surfacePaths.tools.includes('.omp/tools/jev-claim-check.ts'));
  assert.ok(surfacePaths.tools.includes('.omp/tools/jev-screen.ts'));
  assert.ok(surfacePaths.tools.includes('.omp/tools/jev-flag.ts'));
  assert.ok(surfacePaths.tools.includes('.omp/tools/jev-gate.ts'));
  assert.ok(surfacePaths.tools.includes('.omp/tools/jev-classify.ts'));
  const dataSources = detector(surfaceDetectors, 'fm-plugins-omp-tool-missing').data_sources;
  for (const path of [...surfacePaths.tools, ...surfacePaths.hooks, ...surfacePaths.extensions]) assert.ok(dataSources.includes(path));
});

test('missing manifest-listed tool has a named finding; unlisted missing tool is ignored', async () => {
  const repo = await fixture('doctor-surface-manifest');
  await mkdir(join(repo, '.omp'), { recursive: true });
  await writeFile(join(repo, '.omp/jev-kit-manifest.json'), JSON.stringify({ version: 1, files: { 'tools/jev-rerank.ts': 'fixture-sha' } }));
  const run = detector(surfaceDetectors, 'fm-plugins-omp-tool-missing').run;
  const result = await run(base(repo));
  assert.equal(detector(surfaceDetectors, 'fm-plugins-omp-tool-missing').id, 'fm-plugins-omp-tool-missing');
  assert.equal(result.length, 1);
  assert.equal(result[0].title, 'Manifest-listed OMP surface file is missing');
  assert.equal(result[0].evidence.file, '.omp/tools/jev-rerank.ts');
});

test('hook-load failure output maps to fm-hooks-load-failure using injected exec only', async () => {
  const repo = await fixture('doctor-hook-load');
  const calls = [];
  const result = await detector(surfaceDetectors, 'fm-hooks-load-failure').run(base(repo, {
    exec: async (command, args, options) => {
      calls.push({ command, args, options });
      return { code: 1, stdout: '', stderr: 'HOOK_LOAD_FAIL .omp/extensions/example.ts: unresolved import\n' };
    },
  }));
  assert.equal(calls.length, 1);
  assert.deepEqual(calls[0], { command: 'bun', args: ['scripts/check-hook-loads.mjs', '--repo', repo, '--home', '/fixture/home'], options: { cwd: repo, env: {} } });
  assert.equal(detector(surfaceDetectors, 'fm-hooks-load-failure').id, 'fm-hooks-load-failure');
  assert.equal(result.length, 1);
  assert.equal(result[0].title, 'OMP hook or extension failed to load');
  assert.deepEqual(result[0].evidence, { file: '.omp/extensions/example.ts' });
});

test('jev realpath shadowing is reported from injected OMP discovery values', async () => {
  const repo = await fixture('doctor-path-shadow');
  const result = await detector(surfaceDetectors, 'fm-path-jev-shadowed').run(base(repo, {
    omp: { jev_path: { resolved: '/fixture/bin/jev', realpath: '/fixture/other/jev' } },
    exec: async (command, args) => {
      assert.equal(command, 'realpath');
      assert.equal(args[0], join(repo, 'kit/bin/jev.mjs'));
      return { code: 0, stdout: '/fixture/repo/kit/bin/jev.mjs\n', stderr: '' };
    },
  }));
  assert.equal(detector(surfaceDetectors, 'fm-path-jev-shadowed').id, 'fm-path-jev-shadowed');
  assert.equal(result.length, 1);
  assert.equal(result[0].evidence.realpath_matches_package, false);
});

test('missing sibling bin is reported and an executable sibling is healthy', async () => {
  const repo = await fixture('doctor-sibling-bin');
  const run = detector(surfaceDetectors, 'fm-plugins-sibling-bin-missing').run;
  assert.equal((await run(base(repo))).length, 1);
  const binary = join(repo, 'kit/bin/jev-skill-gap.mjs');
  await mkdir(dirname(binary), { recursive: true });
  await writeFile(binary, '#!/usr/bin/env node\n');
  await chmod(binary, 0o755);
  assert.deepEqual(await run(base(repo)), []);
});

async function globalHookFixture(label, hardlink) {
  const root = await fixture(label);
  const repo = join(root, 'repo');
  const home = join(root, 'home');
  const inventory = JSON.parse(await readFile(join(repoRoot, 'work/jev-inventory/expected.json'), 'utf8'));
  const global = inventory.surfaces.filter((surface) => surface.group === 'global' && surface.expect === 'on');
  assert.ok(global.length > 0, 'recorded inventory has no active global hooks');
  await mkdir(join(repo, 'work/jev-inventory'), { recursive: true });
  await writeFile(join(repo, 'work/jev-inventory/expected.json'), JSON.stringify(inventory));
  const sources = [];
  for (const surface of global) {
    const source = join(repo, surface.repo);
    await mkdir(dirname(source), { recursive: true });
    await copyFile(join(repoRoot, surface.repo), source);
    sources.push(surface.repo);
    const destinations = [
      join(home, '.omp/agent/hooks/post', surface.hookfile),
      join(home, '.omp/profiles/fixture/agent/hooks/post', surface.hookfile),
    ];
    for (const destination of destinations) {
      await mkdir(dirname(destination), { recursive: true });
      if (hardlink) await link(source, destination);
      else await copyFile(source, destination);
    }
  }
  const gitEnv = { ...process.env, GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: '/dev/null', GIT_TERMINAL_PROMPT: '0' };
  const git = (args) => {
    const result = spawnSync('git', args, { cwd: repo, env: gitEnv, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    return { code: 0, stdout: result.stdout, stderr: result.stderr };
  };
  git(['init', '--quiet']);
  git(['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'add', '--', 'work/jev-inventory/expected.json', ...sources]);
  git(['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '--quiet', '-m', 'fixture']);
  const ctx = base(repo, {
    home,
    inventory,
    stateDir: join(root, 'state'),
    exec: async (command, args) => {
      const result = spawnSync(command, args, { cwd: repo, env: gitEnv, encoding: 'utf8' });
      return { code: result.status ?? 1, stdout: result.stdout ?? '', stderr: result.stderr ?? '' };
    },
  });
  return { root, repo, home, inventory, global, ctx };
}

test('global hook audit catches copied hooks and accepts only hardlinks to the committed source', async () => {
  const audit = detector(driftDetectors, 'fm-hooks-global-link-broken');
  const broken = await globalHookFixture('doctor-global-link-broken', false);
  const findings = await audit.run(broken.ctx);
  assert.equal(findings.length, broken.global.length * 2);
  assert.ok(findings.every((item) => item.evidence.link_type === 'copy'));

  const healthy = await globalHookFixture('doctor-global-link-healthy', true);
  assert.deepEqual(await audit.run(healthy.ctx), []);
});

test('outside-repo audit remains explicitly unavailable', async () => {
  const item = detector(driftDetectors, 'fm-surfaces-outside-repo-audit');
  assert.equal(item.availability, 'unavailable');
  assert.ok(item.skipped_reason);
  assert.deepEqual(await item.run(base(null)), []);
});

test('fleet watcher is healthy with a fresh liveness row and RED after two intervals', async () => {
  const stateDir = await fixture('doctor-watch-fresh');
  const detectorRun = detector(driftDetectors, 'fm-fleet-watch-stale').run;
  const inventory = { surfaces: [{ id: 'needs-human', expect: 'on', process: 'fleet-idle-watch.py' }] };
  const now = Date.parse('2026-10-06T12:00:00Z');
  const log = join(stateDir, 'fleet-watch-liveness.jsonl');
  await writeFile(log, `${JSON.stringify({ ts: new Date(now - 120_000).toISOString(), status: 'checked' })}\n`);
  assert.deepEqual(await detectorRun(base(null, { stateDir, inventory, now })), []);
  await writeFile(log, `${JSON.stringify({ ts: new Date(now - 120_001).toISOString(), status: 'checked' })}\n`);
  const stale = await detectorRun(base(null, { stateDir, inventory, now }));
  assert.equal(detector(driftDetectors, 'fm-fleet-watch-stale').id, 'fm-fleet-watch-stale');
  assert.equal(stale.length, 1);
  assert.equal(stale[0].severity, 'P2');
});

test('declared ON inventory with a missing path or contradictory verdict is RED', async () => {
  const repo = await fixture('doctor-inventory-stale');
  const inventorySource = JSON.parse(await readFile(join(repoRoot, 'work/jev-inventory/expected.json'), 'utf8'));
  const sourceSurface = inventorySource.surfaces.find((surface) => surface.expect === 'on' && typeof surface.file === 'string');
  assert.ok(sourceSurface);
  const inventory = { surfaces: [
    { id: sourceSurface.id, expect: 'on', file: '.omp/not-present-from-source-fixture.ts', verdict: 'WORKS' },
    { id: 'fixture-contradiction', expect: 'on', verdict: 'REFUTED' },
  ] };
  const findings = await detector(driftDetectors, 'fm-inventory-expected-stale').run(base(repo, { inventory }));
  assert.equal(findings.length, 2);
  assert.ok(findings.some((item) => item.evidence.file === '.omp/not-present-from-source-fixture.ts'));
  assert.ok(findings.some((item) => item.evidence.verdict === 'REFUTED'));
});
test('declared ENFORCING memory-filter requires its state-dir switch', async () => {
  const stateDir = await fixture('doctor-memory-filter-switch');
  const expected = JSON.parse(await readFile(join(repoRoot, 'work/jev-inventory/expected.json'), 'utf8'));
  const memoryFilter = expected.surfaces.find((surface) =>
    surface.id === 'memory-filter' && surface.expect === 'on' && surface.verdict === 'ENFORCING');
  assert.ok(memoryFilter);
  const run = detector(driftDetectors, 'fm-inventory-enforcement-switch-missing').run;
  const ctx = base(null, { stateDir, inventory: { surfaces: [memoryFilter] } });
  const missing = await run(ctx);
  assert.equal(missing.length, 1);
  assert.equal(missing[0].evidence.file, 'memory-filter-enforce');
  await writeFile(join(stateDir, 'memory-filter-enforce'), 'enabled\n');
  assert.deepEqual(await run(ctx), []);
});
