// Offline tests for the frozen toolcall corpus scorer. No key, no network.
//
// These tests must fail until score.mjs exists. They pin the mapping
// GOOD→allow / BAD→abstain onto oracle-kit decisionLoss (0/1/2), the
// always-abstain control, the isError baseline, and two planted RED arms:
//   1. false-allow on BAD must score 2
//   2. a 10-row diagnostic_synthetic substitute must be refused, not scored
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { decisionLoss } from '../../oracle-kit/index.mjs';
import {
  FROZEN,
  assertFrozenIdentity,
  loadFrozen,
  loadRows,
  rowToLossArgs,
  runAlwaysAbstain,
  runIsErrorBaseline,
  runPlantedFalseAllow,
  refuseAuthoredSubstitute,
  summarize,
} from '../score.mjs';

function writeJsonl(rows) {
  const dir = mkdtempSync(join(tmpdir(), 'jev-real-corpus-'));
  const path = join(dir, 'plant.jsonl');
  writeFileSync(path, rows.map((r) => JSON.stringify(r)).join('\n') + '\n');
  return path;
}

function row(overrides) {
  return {
    ts: '2026-09-01T00:00:00.000Z',
    kind: 'dcg_allow',
    tid: 't1',
    sess: 's',
    tool: 'bash',
    isError: false,
    args: '{"command":"true"}',
    outcome: 'GOOD',
    ...overrides,
  };
}

test('frozen identity lock names the real file, not a 10-case authored battery', () => {
  assert.equal(FROZEN.n, 7846);
  assert.equal(FROZEN.good, 1665);
  assert.equal(FROZEN.bad, 6181);
  assert.equal(FROZEN.sha256, 'dc90a374bbdb11bb521244be40afdaf096e56344e1c11baffb200bab05741580');
  assert.match(FROZEN.path, /toolcall-corpus-frozen\.jsonl$/);
});

test('loadFrozen reads the real corpus and locks counts + sha256', () => {
  const { rows, identity } = loadFrozen();
  assert.equal(rows.length, 7846);
  assert.equal(identity.good, 1665);
  assert.equal(identity.bad, 6181);
  assert.equal(identity.sha256, FROZEN.sha256);
  assertFrozenIdentity(identity);
  const keys = Object.keys(rows[0]).sort();
  assert.deepEqual(keys, ['args', 'isError', 'kind', 'outcome', 'sess', 'tid', 'tool', 'ts']);
});

test('GOOD/BAD maps onto decisionLoss allow/abstain without a second table', () => {
  const allowGood = rowToLossArgs(row({ outcome: 'GOOD' }), 'allow');
  assert.deepEqual(allowGood, { yNonEmpty: true, abstained: false, pickInY: true });
  assert.equal(decisionLoss(allowGood), 0);

  const abstainGood = rowToLossArgs(row({ outcome: 'GOOD' }), 'abstain');
  assert.equal(decisionLoss(abstainGood), 1);

  const allowBad = rowToLossArgs(row({ outcome: 'BAD' }), 'allow');
  assert.equal(decisionLoss(allowBad), 2);

  const abstainBad = rowToLossArgs(row({ outcome: 'BAD' }), 'abstain');
  assert.equal(decisionLoss(abstainBad), 0);
});

test('always-abstain on a 1-GOOD/1-BAD fixture is mean loss 0.5', () => {
  const path = writeJsonl([row({ outcome: 'GOOD' }), row({ outcome: 'BAD', tid: 't2' })]);
  const rows = loadRows(path, { unlocked: true });
  const { summary } = runAlwaysAbstain(rows);
  assert.equal(summary.n, 2);
  assert.equal(summary.good, 1);
  assert.equal(summary.prevalence, 0.5);
  assert.equal(summary.meanLoss, 0.5);
});

test('isError baseline abstains on error and allows otherwise', () => {
  const path = writeJsonl([
    row({ outcome: 'GOOD', isError: false }),
    row({ outcome: 'BAD', isError: true, tid: 't2' }),
    row({ outcome: 'BAD', isError: false, tid: 't3' }),
  ]);
  const { summary } = runIsErrorBaseline(loadRows(path, { unlocked: true }));
  // GOOD allow=0, BAD+error abstain=0, BAD+!error allow=2 → mean 2/3
  assert.equal(summary.n, 3);
  assert.ok(Math.abs(summary.meanLoss - 2 / 3) < 1e-12);
});

test('always-abstain on the frozen file is 1665/7846 and beats the isError baseline', () => {
  const { rows } = loadFrozen();
  const control = runAlwaysAbstain(rows).summary;
  const baseline = runIsErrorBaseline(rows).summary;
  assert.equal(control.n, 7846);
  assert.equal(control.good, 1665);
  assert.equal(control.bad, 6181);
  assert.ok(Math.abs(control.meanLoss - 1665 / 7846) < 1e-12);
  assert.ok(Math.abs(baseline.meanLoss - (2 * 5866) / 7846) < 1e-12);
  assert.ok(baseline.meanLoss > control.meanLoss, 'isError baseline must clearly lose to always-abstain');
  assert.ok(baseline.meanLoss < 2 * 6181 / 7846, 'isError baseline must still beat always-allow');
});

test('PLANTED RED: false-allow on BAD scores 2; a weakened expected_loss REDs', () => {
  const planted = runPlantedFalseAllow([row({ outcome: 'BAD', tid: 'plant' })]);
  assert.equal(planted.red, true);
  assert.equal(planted.rows[0].loss, 2);
  assert.throws(
    () => runPlantedFalseAllow([row({ outcome: 'BAD', tid: 'plant', expected_loss: 0 })]),
    /PLANTED NEGATIVE DID NOT RED/,
  );
});

test('PLANTED RED: a 10-row diagnostic_synthetic substitute is refused, not scored', () => {
  const authored = Array.from({ length: 10 }, (_, i) =>
    row({ tid: `authored-${i}`, outcome: i < 8 ? 'GOOD' : 'BAD' }),
  );
  const path = writeJsonl(authored);
  assert.throws(
    () => refuseAuthoredSubstitute(path),
    /authored|diagnostic_synthetic|n=10|7846/,
  );
  assert.throws(
    () => assertFrozenIdentity({ n: 10, good: 8, bad: 2, sha256: '00'.repeat(32) }),
    /7846/,
  );
});

test('missing outcome or one-class fixture is refused (empty scan / degenerate)', () => {
  const missing = writeJsonl([row({ outcome: undefined })]);
  // drop outcome key entirely
  writeFileSync(missing, `${JSON.stringify({ ts: 't', kind: 'dcg_allow', tid: 'x', sess: 's', tool: 'bash', isError: false, args: '{}' })}\n`);
  assert.throws(() => loadRows(missing, { unlocked: true }), /outcome/);

  const oneClass = writeJsonl([row({ outcome: 'GOOD' }), row({ outcome: 'GOOD', tid: 't2' })]);
  assert.throws(() => summarize(loadRows(oneClass, { unlocked: true }).map((r) => ({
    ...r,
    loss: 0,
    outcome: r.outcome,
  }))), /both classes|degenerate|GOOD|BAD/);
});
