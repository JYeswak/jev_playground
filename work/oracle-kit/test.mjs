// oracle-kit self-test. Every case is a defect this lane actually shipped today.
import {
  auc, requireBoth, field, feasibility, ece, eProcess, requireKey, inspectKey,
  decisionLoss, meanDecisionLoss, emissionOnlyLoss, refuseInventedNoulGate,
  assertSdkSelector, SDK_ANSWER_FIELDS, mulberry32, stratifiedHalves, bestThreshold,
  selectSingleSignal, sigmoid, fitLogistic, scoreLogistic,
} from './index.mjs';
import assert from 'node:assert/strict';

let pass = 0;
const check = (name, fn) => { fn(); pass++; console.log(`  ok  ${name}`); };
const throws = (name, fn, re) => { assert.throws(fn, re); pass++; console.log(`  ok  ${name}`); };

// PLANTED NEGATIVE 1: the bug that produced three bogus router runs. A constant score must be
// reported as constant, not silently returned as a clean 0.500.
check('constant score is flagged, not reported as a null', () => {
  const r = auc([0, 0, 0, 0], [true, true, false, false]);
  assert.equal(r.value, 0.5);
  assert.equal(r.constant, true);
});

// PLANTED NEGATIVE 2: the degenerate arm that returned NaN in the gate oracle.
throws('degenerate label throws instead of returning NaN',
  () => auc([1, 2, 3], [true, true, true]), /degenerate label/);

// PLANTED NEGATIVE 3: reading a field name that does not exist in the SDK.
throws('missing field throws instead of scoring silence',
  () => field({ noul: 0.9 }, 'probabilities'), /no 'probabilities'/);
throws('.distribution is not a field in this SDK',
  () => field({ probabilities: { a: 1 } }, 'distribution'), /no 'distribution'/);

check('field reads the names the SDK actually uses', () => {
  assert.equal(field({ noul: 0.97 }, 'noul'), 0.97);
  assert.deepEqual(field({ probabilities: { a: 0.6, b: 0.4 } }, 'probabilities'), { a: 0.6, b: 0.4 });
});

// POSITIVE OBSERVABLE: a real signal scores above chance, a reversed one below.
check('auc separates a real signal in both directions', () => {
  const labels = [true, true, false, false];
  assert.equal(auc([1, 0.9, 0.2, 0.1], labels).value, 1);
  assert.equal(auc([0.1, 0.2, 0.9, 1], labels).value, 0);
});

check('feasibility refuses when the arm is blind', () => {
  assert.equal(feasibility([0.9, 0.8, 0.2, 0.1], [true, true, false, false]).ok, true);
  assert.equal(feasibility([0.5, 0.5, 0.5, 0.5], [true, true, false, false]).ok, false); // constant
});

check('ece is zero for a perfectly calibrated set and large for an overconfident one', () => {
  assert.equal(ece([1, 1, 0, 0], [true, true, false, false]), 0);
  assert.ok(ece([1, 1, 1, 1], [true, false, false, false]) > 0.7);
});

// The e-process must be directionally right and appropriately conservative.
check('eProcess accumulates toward rejection, and stays conservative on few observations', () => {
  assert.equal(eProcess(Array(8).fill(true)).reject, false);      // 8 unanimous is not yet enough
  assert.ok(eProcess(Array(40).fill(true)).reject);               // sustained evidence rejects
  assert.ok(eProcess(Array(8).fill(false)).e < 1);                // evidence the other way
  assert.equal(eProcess([true, false, true, false]).reject, false); // a tie concludes nothing
});

check('requireBoth names the caller', () => {
  assert.throws(() => requireBoth([true, true], 'myarm'), /myarm/);
});


// R33: absence must be proven against the record's own keys, never inferred from a failed lookup.
throws('requireKey names every key present when the field is absent',
  () => requireKey({ command: 'x', kind: 'harm_fire' }, 'toolCallId', 'decision'),
  /Keys present: \[command, kind\]/);

