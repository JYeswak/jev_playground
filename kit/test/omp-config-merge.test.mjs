import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { freshHome } from './cli-support.mjs';
import {
  mergeExtensions,
  readExtensionItems,
  rollbackExtensions,
  verifyConfigSubset,
} from '../dist/install/omp-config-merge.js';

async function snapshotFile(path) {
  const bytes = await readFile(path);
  return `${createHash('sha256').update(bytes).digest('hex')}`;
}

async function writeConfig(home, name, content) {
  const dir = join(home, 'agent');
  await mkdir(dir, { recursive: true });
  const path = join(dir, name);
  await writeFile(path, content);
  return { dir, path };
}

test('merge appends missing entries once and re-run is already', async () => {
  const home = await freshHome('installer-config-block');
  const { dir, path } = await writeConfig(
    home,
    'config.yml',
    'ttsr:\n  enabled: true\nextensions:\n  - /opt/omp/host-ext.ts\n',
  );
  const preImage = await readFile(path, 'utf8');
  const first = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ['/opt/omp/host-ext.ts', 'jev-gate.ts'],
  });
  assert.equal(first.exit, 0);
  assert.equal(first.status, 'merged');
  assert.ok(first.backup.endsWith('.bak'));
  assert.equal(await readFile(first.backup, 'utf8'), preImage);
  const items = readExtensionItems(await readFile(path, 'utf8'));
  assert.ok(items.includes('/opt/omp/host-ext.ts'));
  assert.ok(items.includes('jev-gate.ts'));
  const before = await readFile(path, 'utf8');
  const second = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ['/opt/omp/host-ext.ts', 'jev-gate.ts'],
  });
  assert.equal(second.status, 'already');
  assert.deepEqual(second.writes, []);
  assert.equal(await readFile(path, 'utf8'), before);
});

test('missing extensions key is added', async () => {
  const home = await freshHome('installer-config-missing-key');
  const { dir, path } = await writeConfig(home, 'config.yml', 'ttsr:\n  enabled: true\n');
  const result = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ['jev-gate.ts'],
  });
  assert.equal(result.status, 'merged');
  assert.ok(readExtensionItems(await readFile(path, 'utf8')).includes('jev-gate.ts'));
});

test('commented entries are not treated as installed', async () => {
  const home = await freshHome('installer-config-commented');
  const { dir, path } = await writeConfig(
    home,
    'config.yml',
    'extensions:\n  # - jev-x\n  - jev-gate.ts\n',
  );
  const result = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ['jev-x'],
  });
  assert.equal(result.status, 'merged');
  assert.ok(readExtensionItems(await readFile(path, 'utf8')).includes('jev-x'));
});

test('dedup matches by resolved path and by basename', async () => {
  const home = await freshHome('installer-config-dedup');
  const { dir, path } = await writeConfig(
    home,
    'config.yml',
    'extensions:\n  - /opt/omp/tools/jev-screen.ts\n',
  );
  const result = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ['jev-screen.ts'],
  });
  assert.equal(result.status, 'already');
  assert.deepEqual(result.writes, []);
});

test('an inline empty extensions value refuses with exit 4 and stays byte-identical', async () => {
  const home = await freshHome('installer-config-inline');
  const { path } = await writeConfig(home, 'config.yml', 'extensions: []\n');
  const before = await snapshotFile(path);
  const result = await mergeExtensions({
    configPath: path,
    profileDir: join(home, 'agent'),
    addExtensions: ['jev-gate.ts'],
  });
  assert.equal(result.exit, 4);
  assert.equal(result.status, 'refused');
  assert.deepEqual(result.writes, []);
  assert.equal(await snapshotFile(path), before);
});

