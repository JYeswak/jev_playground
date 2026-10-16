import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { cp, lstat, mkdir, readdir, readFile, readlink, symlink, writeFile } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';
import { freshHome } from './cli-support.mjs';
import {
  installCli,
  rollbackCli,
  uninstallCli,
} from '../dist/install/cli-target.js';

const PACKAGE_DIR = fileURLToPath(new URL('..', import.meta.url));
const prepared = new Map();

async function artifact(version, omit = []) {
  if (omit.length === 0 && prepared.has(version)) return prepared.get(version);
  const directory = await freshHome('installer-cli-prepared-package');
  const pkg = JSON.parse(await readFile(join(PACKAGE_DIR, 'package.json'), 'utf8'));
  const excluded = new Set(omit);
  for (const path of pkg.files) {
    const destination = join(directory, path);
    await mkdir(dirname(destination), { recursive: true });
    await cp(join(PACKAGE_DIR, path), destination, {
      recursive: true,
      filter: (source) => !excluded.has(relative(PACKAGE_DIR, source)),
    });
  }
  for (const name of Object.keys(pkg.dependencies)) {
    const destination = join(directory, 'node_modules', name);
    await mkdir(dirname(destination), { recursive: true });
    await cp(join(PACKAGE_DIR, 'node_modules', name), destination, {
      recursive: true,
      filter: (source) => !excluded.has(relative(PACKAGE_DIR, source)),
    });
  }
  await writeFile(join(directory, 'package.json'), JSON.stringify({ ...pkg, version }));
  if (omit.length === 0) prepared.set(version, directory);
  return directory;
}
const FOREIGN = Buffer.from('#!/bin/sh\necho hermes-foreign-bin\n');

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

function binPaths(home, binName = 'classifier') {
  const base = join(home, '.local', 'share', 'classifier');
  return {
    base,
    versionDir: join(base, 'versions', '1.0.0'),
    link: join(home, '.local', 'bin', binName),
    current: join(base, 'current'),
    state: join(base, 'install-state.json'),
  };
}

test('fresh install lays out versions, current and the bin link', async () => {
  const home = await freshHome('installer-cli-fresh');
  const result = await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') });
  assert.equal(result.exit, 0);
  assert.equal(result.status, 'installed');
  const paths = binPaths(home);
  assert.equal(await readlink(paths.current), paths.versionDir);
  assert.equal(await readlink(paths.link), join(paths.versionDir, 'bin', 'classifier'));
  assert.equal(execFileSync(paths.link, ['--version'], { encoding: 'utf8' }), 'classifier 1.0.0\n');
  const state = JSON.parse(await readFile(paths.state, 'utf8'));
  assert.deepEqual(state.versions, ['1.0.0']);
  assert.equal(state.current, '1.0.0');
});

test('re-run is already with zero writes', async () => {
  const home = await freshHome('installer-cli-rerun');
  const first = await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') });
  assert.equal(first.status, 'installed');
  const before = await snapshotTree(home);
  const second = await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') });
  assert.equal(second.exit, 0);
  assert.equal(second.status, 'already');
  assert.deepEqual(second.writes, []);
  assert.deepEqual(await snapshotTree(home), before);
});

test('a foreign bin without take-over refuses with exit 4 and stays byte-identical', async () => {
  const home = await freshHome('installer-cli-foreign');
  const paths = binPaths(home);
  await mkdir(join(home, '.local', 'bin'), { recursive: true });
  await writeFile(paths.link, FOREIGN);
  const before = await snapshotTree(home);
  const result = await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') });
  assert.equal(result.exit, 4);
  assert.equal(result.status, 'conflict');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await readFile(paths.link), FOREIGN);
  assert.deepEqual(await snapshotTree(home), before);
});

test('take-over records the displaced bin and uninstall restores it', async () => {
  const home = await freshHome('installer-cli-takeover');
  const paths = binPaths(home);
  await mkdir(join(home, '.local', 'bin'), { recursive: true });
  await writeFile(paths.link, FOREIGN);
  const taken = await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0'), takeOverBin: true });
  assert.equal(taken.exit, 0);
  assert.equal(taken.status, 'installed');
  assert.equal(execFileSync(paths.link, ['--version'], { encoding: 'utf8' }), 'classifier 1.0.0\n');
  const beforeDry = await snapshotTree(home);
  const dry = await uninstallCli({ home });
  assert.equal(dry.status, 'dry-run');
  assert.ok(dry.wouldRemove.length > 0);
  assert.deepEqual(await snapshotTree(home), beforeDry);
  const removed = await uninstallCli({ home, apply: true });
  assert.equal(removed.exit, 0);
  assert.equal(removed.status, 'removed');
  assert.deepEqual(await readFile(paths.link), FOREIGN);
});

