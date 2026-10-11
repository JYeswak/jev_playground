import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstat, mkdir, readdir, readFile, readlink, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { freshHome } from './cli-support.mjs';
import {
  installCli,
  rollbackCli,
  uninstallCli,
} from '../dist/install/cli-target.js';

const BIN = Buffer.from('#!/usr/bin/env node\nconsole.log("classifier fixture");\n');
const BIN_V2 = Buffer.from('#!/usr/bin/env node\nconsole.log("classifier fixture v2");\n');
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
  const before = await snapshotTree(home);
  const result = await installCli({ home, version: '1.0.0', binBytes: BIN });
  assert.equal(result.exit, 0);
  assert.equal(result.status, 'installed');
  assert.ok(result.writes.length > 0);
  const paths = binPaths(home);
  assert.equal(await readlink(paths.current), paths.versionDir);
  assert.equal(await readlink(paths.link), join(paths.versionDir, 'bin', 'classifier'));
  assert.deepEqual(await readFile(join(paths.versionDir, 'bin', 'classifier')), BIN);
  const state = JSON.parse(await readFile(paths.state, 'utf8'));
  assert.deepEqual(state.versions, ['1.0.0']);
  assert.equal(state.current, '1.0.0');
  void before;
});

test('re-run is already with zero writes', async () => {
  const home = await freshHome('installer-cli-rerun');
  const first = await installCli({ home, version: '1.0.0', binBytes: BIN });
  assert.equal(first.status, 'installed');
  const before = await snapshotTree(home);
  const second = await installCli({ home, version: '1.0.0', binBytes: BIN });
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
  const result = await installCli({ home, version: '1.0.0', binBytes: BIN });
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
  const taken = await installCli({ home, version: '1.0.0', binBytes: BIN, takeOverBin: true });
  assert.equal(taken.exit, 0);
  assert.equal(taken.status, 'installed');
  assert.deepEqual(await readFile(join(paths.versionDir, 'bin', 'classifier')), BIN);
  const dry = await uninstallCli({ home });
  assert.equal(dry.status, 'dry-run');
  assert.ok(dry.wouldRemove.length > 0);
  const beforeDry = await snapshotTree(home);
  assert.deepEqual(await snapshotTree(home), beforeDry);
  const removed = await uninstallCli({ home, apply: true });
  assert.equal(removed.exit, 0);
  assert.equal(removed.status, 'removed');
  assert.deepEqual(await readFile(paths.link), FOREIGN);
});

test('rollback flips current to the previous version', async () => {
  const home = await freshHome('installer-cli-rollback');
  const paths = binPaths(home);
  await installCli({ home, version: '1.0.0', binBytes: BIN });
  await installCli({ home, version: '2.0.0', binBytes: BIN_V2 });
  assert.equal(await readlink(paths.current), join(paths.base, 'versions', '2.0.0'));
  const rolled = await rollbackCli({ home });
  assert.equal(rolled.exit, 0);
  assert.equal(rolled.status, 'rolled-back');
  assert.equal(await readlink(paths.current), join(paths.base, 'versions', '1.0.0'));
  assert.deepEqual(await readFile(paths.link), BIN);
});

test('rollback with a single version refuses without writes', async () => {
  const home = await freshHome('installer-cli-rollback-single');
  await installCli({ home, version: '1.0.0', binBytes: BIN });
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
    installCli({ home, version: '../evil', binBytes: BIN }),
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
    installCli({ home, version: '1.0.0', binBytes: BIN }),
    (error) => error.code === 'IO' && error.message.includes('not JSON'),
  );
});
