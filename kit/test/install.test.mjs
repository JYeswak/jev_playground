import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';
import { pathToFileURL } from "node:url";
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

function runNode(args, cwd) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, args, { cwd, env: { ...process.env, TYPESAFE_API_KEY: undefined }, stdio: ["ignore", "pipe", "pipe"] });
    let stdout = ""; let stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("close", (code) => resolve({ code, stdout, stderr }));
  });
}

test('omp install copies tools and hook without overwriting user files', async () => {
  const repo = await mkdtemp(join(tmpdir(), 'jev-omp-install-'));
  const first = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(first.code, 0);
  const result = JSON.parse(first.stdout);
  assert.equal(result.status, 'READY');
  assert.equal((await readFile(join(repo, '.omp/jev-kit-manifest.json'), 'utf8')).includes('jev-gate.ts'), true);
  const manifest = await readFile(join(repo, '.omp/jev-kit-manifest.json'), 'utf8');
  assert.equal(manifest.includes('jev-screen.ts'), true);
  assert.equal(manifest.includes('jev-kit/rerank.ts'), true);
  assert.equal(manifest.includes('jev-kit/verify.ts'), true);
  assert.equal(manifest.includes('jev-kit/classify.ts'), true);
  assert.equal(manifest.includes('jev-kit/gate.ts'), true);
  assert.equal(manifest.includes("jev-kit/coding-agent-seat.mjs"), true);
  const imported = await Promise.all(["jev-flag.ts", "jev-screen.ts"].map((name) => runNode(["--experimental-strip-types", "-e", `await import(${JSON.stringify(pathToFileURL(join(repo, ".omp/tools", name)).href)})`], repo)));
  assert.deepEqual(imported.map((row) => row.code), [0, 0]);
  const second = await run(["omp", "install", "--dir", repo, "--robot"], kitRoot);
  assert.equal(second.code, 0);
  assert.equal(JSON.parse(second.stdout).status, 'READY');

  await writeFile(join(repo, '.omp/tools/jev-screen.ts'), 'user-owned');
  const third = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(third.code, 1);
  assert.match(JSON.parse(third.stdout).message, /user-edited/);
});

test('install never replaces the host extension list or silently enables new extensions', async () => {
  const repo = await mkdtemp(join(tmpdir(), 'jev-omp-config-'));
  await mkdir(join(repo, '.omp'));
  const hostConfig = 'extensions:\n  - /host/guard.ts\n';
  await writeFile(join(repo, '.omp/config.yml'), hostConfig);
  const installed = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(installed.code, 0, installed.stdout);
  assert.equal(await readFile(join(repo, '.omp/config.yml'), 'utf8'), hostConfig);
  const result = JSON.parse(installed.stdout);
  assert.equal(result.extensionActivation, 'MANUAL_REQUIRED');
  assert.ok(!result.files.includes('.omp/config.yml'));
});

test('unmanaged tool collision refuses without overwriting its bytes', async () => {
  const repo = await mkdtemp(join(tmpdir(), 'jev-omp-collision-'));
  await mkdir(join(repo, '.omp/tools'), { recursive: true });
  const existing = 'operator tool; do not overwrite';
  await writeFile(join(repo, '.omp/tools/jev-gate.ts'), existing);
  const attempted = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(attempted.code, 1);
  assert.match(JSON.parse(attempted.stdout).message, /existing files without installer manifest/);
  assert.equal(await readFile(join(repo, '.omp/tools/jev-gate.ts'), 'utf8'), existing);
});

test('prior managed config requires an explicit owner migration', async () => {
  const repo = await mkdtemp(join(tmpdir(), 'jev-omp-legacy-'));
  await mkdir(join(repo, '.omp'));
  const oldConfig = 'extensions:\n  - ./.omp/extensions/jev-rerank.ts\n';
  await writeFile(join(repo, '.omp/config.yml'), oldConfig);
  await writeFile(join(repo, '.omp/jev-kit-manifest.json'), JSON.stringify({ version: 1, files: { 'config.yml': 'previous-hash' } }));
  const attempted = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(attempted.code, 1);
  assert.match(JSON.parse(attempted.stdout).message, /owner review/);
  assert.equal(await readFile(join(repo, '.omp/config.yml'), 'utf8'), oldConfig);
});

test('omp uninstall dry-runs by default and removes exactly manifest files on --apply', async () => {
  const repo = await mkdtemp(join(tmpdir(), 'jev-omp-uninstall-'));
  const installed = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(installed.code, 0);
  const listed = await run(['omp', 'uninstall', '--dir', repo, '--robot'], kitRoot);
  assert.equal(listed.code, 0);
  const dry = JSON.parse(listed.stdout);
  assert.equal(dry.status, 'DRY_RUN');
  assert.ok(dry.files.length > 10);
  assert.ok(dry.files.includes('.omp/jev-kit-manifest.json'));
  const stillThere = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(stillThere.code, 0, 'dry run must remove nothing');
  const applied = await run(['omp', 'uninstall', '--dir', repo, '--apply', '--robot'], kitRoot);
  assert.equal(applied.code, 0);
  const done = JSON.parse(applied.stdout);
  assert.equal(done.status, 'REMOVED');
  assert.deepEqual(done.kept, []);
  for (const f of done.files) {
    let gone = false;
    try { await readFile(join(repo, f), 'utf8'); } catch { gone = true; }
    assert.equal(gone, true, `${f} still present after uninstall --apply`);
  }
});

test('omp uninstall keeps user-edited and non-manifest files, refuses without a manifest', async () => {
  const repo = await mkdtemp(join(tmpdir(), 'jev-omp-uninstall-keep-'));
  const installed = await run(['omp', 'install', '--dir', repo, '--robot'], kitRoot);
  assert.equal(installed.code, 0);
  const owned = 'operator-owned tool file';
  await writeFile(join(repo, '.omp/tools/jev-gate.ts'), owned);
  await writeFile(join(repo, '.omp/tools/operator-extra.ts'), 'operator file, never in manifest');
  const applied = await run(['omp', 'uninstall', '--dir', repo, '--apply', '--robot'], kitRoot);
  assert.equal(applied.code, 0);
  const done = JSON.parse(applied.stdout);
  assert.ok(done.kept.includes('.omp/tools/jev-gate.ts'));
  assert.equal(await readFile(join(repo, '.omp/tools/jev-gate.ts'), 'utf8'), owned);
  assert.equal(await readFile(join(repo, '.omp/tools/operator-extra.ts'), 'utf8'), 'operator file, never in manifest');
  const bare = await mkdtemp(join(tmpdir(), 'jev-omp-uninstall-bare-'));
  const refused = await run(['omp', 'uninstall', '--dir', bare, '--robot'], kitRoot);
  assert.equal(refused.code, 1);
  assert.match(JSON.parse(refused.stdout).message, /no installer manifest/);
});
