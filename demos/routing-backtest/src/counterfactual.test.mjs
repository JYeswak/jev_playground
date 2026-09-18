import assert from 'node:assert/strict';
import test from 'node:test';
import { readSessionLogs } from './transcript-reader.mjs';
import { runCounterfactual } from './counterfactual.mjs';
import { PRICE_TABLE } from './pricing.mjs';

const turn = (overrides = {}) => ({
  sessionId: 'test',
  turnIndex: 1,
  model: 'gpt-5.6-luna',
  promptTokens: 1000,
  completionTokens: 100,
  actualSpend: 0.1,
  toolCalls: 0,
  classifiable: true,
  skipReason: null,
  ...overrides,
});

test('routes a small text-only turn to cheap and prices both paths', () => {
  const result = runCounterfactual([{ turns: [turn()] }]);
  assert.equal(result.totals.turnsSeen, 1);
  assert.equal(result.totals.routedCheap, 1);
  assert(result.totals.counterfactualSpend < result.totals.actualSpend);
  assert.equal(result.failures.length, 0);
});

test('tool-call turns stay on the recorded baseline', () => {
  const result = runCounterfactual([{ turns: [turn({ toolCalls: 1 })] }]);
  assert.equal(result.totals.routedCheap, 0);
  assert.equal(result.turns[0].classificationReason, 'tool-call-turn');
  assert.equal(result.turns[0].counterfactualSpend, result.turns[0].actualSpend);
});

test('missing price-table model is an error, never a zero row', () => {
  assert.throws(
    () =>
      runCounterfactual([{ turns: [turn({ model: 'frontier-unlisted-9x' })] }], {
        priceTable: PRICE_TABLE,
      }),
    (error) => error?.code === 'MISSING_PRICE_MODEL',
  );
});

test('committed unknown-model fixture fires the missing-price RED arm', async () => {
  const sessions = await readSessionLogs([
    new URL('../fixtures/unknown-model-turns.jsonl', import.meta.url).pathname,
  ]);
  assert.throws(
    () => runCounterfactual(sessions.sessions),
    (error) => error?.code === 'MISSING_PRICE_MODEL',
  );
});

test('missing actual spend is recorded as a failure, not coerced to zero', () => {
  const result = runCounterfactual([{ turns: [turn({ actualSpend: null })] }]);
  assert.equal(result.totals.turnsSeen, 1);
  assert.equal(result.turns[0].counterfactualSpend, null);
  assert.equal(result.failures[0].code, 'MISSING_ACTUAL_SPEND');
});
