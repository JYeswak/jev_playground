import test from 'node:test';
import assert from 'node:assert/strict';
import { doctorFixture, loadReadiness, snapshot } from './doctor-support.mjs';

test('health forces quick offline checks and returns compact read-only status', async () => {
  const readiness = await loadReadiness();
  const { home, ctx, calls } = await doctorFixture('health-readonly', { tier: 'deep' });
  ctx.online = true;
  const before = await snapshot(home);
  const health = await readiness.runHealth(ctx);
  assert.deepEqual(Object.keys(health).sort(), [
    'checks', 'clef', 'findings', 'key_source', 'last_run', 'schema_version', 'status',
  ].sort());
  assert.equal(typeof health.checks, 'number');
  assert.equal(health.clef, 'up');
  assert.equal(health.last_run, null);
  assert.equal(health.schema_version, '1.0');
  assert.equal(health.status, 'findings');
  assert.equal(health.key_source, 'none');
  assert.ok(health.findings.some((finding) => finding.id === 'fm-secrets-no-key-source'));
  assert.ok(health.findings.every((finding) => Object.keys(finding).sort().join(',') === 'id,severity'));
  assert.equal(calls.fetch.length, 1);
  assert.ok(calls.fetch.every((call) => call.url === 'http://127.0.0.1:11300/healthz'));
  assert.deepEqual(await snapshot(home), before);
});
