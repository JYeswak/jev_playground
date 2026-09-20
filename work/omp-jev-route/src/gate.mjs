/**
 * Preregistered eval gate copied from skillranker @6a74cca
 * tests/eval/evaluation_policy.v1.json (loss_policy + promotion_requirements)
 * and tests/eval/expected_values.v1.json (always_abstain_counterexample).
 *
 * This is the CONTRACT, not a measurement of their corpus. diagnostic_synthetic
 * cannot promote — their own split rule (evaluation_policy.v1.json:53-56).
 */
export const LOSS = {
  correct_recommendation_on_positive: 0,
  correct_no_match_abstention: 0,
  false_abstention_on_positive: 1,
  incorrect_recommendation_on_positive: 2,
  needless_recommendation_on_no_match: 2,
  operationally_unavailable_on_attempted_case: 2,
};

export const POLICY = {
  schema_version: 'skillranker.evaluation_policy.v1',
  policy_id: 'skillranker-eval-policy-v1',
  status: 'frozen_contract_not_evidence',
  split: 'diagnostic_synthetic',
  always_abstain_counterexample_required: true,
  source: 'Dicklesworthstone/skillranker@6a74cca tests/eval/evaluation_policy.v1.json',
  promotion: {
    top_one_precision: 0.9,
    minimum_two_sided_95_wilson_lower_endpoint: 0.8,
    positive_case_suggestion_rate: 0.8,
    needless_suggestion_rate: 0.05,
    relevance_cohort_minimum_primary_cases: 300,
  },
  non_claims: [
    'This artifact is not an evaluator of skillranker the product.',
    'diagnostic_synthetic cannot promote, calibrate, or make a statistical quality claim.',
    'Authored fixtures here are contract oracles only. They are not their corpus.',
  ],
};

export function lossOf(decision, y) {
  const labels = Array.isArray(y) ? y : [];
  const yNonEmpty = labels.length > 0;
  const kind = decision && typeof decision === 'object' ? decision.decision : undefined;
  const top1 = decision?.skills?.[0]?.skill_id;

  if (kind === 'unavailable') {
    return { loss: LOSS.operationally_unavailable_on_attempted_case, why: 'operationally_unavailable_on_attempted_case' };
  }
  if (yNonEmpty && kind === 'abstain') {
    return { loss: LOSS.false_abstention_on_positive, why: 'false_abstention_on_positive' };
  }
  if (yNonEmpty && (kind === 'ranked' || kind === 'explicit') && labels.includes(top1)) {
    return { loss: LOSS.correct_recommendation_on_positive, why: 'correct_recommendation_on_positive' };
  }
  if (yNonEmpty) {
    return { loss: LOSS.incorrect_recommendation_on_positive, why: 'incorrect_recommendation_on_positive' };
  }
  if (kind === 'abstain') {
    return { loss: LOSS.correct_no_match_abstention, why: 'correct_no_match_abstention' };
  }
  return { loss: LOSS.needless_recommendation_on_no_match, why: 'needless_recommendation_on_no_match' };
}

export function alwaysAbstain(cases) {
  return (Array.isArray(cases) ? cases : []).map((c) => ({
    ...c,
    decision: { decision: 'abstain', reason: 'always-abstain-control', skills: [] },
  }));
}

export function evaluate(cases) {
  const rows = Array.isArray(cases) ? cases : [];
  let policyLoss = 0;
  let alwaysLoss = 0;
  let positives = 0;
  let emitted = 0;
  let truePos = 0;
  const scored = [];

  for (const c of rows) {
    const y = Array.isArray(c.y) ? c.y : [];
    const decision = c.decision ?? { decision: 'unavailable', skills: [] };
    const one = lossOf(decision, y);
    const control = lossOf({ decision: 'abstain', skills: [] }, y);
    policyLoss += one.loss;
    alwaysLoss += control.loss;
    if (y.length > 0) positives += 1;
    if (decision.decision === 'ranked' || decision.decision === 'explicit') {
      emitted += 1;
      if (y.includes(decision.skills?.[0]?.skill_id)) truePos += 1;
    }
    scored.push({ case_id: c.case_id, y, decision: decision.decision, ...one });
  }

  const n = rows.length || 1;
  const top1 = emitted > 0 ? truePos / emitted : null;

  return {
    n: rows.length,
    positives,
    mean_loss: policyLoss / n,
    policy_total_loss: policyLoss,
    always_abstain_total_loss: alwaysLoss,
    always_abstain_mean_loss: alwaysLoss / n,
    always_abstain_fails_positive_case_value: alwaysLoss > policyLoss,
    top_one_precision: top1,
    promotion_bar: POLICY.promotion.top_one_precision,
    promoted: false,
    split: POLICY.split,
    status: POLICY.status,
    verdict: 'CANNOT_PROMOTE: diagnostic_synthetic is contract-only; not a holdout',
    rows: scored,
  };
}
