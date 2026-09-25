import test from 'node:test';
import assert from 'node:assert/strict';
import { askJev, askJevChoice, askJevBundle, askJevScore, BILLING_HOLD_MS, observedFetch, resetBillingHold, SYSTEMONE_ENDPOINT } from '../src/index.ts';

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
// Fake Responses must be Response-shaped: the SDK transport reads headers and
// buffers via clone().body (real Responses always carry both; the old fakes
// predated the SDK delegation and omitted them).
const fakeHeaders = () => ({ get: (name) => name.toLowerCase() === 'content-type' ? 'application/json' : null });
const respond = (status, payload) => async () => ({
  ok: status < 400, status, headers: fakeHeaders(), body: null,
  clone() { return this; },
  text: async () => JSON.stringify(payload),
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
    return { ok: true, status: 200, headers: fakeHeaders(), body: null, clone() { return this; }, text: async () => JSON.stringify({ answers: { harm: { noul: 0.91 } } }) };
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

test('a key with no installed SDK is sdk-missing, not unconfigured, and makes no call', async () => {
  // A fresh clone has no work/sdk/node_modules. Rebuild that layout: the client file alone, at
  // the same relative depth, with no SDK beside it.
  const { mkdtempSync, mkdirSync, copyFileSync } = await import('node:fs');
  const { tmpdir } = await import('node:os');
  const { join } = await import('node:path');
  const { pathToFileURL, fileURLToPath } = await import('node:url');
  const root = mkdtempSync(join(tmpdir(), 'jev-client-nosdk-'));
  mkdirSync(join(root, 'work/jev-client/src'), { recursive: true });
  mkdirSync(join(root, 'kit/src'), { recursive: true });
  const copy = join(root, 'work/jev-client/src/index.ts');
  copyFileSync(fileURLToPath(new URL('../src/index.ts', import.meta.url)), copy);
  copyFileSync(fileURLToPath(new URL('../../../kit/src/client.ts', import.meta.url)), join(root, 'kit/src/client.ts'));
  copyFileSync(fileURLToPath(new URL('../../../kit/src/validate.ts', import.meta.url)), join(root, 'kit/src/validate.ts'));
  const bare = await import(pathToFileURL(copy).href);
  let called = false;
  const r = await bare.askJev({
    state: STATE, questions: QUESTIONS, apiKey: 'test-key',
    fetchImpl: async () => { called = true; throw new Error('must not be reached'); },
  });
  assert.equal(r.ok, false);
  assert.equal(r.reason, 'sdk-missing');
  assert.match(r.error, /npm ci --prefix work\/sdk/);   // the fix is IN the error
  assert.equal(called, false);
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
  withFetch(async () => ({ ok: true, status: 200, headers: { get: () => 'text/html' }, body: null, clone() { return this; }, text: async () => '<html>502</html>' }), async () => {
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

// billing_units is on the wire but declared by NEITHER SDK (typesafe-sdk-python
// tests/test_responses.py:143 carries it and :152 proves the Python SDK drops it). The JS SDK
// passes the parsed body through, so this client is where it is kept or lost.
test('usage passes through with billing_units and every other numeric field when the response carries them',
  withFetch(respond(200, { answers: { harm: { noul: 0.7 } }, usage: { input_tokens: 100, output_tokens: 20, billing_units: 3, reasoning_tokens: 9, note: 'text is not a count' }, model: 'jev-1.13.0' }), async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, true);
    assert.deepEqual(r.usage, { input_tokens: 100, output_tokens: 20, billing_units: 3, extra: { reasoning_tokens: 9 } });
  }));

test('usage without billing_units reports billing_units null, never a zero-filled count',
  withFetch(respond(200, { answers: { harm: { noul: 0.7 } }, usage: { input_tokens: 100, output_tokens: 20 } }), async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, true);
    assert.strictEqual(r.usage.billing_units, null);
    assert.deepEqual(r.usage.extra, {});
  }));

// Every answer shape carries usage, and a response with no usage never throws on any of them.
const USAGE = { input_tokens: 381, output_tokens: 18, billing_units: 1 };
const YES_NO = { yes: 'it is', no: 'it is not' };
const SHAPES = {
  noul: { answers: { harm: { noul: 0.7 } }, ask: () => askJev({ state: STATE, questions: QUESTIONS }) },
  choice: {
    answers: { choice: { type: 'choice', choice: 'yes', confidence: 0.9, probabilities: { yes: 0.9, no: 0.1 } } },
    ask: () => askJevChoice({ state: STATE, instructions: 'q', classes: YES_NO }),
  },
  score: {
    answers: { score: { type: 'score', score: 1, confidence: 0.9, legend: { 0: 'none', 1: 'bad' }, probabilities: { 0: 0.1, 1: 0.9 } } },
    ask: () => askJevScore({ state: STATE, instructions: 'how bad?', criteria: ['none', 'bad'] }),
  },
  // A text state, as work/score-sst5 sends it: the bundle forwards a string unchanged.
  bundle: { answers: { a: { type: 'noul', noul: 0.4 } }, ask: () => askJevBundle({ state: 'plain text state', questions: { a: { type: 'noul', instructions: 'q' } } }) },
};

test('every answer shape returns billing_units when the response carries usage', async (t) => {
  for (const [shape, { answers, ask }] of Object.entries(SHAPES)) {
    await t.test(shape, withFetch(respond(200, { answers, usage: USAGE, model: 'jev-1.13.0' }), async () => {
      const r = await ask();
      assert.equal(r.ok, true, `${shape} answered`);
      assert.deepEqual(r.usage, { ...USAGE, extra: {} });
    }));
  }
});

test('every answer shape answers without throwing and reports usage absent when the response has none', async (t) => {
  for (const [shape, { answers, ask }] of Object.entries(SHAPES)) {
    await t.test(shape, withFetch(respond(200, { answers, model: 'jev-1.13.0' }), async () => {
      const r = await ask();
      assert.equal(r.ok, true, `${shape}: a missing usage object must not fail the answer`);
      assert.equal('usage' in r, false, `${shape}: absent usage must not be invented or zero-filled`);
    }));
  }
});

test('usage is absent, never invented, when the response omits it',
  withFetch(respond(200, { answers: { harm: { noul: 0.7 } } }), async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, true);
    assert.equal(r.scores.harm, 0.7);
    assert.equal('usage' in r, false, 'a missing field must not be zero-filled');
  }));

