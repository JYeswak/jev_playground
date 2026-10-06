import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { INSTALL_MANIFEST_MARKER, INSTALL_MANIFEST_VERSION, acquireInstallLock, readInstallManifest, writeInstallManifest } from '../dist/install/manifest.js';
import { freshHome, runCli } from './cli-support.mjs';

function sampleManifest() {
  return {
    version: INSTALL_MANIFEST_VERSION,
    entries: [{ target: 'cli', path: '/opt/classifier', sha256: 'a'.repeat(64), marker: INSTALL_MANIFEST_MARKER, version: '1.0.0' }],
  };
}

async function completedPid() {
  const child = spawn(process.execPath, ['-e', 'process.exit(0)']);
  const pid = child.pid;
  await new Promise((resolve, reject) => {
    child.once('error', reject);
    child.once('exit', resolve);
  });
  assert.ok(pid);
  return pid;
}

test('identical v2 manifest apply preserves bytes and nanosecond mtime', async () => {
  const home = await freshHome('classifier-install-manifest');
  const path = join(home, '.local/state/jev/install/manifest.json');
  const manifest = sampleManifest();

  assert.equal(await readInstallManifest(path), undefined);
  assert.equal(await writeInstallManifest(path, manifest), true);
  const beforeBytes = await readFile(path);
  const beforeStat = await stat(path, { bigint: true });
  assert.deepEqual(await readInstallManifest(path), manifest);
  assert.equal(await writeInstallManifest(path, manifest), false);
  assert.deepEqual(await readFile(path), beforeBytes);
  assert.equal((await stat(path, { bigint: true })).mtimeNs, beforeStat.mtimeNs);
});

test('manifest rejects unknown versions and malformed entry digests without overwriting', async () => {
  const home = await freshHome('classifier-install-manifest-invalid');
  const path = join(home, 'state/install.json');
  await mkdir(join(home, 'state'), { recursive: true });
  const valid = sampleManifest();
  const invalid = { ...valid, version: 1 };
  const original = JSON.stringify(invalid);
  await writeFile(path, original);
  await assert.rejects(writeInstallManifest(path, valid), { code: 'REFUSED' });
  assert.equal(await readFile(path, 'utf8'), original);

  await writeFile(path, JSON.stringify({ ...valid, entries: [{ ...valid.entries[0], sha256: 'not-a-digest' }] }));
  await assert.rejects(readInstallManifest(path), { code: 'REFUSED' });
});

test('install lock refuses a live pid and takes over a dead pid lock', async () => {
  const home = await freshHome('classifier-install-lock');
  const livePath = join(home, 'state/live.lock');
  const live = await acquireInstallLock(livePath);
  await assert.rejects(acquireInstallLock(livePath), { code: 'RETRYABLE' });
  await live.release();

  const stalePath = join(home, 'state/stale.lock');
  await mkdir(stalePath, { recursive: true });
  await writeFile(join(stalePath, 'pid'), `${await completedPid()}\n`);
  const recovered = await acquireInstallLock(stalePath);
  await recovered.release();
  await assert.rejects(stat(stalePath), { code: 'ENOENT' });
});

test('CLI apply reports a live installer lock as retryable and does not install', async () => {
  const home = await freshHome('classifier-install-live-lock');
  const repo = join(home, 'repo');
  await mkdir(join(repo, '.git'), { recursive: true });
  const lock = await acquireInstallLock(join(home, '.local/state/classifier/install.lock'));
  const result = runCli(['install', 'omp-project', '--dir', repo, '--apply', '--robot'], { home });
  assert.equal(result.status, 5, result.stderr);
  assert.equal(JSON.parse(result.stdout).status, 'RETRYABLE');
  await lock.release();
  await assert.rejects(stat(join(repo, '.omp')), { code: 'ENOENT' });
});
