import test from 'node:test';
import assert from 'node:assert/strict';
import { bucketScores, rowUncertainty, sampleRandom, selectUncertain } from '../uncertain.mjs';

const rows = [
  { id: 'a', data: { probabilities: { x: 0.49, y: 0.2 } }, uncertainty: 0.01 },
  { id: 'b', data: { score: 0.9 }, uncertainty: 0.4 },
  { id: 'c', data: { scores: { x: 0.51 } }, uncertainty: 0.01 },
  { id: 'd', data: { scores: { x: 0.1 } }, uncertainty: 0.4 },
];

test('uncertain selection ranks closest scores first', () => {
  assert.deepEqual(selectUncertain(rows, 3).map((row) => row.id), ['a', 'c']);
  assert.equal(rowUncertainty({ data: { probabilities: { x: 0.5, y: 0.1 } } }), 0);
});

test('bucket counts cover all numeric score values', () => {
  assert.deepEqual(bucketScores(rows), { '0.0-0.2': 1, '0.2-0.4': 1, '0.4-0.6': 2, '0.6-0.8': 0, '0.8-1.0': 1 });
});

test('random audit sampling is deterministic and ignores uncertainty ranking', () => {
  const a = sampleRandom(rows, 3, 42).map((row) => row.id);
  const b = sampleRandom(rows, 3, 42).map((row) => row.id);
  assert.deepEqual(a, b);
  assert.equal(a.length, 3);
});

test('no-near-threshold planted negative reports zero', () => {
  const far = [{ id: 'far-a', data: { score: 0.1 }, uncertainty: 0.4 }, { id: 'far-b', data: { score: 0.9 }, uncertainty: 0.4 }];
  assert.equal(far.filter((row) => row.uncertainty <= 0.1).length, 0);
  assert.equal(selectUncertain(far, 5).length, 0);
});
