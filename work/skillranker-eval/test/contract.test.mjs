// Offline contract tests. No key, no network.
//
// PLANTED NEGATIVE: a wrong pick must score 2. If someone weakens
// LOSS.incorrect_recommendation_on_positive, this file goes RED.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  ABSTAIN_CRITERION,
  LOSS,
  NONE,
  PICK_INSTRUCTIONS,
  TOP1_GATE,
  applyPromotionGate,
  assertFrozenLoss,
  canAskChoice,
  criteriaFromRoster,
  expectedCoinFlipLoss,
  exportJsonl,
  installableNotOffered,
  judgeSkillPick,
  loadCases,
  loadExpected,
  loadPlanted,
  loadPolicy,
  rosterOf,
  runAlwaysAbstain,
  runCoinFlip,
  runPlanted,
  scoreDecision,
  scoreExpectedExample,
  stateFromCase,
  verifyExpectedValues,
} from '../score.mjs';

test('frozen loss table matches the pulled policy byte-for-byte on the values', () => {
  const theirs = assertFrozenLoss(loadPolicy());
  assert.equal(theirs.incorrect_recommendation_on_positive, 2);
  assert.equal(LOSS.incorrect_recommendation_on_positive, 2);
  assert.equal(loadPolicy().promotion_requirements.top_one_precision.minimum_rate, TOP1_GATE);
});

test('expected_values.v1.json loss examples recompute', () => {
  const expected = loadExpected();
  assert.equal(expected.status, 'deterministic_contract_examples_not_measured_results');
  for (const ex of expected.loss_examples) {
    assert.equal(scoreExpectedExample(ex).loss, ex.loss, ex.example_id);
  }
  verifyExpectedValues(expected);
});

test('always-abstain on their 12 cases is 10/12 = 0.833 and misses the gate', () => {
  const { rows, summary } = runAlwaysAbstain(loadCases());
  assert.equal(rows.length, 12);
  assert.equal(summary.positives, 10);
  assert.equal(summary.totalLoss, 10);
  assert.ok(Math.abs(summary.meanLoss - 10 / 12) < 1e-12);
  assert.equal(summary.precision, 0);
  const gate = applyPromotionGate(summary, { split: 'diagnostic_synthetic' });
  assert.equal(gate.fail, true, 'always-abstain must FAIL ≥0.90');
  assert.equal(gate.promotable, false);
});

test('coin-flip expected loss is worse than always-abstain', () => {
  const cases = loadCases();
  const expected = expectedCoinFlipLoss(cases);
  const aa = runAlwaysAbstain(cases).summary.meanLoss;
  assert.ok(expected > aa, `coin-flip E=${expected} should exceed always-abstain ${aa}`);
  const sampled = runCoinFlip(cases, { trials: 200, seed: 1 });
  assert.ok(Math.abs(sampled.expected - expected) < 1e-12);
  // 200 trials is noisy; only require it stays on the expensive side of abstain.
  assert.ok(sampled.summary.sampledMean > aa);
});

test('PLANTED NEGATIVE: wrong pick scores 2 and the runner REDs if it does not', () => {
  const planted = loadPlanted();
  assert.equal(planted.length, 1);
  assert.equal(planted[0].planted_pick, 'wrong-skill');
  const got = scoreDecision({ y: planted[0].acceptable_additional_invocations_y, pick: 'wrong-skill' });
  assert.equal(got.loss, 2);
  assert.equal(got.class, 'incorrect_recommendation_on_positive');
  const run = runPlanted(planted);
  assert.equal(run.red, true);
  assert.equal(run.rows[0].loss, 2);
});

test('PLANTED NEGATIVE: a weakened loss table is caught', () => {
  const planted = loadPlanted()[0];
  const weakened = scoreDecision({ y: planted.acceptable_additional_invocations_y, pick: 'wrong-skill' });
  // If this ever equals 0 or 1, the contract is broken. Pin the inequality.
  assert.notEqual(weakened.loss, 0);
  assert.notEqual(weakened.loss, 1);
  assert.equal(weakened.loss, 2);
  const mutant = { ...planted, expected_loss: 2 };
  // Simulate a scorer that awards 1 for a wrong pick by lying about expected_loss.
  assert.throws(
    () => runPlanted([{ ...mutant, planted_pick: 'wrong-skill', expected_loss: 0 }]),
    /PLANTED NEGATIVE DID NOT RED/,
  );
});

