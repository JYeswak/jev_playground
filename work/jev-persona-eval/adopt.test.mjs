// Offline mechanics of the persona adopt delta. No Jev calls, no network.
import test from 'node:test';
import assert from 'node:assert/strict';
import { joinOutcomes } from '../jev-eval-honesty/outcome-join.mjs';
import { randomBaseline, ownConstant } from '../jev-eval-honesty/random-judge.mjs';

const rows = [
  '{"customType": "persona-eval.decision.v1", "data": {"kind": "golden_scored", "toolCallId": "g1"}}',
  '{"customType": "persona-eval.decision.v1", "data": {"kind": "trap_answered", "toolCallId": "t1"}}',
];

test('trap-answered rows survive the join and are detectable as TRAP-LEAK', () => {
  const j = joinOutcomes({ rows, expectKey: ['kind'], idKey: 'toolCallId' });
  assert.equal(j.zeroHit, false);
  assert.equal(j.matched.length, 2);
  const leaks = j.matched.filter((m) => m.verdict === 'trap_answered');
  assert.equal(leaks.length, 1);
  assert.equal(leaks[0].id, 't1');
});

test('constant baseline on golden-style verdicts is the majority share', () => {
  const cases = [{ name: 'g1', truth: true }, { name: 'g2', truth: true }, { name: 'g3', truth: false }];
  const oc = ownConstant({ cases, truthKey: 'truth' });
  assert.equal(oc.accuracy, 2 / 3);
});

test('planted: a unanimous golden set has constant 1.0 that no verdict can beat', () => {
  const cases = [{ name: 'g1', truth: true }, { name: 'g2', truth: true }];
  const oc = ownConstant({ cases, truthKey: 'truth' });
  assert.equal(oc.accuracy, 1.0);
  const rb = randomBaseline({ cases, truthKey: 'truth', seed: 20260920 });
  assert.equal(rb.accuracy, 1.0);
});
