import assert from 'node:assert/strict';
import test from 'node:test';
import { readSessionLogs } from './transcript-reader.mjs';
import { runCounterfactual, validateBacktestFloor } from './counterfactual.mjs';
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

test('one simple tool call can be a cheap candidate', () => {
  const result = runCounterfactual([{ turns: [turn({ toolCalls: 1 })] }]);
  assert.equal(result.totals.routedCheap, 1);
});

test('multiple tool calls stay on the recorded baseline', () => {
  const result = runCounterfactual([{ turns: [turn({ toolCalls: 2 })] }]);
  assert.equal(result.totals.routedCheap, 0);
  assert.equal(result.turns[0].classificationReason, 'tool-call-turn');
  assert.equal(result.turns[0].counterfactualSpend, result.turns[0].actualSpend);
});

test('floor rejects a one-turn no-split run', () => {
  const result = runCounterfactual([{ turns: [turn({ toolCalls: 2 })] }]);
  const failures = validateBacktestFloor(result);
  assert.deepEqual(
    failures.map((failure) => failure.code),
    ['INSUFFICIENT_CLASSIFIABLE_TURNS', 'NO_CHEAP_CANDIDATES'],
  );
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

// --- mutation-driven tests. Each closes a hole tools/mutation-harness.mjs proved open: the suite
// was green at 12/12 while these three behaviours could be deleted or inverted outright.

test('a turn over the completion-token budget is not routed to cheap', () => {
  // HOLE: replacing the completion-budget gate with `if (false)` left the suite green, so nothing
  // asserted the gate existed. The prompt-token twin was covered; this leg was not.
  const result = runCounterfactual([{ turns: [turn({ completionTokens: 999999 })] }]);
  assert.equal(result.totals.routedCheap, 0);
  assert.equal(result.turns[0].classificationReason, 'completion-token-budget');
});

test('missing token counts are never treated as cheap-routable', () => {
  // HOLE: flipping missing-token-counts to cheapSufficient:true left the suite green, so a log with
  // absent counts could be priced as routable and inflate the denominator the README tells a
  // stranger to read first.
  for (const missing of [{ promptTokens: null }, { completionTokens: null }]) {
    const result = runCounterfactual([{ turns: [turn(missing)] }]);
    assert.equal(result.totals.routedCheap, 0);
    assert.equal(result.turns[0].classificationReason, 'missing-token-counts');
  }
});

test('the counterfactual leg actually accumulates, so savings are not a mirror of actual spend', () => {
  // HOLE, and the one that mattered: zeroing the counterfactual accumulator made estimatedSavings a
  // mirror of actualSpend with the suite STILL GREEN — and README.md publishes 0.0447% derived from
  // exactly that leg. Two turns, so a per-turn-only assertion cannot satisfy this by accident.
  const result = runCounterfactual([{ turns: [turn(), turn({ turnIndex: 2 })] }]);
  assert(result.totals.counterfactualSpend > 0, 'counterfactual leg must be nonzero');
  assert.notEqual(result.totals.estimatedSavings, result.totals.actualSpend);
  assert.equal(
    result.totals.estimatedSavings.toFixed(9),
    (result.totals.actualSpend - result.totals.counterfactualSpend).toFixed(9),
  );
});
