import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstat, mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
import { freshHome } from './cli-support.mjs';
import { installProfileTargets } from '../dist/install/omp-profile-target.js';

const testDir = dirname(fileURLToPath(import.meta.url));
const fixtureDir = join(testDir, 'fixtures', 'installer');
const familiesFixture = join(fixtureDir, 'families.json');
const contractsDir = join(fixtureDir, 'contracts');
const surfacesFixture = join(fixtureDir, 'surfaces.json');

async function loadJson(path) {
  return JSON.parse(await readFile(path, 'utf8'));
}

async function loadFamilies(contracts) {
  const families = (await loadJson(familiesFixture)).families;
  return families.map((family) => ({
    id: family.id,
    surfaceType: family.surface_type,
    kind: family.kind,
    declared: family.declared,
    supportedProfiles: family.supported_profiles,
    contract: contracts[family.id],
    manifest: {
      latencyBudgetMs: family.id === 'gate' ? 1500 : 800,
      safeSideTestId: `${family.id}-refuses-when-unreachable`,
      offSwitchPath: `~/.local/state/jev/${family.id}-fixture-off`,
    },
    packageSpecifier: '@classifier/test-kit/families',
    pin: 'abcdef1234567890',
  }));
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

function shimPath(ompHome, profile, family) {
  const agent = profile === 'default' ? 'agent' : `profiles/${profile}/agent`;
  return join(ompHome, agent, 'shims', `jev-${family}.ts`);
}

test('a declared-ON gate family installs its shim on a measured profile', async () => {
  const home = await freshHome('installer-profile-positive');
  const ompHome = join(home, 'omp-home');
  const contracts = {
    gate: await loadJson(join(contractsDir, 'gate.json')),
    screen: await loadJson(join(contractsDir, 'screen.json')),
    hint: await loadJson(join(contractsDir, 'screen.json')),
  };
  const families = (await loadFamilies(contracts)).filter((family) => family.id === 'gate');
  const result = await installProfileTargets({
    ompHome,
    profiles: ['default'],
    families,
    switchRegistry: await loadJson(surfacesFixture),
    maxHandlerLatencyMs: 5000,
  });
  assert.equal(result.exit, 0);
  assert.equal(result.families[0].status, 'installed');
  const shim = await readFile(shimPath(ompHome, 'default', 'gate'), 'utf8');
  assert.ok(shim.includes('classifier-shim-v2 family=gate'));
  assert.ok(shim.includes('@classifier/test-kit/families'));
  assert.equal(shim.includes('/Users/'), false);
  assert.equal(shim.includes('Developer/jev'), false);
  const marker = JSON.parse(
    await readFile(join(ompHome, 'agent', 'jev-shims.json'), 'utf8'),
  );
  assert.ok(marker.shims.gate.sha256.length >= 7);
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
  const dest = shimPath(ompHome, 'default', 'gate');
  await mkdir(join(ompHome, 'agent', 'shims'), { recursive: true });
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
  const dest = shimPath(ompHome, 'default', 'gate');
  await mkdir(join(ompHome, 'agent', 'shims'), { recursive: true });
  await writeFile(dest, 'user-owned predecessor\n');
  const { link } = await import('node:fs/promises');
  await link(dest, `${dest}.sibling`);
  const before = await snapshotTree(ompHome);
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
  void before;
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
