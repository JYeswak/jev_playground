import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstat, mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
import { freshHome } from './cli-support.mjs';
import { installSkills, uninstallSkills } from '../dist/install/skills-target.js';

const testDir = dirname(fileURLToPath(import.meta.url));
const sourceDir = join(testDir, 'fixtures', 'installer', 'skills');

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

test('install copies the packaged skill tree into one store with a marker', async () => {
  const home = await freshHome('installer-skills-fresh');
  const storeDir = join(home, 'skills');
  const result = await installSkills({ storeDir, sourceDir });
  assert.equal(result.exit, 0);
  assert.equal(result.status, 'installed');
  assert.deepEqual(
    await readFile(join(storeDir, 'jev-tools', 'SKILL.md'), 'utf8'),
    await readFile(join(sourceDir, 'jev-tools', 'SKILL.md'), 'utf8'),
  );
  assert.deepEqual(
    await readFile(join(storeDir, 'jev-tools', 'references', 'notes.md'), 'utf8'),
    await readFile(join(sourceDir, 'jev-tools', 'references', 'notes.md'), 'utf8'),
  );
  const marker = JSON.parse(await readFile(join(storeDir, '.classifier-skills.json'), 'utf8'));
  assert.ok(marker.files.includes('jev-tools/SKILL.md'));
  assert.ok(marker.files.includes('jev-tools/references/notes.md'));
});

test('re-run is already with zero writes', async () => {
  const home = await freshHome('installer-skills-rerun');
  const storeDir = join(home, 'skills');
  const first = await installSkills({ storeDir, sourceDir });
  assert.equal(first.status, 'installed');
  const before = await snapshotTree(storeDir);
  const second = await installSkills({ storeDir, sourceDir });
  assert.equal(second.exit, 0);
  assert.equal(second.status, 'already');
  assert.deepEqual(second.writes, []);
  assert.deepEqual(await snapshotTree(storeDir), before);
});

test('a hand-written skill file stays byte-identical on conflict', async () => {
  const home = await freshHome('installer-skills-conflict');
  const storeDir = join(home, 'skills');
  await mkdir(join(storeDir, 'jev-tools'), { recursive: true });
  const handWritten = '# hand-written skill\n';
  await writeFile(join(storeDir, 'jev-tools', 'SKILL.md'), handWritten);
  const before = await snapshotTree(storeDir);
  const result = await installSkills({ storeDir, sourceDir });
  assert.equal(result.exit, 4);
  assert.equal(result.status, 'conflict');
  assert.deepEqual(result.writes, []);
  assert.equal(await readFile(join(storeDir, 'jev-tools', 'SKILL.md'), 'utf8'), handWritten);
  assert.deepEqual(await snapshotTree(storeDir), before);
});

test('uninstall dry-runs by default and removes only marked files on apply', async () => {
  const home = await freshHome('installer-skills-uninstall');
  const storeDir = join(home, 'skills');
  await installSkills({ storeDir, sourceDir });
  await writeFile(join(storeDir, 'unmarked.md'), 'user file\n');
  const dry = await uninstallSkills({ storeDir });
  assert.equal(dry.status, 'dry-run');
  assert.ok(dry.wouldRemove.includes('jev-tools/SKILL.md'));
  assert.equal(dry.wouldRemove.includes('unmarked.md'), false);
  const beforeDry = await snapshotTree(storeDir);
  assert.deepEqual(await snapshotTree(storeDir), beforeDry);
  const removed = await uninstallSkills({ storeDir, apply: true });
  assert.equal(removed.exit, 0);
  assert.equal(removed.status, 'removed');
  assert.equal(await readFile(join(storeDir, 'unmarked.md'), 'utf8'), 'user file\n');
  let markerGone = false;
  try {
    await readFile(join(storeDir, '.classifier-skills.json'));
  } catch (error) {
    if (error && error.code === 'ENOENT') markerGone = true;
    else throw error;
  }
  assert.equal(markerGone, true);
});

test('uninstall without a marker refuses an unmarked tree', async () => {
  const home = await freshHome('installer-skills-unknown');
  const storeDir = join(home, 'skills');
  await mkdir(storeDir, { recursive: true });
  await writeFile(join(storeDir, 'notes.md'), 'user file\n');
  const before = await snapshotTree(storeDir);
  const result = await uninstallSkills({ storeDir, apply: true });
  assert.equal(result.exit, 4);
  assert.equal(result.status, 'unknown-store');
  assert.deepEqual(result.writes, []);
  assert.deepEqual(await snapshotTree(storeDir), before);
});
