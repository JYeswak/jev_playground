import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { cp, lstat, mkdir, readdir, readFile, realpath, symlink, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname } from 'node:path';
import { freshHome } from './cli-support.mjs';
import { installProfileTargets } from '../dist/install/omp-profile-target.js';
import { decide } from '../src/conformance.ts';
const testDir = dirname(fileURLToPath(import.meta.url));
const kitRoot = dirname(testDir);
const fixtureDir = join(testDir, 'fixtures', 'installer');
const familiesFixture = join(fixtureDir, 'families.json');
const contractsDir = join(fixtureDir, 'contracts');
const surfacesFixture = join(fixtureDir, 'surfaces.json');
const nativePkgDir = join(fixtureDir, 'native-pkg');
const PACKAGE_PIN = 'c2d7871afbc14c190b564eebdbaf3de190c35f17';
const PACKAGE_GIT = 'git+https://github.com/JYeswak/jev_playground.git';
const GATE_SAFE_SIDE_TEST = 'installer.gate.unreachable.refuses';
const SCREEN_SAFE_SIDE_TEST = 'installer.screen.unreachable.passes';


async function loadJson(path) {
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch (error) {
    throw new Error('cannot load JSON fixture ' + path + ': ' + (error instanceof Error ? error.message : String(error)));
  }
}

async function makePackageResolution() {
  const host = await freshHome('installer-profile-package-resolution');
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const resolved = PACKAGE_GIT + '#' + PACKAGE_PIN;
  const rootManifest = {
    name: 'installer-profile-fixture',
    version: '1.0.0',
    private: true,
    dependencies: { [packageManifest.name]: resolved },
  };
  const lock = {
    name: rootManifest.name,
    version: rootManifest.version,
    lockfileVersion: 3,
    requires: true,
    packages: {
      '': { name: rootManifest.name, version: rootManifest.version, dependencies: rootManifest.dependencies },
      ['node_modules/' + packageManifest.name]: { version: packageManifest.version, resolved },
    },
  };
  const packageRoot = join(host, 'node_modules', packageManifest.name);
  // Physical recursive copy (symlinks dereferenced): the installed package
  // must be real files so loader behavior matches production. A symlink
  // here would let realpath escape node_modules and mask Node's
  // type-stripping ban, the exact blind spot under test.
  await cp(nativePkgDir, packageRoot, { recursive: true, dereference: true });
  assert.equal(await realpath(packageRoot), packageRoot, 'installed package must be physical files, not a symlink escape');
  await writeFile(join(host, 'package.json'), JSON.stringify(rootManifest, null, 2) + '\n');
  const packageLockPath = join(host, 'package-lock.json');
  await writeFile(packageLockPath, JSON.stringify(lock, null, 2) + '\n');
  return { packageRoot, packageLockPath, packageManifest, resolved };
}

async function loadFamilies(contracts) {
  const families = (await loadJson(familiesFixture)).families;
  const packageResolution = await makePackageResolution();
  return families.map((family) => {
    const subpath = family.id === 'gate' ? 'src/gate-hook.ts' : family.id === 'screen' ? 'src/screen-hook.ts' : 'src/hint-extension.ts';
    return {
      id: family.id,
      surfaceType: family.surface_type,
      kind: family.kind,
      declared: family.declared,
      supportedProfiles: family.supported_profiles,
      contract: contracts[family.id],
      manifest: {
        latencyBudgetMs: family.id === 'gate' ? 1500 : 800,
        safeSideTestId: family.safe_side_test_id,
        offSwitchPath: '~/.local/state/jev/' + family.id + '-fixture-off',
      },
      packageRoot: packageResolution.packageRoot,
      packageLockPath: packageResolution.packageLockPath,
      packageSpecifier: packageResolution.packageManifest.name + '/' + subpath,
      pin: PACKAGE_PIN,
    };
  });
}
async function assertUnreachableSafeSide(contract, expectedAction) {
  const resultValue = { fixture: 'unchanged' };
  const state = Object.fromEntries(contract.state.fields.map((field) => [field, 'fixture']));
  const result = await decide({
    contract,
    state,
    result: resultValue,
    adapter: {
      id: 'offline-unreachable',
      modelId: 'offline-unreachable',
      probabilities: 'required',
      async evaluate(request, transport) { return transport(request); },
    },
    transport: async () => { throw new Error('network unreachable'); },
  });
  assert.equal(result.status, 'transport-error');
  assert.equal(result.reason, 'transport');
  assert.equal(result.action, expectedAction);
  if (expectedAction === 'pass') assert.strictEqual(result.result, resultValue);
  else assert.equal(result.result, undefined);
}

