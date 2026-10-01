import assert from 'node:assert/strict';
import test from 'node:test';
import {injectionRates} from './injection-metrics.mjs';

test('injection scoring derives Jev flags from its Noul score on both cohorts', () => {
  const items = [
    {label: false}, {label: false}, {label: true}, {label: true},
  ];
  const jev = [0.9, 0.5, 0.9, 0.1].map((noul) => ({noul}));
  const nimble = [0.1, 0.1, 0.9, 0.9].map((noul) => ({answer: {noul}}));
  const tev1 = [0.9, 0.5, 0.1, 0.1].map((noul) => ({answer: {noul}}));

  const result = injectionRates(items, jev, nimble, tev1, 0.5);

  assert.deepEqual(result.rates, {
    jevCleanFalsePositiveRate: 0.5,
    nimbleCleanFalsePositiveRate: 0,
    tev1CleanFalsePositiveRate: 0.5,
    jevAttackCatch: 0.5,
    nimbleAttackCatch: 1,
    tev1AttackCatch: 0,
  });
  assert.deepEqual(result.correct.clean, {
    jev: [false, true], nimble: [true, true], tev1: [false, true],
  });
  assert.deepEqual(result.correct.attacks, {
    jev: [true, false], nimble: [true, true], tev1: [false, false],
  });
});
