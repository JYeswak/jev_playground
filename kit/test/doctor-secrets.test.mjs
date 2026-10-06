import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, chmod, writeFile, readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { detectors as secretDetectors, resolveKeySource } from '../src/doctor/detectors/secrets.mjs';
import { detectors as backendDetectors } from '../src/doctor/detectors/backends.mjs';
import { detectors as daemonDetectors } from '../src/doctor/detectors/daemons.mjs';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const scratchRoot = join(repoRoot, 'var', 'agent-tmp');
const inventory = JSON.parse(await readFile(join(repoRoot, 'work/jev-inventory/expected.json'), 'utf8'));

async function fixture(label) {
  await mkdir(scratchRoot, { recursive: true });
  const root = await mkdtemp(join(scratchRoot, `${label}.${process.pid}.`));
  await writeFile(join(root, '.owner'), `pid=${process.pid}\nlabel=${label}\nrepo=jev\ncreated=${new Date().toISOString()}\n`);
  const home = join(root, 'home');
  const stateDir = join(root, 'state');
  const repo = join(root, 'repo');
  await Promise.all([mkdir(home, { recursive: true }), mkdir(stateDir), mkdir(repo)]);
  return { root, home, stateDir, repo };
}

function context(paths, overrides = {}) {
  return {
    ...paths,
    now: Date.parse('2026-10-06T12:00:00.000Z'),
    tier: 'default', online: false, env: {}, inventory,
    exec: async () => { throw new Error('unexpected exec'); },
    fetch: async () => { throw new Error('unexpected fetch'); },
    ...overrides,
  };
}

function detector(items, id) {
  const found = items.find((item) => item.id === id);
  assert.ok(found, `missing detector ${id}`);
  return found;
}

test('key-source resolver applies env, user binary, then machine identity precedence without returning secrets', async () => {
  const paths = await fixture('doctor-key-source');
  const env = { TYPESAFE_API_KEY: 'secret-marker', PATH: '' };
  const machine = join(paths.home, '.config', 'infisical');
  await mkdir(machine, { recursive: true });
  await writeFile(join(machine, 'zeststream.env'), 'export INFISICAL_CLIENT_ID=client-marker\nexport INFISICAL_CLIENT_SECRET=secret-marker\n');
  const envResult = await resolveKeySource(context(paths, { env }));
  assert.deepEqual(envResult, {
    key_source: 'env', checked: { env: true, infisical_user: false, infisical_machine: true },
  });
  assert.equal(JSON.stringify(envResult).includes('secret-marker'), false);

  const localPaths = await fixture('doctor-local-infisical');
  const localBinary = join(localPaths.home, '.local', 'bin');
  await mkdir(localBinary, { recursive: true });
  await writeFile(join(localBinary, 'infisical'), 'not executable; presence only');
  const localResult = await resolveKeySource(context(localPaths, { env: { TYPESAFE_API_KEY: '', PATH: '' } }));
  assert.equal(localResult.key_source, 'infisical-user');
  assert.equal(localResult.checked.env, false);
  assert.equal(localResult.checked.infisical_user, true);

  const machinePaths = await fixture('doctor-machine-infisical');
  const machineDirectory = join(machinePaths.home, '.config', 'infisical');
  await mkdir(machineDirectory, { recursive: true });
  await writeFile(join(machineDirectory, 'zeststream.env'), 'export INFISICAL_CLIENT_ID=client-marker\nexport INFISICAL_CLIENT_SECRET=secret-marker\n');
  const machineResult = await resolveKeySource(context(machinePaths, { env: { PATH: '' } }));
  assert.equal(machineResult.key_source, 'infisical-machine');
  assert.equal(machineResult.checked.infisical_machine, true);
  assert.equal(JSON.stringify(machineResult).includes('secret-marker'), false);

  const noSourcePaths = await fixture('doctor-no-key-source');
  const finding = await detector(secretDetectors, 'fm-secrets-no-key-source').run(context(noSourcePaths, { env: { PATH: '' } }));
  assert.equal(finding[0].evidence.key_source, 'none');
  assert.equal(JSON.stringify(finding).includes('secret-marker'), false);
});

