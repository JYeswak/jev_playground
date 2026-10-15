import assert from 'node:assert/strict';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';
import { link, mkdir, readFile, rename, symlink, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { doctorFixture, loadDoctorEngine, repoRoot, snapshot } from './doctor-support.mjs';

const detector = 'fm-surfaces-outside-repo-audit';

async function fixture() {
  const f = await doctorFixture('outside-repo', { tier: 'default' });
  const observed = f.inventory.surfaces.find((surface) => surface.id === 'webscreen-global');
  f.ctx.inventory = { schema: f.inventory.schema, profiles: ['default', 'codex'], surfaces: [observed] };
  // File bytes are test data derived from the canonical inventory, not executed hooks.
  const bytes = JSON.stringify(observed);
  const source = join(f.repo, observed.repo);
  await mkdir(dirname(source), { recursive: true });
  await writeFile(source, bytes);
  const git = (args) => {
    const result = spawnSync('git', ['-C', f.repo, ...args], { encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    return result;
  };
  git(['init', '--quiet']);
  git(['add', '--', observed.repo]);
  git(['-c', 'user.name=Doctor fixture', '-c', 'user.email=doctor@example.invalid', 'commit', '--quiet', '-m', '[pending] observed inventory fixture']);
  f.ctx.exec = async (command, args, options) => {
    assert.equal(command, 'git', 'audit must not launch a model or change settings');
    const result = spawnSync(command, args, { ...options, encoding: 'utf8' });
    return { code: result.status, stdout: result.stdout, stderr: result.stderr };
  };
  const targets = ['.omp/agent', '.omp/profiles/codex/agent'].map((base) => join(f.home, base, 'hooks/post', observed.hookfile));
  for (const target of targets) {
    await mkdir(dirname(target), { recursive: true });
    await link(source, target);
  }
  const { runDoctor } = await loadDoctorEngine();
  const run = () => runDoctor({ ...f.ctx, only: detector });
  return { ...f, source, targets, bytes, run };
}

function reasons(result) { return result.findings.map((row) => row.evidence.reason); }

test('outside audit accepts committed hardlinks in every declared profile without changing inputs', async () => {
  const f = await fixture();
  const before = await snapshot(f.home);
  const result = await f.run();
  assert.equal(result.exit_code, 0);
  assert.deepEqual(result.findings, []);
  assert.deepEqual(await snapshot(f.home), before);
});

test('outside audit detects changed installed bytes and clears only after identical hardlink restoration', async () => {
  const f = await fixture();
  const target = f.targets[1];
  const preserved = `${target}.preserved`;
  await rename(target, preserved);
  await writeFile(target, `${f.bytes}\n`);
  assert.deepEqual(reasons(await f.run()), ['installed_bytes_differ']);
  await rename(target, `${target}.changed`);
  await rename(preserved, target);
  assert.equal((await f.run()).exit_code, 0);
});

test('outside audit rejects byte-identical detached copies and missing declared profile installs', async () => {
  const f = await fixture();
  const target = f.targets[1];
  await rename(target, `${target}.preserved`);
  assert.deepEqual(reasons(await f.run()), ['required_install_unavailable']);
  await writeFile(target, f.bytes);
  assert.deepEqual(reasons(await f.run()), ['installed_not_source_hardlink']);
  await rename(target, `${target}.copy`);
  await rename(`${target}.preserved`, target);
  assert.equal((await f.run()).exit_code, 0);
});

test('outside audit rejects missing required source and committed-source drift', async () => {
  const f = await fixture();
  await rename(f.source, `${f.source}.preserved`);
  assert.deepEqual(reasons(await f.run()), ['required_source_unavailable']);
  await rename(`${f.source}.preserved`, f.source);
  await writeFile(f.source, `${f.bytes}\n`);
  assert.deepEqual(reasons(await f.run()), ['source_differs_from_committed']);
  await writeFile(f.source, f.bytes);
  assert.equal((await f.run()).exit_code, 0);
});

test('outside audit clears OFF-writer activity on restoration but never treats silence as switch proof', async () => {
  const f = await fixture();
  const off = f.inventory.surfaces.find((surface) => surface.id === 'websearch-rerank');
  f.ctx.inventory.surfaces.push(off);
  const log = join(f.stateDir, off.log);
  const old = `${JSON.stringify({ ts: new Date(f.ctx.now - 4 * 60 * 60 * 1000).toISOString(), status: 'answered' })}\n`;
  await writeFile(log, old);
  assert.deepEqual(reasons(await f.run()), ['off_switch_coverage_unavailable']);
  await writeFile(log, `${old}${JSON.stringify({ ts: new Date(f.ctx.now).toISOString(), status: 'answered' })}\n`);
  assert.deepEqual(reasons(await f.run()), ['off_switch_coverage_unavailable', 'declared_off_writer_active']);
  await writeFile(log, old);
  assert.deepEqual(reasons(await f.run()), ['off_switch_coverage_unavailable']);
  await writeFile(log, '');
  assert.deepEqual(reasons(await f.run()), ['off_switch_coverage_unavailable']);
  await rename(log, `${log}.preserved`);
  assert.deepEqual(reasons(await f.run()), ['off_switch_coverage_unavailable', 'writer_log_unavailable']);
  await writeFile(log, '{');
  assert.deepEqual(reasons(await f.run()), ['off_switch_coverage_unavailable', 'writer_log_unparseable']);
});

test('outside audit treats future timestamps as UNKNOWN, not known current writer activity', async () => {
  const f = await fixture();
  const off = f.inventory.surfaces.find((surface) => surface.id === 'websearch-rerank');
  f.ctx.inventory.surfaces.push(off);
  const log = join(f.stateDir, off.log);
  for (const timestamp of [f.ctx.now + 1, new Date(f.ctx.now + 1).toISOString()]) {
    await writeFile(log, `${JSON.stringify({ ts: timestamp, status: 'answered' })}\n`);
    const future = await f.run();
    assert.equal(future.exit_code, 1);
    assert.deepEqual(reasons(future), ['off_switch_coverage_unavailable', 'writer_log_future_timestamp']);
    assert.equal(future.findings[1].evidence.future_rows, 1);
    await writeFile(log, `${JSON.stringify({ ts: f.ctx.now, status: 'answered' })}\n`);
    const restored = await f.run();
    assert.deepEqual(reasons(restored), ['off_switch_coverage_unavailable', 'declared_off_writer_active']);
    assert.equal(restored.findings[1].evidence.recent_rows, 1);
  }
});

test('outside audit uses the doctor clock when callers omit now', async () => {
  const f = await fixture();
  const off = f.inventory.surfaces.find((surface) => surface.id === 'websearch-rerank');
  f.ctx.inventory.surfaces.push(off);
  delete f.ctx.now;
  await writeFile(join(f.stateDir, off.log), `${JSON.stringify({ ts: new Date().toISOString(), status: 'answered' })}\n`);
  assert.deepEqual(reasons(await f.run()), ['off_switch_coverage_unavailable', 'declared_off_writer_active']);
});

test('outside audit keeps unsupported schema, scope and unsafe install paths non-green', async () => {
  const f = await fixture();
  const inventory = f.ctx.inventory;
  f.ctx.inventory = { ...inventory, schema: 'unknown' };
  assert.deepEqual(reasons(await f.run()), ['required_inventory_or_scope_unavailable']);
  f.ctx.inventory = { ...inventory, surfaces: [f.inventory.surfaces.find((surface) => surface.id === 'find')] };
  assert.deepEqual(reasons(await f.run()), ['unsupported_surface_scope']);
  const offExtension = f.inventory.surfaces.find((surface) => surface.id === 'skill-hint');
  await writeFile(join(f.stateDir, offExtension.log), '');
  f.ctx.inventory = { ...inventory, surfaces: [offExtension] };
  assert.deepEqual(reasons(await f.run()), ['off_switch_coverage_unavailable']);
  f.ctx.inventory = inventory;
  await rename(f.targets[1], `${f.targets[1]}.preserved`);
  await symlink(f.source, f.targets[1]);
  assert.deepEqual(reasons(await f.run()), ['installed_not_regular_file']);
  assert.equal(await readFile(f.source, 'utf8'), f.bytes);
});
