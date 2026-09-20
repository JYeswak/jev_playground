// Offline tests for the shadow policy mapping (no scores needed, no Jev calls).
// The policy table itself is verified, not the model behind any single row.
import test from 'node:test';
import assert from 'node:assert/strict';

function decide(r, kill = false) {
  if (kill) return 'abstain';
  if (r.heavy >= 0.75 && r.mech < 0.5) return 'heavy';
  if (r.mech >= 0.75 && r.heavy < 0.5) return 'light';
  return 'abstain';
}

test('confident heavy routes heavy', () => {
  assert.equal(decide({ heavy: 0.9, mech: 0.1 }), 'heavy');
});

test('confident light routes light', () => {
  assert.equal(decide({ heavy: 0.1, mech: 0.9 }), 'light');
});

test('planted: trap-short shape (low heavy, high mech) does NOT route heavy', () => {
  assert.equal(decide({ heavy: 0.1, mech: 0.94 }), 'light');
});

test('planted: near-threshold pair abstains rather than guessing', () => {
  assert.equal(decide({ heavy: 0.54, mech: 0.14 }), 'abstain');
  assert.equal(decide({ heavy: 0.64, mech: 0.22 }), 'abstain');
});

test('kill switch forces abstain on a would-route row', () => {
  assert.equal(decide({ heavy: 0.95, mech: 0.05 }, true), 'abstain');
});