const safeSideContractTests = new Map([
  [GATE_SAFE_SIDE_TEST, {
    test: 'gateNetworkUnreachableRefuses',
    run: (contract) => assertUnreachableSafeSide(contract, 'refuse'),
  }],
  [SCREEN_SAFE_SIDE_TEST, {
    test: 'screenNetworkUnreachablePasses',
    run: (contract) => assertUnreachableSafeSide(contract, 'pass'),
  }],
  ['installer.hint.unreachable.passes', {
    test: 'hintAdvisoryUnreachablePasses',
    run: (contract) => assertUnreachableSafeSide(contract, 'pass'),
  }],
]);

async function runSafeSideContractTest(id, contract) {
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const registration = packageManifest.jev?.safe_side_tests?.[id];
  const registeredTest = safeSideContractTests.get(id);
  if (!registeredTest) throw new Error('safe-side manifest ID has no executable contract test: ' + id);
  assert.deepEqual(registration, {
    surface_type: contract.surface_type,
    safe_side: contract.safe_side,
    test: registeredTest.test,
  });
  assert.equal(contract.safe_side_test_id, id);
  await registeredTest.run(contract);
}

async function snapshotBytes(paths) {
  return Promise.all(paths.map(async (path) => [path, await readFile(path)]));
}


async function snapshotTree(root) {
  const out = new Map();
  async function walk(dir, rel) {
    let names;
    try {
      names = await readdir(dir);
    } catch (error) {
      if (error && error.code === 'ENOENT') return;
      throw error;
    }
    for (const name of names.sort()) {
      const full = join(dir, name);
      const key = rel ? `${rel}/${name}` : name;
      const st = await lstat(full);
      if (st.isDirectory()) {
        await walk(full, key);
      } else {
        let bytes;
        try {
          bytes = await readFile(full);
        } catch {
          bytes = Buffer.from('<unreadable>');
        }
        out.set(key, `${createHash('sha256').update(bytes).digest('hex')}:${st.mtimeMs}`);
      }
    }
  }
  await walk(root, '');
  return out;
}

function hookShimPath(ompHome, profile, family, hooksDir) {
  const agent = profile === 'default' ? 'agent' : `profiles/${profile}/agent`;
  return join(ompHome, agent, 'hooks', hooksDir, `jev-${family}.ts`);
}

test('a declared-ON gate family installs its locked package shim on a measured profile', async () => {
  const home = await freshHome('installer-profile-positive');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'gate');
  const family = families[0];
  await runSafeSideContractTest(family.manifest.safeSideTestId, family.contract);
  const consumerRoot = dirname(family.packageLockPath);
  const consumer = createRequire(join(consumerRoot, 'package.json'));
  const lockedPackage = await loadJson(family.packageLockPath);
  assert.equal(lockedPackage.packages['node_modules/jev-fixture-native'].resolved, PACKAGE_GIT + '#' + PACKAGE_PIN);
  const resolvedImport = consumer.resolve(family.packageSpecifier);
  assert.equal(await readFile(resolvedImport, 'utf8'), await readFile(join(nativePkgDir, 'src', 'gate-hook.ts'), 'utf8'));
  const probeDir = join(home, 'probe');
  await mkdir(probeDir, { recursive: true });
  const probeNonce = 'positive-install-marker';
  process.env.JEV_HOOK_PROBE_DIR = probeDir;
  process.env.JEV_HOOK_PROBE_NONCE = probeNonce;
  let result;
  try {
    result = await installProfileTargets({
      ompHome,
      profiles: ['default'],
      families,
      switchRegistry: await loadJson(surfacesFixture),
      maxHandlerLatencyMs: 5000,
    });
  } finally {
    delete process.env.JEV_HOOK_PROBE_DIR;
    delete process.env.JEV_HOOK_PROBE_NONCE;
  }
  assert.equal(result.exit, 0);
  assert.equal(result.families[0].status, 'installed');
  // The factory executed during verification (in the staged copy): the
  // marker row proves installation ran the entry, not just screened it.
  const loadRows = (await readFile(join(probeDir, 'hook-loads.jsonl'), 'utf8')).trim().split('\n').map((line) => JSON.parse(line));
  assert.deepEqual(loadRows.map((row) => [row.nonce, row.family]), [[probeNonce, 'gate']]);
  const shim = await readFile(hookShimPath(ompHome, 'default', 'gate', 'pre'), 'utf8');
  assert.ok(shim.includes('classifier-shim-v2 family=gate'));
  assert.ok(shim.includes('jev-fixture-native/src/gate-hook.ts'));
  assert.ok(shim.includes('export { default } from'));
  assert.equal(shim.includes('jev-kit/'), false);
  assert.ok(shim.includes('pin=' + PACKAGE_PIN));
  assert.equal(shim.includes('/Users/'), false);
  assert.equal(shim.includes('Developer/jev'), false);
  const marker = await loadJson(join(ompHome, 'agent', 'jev-shims.json'));
  assert.equal(marker.shims.gate.sha256.length, 64);
  assert.equal(marker.shims.gate.pin, PACKAGE_PIN);
});

