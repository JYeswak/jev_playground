import test from 'node:test';
import assert from 'node:assert/strict';
import { askJevBundle } from '../src/client.ts';
import { ValidationError, validateBundleAnswers, validateChoiceAnswer, validateNoulAnswer, validateScoreAnswer } from '../src/validate.ts';

const classes = ['yes', 'no'];
const choiceQuestion = { type: 'choice', instructions: 'q', criteria: { yes: 'yes', no: 'no' } };
const noulQuestion = { type: 'noul', instructions: 'q' };

test('valid Choice distribution is accepted', () => {
  const result = validateChoiceAnswer({ choice: 'yes', confidence: 0.9, probabilities: { yes: 0.9, no: 0.1 } }, classes);
  assert.equal(result.choice, 'yes');
});

test('malformed Choice answer is refused instead of coerced', () => {
  assert.throws(
    () => validateChoiceAnswer({ choice: 'yes', confidence: 0.9, probabilities: { yes: 0.2, no: 0.2 } }, classes),
    (error) => error instanceof ValidationError,
  );
});

test('Noul and Score answers enforce numeric invariants', () => {
  assert.equal(validateNoulAnswer({ noul: 0.4 }), 0.4);
  assert.throws(() => validateNoulAnswer({ noul: 1.2 }), ValidationError);
  const score = validateScoreAnswer({ score: 0.9, confidence: 0.9, legend: { 0: 'none', 1: 'bad' }, probabilities: { 0: 0.1, 1: 0.9 } }, ['none', 'bad']);
  assert.equal(score.score, 0.9);
});

test('bundle validator refuses missing and malformed typed answers', () => {
  assert.deepEqual(validateBundleAnswers({ harm: noulQuestion }, { harm: { noul: 0.7 } }), { harm: { noul: 0.7 } });
  assert.throws(() => validateBundleAnswers({ harm: noulQuestion }, {}), ValidationError);
  assert.throws(() => validateBundleAnswers({ choice: choiceQuestion }, { choice: { choice: 'yes', confidence: 0.9, probabilities: { yes: 0.9 } } }), ValidationError);
});

function fakeResponse(payload) {
  return async () => ({ ok: true, status: 200, headers: { get: () => 'application/json' }, body: null, clone() { return this; }, text: async () => JSON.stringify(payload) });
}

test('askJevBundle refuses a hostile answer instead of returning unvalidated answers', async () => {
  const result = await askJevBundle({
    state: { command: 'captured' },
    questions: { choice: choiceQuestion },
    apiKey: ['fixture', 'key'].join('-'),
    fetchImpl: fakeResponse({ answers: { choice: { type: 'choice', choice: 'yes', confidence: 0.9, probabilities: { yes: 0.2, no: 0.2 } } } }),
  });
  assert.equal(result.ok, false);
  assert.equal(result.reason, 'no-answers');
});
