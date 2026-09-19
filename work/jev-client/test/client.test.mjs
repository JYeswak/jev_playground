import test from 'node:test';
import assert from 'node:assert/strict';
import { askJev, SYSTEMONE_ENDPOINT } from '../src/index.ts';

const QUESTIONS = { harm: 'is this harmful?' };
const STATE = { command: 'rm -rf /' };

function withFetch(impl, body) {
  return async () => {
    const real = globalThis.fetch;
    const prevKey = process.env.TYPESAFE_API_KEY;
    process.env.TYPESAFE_API_KEY = 'test-key';
    globalThis.fetch = impl;
    try { await body(); }
    finally {
      globalThis.fetch = real;
      if (prevKey === undefined) delete process.env.TYPESAFE_API_KEY;
      else process.env.TYPESAFE_API_KEY = prevKey;
    }
  };
}
const respond = (status, payload) => async () => ({
  ok: status < 400, status, text: async () => JSON.stringify(payload),
});

test('sends the EXACT wire shape that works, not an invented one', withFetch(
  async (url, init) => {
    assert.equal(url, SYSTEMONE_ENDPOINT);
    assert.equal(init.headers.Authorization, 'Bearer test-key');
    const sent = JSON.parse(init.body);
    // the three things every hand-rolled call got wrong
    assert.equal(typeof sent.model, 'string', 'model is required');
    assert.deepEqual(sent.state, STATE, 'payload goes in `state`, not `context`');
    assert.deepEqual(sent.questions, { harm: { type: 'noul', instructions: 'is this harmful?' } },
      'questions is an OBJECT of {type,instructions}, never an array of strings');
    return { ok: true, status: 200, text: async () => JSON.stringify({ answers: { harm: { noul: 0.91 } } }) };
  },
  async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, true);
    assert.deepEqual(r.scores, { harm: 0.91 });
  },
));

test('an unset key is unconfigured, never a score', async () => {
  const prev = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'unconfigured');
    assert.match(r.error, /infisical run --projectId/);   // the fix is IN the error
  } finally {
    if (prev !== undefined) process.env.TYPESAFE_API_KEY = prev;
  }
});

test('HTTP 400 is reported as http with the body, not swallowed',
  withFetch(respond(400, { detail: 'bad shape' }), async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'http');
    assert.match(r.error, /400/);
    assert.match(r.error, /bad shape/, 'the server reason must survive to the caller');
  }));

test('.probability and .distribution are NOT accepted as answers',
  withFetch(respond(200, { answers: { harm: { probability: 0.9, distribution: [0.1, 0.9] } } }), async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, false, 'only .noul counts — SDK-SURFACE.md');
    assert.equal(r.reason, 'no-answers');
  }));

test('a non-JSON body is non-json, not a crash',
  withFetch(async () => ({ ok: true, status: 200, text: async () => '<html>502</html>' }), async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'non-json');
  }));

test('a thrown transport error is transport, and never escapes',
  withFetch(async () => { throw new Error('connection reset'); }, async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'transport');
    assert.match(r.error, /connection reset/);
  }));

test('partial answers still succeed on what came back',
  withFetch(respond(200, { answers: { a: { noul: 0.2 } } }), async () => {
    const r = await askJev({ state: STATE, questions: { a: 'q1', b: 'q2' } });
    assert.equal(r.ok, true);
    assert.deepEqual(r.scores, { a: 0.2 });
    assert.equal('b' in r.scores, false);
  }));

test('no questions is refused before any network call', async () => {
  const real = globalThis.fetch;
  globalThis.fetch = async () => { throw new Error('must not be called'); };
  try {
    const r = await askJev({ state: STATE, questions: {}, apiKey: 'k' });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'no-answers');
  } finally { globalThis.fetch = real; }
});

// Both real omp row shapes. A reader that handles one and not the other reports "no rows"
// on live data that plainly contains them — the exact failure behind R33 and R41.
test('readRow handles BOTH omp row shapes, and rejects neither-shaped input', async () => {
  const { readRow } = await import('../src/index.ts');
  const nested = { customType: { type: 'x.decision.v1', data: { kind: 'harm_fire', score: 1 } } };
  const flat = { customType: 'x.decision.v1', data: { kind: 'failure_scored', score: 2 } };

  assert.deepEqual(readRow(nested), { type: 'x.decision.v1', data: { kind: 'harm_fire', score: 1 } });
  assert.deepEqual(readRow(flat), { type: 'x.decision.v1', data: { kind: 'failure_scored', score: 2 } });
  assert.deepEqual(readRow(JSON.stringify(flat)), { type: 'x.decision.v1', data: { kind: 'failure_scored', score: 2 } });

  assert.equal(readRow('not json'), undefined);
  assert.equal(readRow({ noCustomType: true }), undefined);
  assert.equal(readRow({ customType: 'x', data: 'not-an-object' }), undefined);
});