test('promotion gate is hard: 0.800 FAILs, 0.900 rate-passes, n=12 still cannot promote', () => {
  const miss = applyPromotionGate({ precision: 0.8, positives: 10, n: 12 }, { split: 'diagnostic_synthetic' });
  assert.equal(miss.fail, true);
  assert.ok(miss.failures.some((f) => f.code === 'TOP1_BELOW_GATE'));
  const clear = applyPromotionGate({ precision: 0.9, positives: 10, n: 12 }, { split: 'diagnostic_synthetic' });
  assert.equal(clear.fail, false);
  assert.equal(clear.ratePass, true);
  assert.equal(clear.promotable, false);
  assert.ok(clear.failures.some((f) => f.code === 'SPLIT_FORBIDS_PROMOTION'));
  assert.ok(clear.failures.some((f) => f.code === 'COHORT_TOO_SMALL'));
});

test('overflow case is the installable≠offered hole: Y exists, roster export is empty', () => {
  const overflow = loadCases().find((c) => c.case_id === 'synthetic-overflow-retrieval-paraphrase');
  assert.ok(overflow);
  assert.equal(rosterOf(overflow).length, 0);
  assert.equal(installableNotOffered(overflow), true);
  const criteria = criteriaFromRoster(rosterOf(overflow));
  assert.deepEqual(Object.keys(criteria), [NONE]);
  assert.equal(canAskChoice(criteria), false);
  const { rows } = runAlwaysAbstain([overflow]);
  assert.equal(rows[0].loss, 1);
  assert.equal(rows[0].installableNotOffered, true);
});

test('export JSONL is one score row per case and is not a product claim', () => {
  const { rows } = runAlwaysAbstain(loadCases());
  const path = join(mkdtempSync(join(tmpdir(), 'sr-eval-')), 'scores.jsonl');
  exportJsonl(path, rows);
  const exported = readFileSync(path, 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  assert.equal(exported.length, 12);
  assert.equal(exported[0].schema, 'jev.skillranker-eval.score.v1');
  assert.equal(exported.every((r) => r.measured_product === false), true);
  assert.equal(exported.every((r) => r.binary_path === null), true);
  assert.ok(exported.every((r) => 'pick' in r && 'loss' in r && 'y' in r));
});

test('judge shape: same instructions, __none__ abstain, no second noul, fail-safe abstain', async () => {
  const c = loadCases()[0];
  const state = stateFromCase(c);
  assert.deepEqual(Object.keys(state).sort(), ['already_loaded', 'constraints', 'task']);
  const criteria = criteriaFromRoster(rosterOf(c));
  assert.equal(criteria[NONE], ABSTAIN_CRITERION);
  assert.ok(Object.keys(criteria).length >= 2);

  const asked = [];
  const ask = async (opts) => {
    asked.push(opts);
    return {
      ok: true,
      choice: 'rust-test-triage',
      confidence: 0.9,
      probabilities: { 'rust-test-triage': 0.8, 'release-preparations': 0.1, [NONE]: 0.1 },
      model: 'fake',
    };
  };
  const hit = await judgeSkillPick({
    roster: rosterOf(c),
    task: c.prompt_summary,
    constraints: c.current_constraints,
    already_loaded: c.already_available_references,
    ask,
  });
  assert.equal(asked[0].instructions, PICK_INSTRUCTIONS);
  assert.equal(asked[0].classes[NONE], ABSTAIN_CRITERION);
  assert.equal('helpful' in asked[0], false);
  assert.equal(hit.pick, 'rust-test-triage');
  assert.equal(hit.asked, true);

  const failed = await judgeSkillPick({
    roster: rosterOf(c),
    task: c.prompt_summary,
    ask: async () => ({ ok: false, reason: 'transport' }),
  });
  assert.equal(failed.pick, NONE);
  assert.equal(failed.unavailable, true);

  const empty = await judgeSkillPick({
    roster: [],
    task: 'overflow',
    ask: async () => {
      throw new Error('must not call Jev when roster cannot form a choice');
    },
  });
  assert.equal(empty.asked, false);
  assert.equal(empty.pick, NONE);
  assert.equal(empty.reason, 'roster_too_small_to_ask');
});

test('needless suggestion on a no-match is loss 2 (the other expensive error)', () => {
  const noMatch = loadCases().find((c) => c.case_kind === 'no_match_advisory');
  const needless = scoreDecision({ y: [], pick: rosterOf(noMatch)[0].skill_id });
  assert.equal(needless.loss, 2);
  const abstain = scoreDecision({ y: [], pick: NONE });
  assert.equal(abstain.loss, 0);
});