test('the fixture hook entry registers and judges through a stub pi', async () => {
  // Execution proof for the entry the installer accepts statically: import
  // from the canonical fixture path (outside node_modules, so Node strips
  // types) and drive the registered handler.
  const entry = await import(pathToFileURL(join(nativePkgDir, 'src', 'gate-hook.ts')).href);
  assert.equal(typeof entry.default, 'function');
  const registered = {};
  await entry.default({ on: (event, handler) => { registered[event] = handler; } });
  assert.equal(typeof registered.tool_call, 'function');
  assert.deepEqual(await registered.tool_call({ command: 'rm -rf /important' }), { block: true, reason: 'fixture-risk' });
  assert.deepEqual(await registered.tool_call({ command: 'ls' }), { block: false, reason: 'fixture-allow' });
});

test('the screen safe-side id executes the pass-on-unreachable contract test', async () => {
  const screen = await loadJson(join(contractsDir, 'screen.json'));
  await runSafeSideContractTest(screen.safe_side_test_id, screen);
  assert.equal(screen.safe_side_test_id, SCREEN_SAFE_SIDE_TEST);
});

test('an unknown safe-side id is refused before writing', async () => {
  const home = await freshHome('installer-profile-unknown-safe-test');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, manifest: { ...family.manifest, safeSideTestId: 'installer.gate.unregistered' } }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a screen cannot use the gate refuse-on-unreachable contract test', async () => {
  const home = await freshHome('installer-profile-screen-safe-test-mismatch');
  const ompHome = join(home, 'omp-home');
  const screen = await loadJson(join(contractsDir, 'screen.json'));
  const families = (await loadFamilies({ screen })).filter((family) => family.id === 'screen')
    .map((family) => ({ ...family, declared: 'ON', manifest: { ...family.manifest, safeSideTestId: GATE_SAFE_SIDE_TEST } }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a registered entry naming a nonexistent executable proof is refused', async () => {
  const home = await freshHome('installer-profile-bogus-proof');
  const ompHome = join(home, 'omp-home');
  const packageName = 'jev-bogus-proof-pkg';
  const pin = '1'.repeat(40);
  const resolved = 'git+https://github.com/JYeswak/jev_playground.git#' + pin;
  const packageRoot = join(home, 'pkgroot');
  await mkdir(join(packageRoot, 'src'), { recursive: true });
  await writeFile(join(packageRoot, 'package.json'), JSON.stringify({
    name: packageName,
    version: '0.0.1',
    jev: { safe_side_tests: { 'installer.gate.unreachable.refuses': {
      surface_type: 'command-gate', safe_side: 'refuse', test: 'nonexistentProofName' } } },
  }, null, 2) + '\n');
  await writeFile(join(packageRoot, 'src', 'gate.ts'), 'export const marker = 1;\n');
  await mkdir(join(home, 'node_modules'), { recursive: true });
  await symlink(packageRoot, join(home, 'node_modules', packageName), 'dir');
  await writeFile(join(home, 'package.json'), JSON.stringify({
    name: 'bogus-proof-consumer', version: '1.0.0', private: true,
    dependencies: { [packageName]: resolved },
  }, null, 2) + '\n');
  const packageLockPath = join(home, 'package-lock.json');
  await writeFile(packageLockPath, JSON.stringify({
    name: 'bogus-proof-consumer', version: '1.0.0', lockfileVersion: 3, requires: true,
    packages: {
      '': { name: 'bogus-proof-consumer', version: '1.0.0', dependencies: { [packageName]: resolved } },
      ['node_modules/' + packageName]: { version: '0.0.1', resolved },
    },
  }, null, 2) + '\n');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, packageRoot, packageLockPath,
      packageSpecifier: packageName + '/src/gate.ts', pin }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('not a known executable proof'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a lock resolving the package to another commit is refused before writing', async () => {
  const home = await freshHome('installer-profile-package-lock-drift');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate');
  const family = families[0];
  const lock = await loadJson(family.packageLockPath);
  lock.packages['node_modules/jev-fixture-native'].resolved = PACKAGE_GIT + '#' + '0'.repeat(40);
  await writeFile(family.packageLockPath, JSON.stringify(lock, null, 2) + '\n');
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a declared-OFF family is never installed', async () => {
  const home = await freshHome('installer-profile-off');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'screen');
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 0);
  assert.equal(result.families[0].status, 'skipped-off');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('an extension family on codex is unsupported', async () => {
  const home = await freshHome('installer-profile-codex');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'hint');
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['codex'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 0);
  assert.equal(result.families[0].status, 'unsupported');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('an advisory family registers its packaged entry in profile config', async () => {
  const home = await freshHome('installer-profile-extension');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'hint.json')),
  };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'hint');
  const before = await snapshotTree(ompHome);
  assert.deepEqual(before.size, 0);
  const input = {
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  };
  const result = await installProfileTargets(input);
  assert.equal(result.exit, 0);
  assert.equal(result.families[0].status, 'installed');
  const config = await readFile(join(ompHome, 'agent', 'config.yml'), 'utf8');
  assert.ok(config.includes('hint-extension.ts'));
  const marker = await loadJson(join(ompHome, 'agent', 'jev-shims.json'));
  assert.equal(marker.extensions.hint.pin, PACKAGE_PIN);
  assert.ok(marker.extensions.hint.entry.endsWith('hint-extension.ts'));
  const secondBefore = await snapshotTree(ompHome);
  const second = await installProfileTargets(input);
  assert.equal(second.exit, 0);
  assert.equal(second.families[0].status, 'already');
  assert.deepEqual(second.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), secondBefore);
});

