import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const kitRoot = new URL('..', import.meta.url);
const cli = new URL('../bin/jev.mjs', import.meta.url);

function run(args, cwd) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [cli.pathname, ...args], { cwd, env: { ...process.env, TYPESAFE_API_KEY: undefined }, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

test('omp install copies tools and hook without overwriting user files', async () => {
  const repo = await mkdtemp(join(tmpdir(), 'jev-omp-install-'));
  const first = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(first.code, 0);
  const result = JSON.parse(first.stdout);
  assert.equal(result.status, 'READY');
  assert.equal(result.files.length, 21);
  assert.equal((await readFile(join(repo, '.omp/jev-kit-manifest.json'), 'utf8')).includes('jev-screen.ts'), true);
  const second = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(second.code, 0);
  assert.equal(JSON.parse(second.stdout).status, 'READY');

  await writeFile(join(repo, '.omp/tools/jev-screen.ts'), 'user-owned');
  const third = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(third.code, 1);
  assert.match(JSON.parse(third.stdout).message, /user-edited/);
});
