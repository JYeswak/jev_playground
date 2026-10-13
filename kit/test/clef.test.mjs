import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import { BANKING77_INSTRUCTIONS } from '../src/classify.ts';
import { plattMap, questionSha } from '../src/calibration.ts';
import { askClef } from '../src/clef.ts';

const b77Response = JSON.parse(await readFile(new URL('./fixtures/banking77-answer.json', import.meta.url), 'utf8'))[0];
const labels = Object.keys(b77Response.answers.choice.probabilities);
const b77Question = {
  type: 'choice',
  instructions: BANKING77_INSTRUCTIONS,
  criteria: Object.fromEntries(labels.map((label) => [label, null])),
};
const b77State = { customer_message: 'recorded Banking77 shape' };
const b77Calibration = {
  schema: 'jev.clef-calibration.v1',
  task_id: 'banking77-intent',
  version: 1,
  primitive: 'choice',
  question_key: 'intent',
  question_sha256: questionSha(b77Question, Object.keys(b77State)),
  model: {
    id: 'clef-flash',
    joint_head_sha256: 'a'.repeat(64),
    index_sha256: 'b'.repeat(64),
  },
  map: { kind: 'platt-logit', target: 'p_choice', a: 1.3526520145076346, b: 0.0002885751250081534, clip: 1e-4 },
  receipt: { prereg_commit: 'ca787540', result_commit: '8b1bb513', verdict: 'PASS' },
};
const testGatewayUrl = 'http://127.0.0.1:11300/test-only-clef-path';

function successfulResponse(body) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'content-type': 'application/json' },
  });
}

test('Clef uses the receipt question key, sends no Authorization header, and returns calibrated choice', async () => {
  let calls = 0;
  let request;
  const result = await askClef({
    primitive: 'choice',
    state: b77State,
    question: b77Question,
    callerKey: 'choice',
    calibration: b77Calibration,
    fingerprint: b77Calibration.model,
    url: testGatewayUrl,
    fetchImpl: async (url, init) => {
      calls += 1;
      request = { url: String(url), init };
      return successfulResponse({
        answers: { intent: b77Response.answers.choice },
        usage: { input_tokens: 950, output_tokens: 755 },
      });
    },
  });

  assert.equal(calls, 1);
  assert.equal(request.url, testGatewayUrl);
  assert.equal(new Headers(request.init.headers).has('authorization'), false);
  const body = JSON.parse(request.init.body);
  assert.equal(body.model, 'clef-flash');
  assert.deepEqual(body.state, b77State);
  assert.deepEqual(Object.keys(body.questions), ['intent']);
  assert.deepEqual(body.questions.intent, b77Question);
  assert.equal(result.ok, true);
  assert.equal(result.choice, b77Response.answers.choice.choice);
  assert.equal(result.confidence, plattMap(b77Response.answers.choice.probabilities[result.choice], b77Calibration.map));
  assert.equal(result.probabilitiesRaw, true);
  assert.equal(result.model, 'clef-flash+platt:banking77-intent.v1');
  assert.equal(result.usage.input_tokens, 950);
});

test('Clef refuses a question-hash mismatch without returning raw probabilities', async () => {
  let calls = 0;
  const result = await askClef({
    primitive: 'choice',
    state: b77State,
    question: { ...b77Question, instructions: `${b77Question.instructions} ` },
    callerKey: 'choice',
    calibration: b77Calibration,
    fingerprint: b77Calibration.model,
    url: testGatewayUrl,
    fetchImpl: async () => { calls += 1; return successfulResponse({}); },
  });

  assert.equal(calls, 0);
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'uncalibrated');
  for (const field of ['choice', 'confidence', 'probabilities', 'score', 'noul']) {
    assert.equal(Object.hasOwn(result, field), false, `${field} must not expose an uncalibrated value`);
  }
});

