import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  DEFAULT_MODEL,
  SYSTEMONE_ENDPOINT,
  askJevBundle,
  askJevChoice,
  askJevScore,
  clefBackendHoldActive,
  recordClefFailure,
  resetBillingHold,
  resetClefBackendHold,
  resolveBackendRoute,
  withAutoFallback,
} from '../src/client.ts';
import { classifyText } from '../src/classify.ts';
import { gateCommand, RISK, STATE_CONTEXT } from '../src/gate.ts';
import { rerankTop1, INSTRUCTIONS as RERANK_INSTRUCTIONS } from '../src/rerank.ts';
import { scoreText, SST5_INSTRUCTIONS } from '../src/score.ts';
import { verifyClaim, SCIFACT_INSTRUCTIONS, SCIFACT_CRITERIA } from '../src/verify.ts';
import { parseArgv } from '../src/cli/argv.mjs';
import { createEnvelope } from '../src/cli/envelope.mjs';
import { exitCodeForFailure, statusForFailure } from '../src/cli/exit.mjs';
// Safe corrective-command wording is exercised in kit/test/errors.test.mjs.

const b77Fixture = JSON.parse(await readFile(new URL('./fixtures/banking77-answer.json', import.meta.url), 'utf8'))[0];
const labels = Object.keys(b77Fixture.answers.choice.probabilities);
const classes = Object.fromEntries(labels.map((label) => [label, null]));
const instructions = 'The primary intent of this customer banking message';
const state = { customer_message: 'recorded Banking77 request shape' };
const question = { type: 'choice', instructions, criteria: classes };
const calibration = {
  schema: 'jev.clef-calibration.v1',
  task_id: 'banking77-intent',
  version: 1,
  primitive: 'choice',
  question_key: 'intent',
  question_sha256: '0'.repeat(64),
  model: { id: 'clef-flash', joint_head_sha256: 'a'.repeat(64), index_sha256: 'b'.repeat(64) },
  map: { kind: 'platt-logit', target: 'p_choice', a: 1.3526520145076346, b: 0.0002885751250081534, clip: 1e-4 },
  fit: { split: 'dev', n: 200 },
  receipt: { prereg_commit: 'ca787540', result_commit: '8b1bb513', verdict: 'PASS' },
};
const fingerprint = calibration.model;
const gatewayUrl = 'http://127.0.0.1:11300/test-only-clef-path';
const jsonResponse = (body, status = 200) => new Response(JSON.stringify(body), {
  status,
  headers: { 'content-type': 'application/json' },
});

function recordedJevResponse(answer = b77Fixture.answers.choice) {
  return jsonResponse({ answers: { choice: answer }, usage: b77Fixture.usage, model: 'jev-1.13.0' });
}

test('default Jev keeps the exact System One request bytes and makes no Clef request', async () => {
  let jevCalls = 0;
  let clefCalls = 0;
  let bodyBytes;
  const result = await askJevChoice({
    state,
    instructions,
    classes,
    model: 'jev-1.13.0',
    apiKey: 'offline-test-only',
    fetchImpl: async (_url, init) => {
      jevCalls += 1;
      bodyBytes = init.body;
      return recordedJevResponse();
    },
    clefFetchImpl: async () => { clefCalls += 1; return jsonResponse({}); },
  });
  const expected = JSON.stringify({
    state,
    questions: { choice: question },
    model: 'jev-1.13.0',
  });
  assert.equal(result.ok, true);
  assert.equal(result.backend, 'jev');
  assert.equal(result.backendRequested, 'jev');
  assert.equal(bodyBytes, expected);
  assert.equal(jevCalls, 1);
  assert.equal(clefCalls, 0);
});

test('auto rejects the public Banking77 calibration as a family receipt', async () => {
  let jevCalls = 0;
  let clefCalls = 0;
  const result = await classifyText({
    text: state.customer_message,
    labels,
    backend: 'auto',
    apiKey: 'offline-test-only',
    model: 'jev-1.13.0',
    fetchImpl: async () => { jevCalls += 1; return recordedJevResponse(); },
    clefFetchImpl: async () => { clefCalls += 1; return jsonResponse({}); },
    clefCalibration: calibration,
    clefFingerprint: fingerprint,
    clefUrl: gatewayUrl,
  });
  assert.equal(result.label, b77Fixture.answers.choice.choice);
  assert.equal(result.backend, 'jev');
  assert.equal(result.backendRequested, 'auto');
  assert.equal(result.routeReason, 'not-a-family-receipt');
  assert.equal(jevCalls, 1);
  assert.equal(clefCalls, 0);
});

