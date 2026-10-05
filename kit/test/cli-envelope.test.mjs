import test from 'node:test';
import assert from 'node:assert/strict';
import { createEnvelope } from '../src/cli/envelope.mjs';
import { examplePath, freshHome, runCli } from './cli-support.mjs';

function withoutVolatileMeta(stdout) {
  const value = JSON.parse(stdout);
  delete value.meta.latency_ms;
  delete value.meta.usage;
  return `${JSON.stringify(value)}\n`;
}

test('a fake decision emits the required envelope and deterministic bytes outside the two volatile meta fields', async () => {
  const home = await freshHome('classifier-envelope');
  const args = [
    'ask', 'choice', '--state', examplePath('state.json'), '--question', examplePath('question.json'), '--fake', '--json',
  ];
  const first = runCli(args, { home, env: { SOURCE_DATE_EPOCH: '1791158400' } });
  const second = runCli(args, { home, env: { SOURCE_DATE_EPOCH: '1791158400' } });
  assert.equal(first.status, 0, first.stderr);
  assert.equal(second.status, 0, second.stderr);
  assert.equal(first.stderr, '');
  const body = JSON.parse(first.stdout);
  assert.deepEqual(Object.keys(body).sort(), ['ok', 'schema', 'status', 'data', 'meta', 'warnings', 'commands', 'errors'].sort());
  assert.equal(body.ok, true);
  assert.equal(body.schema, 'classifier.ask.v1');
  assert.equal(body.status, 'OK');
  assert.equal(body.data.choice, 'c1');
  assert.equal(typeof body.meta.latency_ms, 'number');
  assert.ok(Object.hasOwn(body.meta, 'usage'));
  assert.equal(Object.hasOwn(body.data, 'latency_ms'), false);
  assert.equal(Object.hasOwn(body.data, 'latencyMs'), false);
  assert.equal(Object.hasOwn(body.data, 'usage'), false);
  assert.equal(withoutVolatileMeta(first.stdout), withoutVolatileMeta(second.stdout));
});

test('the envelope helper keeps only meta latency and usage volatile', () => {
  const body = createEnvelope('ask', { ok: true, choice: 'c1', latencyMs: 17, model: 'fake', usage: { input_tokens: 4 } });
  assert.equal(body.schema, 'classifier.ask.v1');
  assert.equal(body.data.latency_ms, undefined);
  assert.equal(body.data.latencyMs, undefined);
  assert.equal(body.data.usage, undefined);
  assert.equal(body.meta.latency_ms, 17);
  assert.deepEqual(body.meta.usage, { input_tokens: 4 });
});