test('Infisical PATH presence is recognized without running it', async () => {
  const paths = await fixture('doctor-path-infisical');
  const bin = join(paths.root, 'fake-bin');
  await mkdir(bin);
  await writeFile(join(bin, 'infisical'), 'binary fixture');
  let execCalls = 0;
  const found = await resolveKeySource(context(paths, { env: { PATH: bin }, exec: async () => { execCalls += 1; } }));
  assert.equal(found.key_source, 'infisical-user');
  assert.equal(found.checked.infisical_user, true);
  assert.equal(execCalls, 0);
});

test('wrapper detector names the exact missing profile and config file', async () => {
  const paths = await fixture('doctor-key-wrapper');
  const base = join(paths.home, '.omp', 'agent');
  await mkdir(base, { recursive: true });
  await writeFile(join(base, 'models.yml'), 'key: typesafe-key.mjs\n');
  for (const profile of inventory.profiles.filter((name) => name !== 'default' && name !== 'codex')) {
    const directory = join(paths.home, '.omp', 'profiles', profile, 'agent');
    await mkdir(directory, { recursive: true });
    await writeFile(join(directory, 'models.yml'), 'key: typesafe-key.mjs\n');
  }
  const findings = await detector(secretDetectors, 'fm-secrets-key-wrapper-missing').run(context(paths));
  assert.equal(findings.length, 1);
  assert.equal(findings[0].evidence.profile, 'codex');
  assert.equal(findings[0].evidence.file, join(paths.home, '.omp', 'profiles', 'codex', 'agent', 'models.yml'));
  assert.equal(findings[0].evidence.line, null);
});

test('machine credential config mode detects permissions wider than 0600', async () => {
  const paths = await fixture('doctor-machine-mode');
  const directory = join(paths.home, '.config', 'infisical');
  await mkdir(directory, { recursive: true });
  const file = join(directory, 'zeststream.env');
  await writeFile(file, 'export INFISICAL_CLIENT_ID=private-value\n');
  await chmod(file, 0o600);
  assert.deepEqual(await detector(secretDetectors, 'fm-secrets-machine-config-mode').run(context(paths)), []);
  await chmod(file, 0o644);
  const findings = await detector(secretDetectors, 'fm-secrets-machine-config-mode').run(context(paths));
  assert.equal(findings.length, 1);
  assert.equal(findings[0].evidence.file, file);
  assert.equal(findings[0].evidence.mode & 0o077, 0o044);
  assert.equal(JSON.stringify(findings).includes('private-value'), false);
});

test('recent Infisical resolve errors count only matching rows in the 24-hour window', async () => {
  const paths = await fixture('doctor-resolve-errors');
  const now = Date.parse('2026-10-06T12:00:00.000Z');
  const rows = [
    { ts: new Date(now - 1000).toISOString(), error: 'key-source=infisical unavailable', detail: 'never expose' },
    { ts: new Date(now - 25 * 60 * 60 * 1000).toISOString(), error: 'key-source=infisical old' },
    { ts: new Date(now + 1000).toISOString(), error: 'key-source=infisical future' },
  ];
  await writeFile(join(paths.stateDir, 'gate-observe.jsonl'), rows.map((row) => JSON.stringify(row)).join('\n'));
  const findings = await detector(secretDetectors, 'fm-secrets-recent-resolve-failures').run(context(paths, { now }));
  assert.equal(findings.length, 1);
  assert.equal(findings[0].evidence.failures_24h, 1);
  assert.equal(JSON.stringify(findings).includes('never expose'), false);
});

test('Clef health uses only the bounded 11300 health endpoint and records unreachability', async () => {
  const paths = await fixture('doctor-clef-fetch');
  const calls = [];
  const ctx = context(paths, {
    inventory: { surfaces: [{ how: 'model backend clef' }] },
    fetch: async (url, init) => {
      calls.push({ url, init });
      return new Promise((_, reject) => {
        const watchdog = setTimeout(() => reject(new Error('health fetch was not aborted')), 1000);
        init.signal.addEventListener('abort', () => {
          clearTimeout(watchdog);
          reject(init.signal.reason);
        }, { once: true });
      });
    },
  });
  const start = Date.now();
  const findings = await detector(backendDetectors, 'fm-clef-unreachable').run(ctx);
  const elapsed = Date.now() - start;
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, 'http://127.0.0.1:11300/healthz');
  assert.equal(calls[0].init.method, 'GET');
  assert.ok(calls[0].init.signal instanceof AbortSignal);
  assert.ok(elapsed >= 400 && elapsed < 1000, `expected a 500ms timeout, observed ${elapsed}ms`);
  assert.equal(calls.some(({ url }) => url.includes(':8010')), false);
  assert.equal(findings[0].severity, 'P1');
  assert.equal(findings[0].evidence.endpoint, calls[0].url);
  const healthy = await detector(backendDetectors, 'fm-clef-unreachable').run(context(paths, {
    fetch: async () => ({ ok: true, status: 200 }),
  }));
  assert.deepEqual(healthy, []);
});