test('the auto route gate requires every family, receipt, question, fingerprint, and hold condition', () => {
  // This policy tuple is a unit fixture only; it is not a calibration artifact or quality claim.
  const complete = {
    requested: 'auto',
    primitive: 'choice',
    questionCount: 1,
    calibration,
    questionKey: 'intent',
    questionHash: calibration.question_sha256,
    fingerprint,
    familyReceiptRegistered: true,
    backendHoldActive: false,
  };
  assert.equal(resolveBackendRoute(complete).backend, 'clef');
  assert.equal(resolveBackendRoute({ ...complete, familyReceiptRegistered: false }).routeReason, 'not-a-family-receipt');
  assert.equal(resolveBackendRoute({ ...complete, questionCount: 2 }).routeReason, 'multi-question');
  assert.equal(resolveBackendRoute({ ...complete, questionHash: '1'.repeat(64) }).routeReason, 'question-mismatch');
  assert.equal(resolveBackendRoute({ ...complete, fingerprint: undefined }).routeReason, 'fingerprint-unavailable');
  assert.equal(resolveBackendRoute({ ...complete, backendHoldActive: true }).routeReason, 'backend-hold');
});

test('auto makes at most one Clef attempt and one Jev fallback; explicit Clef never falls back', async () => {
  const calls = [];
  const clefFailure = async () => { calls.push('clef'); return { ok: false, reason: 'transport' }; };
  const jevAnswer = async () => { calls.push('jev'); return { ok: true, backend: 'jev' }; };
  const autoResult = await withAutoFallback('auto', true, clefFailure, jevAnswer);
  assert.equal(autoResult.ok, true);
  assert.deepEqual(calls, ['clef', 'jev']);

  calls.length = 0;
  const explicitResult = await withAutoFallback('clef', true, clefFailure, jevAnswer);
  assert.equal(explicitResult.ok, false);
  assert.deepEqual(calls, ['clef']);
});

test('two consecutive Clef transport failures start a 60-second hold', () => {
  resetClefBackendHold();
  try {
    recordClefFailure('transport', 1000);
    assert.equal(clefBackendHoldActive(1001), false);
    recordClefFailure('transport', 1001);
    assert.equal(clefBackendHoldActive(1001), true);
    assert.equal(clefBackendHoldActive(61000), true);
    assert.equal(clefBackendHoldActive(61001), false);
  } finally {
    resetClefBackendHold();
  }
});

test('bundles and score never route to Clef', async () => {
  let jevCalls = 0;
  let clefCalls = 0;
  const bundle = await askJevBundle({
    state: { task: 'captured' },
    questions: {
      first: { type: 'noul', instructions: 'First recorded question' },
      second: { type: 'noul', instructions: 'Second recorded question' },
    },
    backend: 'clef',
    clefFetchImpl: async () => { clefCalls += 1; return jsonResponse({}); },
    apiKey: 'offline-test-only',
    fetchImpl: async () => { jevCalls += 1; return jsonResponse({ answers: { first: { noul: 0.8 }, second: { noul: 0.2 } } }); },
  });
  assert.equal(bundle.ok, false);
  assert.equal(bundle.reason, 'uncalibrated');
  assert.equal(clefCalls, 0);
  assert.equal(jevCalls, 0);

  const levels = ['negative', 'neutral', 'positive'];
  const score = await askJevScore({
    state: { text: 'recorded review shape' },
    instructions: 'How positive is this movie review sentence?',
    criteria: levels,
    backend: 'auto',
    apiKey: 'offline-test-only',
    fetchImpl: async () => {
      jevCalls += 1;
      return jsonResponse({ answers: { score: { type: 'score', score: 2, confidence: 0.8, legend: { '0': 'negative', '1': 'neutral', '2': 'positive' }, probabilities: { '0': 0.1, '1': 0.1, '2': 0.8 } } } });
    },
    clefFetchImpl: async () => { clefCalls += 1; return jsonResponse({}); },
  });
  assert.equal(score.ok, true);
  assert.equal(score.backend, 'jev');
  assert.equal(clefCalls, 0);
});