test('a package entry without a native default export is refused before writing', async () => {
  const home = await freshHome('installer-profile-lib-only');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, packageSpecifier: packageManifest.name + '/src/lib-only.ts' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('no default function export'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a default export that is not a function is refused before writing', async () => {
  const home = await freshHome('installer-profile-null-default');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'hint.json')),
  };
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'hint')
    .map((family) => ({ ...family, packageSpecifier: packageManifest.name + '/src/null-default.ts' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('no default function export'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a factory that never registers the declared event is refused before writing', async () => {
  const home = await freshHome('installer-profile-inert');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, packageSpecifier: packageManifest.name + '/src/inert-hook.ts' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('does not register tool_call'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a factory with only dead-code registration is refused before writing', async () => {
  // Textual presence of pi.on is not registration: the branch never runs,
  // so execution proves no handler registers.
  const home = await freshHome('installer-profile-dead-hook');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, packageSpecifier: packageManifest.name + '/src/dead-hook.ts' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('does not register tool_call'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('an entry with an unresolvable import is refused before writing', async () => {
  const home = await freshHome('installer-profile-missing-dep');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, packageSpecifier: packageManifest.name + '/src/missing-dep.ts' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('does not load'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a null handler registration does not satisfy the event proof', async () => {
  const home = await freshHome('installer-profile-bad-handler');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, packageSpecifier: packageManifest.name + '/src/bad-handler.ts' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('does not register tool_call'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a factory that throws when invoked is refused before writing', async () => {
  const home = await freshHome('installer-profile-throwing');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'hint.json')),
  };
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'hint')
    .map((family) => ({ ...family, packageSpecifier: packageManifest.name + '/src/throwing.ts' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('factory throws'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('an unknown host method call fails closed like the real host', async () => {
  const home = await freshHome('installer-profile-unknown-method');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const packageManifest = await loadJson(join(nativePkgDir, 'package.json'));
  const families = (await loadFamilies({ gate })).filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, packageSpecifier: packageManifest.name + '/src/unknown-method.ts' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.ok((result.families[0].reason ?? '').includes('factory throws'));
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a surface absent from the switch registry is refused with exit 4', async () => {
  const home = await freshHome('installer-profile-ghost');
  const ompHome = join(home, 'omp-home');
  const contracts = { gate: await loadJson(join(contractsDir, 'gate.json')) };
  const families = (await loadFamilies({ ...contracts, screen: contracts.gate, hint: contracts.gate }))
    .filter((family) => family.id === 'gate')
    .map((family) => ({ ...family, id: 'ghost' }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a registry surface with a null off switch is refused with exit 4', async () => {
  const home = await freshHome('installer-profile-null-switch');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'gate');
  const registry = await loadJson(surfacesFixture);
  registry.surfaces = registry.surfaces.map((surface) =>
    (surface.id === 'gate' ? { ...surface, off_switch: null } : surface),
  );
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: registry,
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a manifest naming a different switch path is refused with exit 4', async () => {
  const home = await freshHome('installer-profile-switch-mismatch');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const families = (await loadFamilies(contracts))
    .filter((family) => family.id === 'gate')
    .map((family) => ({
      ...family,
      manifest: { ...family.manifest, offSwitchPath: '~/.local/state/jev/other-switch' },
    }));
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a manifest without latency, test id, or over the handler limit is refused', async () => {
  const home = await freshHome('installer-profile-manifest-gaps');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const base = (await loadFamilies(contracts)).filter((family) => family.id === 'gate');
  for (const manifest of [
    { ...base[0].manifest, latencyBudgetMs: 0 },
    { ...base[0].manifest, safeSideTestId: '' },
    { ...base[0].manifest, latencyBudgetMs: 6000 },
  ]) {
    const before = await snapshotTree(ompHome);
    const result = await installProfileTargets({
      ompHome,
      profiles: ['default'],
      families: [{ ...base[0], manifest }],
      switchRegistry: await loadJson(surfacesFixture),
      maxHandlerLatencyMs: 5000,
    });
    assert.equal(result.exit, 4);
    assert.equal(result.families[0].status, 'refused');
    assert.deepEqual(result.writes, []);
    assert.deepEqual(await snapshotTree(ompHome), before);
  }
});

test('a screen contract declaring refuse contradicts its surface type and is refused', async () => {
  const home = await freshHome('installer-profile-contradiction');
  const ompHome = join(home, 'omp-home');
  const gate = await loadJson(join(contractsDir, 'gate.json'));
  const screenRefuse = { ...gate, family: 'screen', surface_type: 'result-screen' };
  const contracts = { gate, screen: screenRefuse, hint: screenRefuse };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'screen');
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families: families.map((family) => ({ ...family, declared: 'ON' })),
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a repo-path predecessor shim is refused and stays byte-identical', async () => {
  const home = await freshHome('installer-profile-repopath');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'gate');
  const dest = hookShimPath(ompHome, 'default', 'gate', 'pre');
  await mkdir(join(ompHome, 'agent', 'hooks', 'pre'), { recursive: true });
  const repoShim = "export * from '/Users/someone/Developer/jev/kit/src/gate.ts';\n";
  await writeFile(dest, repoShim);
  const before = await snapshotTree(ompHome);
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 4);
  assert.equal(result.families[0].status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.equal(await readFile(dest, 'utf8'), repoShim);
  assert.deepEqual(await snapshotTree(ompHome), before);
});

test('a hardlink predecessor conflicts unless migrated with backup', async () => {
  const home = await freshHome('installer-profile-hardlink');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'gate');
  const dest = hookShimPath(ompHome, 'default', 'gate', 'pre');
  await mkdir(join(ompHome, 'agent', 'hooks', 'pre'), { recursive: true });
  await writeFile(dest, 'user-owned predecessor\n');
  const { link } = await import('node:fs/promises');
  await link(dest, `${dest}.sibling`);
  const before = await snapshotTree(ompHome);
  const beforeBytes = await snapshotBytes([dest, dest + '.sibling']);

  const refused = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(refused.exit, 4);
  assert.equal(refused.families[0].status, 'conflict');
  assert.deepEqual(refused.writes, []);
  assert.deepEqual(await snapshotBytes([dest, dest + '.sibling']), beforeBytes);
  assert.deepEqual(await snapshotTree(ompHome), before);
  const migrated = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
    migrate: true,
  });
  assert.equal(migrated.exit, 0);
  assert.equal(migrated.families[0].status, 'installed');
  assert.equal(await readFile(`${dest}.migrate-bak`, 'utf8'), 'user-owned predecessor\n');
});

test('re-run is already with zero writes', async () => {
  const home = await freshHome('installer-profile-rerun');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const input = {
    ompHome,
    profiles: ['default'],
    families: (await loadFamilies(contracts)).filter((family) => family.id === 'gate'),
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  };
  const first = await installProfileTargets(input);
  assert.equal(first.families[0].status, 'installed');
  const before = await snapshotTree(ompHome);
  const second = await installProfileTargets(input);
  assert.equal(second.exit, 0);
  assert.equal(second.families[0].status, 'already');
  assert.deepEqual(second.writes, []);
  assert.deepEqual(await snapshotTree(ompHome), before);
});
