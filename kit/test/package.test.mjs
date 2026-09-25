import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

function run(command, args, options) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', reject);
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

test('npm pack installs a stranger copy and doctor reports NOT_RUN without a key', async () => {
  const scratch = await mkdtemp(join(tmpdir(), 'jev-kit-pack-'));
  const packed = await run('npm', ['pack', '--pack-destination', scratch], { cwd: new URL('..', import.meta.url), env: { ...process.env } });
  assert.equal(packed.code, 0, packed.stderr);
  const files = await import('node:fs/promises');
  const names = await files.readdir(scratch);
  const archive = join(scratch, names.find((name) => name.endsWith('.tgz')));
  const install = await run('npm', ['install', '--prefix', scratch, '--ignore-scripts', '--no-audit', '--no-fund', archive], { cwd: scratch, env: { ...process.env, TYPESAFE_API_KEY: undefined } });
  assert.equal(install.code, 0, install.stderr);
  const entry = join(scratch, 'node_modules', 'jev-kit', 'bin', 'jev.mjs');
  const doctor = await run(process.execPath, [entry, 'doctor', '--robot'], { cwd: scratch, env: { ...process.env, TYPESAFE_API_KEY: undefined } });
  assert.equal(doctor.code, 2, doctor.stderr);
  assert.deepEqual(JSON.parse(doctor.stdout).status, 'NOT_RUN');
});
