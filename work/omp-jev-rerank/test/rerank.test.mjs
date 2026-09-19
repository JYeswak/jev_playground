import test from 'node:test';
import assert from 'node:assert/strict';
import ompJevRerank from '../src/index.ts';

function host() {
  const rows = [];
  let handler;
  return {
    rows,
    fire: (event) => handler(event),
    pi: { on: (_e, cb) => { handler = cb; }, appendEntry: async (t, d) => { rows.push({ t, d }); } },
  };
}
const decisions = (h) => h.rows.filter((r) => r.t.endsWith('decision.v1'));
const lines = (n) => Array.from({ length: n }, (_, i) => `src/file${i}.ts:${i}: const thing = ${i};`).join('\n');
const grepResult = (n, extra = {}) => ({
  toolName: 'grep',
  toolCallId: 'tc-1',
  input: { pattern: 'const thing', i: 'find the definition' },
  content: [{ type: 'text', text: lines(n) }],
  ...extra,
});

function withFetch(impl, body) {
  return async () => {
    const real = globalThis.fetch;
    const prev = process.env.TYPESAFE_API_KEY;
    process.env.TYPESAFE_API_KEY = 'test-key';
    globalThis.fetch = impl;
    try { await body(); }
    finally {
      globalThis.fetch = real;
      if (prev === undefined) delete process.env.TYPESAFE_API_KEY; else process.env.TYPESAFE_API_KEY = prev;
    }
  };
}
const answers = (payload) => async () => ({ ok: true, status: 200, text: async () => JSON.stringify(payload) });

test('ignores tools that are not searches, and errored results', async () => {
  const h = host();
  ompJevRerank(h.pi);
  await h.fire({ toolName: 'bash', content: [{ text: lines(20) }] });
  await h.fire(grepResult(20, { isError: true }));
  assert.equal(h.rows.length, 0, 'no diagnostic, no decision, no API call');
});

test('a short result list is not worth an API call', async () => {
  const h = host();
  ompJevRerank(h.pi);
  await h.fire(grepResult(3));
  assert.equal(h.rows.length, 0);
});

test('content that is a bare string, not an array of parts, is ignored rather than crashing', async () => {
  const h = host();
  ompJevRerank(h.pi);
  // the shape I originally invented — must not be silently accepted
  assert.equal(await h.fire({ toolName: 'grep', result: lines(20), input: {} }), undefined);
  assert.equal(h.rows.length, 0);
});

test('a scored list records scores, hit count, and the count actually scored', withFetch(
  answers({ answers: { definitional: { noul: 0.81 }, ordered: { noul: 0.22 }, noise: { noul: 0.4 } } }),
  async () => {
    const h = host();
    ompJevRerank(h.pi);
    await h.fire(grepResult(42));            // above MAX_HITS, must be capped
    const [row] = decisions(h);
    assert.equal(row.d.kind, 'rerank_scored');
    assert.deepEqual(row.d.scores, { definitional: 0.81, ordered: 0.22, noise: 0.4 });
    assert.equal(row.d.hitCount, 42, 'the real hit count is reported');
    assert.equal(row.d.scoredCount, 30, 'only MAX_HITS candidates were sent');
    assert.equal('error' in row.d, false);
  },
));

test('an unset key records rerank_error with no scores, never a clean list', async () => {
  const prev = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevRerank(h.pi);
    await h.fire(grepResult(20));
    const [row] = decisions(h);
    assert.equal(row.d.kind, 'rerank_error');
    assert.equal('scores' in row.d, false);
    assert.equal(row.d.failure, 'unconfigured');
  } finally { if (prev !== undefined) process.env.TYPESAFE_API_KEY = prev; }
});

test('a transport failure records rerank_error and never throws into the host', withFetch(
  async () => { throw new Error('connection reset'); },
  async () => {
    const h = host();
    ompJevRerank(h.pi);
    assert.equal(await h.fire(grepResult(20)), undefined);
    const [row] = decisions(h);
    assert.equal(row.d.kind, 'rerank_error');
    assert.equal(row.d.failure, 'transport');
  },
));

test('a host whose appendEntry throws still returns undefined', withFetch(
  answers({ answers: { definitional: { noul: 0.5 } } }),
  async () => {
    const h = host();
    ompJevRerank({ on: h.pi.on, appendEntry: async () => { throw new Error('sink down'); } });
    assert.equal(await h.fire(grepResult(20)), undefined);
  },
));
