import assert from 'node:assert/strict';
import test from 'node:test';
import {call, cohortCoverage, cohortVerdict} from './run.mjs';

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
test('only complete supported cohorts receive an exploratory bar verdict', () => {
  assert.equal(cohortVerdict('noul', true), 'EXPLORED');
  assert.equal(cohortVerdict('gate', false), 'NOT_RUN');
  assert.equal(cohortVerdict('fiqa', true), 'NOT_RUN');
});
test('complete FiQA answers remain unscoreable under the multi-positive metric', () => {
  const answerMaps = {
    'nimble:latest': {'fiqa/regression-control': {}},
    'tev1:latest': {'fiqa/regression-control': {}},
  };
  const attempts = {'nimble:latest': [], 'tev1:latest': []};

  const coverage = cohortCoverage('fiqa', [fiqaItem], answerMaps, attempts);

  assert.equal(coverage.complete, true);
  assert.equal(coverage.scoreable, false);
  assert.equal(coverage.verdict, 'NOT_RUN');
});
