/**
 * The test §16 proved was missing.
 *
 * `safeAppend` was called at four sites and defined at none, so the first tool_call threw
 * ReferenceError into the outer catch and the observer emitted NOTHING — deterministically,
 * on every run, for as long as the package has existed. Every existing test passed throughout,
 * because they asserted the handler does not throw, and a handler that silently swallows
 * everything does not throw.
 *
 * So these assert the opposite thing: that rows ARE produced. An observer's contract is to
 * observe; "did not crash" is not evidence that it did.
 *
 * Run: node --test work/omp-jev-observer/test/emits-rows.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import observer from '../src/observer.mjs';

/** Minimal host stand-in: captures rows and exposes the registered handler. */
function harness(overrides = {}) {
  const rows = [];
  let handler;
  const pi = {
    on: (_event, h) => {
      handler = h;
    },
    appendEntry: async (type, data) => {
      rows.push({ type, data });
    },
  };
  observer(pi, {
    enabled: true,
    classify: async () => ({
      questionSet: ['q'],
      probabilities: { flag: 0.9, pass: 0.1 },
      costUsd: 0,
    }),
    ...overrides,
  });
  return { rows, run: (event) => handler(event) };
}

const EVENT = { toolName: 'bash', toolCallId: 'tc-1', input: { command: 'echo hello' } };

test('PLANTED NEGATIVE for the safeAppend defect: a tool_call produces at least one row', async () => {
  const h = harness();
  await h.run(EVENT);
  assert.ok(h.rows.length > 0, 'observer emitted NOTHING — this is the §16 defect (11ff17b)');
});

test('a decision row is emitted, not only diagnostics', async () => {
  const h = harness();
  await h.run(EVENT);
  const decisions = h.rows.filter((r) => r.type.endsWith('decision.v1'));
  assert.ok(decisions.length > 0, `no decision row; saw types: ${h.rows.map((r) => r.type).join(', ')}`);
});

test('the decision row carries the toolCallId it observed', async () => {
  const h = harness();
  await h.run(EVENT);
  const decision = h.rows.find((r) => r.type.endsWith('decision.v1'));
  assert.equal(decision.data.toolCallId, 'tc-1');
});

test('a failure still emits a decision row carrying the error, never silence', async () => {
  // Note: the API-key check runs BEFORE classify, so on an unconfigured machine the recorded
  // error is the key error rather than an injected one. Either way the contract under test is
  // the same and is the one §16 found broken: a failure must be RECORDED, not swallowed.
  const h = harness({
    classify: async () => {
      throw new Error('boom');
    },
  });
  await h.run(EVENT);
  const decision = h.rows.find((r) => r.type.endsWith('decision.v1'));
  assert.ok(decision, 'a failed observation must still be recorded');
  assert.ok(decision.data.error, `error must be populated, got ${JSON.stringify(decision.data.error)}`);
});
test('an unwritable host does not throw into it — the swallow is deliberate, and now tested', async () => {
  const rows = [];
  let handler;
  const pi = {
    on: (_e, h) => {
      handler = h;
    },
    appendEntry: async () => {
      throw new Error('host refused the row');
    },
  };
  observer(pi, { enabled: true, classify: async () => ({ questionSet: ['q'], probabilities: { flag: 0.5, pass: 0.5 } }) });
  await assert.doesNotReject(() => handler(EVENT));
  assert.equal(rows.length, 0);
});
