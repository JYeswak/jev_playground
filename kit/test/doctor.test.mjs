import test from 'node:test';
import assert from 'node:assert/strict';
import { chmod, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { freshHome, runCli } from './cli-support.mjs';
import { doctorFixture, loadDoctorEngine, snapshot } from './doctor-support.mjs';

test('keyless doctor exits 1, reports the absent source, and enumerates six OMP tools', async () => {
  const home = await freshHome('doctor-keyless');
  const result = runCli(['doctor', '--json', '--only', 'fm-secrets-no-key-source'], { home, env: { PATH: '' } });
  assert.equal(result.status, 1, result.stderr);
  assert.equal(result.stderr, '');
  const report = JSON.parse(result.stdout);
  assert.equal(report.schema_version, '1.0');
  assert.equal(Object.hasOwn(report, 'schema'), false);
  assert.equal(report.state, 'DONE_FINDINGS');
  assert.equal(report.backends.jev.key_source, 'none');
  assert.equal(report.backends.jev.status, 'NOT_RUN');
  assert.ok(report.findings.some((finding) => finding.id === 'fm-secrets-no-key-source'));
  assert.deepEqual(
    report.checks.filter((check) => check.ran).map((check) => check.id),
    ['fm-secrets-no-key-source'],
  );
  const toolsCheck = report.checks.find((check) => check.id === 'fm-plugins-omp-tool-missing');
  assert.equal(toolsCheck.data_sources.filter((source) => source.includes('/.omp/tools/')).length, 6);
});

test('robot doctor wraps the same report in the CLI envelope', async () => {
  const home = await freshHome('doctor-robot');
  const result = runCli(['doctor', '--robot', '--only', 'fm-secrets-no-key-source'], {
    home,
    env: { PATH: '', NO_COLOR: '1', CI: 'true' },
  });
  assert.equal(result.status, 1, result.stderr);
  assert.equal(result.stderr, '');
  const envelope = JSON.parse(result.stdout);
  assert.equal(envelope.schema, 'classifier.doctor.v1');
  assert.equal(envelope.status, 'FINDINGS');
  assert.equal(envelope.data.backends.jev.key_source, 'none');
  assert.deepEqual(
    envelope.data.checks.filter((check) => check.ran).map((check) => check.id),
    ['fm-secrets-no-key-source'],
  );
  assert.ok(!result.stdout.includes('\u001b['));
});

test('doctor schema is deterministic and diagnosis leaves the target tree unchanged', async () => {
  const engine = await loadDoctorEngine();
  const { home, ctx, calls } = await doctorFixture('doctor-readonly');
  const before = await snapshot(home);
  const first = await engine.runDoctor(ctx);
  const second = await engine.runDoctor(ctx);
  const stable = (report) => ({
    ...report,
    duration_ms: 0,
    checks: report.checks.map(({ duration_ms, ...check }) => check),
  });
  assert.deepEqual(stable(first), stable(second));
  assert.deepEqual(Object.keys(first).sort(), [
    'backends', 'checks', 'doctor_contract_version', 'doctor_version', 'duration_ms',
    'exit_code', 'findings', 'finished_at', 'jev_on_path', 'next_steps', 'notes', 'ok',
    'online', 'repo', 'run_dir', 'run_id', 'schema_version', 'started_at', 'state',
    'summary', 'target_sha', 'tier', 'tool', 'tool_version',
  ].sort());
  assert.equal(first.schema_version, '1.0');
  assert.equal(first.doctor_contract_version, '1.0');
  assert.equal(first.run_dir, null);
  assert.equal(first.repo, ctx.repo);
  assert.equal(first.tier, 'quick');
  assert.equal(first.backends.jev.status, 'NOT_RUN');
  assert.equal(first.backends.jev.key_source, 'none');
  assert.ok(first.findings.some((finding) => finding.id === 'fm-secrets-no-key-source'));
  assert.ok(first.checks.every((check) => Array.isArray(check.data_sources)
    && check.data_sources.every((source) => typeof source === 'string' && source.length > 0)));
  assert.ok(calls.fetch.every((call) => call.url === 'http://127.0.0.1:11300/healthz'));
  assert.equal(calls.fetch.length, 2);
  assert.ok(calls.exec.every((call) => !call.args.join(' ').includes('check-hook-loads.mjs')));
  assert.deepEqual(await snapshot(home), before);
});

test('doctor redacts command-bearing log values from the JSON report', async () => {
  const engine = await loadDoctorEngine();
  const { stateDir, ctx } = await doctorFixture('doctor-secret-redaction');
  const logPath = join(stateDir, 'gate-observe.jsonl');
  await writeFile(logPath, `${JSON.stringify({ cmd: 'sk-test-abc123', reason: 'daily-cap' })}\n`);
  await chmod(logPath, 0o600);
  const report = await engine.runDoctor(ctx);
  assert.ok(report.findings.some((finding) => finding.id === 'fm-logs-mode-too-open'));
  assert.ok(!JSON.stringify(report).includes('sk-test-abc123'));
});

test('doctor marks repository-scoped checks unavailable without a repository', async () => {
  const engine = await loadDoctorEngine();
  const { ctx } = await doctorFixture('doctor-no-repo');
  ctx.repo = null;
  ctx.inventory = null;
  const report = await engine.runDoctor(ctx);
  const repoChecks = report.checks.filter((check) => check.id === 'fm-plugins-omp-tool-missing'
    || check.id === 'fm-hooks-load-failure');
  assert.ok(repoChecks.length > 0);
  assert.ok(repoChecks.every((check) => check.ran === false && check.provenance === 'unavailable'));
  assert.ok(!report.findings.some((finding) => repoChecks.some((check) => check.id === finding.id)));
});