test('corrupt YAML fails without writing', async () => {
  const home = await freshHome('installer-config-corrupt');
  const { path } = await writeConfig(home, 'config.yml', 'extensions:\n\t- jev-gate.ts\n');
  const before = await snapshotFile(path);
  const result = await mergeExtensions({
    configPath: path,
    profileDir: join(home, 'agent'),
    addExtensions: ['jev-gate.ts'],
  });
  assert.equal(result.status, 'failed');
  assert.deepEqual(result.writes, []);
  assert.equal(await snapshotFile(path), before);
});

test('CRLF files keep every host entry', async () => {
  const home = await freshHome('installer-config-crlf');
  const { dir, path } = await writeConfig(
    home,
    'config.yml',
    'extensions:\r\n  - /opt/omp/host-ext.ts\r\n',
  );
  const result = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ['jev-gate.ts'],
  });
  assert.equal(result.status, 'merged');
  const crlfItems = readExtensionItems(await readFile(path, 'utf8'));
  assert.ok(crlfItems.includes('/opt/omp/host-ext.ts'));
  assert.ok(crlfItems.includes('jev-gate.ts'));
});
test('a nested map item under extensions fails without writing', async () => {
  const home = await freshHome('installer-config-nested');
  const { path } = await writeConfig(home, 'config.yml', 'extensions:\n  - name: jev-gate.ts\n');
  const before = await snapshotFile(path);
  const result = await mergeExtensions({
    configPath: path,
    profileDir: join(home, 'agent'),
    addExtensions: ['jev-gate.ts'],
  });
  assert.equal(result.status, 'failed');
  assert.deepEqual(result.writes, []);
  assert.equal(await snapshotFile(path), before);
});

test('quoted items with shell-special characters merge verbatim', async () => {
  const home = await freshHome('installer-config-quoted');
  const { dir, path } = await writeConfig(home, 'config.yml', 'extensions:\n');
  const result = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ["'a*b'", "'it''s'", '"hash#tag"'],
  });
  assert.equal(result.status, 'merged');
  const items = readExtensionItems(await readFile(path, 'utf8'));
  assert.ok(items.includes('a*b'));
  assert.ok(items.includes("it's"));
  assert.ok(items.includes('hash#tag'));
});


test('an absolute dev-path predecessor is preserved', async () => {
  const home = await freshHome('installer-config-devpath');
  const { dir, path } = await writeConfig(
    home,
    'config.yml',
    'extensions:\n  - /Users/dev/Developer/jev/.omp/tools/jev-gate.ts\n',
  );
  const result = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ['jev-screen.ts'],
  });
  assert.equal(result.status, 'merged');
  const items = readExtensionItems(await readFile(path, 'utf8'));
  assert.ok(items.includes('/Users/dev/Developer/jev/.omp/tools/jev-gate.ts'));
  assert.ok(items.includes('jev-screen.ts'));
});

test('a read-back that drops a host entry throws', () => {
  assert.throws(
    () => verifyConfigSubset(['/opt/omp/host-ext.ts', 'jev-gate.ts'], ['jev-gate.ts']),
    (error) => error.code === 'CONFIG_MERGE',
  );
  verifyConfigSubset(['/opt/omp/host-ext.ts'], ['/opt/omp/host-ext.ts', 'jev-gate.ts']);
});

test('rollback restores the backup bytes', async () => {
  const home = await freshHome('installer-config-rollback');
  const { dir, path } = await writeConfig(home, 'config.yml', 'extensions:\n  - a.ts\n');
  const original = await readFile(path, 'utf8');
  const merged = await mergeExtensions({
    configPath: path,
    profileDir: dir,
    addExtensions: ['jev-gate.ts'],
  });
  assert.equal(merged.status, 'merged');
  const rolled = await rollbackExtensions({ configPath: path });
  assert.equal(rolled.exit, 0);
  assert.equal(rolled.status, 'rolled-back');
  assert.equal(await readFile(path, 'utf8'), original);
  const missing = await rollbackExtensions({ configPath: join(dir, 'absent.yml') });
  assert.equal(missing.exit, 4);
  assert.equal(missing.status, 'no-backup');
});