check('requireKey returns the value when present, and inspectKey reports evidence either way', () => {
  assert.equal(requireKey({ command: 'chmod -R 777 /etc' }, 'command'), 'chmod -R 777 /etc');
  const miss = inspectKey({ a: 1, b: 2 }, 'c');
  assert.equal(miss.present, false);
  assert.deepEqual(miss.keys, ['a', 'b']);   // absence reported WITH the key list
  assert.equal(inspectKey({ noul: 0.9 }, 'noul').present, true);
});

throws('requireKey refuses a non-object rather than reporting a false absence',
  () => requireKey(undefined, 'command', 'decision'), /not an object/);

// §4(a) math-and-next-level-20260919.md — skillranker 0/1/2 as a proper *decision* score.
// Always-abstain mean loss = nPos/n = 10/12 = 0.833. A table that only charges wrong
// *emissions* lets silence win; that planted negative must fail the proper table.
const SKILLRANKER_12 = [
  ...Array(10).fill({ yNonEmpty: true, abstained: true, pickInY: false }),
  ...Array(2).fill({ yNonEmpty: false, abstained: true, pickInY: false }),
];

check('always-abstain mean loss equals nPos/n on the skillranker 10/12 identity (0.833)', () => {
  const mean = meanDecisionLoss(SKILLRANKER_12, decisionLoss);
  assert.equal(mean, 10 / 12);
  assert.equal(mean.toFixed(3), '0.833');
});

check('false abstention costs 1; wrong pick costs 2; needless costs 2', () => {
  assert.equal(decisionLoss({ yNonEmpty: true, abstained: true, pickInY: false }), 1);
  assert.equal(decisionLoss({ yNonEmpty: true, abstained: false, pickInY: false }), 2);
  assert.equal(decisionLoss({ yNonEmpty: false, abstained: false, pickInY: false }), 2);
  assert.equal(decisionLoss({ yNonEmpty: true, abstained: false, pickInY: true }), 0);
  assert.equal(decisionLoss({ yNonEmpty: false, abstained: true, pickInY: false }), 0);
});

check('planted negative: a table that omits false_abstention_on_positive makes always-abstain win', () => {
  const aaProper = meanDecisionLoss(SKILLRANKER_12, decisionLoss);
  const aaEmission = meanDecisionLoss(SKILLRANKER_12, emissionOnlyLoss);
  assert.equal(aaEmission, 0, 'emission-only charges silence nothing, so always-abstain scores 0');
  assert.ok(aaProper > aaEmission, 'proper table must charge false abstain, else silence wins');
  // A judge that emits a wrong pick on every positive: emission-only = 2*10/12, proper = same.
  const wrongEmit = SKILLRANKER_12.map((r) => (
    r.yNonEmpty ? { yNonEmpty: true, abstained: false, pickInY: false } : r
  ));
  const emitProper = meanDecisionLoss(wrongEmit, decisionLoss);
  const emitEmission = meanDecisionLoss(wrongEmit, emissionOnlyLoss);
  assert.ok(aaEmission < emitEmission, 'under emission-only, always-abstain beats a wrong emitter');
  assert.ok(aaProper < emitProper, 'under the proper table, false-abstain (1) still beats wrong pick (2)');
  // THE GATE: a harness that only charges wrong emissions must be refused.
  assert.notEqual(aaEmission, aaProper, 'if these are equal the false-abstain cell was dropped');
});

// §4(d) selector ≡ claim. Scorers cannot silently read .distribution or invent a noul gate.
throws('planted: a fixture answer {noul:0.9} scored as probabilities must throw',
  () => field({ noul: 0.9 }, 'probabilities'), /no 'probabilities'/);

throws('assertSdkSelector refuses .distribution and .probability',
  () => assertSdkSelector('distribution'), /no \.probability or \.distribution/);

