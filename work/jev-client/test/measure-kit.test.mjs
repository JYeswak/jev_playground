// Offline tests for measure-kit: pure arithmetic + driver behavior. No key, no network.
import test from 'node:test';
import assert from 'node:assert/strict';
import { gradeQuestion, measure } from '../measure-kit.mjs';

// PLANTED DEGENERATE: 6/7 correct but the same verdict on every case —
// a base rate wearing a signal's clothes (the destructive-holdout shape).
test('a constant verdict is DEGENERATE however high its raw score', () => {
  const samples = [
    { score: 0.1, truth: false }, { score: 0.2, truth: false }, { score: 0.15, truth: false },
    { score: 0.3, truth: false }, { score: 0.25, truth: false }, { score: 0.4, truth: false },
    { score: 0.2, truth: true },
  ];
  const g = gradeQuestion(samples);
  assert.equal(g.correct, 6);
  assert.equal(g.verdict, 'DEGENERATE');
});

// PLANTED ONE-ITEM MARGIN: correct beats the best constant by exactly one, but one verdict
// was decided within the near window — the threshold made it, not the model. Must be WEAK.
// (This is the 010dd96 correction, encoded as a test.)
test('a one-item margin with a near-threshold decider is WEAK, not DISCRIMINATES', () => {
  const samples = [
    { score: 0.9, truth: true }, { score: 0.85, truth: true }, { score: 0.8, truth: false },
    { score: 0.1, truth: false }, { score: 0.2, truth: false }, { score: 0.52, truth: true },
    { score: 0.62, truth: false },
  ];
  // correct=5, best constant=4 (always-no), near=1 (0.52): 5 > 4+1 fails -> WEAK.
  const g = gradeQuestion(samples);
  assert.equal(g.correct, 5);
  assert.equal(g.best, 4);
  assert.equal(g.near, 1);
  assert.equal(g.verdict, 'WEAK');
});

test('a clear separator DISCRIMINATES with spread and counts', () => {
  const samples = [
    { score: 0.91, truth: true }, { score: 0.93, truth: true }, { score: 0.9, truth: true },
    { score: 0.1, truth: false }, { score: 0.23, truth: false }, { score: 0.21, truth: false },
  ];
  const g = gradeQuestion(samples);
  assert.equal(g.verdict, 'DISCRIMINATES');
  assert.ok(g.spread > 0.5);
});

// Driver: fake ask proves table assembly, drift flips, and error rows without network.
test('measure() counts flips, errors, and per-question verdicts', async () => {
  const calls = [];
  const fakeAsk = async ({ state }) => {
    calls.push(state);
    if (state.boom) return { ok: false, reason: 'transport', error: 'down' };
    // q flips verdict across runs on case b only.
    const run = calls.filter((s) => s.id === state.id).length;
    const flippy = state.id === 'b' && run >= 3;
    return { ok: true, scores: { q: state.id === 'a' ? 0.9 : (flippy ? 0.6 : 0.4) } };
  };
  const cases = [
    { name: 'a', state: { id: 'a' }, truth: { q: true } },
    { name: 'b', state: { id: 'b' }, truth: { q: false } },
    { name: 'c', state: { id: 'c', boom: true }, truth: { q: false } },
  ];
  const out = await measure({ cases, questions: { q: 'Is it?' }, runs: 3, ask: fakeAsk });
  assert.equal(out.errors, 3);
  assert.equal(out.flips, 1);
  assert.equal(out.perQuestion.q.asked, 2);
});
