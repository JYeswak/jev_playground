import test from 'node:test';
import assert from 'node:assert/strict';
import jevWebSearchRerankHook, { makeWebSearchRerankHandler, parseSearchResult } from './jev-web-search-rerank.ts';

// A recorded synthetic event ID plus a fake requester is the only offline approval.
const APPROVED_EVENT_ID = 'offline-web-search-rerank-001';

function searchEvent() {
  return {
    toolCallId: APPROVED_EVENT_ID,
    toolName: 'web_search',
    input: { query: 'captured query' },
    details: { results: [
      { title: 'First', url: 'https://one.example', snippet: 'first passage' },
      { title: 'Second', url: 'https://two.example', snippet: 'second passage' },
    ] },
  };
}

function answer(choice = 'result-1') {
  return async () => ({ ok: true, choice, confidence: 0.9, probabilities: { 'result-0': 0.1, 'result-1': 0.9 }, latencyMs: 7, model: 'jev-1.13.0', usage: { input_tokens: 10, output_tokens: 2 } });
}

test('non-search events pass through without a call or row', async () => {
  let calls = 0;
  const rows = [];
  const handler = makeWebSearchRerankHandler({ approvedEventId: APPROVED_EVENT_ID, ask: async () => { calls += 1; return answer()(); }, append: async (_path, line) => rows.push(JSON.parse(line)) });
  await handler({ toolName: 'web_fetch', content: 'unchanged' });
  assert.equal(calls, 0);
  assert.equal(rows.length, 0);
});

test('shadow is fail-open and logs hashes plus opened pick/rank1 after ten calls', async () => {
  const rows = [];
  const handler = makeWebSearchRerankHandler({ approvedEventId: APPROVED_EVENT_ID, ask: answer(), append: async (_path, line) => rows.push(JSON.parse(line)), session: 'session-a', now: () => '2026-09-27T00:00:00.000Z' });
  await handler(searchEvent());
  for (let i = 0; i < 10; i += 1) await handler({ toolName: 'open_url', input: { url: i === 0 ? 'https://two.example' : 'https://other.example' } });
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, 'answered');
  assert.equal(rows[0].openedPick, true);
  assert.equal(rows[0].openedRank1, false);
  assert.equal(rows[0].queryHash.length, 64);
  assert.equal(JSON.stringify(rows[0]).includes('captured query'), false);
  assert.equal(JSON.stringify(rows[0]).includes('two.example'), false);
});

test('ten distinct ordinary tool results close the search window before an eleventh-call open', async () => {
  const rows = [];
  const handlers = new Map();
  jevWebSearchRerankHook(
    { on: (name, handler) => handlers.set(name, handler) },
    {
      approvedEventId: APPROVED_EVENT_ID, ask: answer(),
      append: async (_path, line) => rows.push(JSON.parse(line)),
      now: () => '2026-09-27T00:00:00.000Z',
    },
  );
  const ctx = { sessionManager: { getSessionId: () => 'session-a' } };
  await handlers.get('tool_result')(searchEvent(), ctx);
  for (let i = 0; i < 10; i += 1) {
    const event = { toolCallId: `ordinary-${i}`, toolName: 'web_fetch', content: 'unrelated' };
    await handlers.get('tool_result')(event, ctx);
    await handlers.get('tool_execution_end')(event, ctx);
  }
  assert.equal(rows.length, 1);
  assert.equal(rows[0].nextToolCalls, 10);
  assert.equal(rows[0].openedPick, false);
  assert.equal(rows[0].openedRank1, false);
  await handlers.get('tool_result')({ toolCallId: 'eleventh-open', toolName: 'open_url', input: { url: 'https://two.example' } }, ctx);
  assert.equal(rows.length, 1);
});

test('registered callbacks keep repeated call IDs separate across sessions', async () => {
  const rows = [];
  const handlers = new Map();
  jevWebSearchRerankHook(
    { on: (name, handler) => handlers.set(name, handler) },
    { approvedEventId: APPROVED_EVENT_ID, ask: answer(), append: async (_path, line) => rows.push(JSON.parse(line)) },
  );
  for (const session of ['session-a', 'session-b']) {
    const ctx = { sessionManager: { getSessionId: () => session } };
    await handlers.get('tool_result')(searchEvent(), ctx);
    for (let i = 0; i < 10; i += 1) {
      const event = { toolCallId: `ordinary-${i}`, toolName: 'web_fetch', content: 'unrelated' };
      await handlers.get('tool_result')(event, ctx);
      await handlers.get('tool_execution_end')(event, ctx);
    }
  }
  assert.equal(rows.length, 2);
  assert.equal(rows[0].nextToolCalls, 10);
  assert.equal(rows[1].nextToolCalls, 10);
  assert.notEqual(rows[0].sessionHash, rows[1].sessionHash);
});

