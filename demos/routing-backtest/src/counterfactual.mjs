import { PRICE_TABLE, priceScenarioTokens, requireModel } from './pricing.mjs';

export const DEFAULT_POLICY = {
  cheapModel: 'cheap-1',
  maxPromptTokens: 20_000,
  maxCompletionTokens: 2_000,
  maxToolCalls: 1,
};

function classifyTurn(turn, policy) {
  if (!turn.classifiable) {
    return { cheapSufficient: false, reason: `unclassifiable:${turn.skipReason}` };
  }
  if (turn.promptTokens === null || turn.completionTokens === null) {
    return { cheapSufficient: false, reason: 'missing-token-counts' };
  }
  if (turn.toolCalls > policy.maxToolCalls) {
    return { cheapSufficient: false, reason: 'tool-call-turn' };
  }
  if (turn.promptTokens > policy.maxPromptTokens) {
    return { cheapSufficient: false, reason: 'prompt-token-budget' };
  }
  if (turn.completionTokens > policy.maxCompletionTokens) {
    return { cheapSufficient: false, reason: 'completion-token-budget' };
  }
  return { cheapSufficient: true, reason: 'text-only-within-token-budgets' };
}

export function runCounterfactual(sessions, options = {}) {
  const policy = { ...DEFAULT_POLICY, ...(options.policy ?? {}) };
  const priceTable = options.priceTable ?? PRICE_TABLE;
  requireModel(priceTable, policy.cheapModel);
  const failures = [];
  const turns = [];
  const perModel = {};
  let actualSpend = 0;
  let counterfactualSpend = 0;

  for (const session of sessions) {
    for (const turn of session.turns) {
      const classification = classifyTurn(turn, policy);
      if (turn.classifiable && turn.actualSpend === null) {
        failures.push({
          code: 'MISSING_ACTUAL_SPEND',
          sessionId: turn.sessionId,
          turnIndex: turn.turnIndex,
          reason: 'classifiable turn has no usage.cost.total',
        });
        turns.push({
          classifiable: true,
          sessionId: turn.sessionId,
          turnIndex: turn.turnIndex,
          model: turn.model,
          promptTokens: turn.promptTokens,
          completionTokens: turn.completionTokens,
          toolCalls: turn.toolCalls,
          actualSpend: null,
          cheapModel: policy.cheapModel,
          cheapSufficient: false,
          classificationReason: 'missing-actual-spend',
          counterfactualSpend: null,
          estimatedSavings: null,
        });
        continue;
      }
      if (turn.classifiable) requireModel(priceTable, String(turn.model));
      const actual = turn.actualSpend;
      const counterfactual =
        classification.cheapSufficient && turn.promptTokens !== null && turn.completionTokens !== null
          ? priceScenarioTokens(
              priceTable,
              policy.cheapModel,
              turn.promptTokens,
              turn.completionTokens,
            )
          : actual;
      if (actual !== null) actualSpend += actual;
      if (counterfactual !== null) counterfactualSpend += counterfactual;
      if (turn.classifiable) {
        const model = String(turn.model);
        const bucket = (perModel[model] ??= {
          turns: 0,
          actualSpend: 0,
          counterfactualSpend: 0,
          routedCheap: 0,
        });
        bucket.turns += 1;
        bucket.actualSpend += actual;
        bucket.counterfactualSpend += counterfactual;
        if (classification.cheapSufficient) bucket.routedCheap += 1;
      }
      turns.push({
        classifiable: turn.classifiable,
        sessionId: turn.sessionId,
        turnIndex: turn.turnIndex,
        model: turn.model,
        promptTokens: turn.promptTokens,
        completionTokens: turn.completionTokens,
        toolCalls: turn.toolCalls,
        actualSpend: actual,
        cheapModel: policy.cheapModel,
        cheapSufficient: classification.cheapSufficient,
        classificationReason: classification.reason,
        counterfactualSpend: counterfactual,
        estimatedSavings: actual === null ? null : actual - counterfactual,
      });
    }
  }
  if (turns.length === 0 || !turns.some((turn) => turn.classifiable)) {
    const error = new Error('no priced turns found; empty scan set is an error');
    error.code = 'EMPTY_PRICED_SET';
    throw error;
  }
  return {
    policy,
    priceTable,
    turns,
    perModel,
    totals: {
      turnsSeen: turns.length,
      classifiableTurns: turns.filter((turn) => turn.classifiable).length,
      routedCheap: turns.filter((turn) => turn.cheapSufficient).length,
      actualSpend,
      counterfactualSpend,
      estimatedSavings: actualSpend - counterfactualSpend,
    },
    failures,
  };
}

export const MIN_CLASSIFIABLE_TURNS = 2;

export function validateBacktestFloor(result, minimum = MIN_CLASSIFIABLE_TURNS) {
  const failures = [...result.failures];
  if (result.totals.classifiableTurns < minimum) {
    failures.push({
      code: 'INSUFFICIENT_CLASSIFIABLE_TURNS',
      reason: `classifiable turns ${result.totals.classifiableTurns} < required floor ${minimum}`,
    });
  }
  if (result.totals.classifiableTurns > 0 && result.totals.routedCheap === 0) {
    failures.push({ code: 'NO_CHEAP_CANDIDATES', reason: 'no turn qualifies for the cheap scenario' });
  }
  if (result.totals.classifiableTurns > 0 && result.totals.routedCheap === result.totals.classifiableTurns) {
    failures.push({ code: 'NO_BASELINE_CANDIDATES', reason: 'every turn qualifies for the cheap scenario' });
  }
  return failures;
}