test('rollback flips current to the previous version', async () => {
  const home = await freshHome('installer-cli-rollback');
  const paths = binPaths(home);
  await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') });
  await installCli({ home, version: '2.0.0', packageDir: await artifact('2.0.0') });
  assert.equal(await readlink(paths.current), join(paths.base, 'versions', '2.0.0'));
  const rolled = await rollbackCli({ home });
  assert.equal(rolled.exit, 0);
  assert.equal(rolled.status, 'rolled-back');
  assert.equal(await readlink(paths.current), join(paths.base, 'versions', '1.0.0'));
  assert.equal(execFileSync(paths.link, ['--version'], { encoding: 'utf8' }), 'classifier 1.0.0\n');
});

test('rollback with a single version refuses without writes', async () => {
  const home = await freshHome('installer-cli-rollback-single');
  await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') });
  const before = await snapshotTree(home);
  const rolled = await rollbackCli({ home });
  assert.equal(rolled.exit, 4);
  assert.equal(rolled.status, 'no-previous-version');
  assert.deepEqual(rolled.writes, []);
  assert.deepEqual(await snapshotTree(home), before);
});

test('a traversal version is refused as usage with no writes', async () => {
  const home = await freshHome('installer-cli-traversal');
  const before = await snapshotTree(home);
  await assert.rejects(
    installCli({ home, version: '../evil', packageDir: await artifact('1.0.0') }),
    (error) => error.code === 'USAGE',
  );
  assert.deepEqual(await snapshotTree(home), before);
});

test('a corrupt state file fails typed IO, not a raw parse throw', async () => {
  const home = await freshHome('installer-cli-corrupt-state');
  const paths = binPaths(home);
  await mkdir(join(home, '.local', 'share', 'classifier'), { recursive: true });
  await writeFile(paths.state, 'not-json{{{');
  await assert.rejects(
    installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') }),
    (error) => error.code === 'IO' && error.message.includes('not JSON'),
  );
});

test('the real prepared classifier stays runnable after versioned installation', async () => {
  const home = await freshHome('installer-cli-real-artifact');
  const packageDir = fileURLToPath(new URL('..', import.meta.url));
  const pkg = JSON.parse(await readFile(join(packageDir, 'package.json'), 'utf8'));
  const result = await installCli({
    home,
    version: pkg.version,
    packageDir,
  });
  assert.equal(result.status, 'installed');
  const output = execFileSync(join(home, '.local', 'share', 'classifier', 'current', 'bin', 'classifier'), [
    '--version',
  ], { encoding: 'utf8', env: { ...process.env, HOME: home }, timeout: 10000 });
  assert.equal(output, `classifier ${pkg.version}\n`);
});

test('an incomplete real package refuses before publishing any consumer state', async () => {
  const home = await freshHome('installer-cli-incomplete-artifact');
  const before = await snapshotTree(home);
  await assert.rejects(installCli({
    home,
    version: '1.0.0',
    packageDir: await artifact('1.0.0', ['dist/client.js']),
  }), (error) => error.code === 'USAGE');
  assert.deepEqual(await snapshotTree(home), before);
});

test('a modified installed dependency refuses reinstallation without overwriting it', async () => {
  const home = await freshHome('installer-cli-modified-payload');
  const packageDir = await artifact('1.0.0');
  await installCli({ home, version: '1.0.0', packageDir });
  const modified = join(binPaths(home).versionDir, 'dist', 'client.js');
  await writeFile(modified, '// operator-owned change\n');
  const before = await snapshotTree(home);
  const refused = await installCli({ home, version: '1.0.0', packageDir });
  assert.equal(refused.status, 'conflict');
  assert.equal(refused.exit, 4);
  assert.deepEqual(await snapshotTree(home), before);
});

test('rollback refuses a previous version whose real runtime payload was changed', async () => {
  const home = await freshHome('installer-cli-rollback-modified-payload');
  await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') });
  await installCli({ home, version: '2.0.0', packageDir: await artifact('2.0.0') });
  await writeFile(join(binPaths(home).versionDir, 'dist', 'client.js'), '// changed previous version\n');
  const before = await snapshotTree(home);
  const refused = await rollbackCli({ home });
  assert.equal(refused.status, 'conflict');
  assert.equal(refused.exit, 4);
  assert.deepEqual(await snapshotTree(home), before);
});

