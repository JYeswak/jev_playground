import test from 'node:test';
import assert from 'node:assert/strict';
import ompJevReview from '../src/index.ts';

function host() {
  const rows = [];
  let handler;
  return {
    rows,
    fire: (event) => handler(event),
    pi: {
      on: (_e, cb) => { handler = cb; },
      appendEntry: async (type, data) => { rows.push({ type, data }); },
    },
  };
}
const decisions = (h) => h.rows.filter((r) => r.type.endsWith('decision.v1'));
const diffCall = (command) => ({ toolName: 'bash', toolCallId: 'tc-1', input: { command } });

test('ignores every tool call that is not a git diff or show', async () => {
  const h = host();
  ompJevReview(h.pi);
  for (const event of [
    diffCall('echo hello'),
    { toolName: 'read', toolCallId: 'x', input: { command: 'git diff' } },
    { toolName: 'bash', toolCallId: 'y', input: {} },
  ]) assert.equal(await h.fire(event), undefined);
  assert.equal(h.rows.length, 0, 'a non-diff call must not even emit a diagnostic');
});

test('an unset API key records review_error, never a scored pass', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff HEAD~1'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_error');
    assert.equal('probabilities' in row.data, false);   // RED if a default ever reappears
    assert.match(row.data.error, /TYPESAFE_API_KEY is not set/);
    assert.equal(row.data.model, 'none-unconfigured');
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a throwing transport records review_error and never breaks the session', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  globalThis.fetch = async () => { throw new Error('connection reset'); };
  try {
    const h = host();
    ompJevReview(h.pi);
    assert.equal(await h.fire(diffCall('git show abc123')), undefined);
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_error');
    assert.equal('probabilities' in row.data, false);
    assert.match(row.data.error, /connection reset/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a real score is recorded as review_scored with its probabilities', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  globalThis.fetch = async () => ({ ok: true, json: async () => ({ probabilities: { yes: 0.82, no: 0.18 } }) });
  try {
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff --cached'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_scored');
    assert.deepEqual(row.data.probabilities, { yes: 0.82, no: 0.18 });
    assert.equal('error' in row.data, false);
    assert.equal(row.data.model, 'typesafe-systemone');
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a 200 with no probabilities is an error, not a silent pass', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  globalThis.fetch = async () => ({ ok: true, json: async () => ({ unexpected: true }) });
  try {
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_error');
    assert.match(row.data.error, /no probabilities/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a host whose appendEntry throws still returns undefined', async () => {
  const h = host();
  ompJevReview({ on: h.pi.on, appendEntry: async () => { throw new Error('log sink down'); } });
  assert.equal(await h.fire(diffCall('git diff')), undefined);
});