test('a replacement search logs its partial prior window instead of losing it', async (t) => {
  const nativeTimeout = globalThis.setTimeout;
  let expireDedup;
  t.mock.method(globalThis, 'setTimeout', (fn, delay, ...args) => {
    if (delay === 60_000) { expireDedup ??= fn; return 0; }
    return nativeTimeout(fn, delay, ...args);
  });
  const rows = [];
  const handler = makeWebSearchRerankHandler({
    approvedEventId: APPROVED_EVENT_ID, ask: answer(), session: 'session-a',
    append: async (_path, line) => rows.push(JSON.parse(line)),
  });
  await handler(searchEvent());
  await handler({ toolCallId: 'ordinary-first', toolName: 'web_fetch', content: 'unrelated' });
  expireDedup();
  await handler(searchEvent());
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, 'answered');
  assert.equal(rows[0].nextToolCalls, 2);
  assert.equal(rows[0].openedPick, false);
  for (let i = 0; i < 10; i += 1) {
    await handler({ toolCallId: `later-${i}`, toolName: 'web_fetch', content: 'unrelated' });
  }
  assert.equal(rows.length, 2);
  assert.equal(rows[1].nextToolCalls, 10);
});

test('shadow cap records no call and does not throw', async () => {
  let calls = 0;
  const rows = [];
  const handler = makeWebSearchRerankHandler({ approvedEventId: APPROVED_EVENT_ID, cap: 0, ask: async () => { calls += 1; return answer()(); }, append: async (_path, line) => rows.push(JSON.parse(line)), session: 'session-a' });
  await handler(searchEvent());
  assert.equal(calls, 0);
  assert.equal(rows[0].status, 'not-admitted');
});

test('402 records the failure without changing the observed web result', async () => {
  let calls = 0;
  const rows = [];
  const handler = makeWebSearchRerankHandler({ approvedEventId: APPROVED_EVENT_ID, ask: async () => { calls += 1; throw new Error('HTTP 402 credits exhausted'); }, append: async (_path, line) => rows.push(JSON.parse(line)), session: 'session-a' });
  assert.equal(await handler(searchEvent()), undefined);
  assert.equal(calls, 1);
  assert.equal(rows[0].status, 'auth-or-billing');
  assert.match(rows[0].error, /HTTP 402 credits exhausted/);
});

test('captured event parser ignores malformed or underspecified results', () => {
  assert.equal(parseSearchResult({ toolName: 'web_search', input: { query: 'q' }, details: { results: [{ url: 'one' }] } }), undefined);
});

test('registered callbacks deny before any worker or requester, while retaining a local hashed row', async () => {
  const rows = [];
  const handlers = new Map();
  let requests = 0;
  jevWebSearchRerankHook(
    { on: (name, handler) => handlers.set(name, handler) },
    { ask: async () => { requests++; return answer()(); }, append: async (_path, line) => rows.push(JSON.parse(line)) },
  );
  const event = searchEvent();
  const ctx = { sessionManager: { getSessionId: () => 'session-a' } };
  await handlers.get('tool_result')(event, ctx);
  await handlers.get('tool_execution_end')(event, ctx);
  assert.equal(requests, 0);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, 'not-admitted');
  assert.equal(rows[0].error, 'permission-required');
  assert.equal(rows[0].resultCount, 2);
  assert.equal(JSON.stringify(rows).includes('captured query'), false);
  assert.equal(JSON.stringify(rows).includes('first passage'), false);
});

test('fake approval is bound to the exact event ID; a different event remains denied', async () => {
  const rows = [];
  let requests = 0;
  const handler = makeWebSearchRerankHandler({
    approvedEventId: APPROVED_EVENT_ID, ask: async () => { requests++; return answer()(); },
    append: async (_path, line) => rows.push(JSON.parse(line)), session: 'session-a',
  });
  await handler({ ...searchEvent(), toolCallId: 'another-event' });
  assert.equal(requests, 0);
  assert.equal(rows[0].error, 'permission-required');
  await handler(searchEvent());
  assert.equal(requests, 1);
});
