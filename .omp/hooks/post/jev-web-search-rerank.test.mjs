import test from 'node:test';
import assert from 'node:assert/strict';
import { makeWebSearchRerankHandler, parseSearchResult } from './jev-web-search-rerank.ts';

function searchEvent() {
  return {
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
  const handler = makeWebSearchRerankHandler({ ask: async () => { calls += 1; return answer()(); }, append: async (_path, line) => rows.push(JSON.parse(line)) });
  await handler({ toolName: 'web_fetch', content: 'unchanged' });
  assert.equal(calls, 0);
  assert.equal(rows.length, 0);
});

test('shadow is fail-open and logs hashes plus opened pick/rank1 after ten calls', async () => {
  const rows = [];
  const handler = makeWebSearchRerankHandler({ ask: answer(), append: async (_path, line) => rows.push(JSON.parse(line)), session: 'session-a', now: () => '2026-09-27T00:00:00.000Z' });
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

test('shadow cap records no call and does not throw', async () => {
  let calls = 0;
  const rows = [];
  const handler = makeWebSearchRerankHandler({ cap: 0, ask: async () => { calls += 1; return answer()(); }, append: async (_path, line) => rows.push(JSON.parse(line)) });
  await handler(searchEvent());
  assert.equal(calls, 0);
  assert.equal(rows[0].status, 'not-admitted');
});

test('402 pauses the shadow and fails open', async () => {
  let calls = 0;
  const rows = [];
  const handler = makeWebSearchRerankHandler({ ask: async () => { calls += 1; throw new Error('HTTP 402 credits exhausted'); }, append: async (_path, line) => rows.push(JSON.parse(line)) });
  await handler(searchEvent());
  await handler(searchEvent());
  assert.equal(calls, 1);
  assert.equal(rows[0].status, 'auth-or-billing');
  assert.equal(rows[1].status, 'not-admitted');
});

test('captured event parser ignores malformed or underspecified results', () => {
  assert.equal(parseSearchResult({ toolName: 'web_search', input: { query: 'q' }, details: { results: [{ url: 'one' }] } }), undefined);
});
