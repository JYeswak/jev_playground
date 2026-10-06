import test from 'node:test';
import assert from 'node:assert/strict';
import { costCut, npZeroErrorBound, ppvAtPrevalence, ppvReplay } from '../src/measurement-thresholds.mjs';

test('PPV formula reproduces D9 projections at prevalence .29', () => {
  assert.ok(Math.abs(ppvAtPrevalence(199 / 240, 2 / 10, 0.29).ppv - 0.629) < 0.001);
  assert.ok(Math.abs(ppvAtPrevalence(199 / 240, 0.510, 0.29).ppv - 0.399) < 0.001);
});

test('PPV projection recovers a synthetic label-shift mixture within .01', () => {
  const sensitivity = 0.8;
  const falsePositiveRate = 0.1;
  const prevalence = 0.2;
  const positives = 100_000;
  const predictedPositive = positives * prevalence * sensitivity + positives * (1 - prevalence) * falsePositiveRate;
  const truePositive = positives * prevalence * sensitivity;
  const observed = truePositive / predictedPositive;
  assert.ok(Math.abs(ppvAtPrevalence(sensitivity, falsePositiveRate, prevalence).ppv - observed) <= 0.01);
});

test('prior-shifted cost cut requires a cost matrix and both class counts', () => {
  const input = { sensitivity: 0.8, falsePositiveRate: 0.1, devPrevalence: 0.5, deploymentPrevalence: 0.05, costMatrix: { falsePositive: 4, falseNegative: 1 }, positiveCount: 20, negativeCount: 20 };
  const result = costCut(input);
  assert.equal(result.status, 'READY');
  assert.equal(result.threshold, 0.8);
  assert.ok(result.priorOddsMultiplier < 1);
  assert.equal(costCut({ ...input, costMatrix: undefined }).status, 'NOT_RUN');
  assert.equal(costCut({ ...input, positiveCount: 0 }).status, 'NOT_RUN');
});

test('NP zero-error audit uses separate fit and independent negatives', () => {
  const expected = [[0.10, 29], [0.05, 59], [0.02, 149], [0.01, 299]];
  for (const [alpha, n] of expected) {
    const result = npZeroErrorBound({ alpha, delta: 0.05, negatives: { fit: 100, audit: n }, independent: true });
    assert.equal(result.status, 'READY');
    assert.equal(result.requiredAudit, n);
  }
  assert.equal(npZeroErrorBound({ alpha: 0.05, negatives: { fit: 100, audit: 58 }, independent: true }).status, 'NOT_RUN');
  assert.equal(npZeroErrorBound({ alpha: 0.05, negatives: { fit: 100, audit: 59 }, independent: false }).status, 'NOT_RUN');
});

test('skill-veto conditional-shift replay is ASSUMPTION-VIOLATED', () => {
  const result = ppvReplay({ sensitivity: 199 / 240, falsePositiveRate: 0.510, prevalence: 0.29, observedPpv: 0.335 });
  assert.equal(result.status, 'ASSUMPTION-VIOLATED');
  assert.ok(result.absoluteError > 0.01);
});
