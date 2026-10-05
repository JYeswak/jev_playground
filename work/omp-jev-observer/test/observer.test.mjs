import test from 'node:test';
import assert from 'node:assert/strict';
import ompJevObserver, { createObserver, installObserver } from '../src/observer.mjs';
import { mkdir, unlink, writeFile } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join } from 'node:path';

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
  assert.equal(records[0].toolCallId, 'synthetic-1');
  assert.equal('dcgVerdict' in records[0], false);
  assert.equal(records[0].tool, 'bash');
  assert.equal(records[0].costUsd, 0.001);
});

test('Jev error returns undefined and records the error without cost', async () => {
  const { observer, records } = setup({ classify: async () => { throw new Error('synthetic Jev failure'); } });
  const result = await observer(event, context);
  assert.equal(result, undefined);
  assert.match(records[0].error, /synthetic Jev failure/);
  assert.equal('costUsd' in records[0], false);
  assert.equal(records[0].probabilities.flag, null);
  assert.equal(records[0].probabilities.pass, null);
});

test('missing classifier cost is absent rather than zero', async () => {
  const { observer, records } = setup({ classify: async () => ({ questionSet: [], probabilities: {} }) });
  const result = await observer(event, context);
  assert.equal(result, undefined);
  assert.equal(records.length, 1);
  assert.equal('costUsd' in records[0], false);
});

test('timeout returns undefined and records a timeout decision', async () => {
  const { observer, records } = setup({ timeoutMs: 5, classify: () => new Promise(() => {}) });
  const result = await observer(event, context);
  assert.equal(result, undefined);
  assert.equal(records.length, 1);
  assert.match(records[0].error, /observer timeout/);
  assert.equal('costUsd' in records[0], false);
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

test('live-shaped bash event preserves toolCallId', async () => {
  const { observer, records } = setup();
  const result = await observer({ type: 'tool_call', name: 'bash', toolCallId: 'live-shaped-1', input: { command: 'echo live-shaped' } }, context);
  assert.equal(result, undefined);
  assert.equal(records.length, 1);
  assert.equal(records[0].tool, 'bash');
  assert.equal(records[0].toolCallId, 'live-shaped-1');
});

test('missing gate and session context stay absent without blocking', async () => {
  let handler;
  const records = [];
  const pi = {
    on: (_event, callback) => { handler = callback; },
    appendEntry: async (type, data) => {
      if (type === 'com.zeststream.omp-jev-observer.decision.v1') records.push(data);
    },
  };
  installObserver(pi, { classify: async () => ({ questionSet: [], probabilities: {}, costUsd: 0 }), logger: { append: async (record) => { records.push(record); return true; } }, diagnostic: async () => {} });
  const result = await handler({ type: 'tool_call', toolName: 'bash', toolCallId: 'no-context-1', input: { command: 'echo no-context' } }, {});
  assert.equal(result, undefined);
  assert.equal(records.length, 1);
  assert.equal(records[0].toolCallId, 'no-context-1');
  assert.equal('sessionId' in records[0], false);
  assert.equal('dcgVerdict' in records[0], false);
});
test('presence-OFF skips observer classification in the exported extension and factory', async () => {
  const stateDir = join(homedir(), '.local', 'state', 'jev');
  const marker = join(stateDir, 'jev-lab-observer.off');
  await mkdir(stateDir, { recursive: true });
  await writeFile(marker, 'operator off');
  const previousKey = process.env.TYPESAFE_API_KEY;
  const previousFetch = globalThis.fetch;
  let classifyCalls = 0;
  let fetchCalls = 0;
  process.env.TYPESAFE_API_KEY = 'offline-test-key';
  globalThis.fetch = async () => { fetchCalls += 1; throw new Error('unexpected Jev request'); };
  try {
    let extensionHandler;
    const entries = [];
    ompJevObserver({
      on: (_name, handler) => { extensionHandler = handler; },
      appendEntry: async (type, data) => { entries.push({ type, data }); },
    });
    assert.equal(await extensionHandler(event, context), undefined);
    const observer = createObserver({
      logger: { append: async () => { throw new Error('unexpected decision row'); } },
      dcg: async () => ({ verdict: 'allow' }),
      classify: async () => { classifyCalls += 1; return { questionSet: [], probabilities: {} }; },
    });
    assert.equal(await observer(event, context), undefined);
    assert.equal(classifyCalls, 0);
    assert.equal(fetchCalls, 0);
    assert.equal(entries.some((row) => row.type.endsWith('decision.v1')), false);
  } finally {
    globalThis.fetch = previousFetch;
    if (previousKey === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previousKey;
    await unlink(marker);
  }
});