throws('assertSdkSelector refuses an invented selector',
  () => assertSdkSelector('helpfulNoul'), /not a declared SDK answer field/);

check('assertSdkSelector admits only the SDK-SURFACE answer fields', () => {
  for (const k of SDK_ANSWER_FIELDS) assertSdkSelector(k);
});

throws('refuseInventedNoulGate: a second noul cannot override a choice pick',
  () => refuseInventedNoulGate({ pick: 'rust-test-triage', helpfulNoul: 0.07 }),
  /invented noul gate/);

check('refuseInventedNoulGate is silent when no second noul is supplied', () => {
  assert.equal(refuseInventedNoulGate({ pick: 'rust-test-triage' }), undefined);
});

// SELECT-ON-A / REPORT-ON-B (jev-phishing-bench/bench/protocol.py port).
const splitRows = (n) => {
  const rows = [];
  for (let i = 0; i < n; i++) {
    const label = i % 2;
    rows.push({
      id: `m${String(i).padStart(3, '0')}`,
      label,
      feats: { good: label ? 0.9 : 0.1, bad: (i * 37) % 10 / 10 },
    });
  }
  return rows;
};

check('stratifiedHalves is deterministic and stratified', () => {
  const ids = ['a', 'b', 'c', 'd', 'e', 'f'];
  const labels = [true, true, true, false, false, false];
  const r1 = stratifiedHalves(ids, labels, 7);
  const r2 = stratifiedHalves(ids, labels, 7);
  assert.deepEqual(r1, r2);
  assert.equal(r1.a.filter((id) => labels[ids.indexOf(id)]).length, 1);
  assert.equal(r1.b.filter((id) => !labels[ids.indexOf(id)]).length, 2);
  assert.deepEqual([...r1.a, ...r1.b].sort(), [...ids].sort());
});

throws('stratifiedHalves refuses a degenerate label',
  () => stratifiedHalves(['a', 'b'], [true, true]), /degenerate label/);

check('bestThreshold mirrors protocol.py: ties keep the lowest, single value gives 0.5', () => {
  assert.equal(bestThreshold([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]), 0.5);
  assert.equal(bestThreshold([0, 1], [0.4, 0.4]), 0.5);
  assert.equal(bestThreshold([0, 0, 1, 1], [0.1, 0.35, 0.4, 0.9]), 0.375);
});

check('selectSingleSignal picks the best-A feature on A and reports on B', () => {
  const r = selectSingleSignal(splitRows(8), ['good', 'bad'], 3);
  assert.equal(r.feature, 'good');
  assert.equal(r.selected, true);
  assert.equal(r.accuracyB, 1);
  assert.equal(r.nA + r.nB, 8);
});

// PLANTED NEGATIVE: one signal cannot gain from selection. The helper must say
// so (selected: false) instead of dressing a trivial pick as a discovery.
check('single-signal input returns the single with selected:false', () => {
  const r = selectSingleSignal(splitRows(8), ['good'], 3);
  assert.equal(r.feature, 'good');
  assert.equal(r.selected, false);
  assert.equal(r.accuracyB, 1);
});

throws('selectSingleSignal refuses a missing score instead of scoring silence', () => {
  const rows = [{ id: 'm000', label: 1, feats: {} }, { id: 'm001', label: 0, feats: { good: 0.1 } }];
  return selectSingleSignal(rows, ['good']);
}, /missing score/);

check('fitLogistic separates separable data deterministically', () => {
  const XA = [[0.1], [0.2], [0.8], [0.9]];
  const yA = [0, 0, 1, 1];
  const w1 = fitLogistic(XA, yA);
  const w2 = fitLogistic(XA, yA);
  assert.deepEqual(w1, w2);
  assert.equal(auc(scoreLogistic(w1, XA), [false, false, true, true]).value, 1);
});

console.log(`\noracle-kit: ${pass}/${pass} checks passed`);
