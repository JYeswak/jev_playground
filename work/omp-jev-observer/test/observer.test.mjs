import test from 'node:test';
import assert from 'node:assert/strict';
import { createObserver } from '../src/observer.mjs';

function setup({ classify, dcg = async () => ({ verdict: 'allow' }), enabled = true, timeoutMs = 25 } = {}) {
  const records = [];
  const observer = createObserver({
    logger: { append: async (record) => { records.push(record); return true; } },
    dcg,
    classify: classify ?? (async () => ({ questionSet: ['flag?'], probabilities: { flag: 0.1, pass: 0.9 }, costUsd: 0.001 })),
    enabled,
    timeoutMs,
    now: () => '2026-09-19T00:00:00.000Z',
  });
  return { observer, records };
}

const event = { type: 'tool_call', toolName: 'bash', input: { command: 'printf hello' }, toolCallId: 'synthetic-1' };
const context = { sessionId: 'offline-session' };

test('success returns undefined and records an allow decision', async () => {
  const { observer, records } = setup();
  const result = await observer(event, context);
  assert.equal(result, undefined);
  assert.equal(records.length, 1);
  assert.equal(records[0].recordType, 'decision');
  assert.equal(records[0].dcgVerdict, 'allow');
  assert.equal(records[0].tool, 'bash');
});

test('Jev error returns undefined and records the error', async () => {
  const { observer, records } = setup({ classify: async () => { throw new Error('synthetic Jev failure'); } });
  const result = await observer(event, context);
  assert.equal(result, undefined);
  assert.equal(records.length, 1);
  assert.match(records[0].error, /synthetic Jev failure/);
});

test('timeout returns undefined and records a timeout decision', async () => {
  const { observer, records } = setup({ timeoutMs: 5, classify: () => new Promise(() => {}) });
  const result = await observer(event, context);
  assert.equal(result, undefined);
  assert.equal(records.length, 1);
  assert.match(records[0].error, /observer timeout/);
});

test('dcg block is skipped and never returned by the observer', async () => {
  const { observer, records } = setup({ dcg: async () => ({ verdict: 'block' }) });
  const result = await observer(event, context);
  assert.equal(result, undefined);
  assert.equal(records.length, 0);
});

test('disabled observer is inert', async () => {
  const { observer, records } = setup({ enabled: false });
  const result = await observer(event, context);
  assert.equal(result, undefined);
  assert.equal(records.length, 0);
});