test('CLI accepts backend and dry-run flags and reports class-correct refusal envelopes', () => {
  const parsed = parseArgv(['classify', '--text', 'recorded', '--labels', 'labels.json', '--backend', 'auto', '--dry-run', '--robot']);
  assert.equal(parsed.error, undefined);
  assert.equal(parsed.options.backend, 'auto');
  assert.equal(parsed.options['dry-run'], true);
  const invalid = parseArgv(['classify', '--text', 'recorded', '--labels', 'labels.json', '--backend', 'llm']);
  assert.ok(invalid.error);

  const envelope = createEnvelope('classify', {
    ok: false,
    reason: 'uncalibrated',
    error: 'No calibration for this question',
    backend: 'clef',
    backendRequested: 'clef',
    routeReason: 'no-calibration',
  }, { backend: 'clef', backendRequested: 'clef', fallbackReason: 'no-calibration' });
  assert.equal(envelope.schema, 'classifier.classify.v1');
  assert.equal(envelope.status, 'NOT_RUN');
  assert.equal(envelope.errors[0].exit_code, 2);
  assert.equal(envelope.meta.backend, 'clef');
  assert.equal(envelope.meta.backend_requested, 'clef');
  assert.equal(envelope.meta.fallback_reason, 'no-calibration');
  assert.equal(statusForFailure({ reason: 'online-required' }), 'ONLINE_REQUIRED');
  assert.equal(exitCodeForFailure({ reason: 'online-required' }), 6);
  assert.equal(statusForFailure({ reason: 'truncated' }), 'REFUSED');
  assert.equal(exitCodeForFailure({ reason: 'truncated' }), 3);
});

test('dry-run previews the canonical Jev request without calling the asker', async () => {
  let askerCalls = 0;
  const result = await classifyText({
    text: state.customer_message,
    labels,
    backend: 'auto',
    dryRun: true,
    model: DEFAULT_MODEL,
    ask: async () => { askerCalls += 1; throw new Error('dry-run called the asker'); },
  });

  assert.equal(askerCalls, 0);
  assert.equal(result.ok, true);
  assert.equal(result.backend, 'jev');
  assert.equal(result.backendRequested, 'auto');
  assert.equal(result.routeReason, 'not-a-family-receipt');
  assert.deepEqual(result.request, {
    endpoint: SYSTEMONE_ENDPOINT,
    method: 'POST',
    body: { state: { customer_message: state.customer_message }, questions: { choice: question }, model: DEFAULT_MODEL },
  });
  const envelope = createEnvelope('classify', result);
  assert.equal(envelope.status, 'OK');
  assert.equal(envelope.meta.backend, 'jev');
  assert.equal(envelope.meta.backend_requested, 'auto');
  assert.equal(envelope.meta.fallback_reason, 'not-a-family-receipt');
  assert.equal(envelope.data.dryRun, true);
  assert.deepEqual(envelope.data.request, result.request);
});

test('rerank, score, verify, and gate dry-runs preserve their canonical question shapes without calling askers', async () => {
  let askerCalls = 0;
  const ask = async () => { askerCalls += 1; throw new Error('dry-run called an asker'); };
  const candidates = [{ id: 'a', text: 'recorded candidate A' }, { id: 'b', text: 'recorded candidate B' }];
  const rerank = await rerankTop1({ query: 'recorded ranking query', candidates, backend: 'auto', dryRun: true, model: DEFAULT_MODEL, ask });
  assert.deepEqual(rerank.request.body, {
    state: { query: 'recorded ranking query', candidates },
    questions: { choice: { type: 'choice', instructions: RERANK_INSTRUCTIONS, criteria: { a: 'Candidate passage a', b: 'Candidate passage b' } } },
    model: DEFAULT_MODEL,
  });

  const levels = ['low', 'middle', 'high'];
  const score = await scoreText({ text: 'recorded review', levels, backend: 'auto', dryRun: true, model: DEFAULT_MODEL, ask });
  assert.deepEqual(score.request.body, {
    state: { text: 'recorded review' },
    questions: { score: { type: 'score', instructions: SST5_INSTRUCTIONS, criteria: levels } },
    model: DEFAULT_MODEL,
  });

  const verify = await verifyClaim({ claim: 'recorded claim', evidence: 'recorded evidence', backend: 'auto', dryRun: true, model: DEFAULT_MODEL, ask });
  assert.deepEqual(verify.request.body, {
    state: { claim: 'recorded claim', evidence: 'recorded evidence' },
    questions: { value: { type: 'noul', instructions: SCIFACT_INSTRUCTIONS, criteria: SCIFACT_CRITERIA } },
    model: DEFAULT_MODEL,
  });

  const gateCommandText = 'npm test';
  const gate = await gateCommand({ command: gateCommandText, backend: 'auto', dryRun: true, model: DEFAULT_MODEL, ask });
  assert.deepEqual(gate.request.body, { state: { command: gateCommandText, context: STATE_CONTEXT }, questions: RISK, model: DEFAULT_MODEL });
  assert.equal(askerCalls, 0);
});