test('Clef refuses absent calibration and >=16384 post-truncation input tokens', async () => {
  let calls = 0;
  const absent = await askClef({
    primitive: 'choice', state: b77State, question: b77Question, callerKey: 'choice',
    url: testGatewayUrl, fetchImpl: async () => { calls += 1; return successfulResponse({}); },
  });
  assert.equal(absent.ok, false);
  assert.equal(absent.reason, 'uncalibrated');
  assert.equal(calls, 0);

  const truncated = await askClef({
    primitive: 'choice', state: b77State, question: b77Question, callerKey: 'choice',
    calibration: b77Calibration, fingerprint: b77Calibration.model, url: testGatewayUrl,
    fetchImpl: async () => {
      calls += 1;
      return successfulResponse({ answers: { intent: b77Response.answers.choice }, usage: { input_tokens: 16384, output_tokens: 0 } });
    },
  });
  assert.equal(calls, 1);
  assert.equal(truncated.ok, false);
  assert.equal(truncated.reason, 'truncated');
  assert.equal(Object.hasOwn(truncated, 'choice'), false);
  assert.equal(Object.hasOwn(truncated, 'probabilities'), false);
});

test('Clef HTTP 500 is a typed failure and never returns raw scores', async () => {
  const result = await askClef({
    primitive: 'choice', state: b77State, question: b77Question, callerKey: 'choice',
    calibration: b77Calibration, fingerprint: b77Calibration.model, url: testGatewayUrl,
    fetchImpl: async () => new Response(JSON.stringify({ error: 'fixture server failure' }), {
      status: 500, headers: { 'content-type': 'application/json' },
    }),
  });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'http');
  assert.equal(Object.hasOwn(result, 'choice'), false);
  assert.equal(Object.hasOwn(result, 'probabilities'), false);
});

test('Clef requires an explicit safe gateway URL and refuses the direct server', async () => {
  const previous = process.env.JEV_CLEF_URL;
  delete process.env.JEV_CLEF_URL;
  let calls = 0;
  const options = {
    primitive: 'choice', state: b77State, question: b77Question, callerKey: 'choice',
    calibration: b77Calibration, fingerprint: b77Calibration.model,
    fetchImpl: async () => { calls += 1; return successfulResponse({}); },
  };
  try {
    const missing = await askClef(options);
    assert.equal(missing.ok, false);
    assert.equal(missing.reason, 'online-required');
    for (const url of ['http://127.0.0.1:8010/v1/systemone', 'http://192.0.2.1:11300/clef']) {
      const refused = await askClef({ ...options, url });
      assert.equal(refused.ok, false);
      assert.equal(refused.reason, 'refused-unsafe');
    }
    assert.equal(calls, 0);
  } finally {
    if (previous === undefined) delete process.env.JEV_CLEF_URL;
    else process.env.JEV_CLEF_URL = previous;
  }
});

test('Clef serializes concurrent requests in one process', async () => {
  let active = 0;
  let maxActive = 0;
  let requests = 0;
  let firstStartedResolve;
  let secondStartedResolve;
  const firstStarted = new Promise((resolve) => { firstStartedResolve = resolve; });
  const secondStarted = new Promise((resolve) => { secondStartedResolve = resolve; });
  const releases = [];
  const fetchImpl = async () => {
    requests += 1;
    active += 1;
    maxActive = Math.max(maxActive, active);
    if (requests === 1) firstStartedResolve();
    if (requests === 2) secondStartedResolve();
    await new Promise((resolve) => releases.push(resolve));
    active -= 1;
    return successfulResponse({ answers: { intent: b77Response.answers.choice }, usage: { input_tokens: 950, output_tokens: 755 } });
  };
  const options = {
    primitive: 'choice', state: b77State, question: b77Question, callerKey: 'choice',
    calibration: b77Calibration, fingerprint: b77Calibration.model, url: testGatewayUrl, fetchImpl,
  };
  const first = askClef(options);
  await firstStarted;
  const second = askClef(options);
  try {
    assert.equal(active, 1);
    assert.equal(releases.length, 1);
    releases.shift()();
    await secondStarted;
    assert.equal(active, 1);
    releases.shift()();
    const results = await Promise.all([first, second]);
    assert.ok(results.every((result) => result.ok));
    assert.equal(maxActive, 1);
  } finally {
    for (const release of releases) release();
  }
});
