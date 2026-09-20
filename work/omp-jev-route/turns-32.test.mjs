// Offline shape test for the eww turn set. No Jev calls.
// Guards the bug caught live: truth keys {heavyweight, mechanical} must map to
// question keys {needs_heavyweight, mechanical}, else gradeQuestion drops the
// whole column as non-boolean and a verdict reads DEGENERATE on zero rows.
import test from 'node:test';
import assert from 'node:assert/strict';
import { TURNS } from './turns-32.mjs';
import { QUESTIONS } from './src/index.ts';

const truthKey = (k) => (k === 'needs_heavyweight' ? 'heavyweight' : k);

test('32 distinct turns with boolean truths', () => {
  assert.equal(TURNS.length, 32);
  assert.equal(new Set(TURNS.map((t) => t.id)).size, 32);
  for (const t of TURNS) {
    assert.equal(typeof t.prompt, 'string');
    assert.ok(t.prompt.length > 0);
    assert.equal(typeof t.truth.heavyweight, 'boolean', t.id);
    assert.equal(typeof t.truth.mechanical, 'boolean', t.id);
  }
});

test('trap classes kept as named subsets (10/10/6/6)', () => {
  const counts = {};
  for (const t of TURNS) counts[t.cls] = (counts[t.cls] ?? 0) + 1;
  assert.deepEqual(counts, { 'heavy-clear': 10, 'mech-clear': 10, 'trap-short': 6, 'trap-long': 6 });
});

test('every question key resolves to a boolean truth on every turn', () => {
  for (const t of TURNS) {
    for (const k of Object.keys(QUESTIONS)) {
      assert.equal(typeof t.truth[truthKey(k)], 'boolean', `${t.id}/${k}`);
    }
  }
});