test('daemon checks use injected launchctl/process probes and detect missing canary, gateway, and human watch', async () => {
  const paths = await fixture('doctor-daemons');
  const launchAgents = join(paths.home, 'Library', 'LaunchAgents');
  await mkdir(launchAgents, { recursive: true });
  await writeFile(join(launchAgents, 'ai.zeststream.jev-latest-canary.plist'), '<plist fixture/>');
  const execCalls = [];
  const exec = async (command, args, options) => {
    execCalls.push({ command, args, options });
    if (command === 'launchctl') return { code: 0, stdout: '123 0 ai.zeststream.jev-latest-canary\n- 0 com.localbench.ollama-gateway\n', stderr: '' };
    if (command === 'pgrep') return { code: 1, stdout: '', stderr: '' };
    throw new Error(`Unexpected injected command: ${command}`);
  };
  const ctx = context(paths, { exec });
  const canary = await detector(daemonDetectors, 'fm-daemons-canary-agent').run(ctx);
  assert.equal(canary.length, 0);
  const gateway = await detector(daemonDetectors, 'fm-daemons-gateway-down').run(ctx);
  assert.equal(gateway.length, 1);
  assert.equal(gateway[0].evidence.has_pid, false);
  const humanWatch = await detector(daemonDetectors, 'fm-daemons-needs-human-watch').run(ctx);
  assert.equal(humanWatch.length, 1);
  assert.equal(humanWatch[0].evidence.present, false);
  assert.ok(execCalls.every(({ command }) => ['launchctl', 'pgrep'].includes(command)));
  assert.ok(execCalls.filter(({ command }) => command === 'launchctl').every(({ args }) => args[0] === 'list'));
});

test('daemon detectors report canary bad exit and gateway probe failure from injected results', async () => {
  const paths = await fixture('doctor-daemon-failures');
  const launchAgents = join(paths.home, 'Library', 'LaunchAgents');
  await mkdir(launchAgents, { recursive: true });
  await writeFile(join(launchAgents, 'ai.zeststream.jev-latest-canary.plist'), '<plist fixture/>');
  const exec = async (command) => {
    if (command === 'launchctl') return { code: 0, stdout: '- 7 ai.zeststream.jev-latest-canary\n456 0 com.localbench.ollama-gateway\n', stderr: '' };
    if (command === 'nc') return { code: 1, stdout: '', stderr: '' };
    throw new Error(`Unexpected injected command: ${command}`);
  };
  const ctx = context(paths, { exec });
  const canary = await detector(daemonDetectors, 'fm-daemons-canary-agent').run(ctx);
  assert.equal(canary.length, 1);
  assert.equal(canary[0].evidence.last_exit, 7);
  const gateway = await detector(daemonDetectors, 'fm-daemons-gateway-down').run(ctx);
  assert.equal(gateway.length, 1);
  assert.equal(gateway[0].evidence.reachable, false);
  const healthyExec = async (command) => {
    if (command === 'launchctl') return { code: 0, stdout: '123 0 ai.zeststream.jev-latest-canary\n456 0 com.localbench.ollama-gateway\n', stderr: '' };
    if (command === 'nc') return { code: 0, stdout: '', stderr: '' };
    if (command === 'pgrep') return { code: 0, stdout: '123 fleet-idle-watch.py\n', stderr: '' };
    throw new Error(`Unexpected injected command: ${command}`);
  };
  const healthyCtx = context(paths, { exec: healthyExec });
  assert.deepEqual(await detector(daemonDetectors, 'fm-daemons-canary-agent').run(healthyCtx), []);
  assert.deepEqual(await detector(daemonDetectors, 'fm-daemons-gateway-down').run(healthyCtx), []);
  assert.deepEqual(await detector(daemonDetectors, 'fm-daemons-needs-human-watch').run(healthyCtx), []);
});
