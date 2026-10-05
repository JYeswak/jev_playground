import test from 'node:test';
import assert from 'node:assert/strict';
import { cp, mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
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

test('npm pack installs a stranger copy and doctor reports NOT_RUN without a key', async (t) => {
  const repo = new URL('../..', import.meta.url).pathname;
  const tempRoot = join(repo, 'var', 'agent-tmp');
  await mkdir(tempRoot, { recursive: true });
  const owned = await mkdtemp(join(tempRoot, 'jev-kit-pack-build.'));
  await writeFile(join(owned, '.owner'), JSON.stringify({
    pid: process.pid, label: 'jev-kit-pack-build', repo, created: new Date().toISOString(),
  }) + '\n');
  t.after(() => rm(owned, { recursive: true, force: true }));
  const scratch = join(owned, 'pack');
  const build = join(owned, 'build');
  await mkdir(scratch);
  const kitRoot = new URL('..', import.meta.url).pathname;
  await cp(kitRoot, build, {
    recursive: true,
    filter: (name) => !name.startsWith(join(kitRoot, 'dist')) && !name.includes('/.git/'),
  });
  const packed = await run('npm', ['pack', '--pack-destination', scratch], { cwd: build, env: { ...process.env } });
  assert.equal(packed.code, 0, packed.stderr);
  const files = await import('node:fs/promises');
  const names = await files.readdir(scratch);
  const archive = join(scratch, names.find((name) => name.endsWith('.tgz')));
  const install = await run('npm', ['install', '--prefix', scratch, '--ignore-scripts', '--no-audit', '--no-fund', archive], { cwd: scratch, env: { ...process.env, TYPESAFE_API_KEY: undefined } });
  assert.equal(install.code, 0, install.stderr);
  const entry = join(scratch, 'node_modules', 'jev-kit', 'bin', 'jev.mjs');
  const doctor = await run(process.execPath, [entry, 'doctor', '--robot'], { cwd: scratch, env: { ...process.env, TYPESAFE_API_KEY: undefined } });
  assert.equal(doctor.code, 1, doctor.stderr);
  const body = JSON.parse(doctor.stdout);
  assert.equal(body.schema, 'classifier.doctor.v1');
  assert.equal(body.status, 'NOT_RUN');
  assert.equal(body.data.status, 'NOT_RUN');
});
