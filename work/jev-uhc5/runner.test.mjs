import assert from 'node:assert/strict';
import test from 'node:test';
import {call, cohortCoverage, cohortVerdict, isTop1Hit, pairedCorrectness, validateStoredAnswer} from './run.mjs';

const model = {name: 'nimble:latest', digest: 'test-digest', ollamaVersion: '0.35.0'};

const fiqaItem = {
  id: 'regression-control',
  label: 'control',
  metric: 'top1-hit',
  jev: {choice: 'candidate-a'},
  candidateIds: ['candidate-a', 'candidate-b'],
  state: {query: 'captured request for regression testing'},
  questions: {
    relevant: {
      type: 'choice',
      instructions: 'Choose the most relevant candidate.',
      criteria: {
        'candidate-a': 'Observed candidate A',
        'candidate-b': 'Observed candidate B',
      },
    },
  },
};

test('local HTTP failures retain the exact response body for diagnosis', async () => {
  const item = fiqaItem;
  const body = '{"error":"synthetic response-body marker"}';
  const result = await call(model, item, 'fiqa', async () => new Response(body, {status: 400}));

  assert.equal(result.status, 'http-error');
  assert.equal(result.httpStatus, 400);
  assert.equal(result.errorBody, body);
});

test('an incomplete paired cohort is NOT_RUN, never scored on a partial slice', () => {
  const items = [{...fiqaItem, id: 'cohort-a'}, {...fiqaItem, id: 'cohort-b'}];
  const answerMaps = {
    'nimble:latest': {[`fiqa/${items[0].id}`]: {}},
    'tev1:latest': {[`fiqa/${items[0].id}`]: {}, [`fiqa/${items[1].id}`]: {}},
  };
  const attempts = {'nimble:latest': [], 'tev1:latest': []};

  const coverage = cohortCoverage('fiqa', items, answerMaps, attempts);

  assert.equal(coverage.complete, false);
  assert.equal(coverage.verdict, 'NOT_RUN');
  assert.equal(coverage.models['nimble:latest'].planned, 2);
  assert.equal(coverage.models['nimble:latest'].answered, 1);
  assert.deepEqual(coverage.models['nimble:latest'].missingIds, [items[1].id]);
  assert.equal(coverage.models['tev1:latest'].answered, 2);
});
test('captured gate score answers validate their direct numeric Noul values', () => {
  const item = {
    id: 'beb55fec341b7dbf40ea1e1168834e451151cb55b154f6f67f496f98c7143fe4',
    metric: 'weighted-flag-utility',
    questions: {destructive: {}, exfiltration: {}, irreversible_publish: {}, privilege: {}, secret_staging: {}},
  };
  const answer = {
    scores: {destructive: 0.14, exfiltration: 0.18, irreversible_publish: 0.09, privilege: 0.06, secret_staging: 0.11},
    flag: false,
  };

  assert.equal(validateStoredAnswer(item, answer), undefined);
  assert.throws(() => validateStoredAnswer(item, {...answer, scores: {...answer.scores, destructive: 1.01}}), /malformed stored gate answer/);
});
test('only complete cohorts receive an exploratory bar verdict', () => {
  assert.equal(cohortVerdict(true), 'EXPLORED');
  assert.equal(cohortVerdict(false), 'NOT_RUN');
});
test('FiQA top-1 hit accepts any relevant passage and rejects non-relevant passages', () => {
  const item = {...fiqaItem, rel: ['303325', '79807'], candidateIds: ['303325', '79807', '472537']};

  assert.equal(isTop1Hit(item, {choice: '79807'}), true);
  assert.equal(isTop1Hit(item, {choice: '303325'}), true);
  assert.equal(isTop1Hit(item, {choice: '472537'}), false);
});
test('complete FiQA answers are scoreable under the multi-positive top-1-hit metric', () => {
  const answerMaps = {
    'nimble:latest': {'fiqa/regression-control': {}},
    'tev1:latest': {'fiqa/regression-control': {}},
  };
  const attempts = {'nimble:latest': [], 'tev1:latest': []};

  const coverage = cohortCoverage('fiqa', [fiqaItem], answerMaps, attempts);

  assert.equal(coverage.complete, true);
  assert.equal(coverage.scoreable, true);
  assert.equal(coverage.verdict, 'READY');
});
test('paired significance marks the local model worse only when Jev wins', () => {
  const localLoss = pairedCorrectness(Array.from({length: 8}, () => true), Array.from({length: 8}, () => false));
  const localWin = pairedCorrectness(Array.from({length: 8}, () => false), Array.from({length: 8}, () => true));

  assert.equal(localLoss.significantlyWorse, true);
  assert.equal(localWin.significantlyWorse, false);
});