test('malformed usage is dropped while scores stand',
  withFetch(respond(200, { answers: { harm: { noul: 0.7 } }, usage: { input_tokens: 'lots' } }), async () => {
    const r = await askJev({ state: STATE, questions: QUESTIONS });
    assert.equal(r.ok, true);
    assert.equal(r.scores.harm, 0.7);
    assert.equal('usage' in r, false);
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

// --- MULTICLASS -----------------------------------------------------------------------------
// One question, mutually-exclusive labels, exactly one answer. The wire shape below was read off
// a live 200 on 2026-09-19, not inferred: an invented body got HTTP 400 earlier the same night.
const CLASSES = {
  transient: 'the environment flaked',
  argument: 'the invocation was wrong',
  bug: 'the code under edit is broken',
};
const CHOICE_OK = {
  answers: { choice: { type: 'choice', choice: 'argument', confidence: 0.97,
                       probabilities: { transient: 0, argument: 0.98, bug: 0.02 } } },
};

test('askJevChoice sends type:"choice" with criteria as a MAP of label -> description', withFetch(
  async (url, init) => {
    assert.equal(url, SYSTEMONE_ENDPOINT);
    const sent = JSON.parse(init.body);
    assert.equal(typeof sent.model, 'string');
    assert.deepEqual(sent.state, STATE);
    assert.deepEqual(sent.questions, {
      choice: { type: 'choice', instructions: 'which class?', criteria: CLASSES },
    }, 'ONE question, type "choice", criteria a map — the SDK rejects a list outright');
    return { ok: true, status: 200, headers: fakeHeaders(), body: null, clone() { return this; }, text: async () => JSON.stringify(CHOICE_OK) };
  },
  async () => {
    const r = await askJevChoice({ state: STATE, instructions: 'which class?', classes: CLASSES });
    assert.equal(r.ok, true);
    assert.equal(r.choice, 'argument');
    assert.equal(r.confidence, 0.97);
    assert.deepEqual(r.probabilities, { transient: 0, argument: 0.98, bug: 0.02 });
  },
));

test('askJevBundle sends Choice and Noul in ONE request against the same state', withFetch(
  async (url, init) => {
    assert.equal(url, SYSTEMONE_ENDPOINT);
    const sent = JSON.parse(init.body);
    assert.equal(sent.questions.verdict.type, 'choice');
    assert.equal(sent.questions.defect.type, 'noul');
    assert.deepEqual(sent.state, STATE);
    return {
      ok: true,
      status: 200,
      headers: fakeHeaders(), body: null, clone() { return this; },
      text: async () => JSON.stringify({
        model: 'jev-1.13.0',
        answers: {
          verdict: { type: 'choice', choice: 'argument', confidence: 0.9,
                     probabilities: { transient: 0.05, argument: 0.9, bug: 0.05 } },
          defect: { type: 'noul', noul: 0.81 },
        },
      }),
    };
  },
  async () => {
    const r = await askJevBundle({
      state: STATE,
      questions: {
        verdict: { type: 'choice', instructions: 'which class?', criteria: CLASSES },
        defect: { type: 'noul', instructions: 'is this a defect?' },
      },
    });
    assert.equal(r.ok, true);
    assert.equal(r.resolvedModel, 'jev-1.13.0');
    assert.equal(r.answers.defect.noul, 0.81);
    assert.equal(r.answers.verdict.choice, 'argument');
  },
));

test('askJevChoice refuses a degenerate class set before any network call', async () => {
  const real = globalThis.fetch;
  globalThis.fetch = async () => { throw new Error('must not be called'); };
  try {
    for (const classes of [{}, { only: 'one label has nothing to choose against' }]) {
      const r = await askJevChoice({ state: STATE, instructions: 'q', classes, apiKey: 'k' });
      assert.equal(r.ok, false);
      assert.equal(r.reason, 'no-answers');
      assert.match(r.error, /at least 2 labels/);
    }
    // A list is the one shape the SDK itself names and refuses (dist/index.mjs:339).
    const listy = await askJevChoice({ state: STATE, instructions: 'q', classes: ['a', 'b'], apiKey: 'k' });
    assert.equal(listy.ok, false);
    assert.match(listy.error, /not a list/);
  } finally { globalThis.fetch = real; }
});

test('askJevChoice with no key is unconfigured, never a choice', async () => {
  const prev = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const r = await askJevChoice({ state: STATE, instructions: 'q', classes: CLASSES });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'unconfigured');
    assert.match(r.error, /infisical run --projectId/);
  } finally {
    if (prev !== undefined) process.env.TYPESAFE_API_KEY = prev;
  }
});

// Each of these returns a plausible-looking 200. A reader that shrugs at one of them reports a
// confident label it never received — the 0.500-AUC failure mode in SDK-SURFACE.md, one layer up.
test('askJevChoice refuses an answer it cannot read, rather than inventing one', async (t) => {
  const bad = {
    'a label that was never offered': { choice: 'flake', confidence: 0.9, probabilities: { flake: 1 } },
    'no choice field at all': { confidence: 0.9, probabilities: { argument: 1 } },
    '.distribution instead of .probabilities': { choice: 'argument', confidence: 0.9, distribution: [0, 1, 0] },
    'a label missing from probabilities': { choice: 'argument', confidence: 0.9, probabilities: { argument: 0.9, bug: 0.1 } },
    'non-numeric confidence': { choice: 'argument', confidence: 'high', probabilities: { transient: 0, argument: 1, bug: 0 } },
  };
  for (const [name, answer] of Object.entries(bad)) {
    await t.test(name, withFetch(respond(200, { answers: { choice: answer } }), async () => {
      const r = await askJevChoice({ state: STATE, instructions: 'q', classes: CLASSES });
      assert.equal(r.ok, false, `${name} must not be read as an answer`);
      assert.equal(r.reason, 'no-answers');
    }));
  }
});

test('askJevChoice reports HTTP and transport failures the same way askJev does', async (t) => {
  await t.test('http', withFetch(respond(400, { detail: 'bad shape' }), async () => {
    const r = await askJevChoice({ state: STATE, instructions: 'q', classes: CLASSES });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'http');
    assert.match(r.error, /400/);
    assert.match(r.error, /bad shape/);
  }));
  await t.test('transport', withFetch(async () => { throw new Error('connection reset'); }, async () => {
    const r = await askJevChoice({ state: STATE, instructions: 'q', classes: CLASSES });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'transport');
  }));
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

// --- SCORE ------------------------------------------------------------------
// Rubric question type the wrapper did not ship until now. Same contract as
// Choice: typed answers read strictly, degenerate input refused pre-network.

test('askJevScore sends type:"score" with a criteria LIST and reads score+legend', withFetch(
  async (url, init) => {
    assert.equal(url, SYSTEMONE_ENDPOINT);
    const sent = JSON.parse(init.body);
    assert.deepEqual(sent.questions, {
      score: { type: 'score', instructions: 'how bad?', criteria: ['none', 'bad', 'severe'] },
    }, 'ONE question, type "score", criteria a list — the SDK rejects a map outright');
    return { ok: true, status: 200, headers: fakeHeaders(), body: null, clone() { return this; }, text: async () => JSON.stringify({
      answers: { score: { type: 'score', score: 2, confidence: 0.88, legend: { 0: 'none', 1: 'bad', 2: 'severe' }, probabilities: { 0: 0.02, 1: 0.1, 2: 0.88 } } },
    }) };
  },
  async () => {
    const r = await askJevScore({ state: STATE, instructions: 'how bad?', criteria: ['none', 'bad', 'severe'] });
    assert.equal(r.ok, true);
    assert.equal(r.score, 2);
    assert.equal(r.confidence, 0.88);
    assert.deepEqual(r.legend, { 0: 'none', 1: 'bad', 2: 'severe' });
    assert.deepEqual(r.probabilities, { 0: 0.02, 1: 0.1, 2: 0.88 });
  },
));

test('askJevScore refuses a one-element criteria list BEFORE any network call', async () => {
  const real = globalThis.fetch;
  let called = 0;
  globalThis.fetch = async () => { called += 1; throw new Error('must not be called'); };
  try {
    // apiKey present so the refusal tested is the criteria gate, not the key gate.
    const r = await askJevScore({ state: STATE, instructions: 'how bad?', criteria: ['only'], apiKey: 'k' });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'no-answers');
    assert.equal(called, 0, 'planted negative: no fetch may fire');
  } finally { globalThis.fetch = real; }
});