test('a package version mismatch refuses before consumer writes', async () => {
  const home = await freshHome('installer-cli-version-mismatch');
  const before = await snapshotTree(home);
  await assert.rejects(
    installCli({ home, version: '2.0.0', packageDir: await artifact('1.0.0') }),
    (error) => error.code === 'USAGE',
  );
  assert.deepEqual(await snapshotTree(home), before);
});

test('a declared asset cannot escape the prepared package through a symlinked parent', async () => {
  const home = await freshHome('installer-cli-source-escape');
  const packageDir = await artifact('3.0.0');
  const pkg = JSON.parse(await readFile(join(packageDir, 'package.json'), 'utf8'));
  await symlink(join(PACKAGE_DIR, 'dist'), join(packageDir, 'external'));
  await writeFile(join(packageDir, 'package.json'), JSON.stringify({
    ...pkg, files: [...pkg.files, 'external/client.js'],
  }));
  const before = await snapshotTree(home);
  await assert.rejects(installCli({ home, version: '3.0.0', packageDir }),
    (error) => error.code === 'USAGE');
  assert.deepEqual(await snapshotTree(home), before);
});

test('unsafe recorded version paths cannot delete files outside the owned payload', async () => {
  const home = await freshHome('installer-cli-unsafe-recorded-version');
  await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0') });
  const paths = binPaths(home);
  const foreign = join(home, 'foreign-retained-file');
  await writeFile(foreign, FOREIGN);
  const state = JSON.parse(await readFile(paths.state, 'utf8'));
  await writeFile(paths.state, JSON.stringify({
    ...state, versions: [relative(join(paths.base, 'versions'), foreign)],
  }));
  const before = await snapshotTree(home);
  await assert.rejects(uninstallCli({ home, apply: true }), (error) => error.code === 'IO');
  assert.deepEqual(await snapshotTree(home), before);
});

test('a displaced backup outside its owned location cannot be restored as the bin', async () => {
  const home = await freshHome('installer-cli-unsafe-recorded-backup');
  const paths = binPaths(home);
  await mkdir(dirname(paths.link), { recursive: true });
  await writeFile(paths.link, FOREIGN);
  await installCli({ home, version: '1.0.0', packageDir: await artifact('1.0.0'), takeOverBin: true });
  const state = JSON.parse(await readFile(paths.state, 'utf8'));
  const unrelated = join(home, 'unrelated-retained-file');
  await writeFile(unrelated, FOREIGN);
  await writeFile(paths.state, JSON.stringify({
    ...state, displaced: { ...state.displaced, backup: unrelated },
  }));
  const before = await snapshotTree(home);
  const refused = await uninstallCli({ home, apply: true });
  assert.equal(refused.exit, 4);
  assert.equal(refused.status, 'conflict');
  assert.deepEqual(await snapshotTree(home), before);
});

test('a missing real SDK runtime entry refuses before installation despite a working CLI version', async () => {
  const home = await freshHome('installer-cli-incomplete-sdk');
  const packageDir = await artifact('4.0.0', ['node_modules/@typesafe-ai/sdk/dist/index.mjs']);
  const before = await snapshotTree(home);
  await assert.rejects(installCli({ home, version: '4.0.0', packageDir }),
    (error) => error.code === 'USAGE');
  assert.deepEqual(await snapshotTree(home), before);
});

test('a declared asset cannot occupy the installer manifest namespace', async () => {
  for (const [version, path] of [
    ['5.0.0', '.classifier-install.json'],
    ['6.0.0', '.CLASSIFIER-INSTALL.JSON'],
  ]) {
    const home = await freshHome('installer-cli-reserved-manifest');
    const packageDir = await artifact(version);
    const pkg = JSON.parse(await readFile(join(packageDir, 'package.json'), 'utf8'));
    await writeFile(join(packageDir, path), JSON.stringify({ version: 2, entries: [] }));
    await writeFile(join(packageDir, 'package.json'), JSON.stringify({
      ...pkg, files: [...pkg.files, path],
    }));
    const before = await snapshotTree(home);
    await assert.rejects(installCli({ home, version, packageDir }),
      (error) => error.code === 'USAGE');
    assert.deepEqual(await snapshotTree(home), before);
  }
});
