import assert from 'node:assert/strict';
import test from 'node:test';
import { requestedVerdict, summarizeSamples } from '../ab/verdict.js';

test('single stochastic observations carry spread and no established determinism', () => {
  const armA = summarizeSamples([1]);
  const armB = summarizeSamples([3]);

  assert.equal(armA.deterministic, false);
  assert.equal(armB.determinism, 'unestablished');
  assert.equal(armB.sampleCount, 1);
  assert.equal(armB.spread, 0);
  assert.throws(() => requestedVerdict(armA, armB), /requires >=10 zero-spread samples/);
});

test('a differing stochastic sample set refuses a verdict', () => {
  const armA = summarizeSamples([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]);
  const armB = summarizeSamples([3, 1, 3, 1, 3, 1, 3, 1, 3, 1]);

  assert.equal(armA.determinism, 'established');
  assert.equal(armB.determinism, 'unestablished');
  assert.equal(armB.spread, 2);
  assert.throws(() => requestedVerdict(armA, armB), /armB n=10 spread=2/);
});

test('zero-spread samples permit a requested verdict', () => {
  const armA = summarizeSamples(Array(10).fill(1));
  const armB = summarizeSamples(Array(10).fill(3));

  assert.equal(requestedVerdict(armA, armB), 'B wins');
});