test('askJevScore refuses an answer it cannot read', withFetch(
  respond(200, { answers: { score: { score: 'high', confidence: 0.9 } } }), async () => {
    const r = await askJevScore({ state: STATE, instructions: 'how bad?', criteria: ['none', 'bad'] });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'no-answers');
  },
));

test('askJevBundle defaults to a single attempt: a 503 is reported, not retried', async () => {
  const real = globalThis.fetch;
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    return { ok: false, status: 503, headers: fakeHeaders(), body: null, clone() { return this; }, text: async () => JSON.stringify({ detail: 'overloaded' }) };
  };
  try {
    const r = await askJevBundle({ state: STATE, questions: { a: { type: 'noul', instructions: 'q' } }, apiKey: 'k' });
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'http');
    assert.equal(calls, 1, 'default retry is maxRetries 0: the SDK owns retry, the runner owns rows');
  } finally { globalThis.fetch = real; }
});

test('the hold window is the pinned 15 minute literal, not a 1 ms stand-in', () => {
  assert.equal(BILLING_HOLD_MS, 15 * 60 * 1000);
});

test('a 402 then N calls inside the window makes 1 network call and N billing-hold results', async () => {
  resetBillingHold();
  let clock = 1_000_000;
  let calls = 0;
  const real = globalThis.fetch;
  globalThis.fetch = async () => {
    calls += 1;
    return { ok: false, status: 402, headers: fakeHeaders(), body: null, clone() { return this; }, text: async () => JSON.stringify({ error: 'no credits' }) };
  };
  try {
    const first = await askJev({ state: STATE, questions: QUESTIONS, apiKey: 'k', nowMs: () => clock });
    assert.equal(first.ok, false);
    assert.equal(first.reason, 'http');
    assert.match(first.error, /HTTP 402/);
    const held = [];
    for (let i = 0; i < 4; i += 1) {
      clock += 1000;
      held.push(await askJev({ state: STATE, questions: QUESTIONS, apiKey: 'k', nowMs: () => clock }));
    }
    assert.equal(calls, 1);
    assert.equal(held.length, 4);
    for (const row of held) {
      assert.equal(row.ok, false);
      assert.equal(row.reason, 'billing-hold');
      assert.match(row.error, /until=/);
    }
    clock = 1_000_000 + 15 * 60 * 1000;
    const after = await askJev({ state: STATE, questions: QUESTIONS, apiKey: 'k', nowMs: () => clock });
    assert.equal(calls, 2, 'the first call after the window goes out');
    assert.equal(after.reason, 'http');
  } finally {
    globalThis.fetch = real;
    resetBillingHold();
  }
});

