import test from 'node:test';
import assert from 'node:assert/strict';
import { LOSS, POLICY, lossOf, evaluate, alwaysAbstain } from '../src/gate.mjs';

test('LOSS table is copied from skillranker evaluation_policy.v1, not invented', () => {
  assert.deepEqual(LOSS, {
    correct_recommendation_on_positive: 0,
    correct_no_match_abstention: 0,
    false_abstention_on_positive: 1,
    incorrect_recommendation_on_positive: 2,
    needless_recommendation_on_no_match: 2,
    operationally_unavailable_on_attempted_case: 2,
  });
  assert.equal(POLICY.schema_version, 'skillranker.evaluation_policy.v1');
  assert.equal(POLICY.status, 'frozen_contract_not_evidence');
  assert.equal(POLICY.split, 'diagnostic_synthetic');
  assert.equal(POLICY.always_abstain_counterexample_required, true);
  assert.equal(POLICY.promotion.top_one_precision, 0.9);
});

test('lossOf assigns the six contract classes', () => {
  assert.equal(lossOf({ decision: 'ranked', skills: [{ skill_id: 'a' }] }, ['a']).why, 'correct_recommendation_on_positive');
  assert.equal(lossOf({ decision: 'ranked', skills: [{ skill_id: 'a' }] }, ['a']).loss, 0);
  assert.equal(lossOf({ decision: 'abstain', skills: [] }, ['a']).why, 'false_abstention_on_positive');
  assert.equal(lossOf({ decision: 'abstain', skills: [] }, ['a']).loss, 1);
  assert.equal(lossOf({ decision: 'ranked', skills: [{ skill_id: 'b' }] }, ['a']).why, 'incorrect_recommendation_on_positive');
  assert.equal(lossOf({ decision: 'ranked', skills: [{ skill_id: 'b' }] }, ['a']).loss, 2);
  assert.equal(lossOf({ decision: 'abstain', skills: [] }, []).why, 'correct_no_match_abstention');
  assert.equal(lossOf({ decision: 'abstain', skills: [] }, []).loss, 0);
  assert.equal(lossOf({ decision: 'ranked', skills: [{ skill_id: 'a' }] }, []).why, 'needless_recommendation_on_no_match');
  assert.equal(lossOf({ decision: 'ranked', skills: [{ skill_id: 'a' }] }, []).loss, 2);
  assert.equal(lossOf({ decision: 'unavailable', skills: [] }, ['a']).why, 'operationally_unavailable_on_attempted_case');
  assert.equal(lossOf({ decision: 'unavailable', skills: [] }, ['a']).loss, 2);
});

test('always-abstain counterexample: doing nothing loses on positives (their cohort shape)', () => {
  // Transcribed from skillranker tests/eval/expected_values.v1.json
  // always_abstain_counterexample.cohort — NOT their synthetic_cases corpus.
  const cohort = [
    { case_id: 'p1', y: ['s'], decision: { decision: 'ranked', skills: [{ skill_id: 's' }] } },
    { case_id: 'p2', y: ['s'], decision: { decision: 'ranked', skills: [{ skill_id: 's' }] } },
    { case_id: 'p3', y: ['s'], decision: { decision: 'ranked', skills: [{ skill_id: 's' }] } },
    { case_id: 'p4', y: ['s'], decision: { decision: 'ranked', skills: [{ skill_id: 'wrong' }] } },
    { case_id: 'n1', y: [], decision: { decision: 'abstain', skills: [] } },
    { case_id: 'n2', y: [], decision: { decision: 'abstain', skills: [] } },
  ];
  const report = evaluate(cohort);
  assert.equal(report.always_abstain_total_loss, 4);
  assert.ok(Math.abs(report.always_abstain_mean_loss - 4 / 6) < 1e-9);
  assert.equal(report.policy_total_loss, 2);
  assert.ok(report.always_abstain_mean_loss > report.mean_loss);
  assert.equal(report.always_abstain_fails_positive_case_value, true);
});

test('alwaysAbstain is a real function that abstains every case', () => {
  const cases = [
    { y: ['s'] },
    { y: [] },
  ];
  const rows = alwaysAbstain(cases);
  assert.equal(rows.every((r) => r.decision.decision === 'abstain'), true);
  const report = evaluate(rows.map((r, i) => ({ ...cases[i], decision: r.decision })));
  assert.equal(report.always_abstain_total_loss, report.policy_total_loss);
});

test('diagnostic_synthetic cannot promote even on a perfect authored fixture', () => {
  const perfect = [
    { y: ['a'], decision: { decision: 'ranked', skills: [{ skill_id: 'a' }] } },
    { y: [], decision: { decision: 'abstain', skills: [] } },
  ];
  const report = evaluate(perfect);
  assert.equal(report.top_one_precision, 1);
  assert.equal(report.promoted, false);
  assert.equal(report.split, 'diagnostic_synthetic');
  assert.equal(report.status, 'frozen_contract_not_evidence');
  assert.ok(report.always_abstain_mean_loss !== undefined);
  assert.match(report.verdict, /CANNOT_PROMOTE|cannot promote/i);
});
