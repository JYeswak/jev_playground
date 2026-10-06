import assert from 'node:assert/strict';
import { mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
import { freshHome, repoRoot } from './cli-support.mjs';

export async function loadDoctorEngine() {
  const engine = await import('../src/doctor/engine.mjs');
  assert.equal(typeof engine.runDoctor, 'function', 'doctor engine must implement the report contract');
  return engine;
}

export async function loadReadiness() {
  const readiness = await import('../src/doctor/readiness.mjs');
  assert.equal(typeof readiness.runHealth, 'function', 'health must expose the quick read-only projection');
  return readiness;
}


export async function doctorFixture(label, { tier = 'quick' } = {}) {
  const home = await freshHome(label);
  const repo = join(home, 'repo');
  const stateDir = join(home, 'state');
  await mkdir(join(repo, 'work/jev-inventory'), { recursive: true });
  await mkdir(stateDir, { recursive: true });
  const inventory = JSON.parse(await readFile(join(repoRoot, 'work/jev-inventory/expected.json'), 'utf8'));
  await writeFile(join(repo, 'work/jev-inventory/expected.json'), JSON.stringify(inventory));
  const calls = { exec: [], fetch: [] };
  const ctx = {
    repo,
    home,
    stateDir,
    inventory,
    now: Date.parse('2026-10-06T12:00:00Z'),
    tier,
    online: false,
    env: { PATH: '', SOURCE_DATE_EPOCH: '1791288000' },
    exec: async (command, args = [], options = {}) => {
      calls.exec.push({ command, args, options });
      return { code: 1, stdout: '', stderr: '' };
    },
    fetch: async (url, init = {}) => {
      calls.fetch.push({ url, init });
      return { ok: true, status: 200 };
    },
    calls,
  };
  return { home, repo, stateDir, inventory, ctx, calls };
}

export async function snapshot(root) {
  const result = [];
  async function walk(dir) {
    for (const entry of await readdir(dir, { withFileTypes: true })) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) {
        await walk(path);
      } else if (entry.isFile()) {
        const bytes = await readFile(path);
        result.push([path.slice(root.length), createHash('sha256').update(bytes).digest('hex')]);
      } else {
        result.push([path.slice(root.length), (await stat(path)).mode]);
      }
    }
  }
  await walk(root);
  return result.sort(([left], [right]) => left.localeCompare(right));
}

export { repoRoot };