test('a 429 and a 503 do not start a hold: the next call inside the window still reaches the network', async () => {
  // postSystemOne passes maxRetries 0 when the caller omits retry. The SDK's
  // default would retry 429/503 and sleep; that default is not used here.
  resetBillingHold();
  const real = globalThis.fetch;
  const headers = {
    get: (name) => String(name).toLowerCase() === 'content-type' ? 'application/json' : null,
    has: (name) => String(name).toLowerCase() === 'content-type',
  };
  try {
    for (const status of [429, 503]) {
      let calls = 0;
      globalThis.fetch = async () => {
        calls += 1;
        return { ok: false, status, headers, body: null, clone() { return this; }, text: async () => JSON.stringify({ detail: 'no' }) };
      };
      const clock = 8_000_000;
      const first = await askJev({ state: STATE, questions: QUESTIONS, apiKey: 'k', nowMs: () => clock });
      const second = await askJev({ state: STATE, questions: QUESTIONS, apiKey: 'k', nowMs: () => clock + 1 });
      assert.notEqual(first.reason, 'billing-hold', String(status));
      assert.notEqual(second.reason, 'billing-hold', String(status));
      assert.equal(calls, 2, `status ${status}: the second call inside the window must reach the network`);
      resetBillingHold();
    }
    let thrown = 0;
    globalThis.fetch = async () => { thrown += 1; throw new Error('socket hang up after 4020 ms'); };
    const a = await askJev({ state: STATE, questions: QUESTIONS, apiKey: 'k', nowMs: () => 9_000_000 });
    const b = await askJev({ state: STATE, questions: QUESTIONS, apiKey: 'k', nowMs: () => 9_000_001 });
    assert.equal(a.reason, 'transport');
    assert.equal(b.reason, 'transport');
    assert.equal(thrown, 2);
  } finally {
    globalThis.fetch = real;
    resetBillingHold();
  }
});

test('observedFetch marks transport entry and forwards the request', async () => {
  let observed = 0;
  let forwarded;
  const wrapped = observedFetch(() => { observed += 1; }, async (input, init) => {
    forwarded = { input, init };
    return new Response('{}', { status: 200 });
  });
  const init = { method: 'POST', body: 'payload' };
  await wrapped('https://example.test/systemone', init);
  assert.equal(observed, 1);
  assert.deepEqual(forwarded, { input: 'https://example.test/systemone', init });
});
