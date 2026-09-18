export const PRICE_TABLE = {
  schema: 'jev-route-backtest.price-table.v1',
  as_of: '2026-09-18',
  currency: 'USD',
  unit: 'USD per million tokens for scenario prices',
  rederivation:
    'Baseline spend is read from usage.cost.total in each session log. cheap-1 rates are an explicit counterfactual assumption and must be refreshed from the provider price sheet before any live routing.',
  models: {
    'gpt-5.6-luna': { source: 'observed usage.cost.total', mode: 'recorded' },
    'muse-spark-1.3-contributor': { source: 'observed usage.cost.total', mode: 'recorded' },
    'cheap-1': {
      source: 'scenario assumption; refresh before live use',
      mode: 'scenario',
      inputPerMillion: 0.2,
      outputPerMillion: 0.8,
    },
  },
};

export function requireModel(priceTable, model) {
  const entry = priceTable.models[model];
  if (!entry) {
    const error = new Error(`missing price-table entry for model: ${model}`);
    error.code = 'MISSING_PRICE_MODEL';
    throw error;
  }
  return entry;
}

export function priceScenarioTokens(priceTable, model, promptTokens, completionTokens) {
  const entry = requireModel(priceTable, model);
  if (entry.mode !== 'scenario') {
    throw new Error(`model ${model} has no scenario token price`);
  }
  if (!Number.isFinite(promptTokens) || !Number.isFinite(completionTokens)) {
    throw new Error(`missing token counts for scenario model: ${model}`);
  }
  return (
    (promptTokens / 1_000_000) * entry.inputPerMillion +
    (completionTokens / 1_000_000) * entry.outputPerMillion
  );
}
