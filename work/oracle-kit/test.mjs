// oracle-kit self-test. Every case is a defect this lane actually shipped today.
import { auc, requireBoth, field, feasibility, ece, eProcess } from './index.mjs';
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

console.log(`\noracle-kit: ${pass}/${pass} checks passed`);
