import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { splitConformalLac } from '../src/measurement-conformal.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const B77 = path.join(ROOT, 'work', 'choice-banking77');
const ARMS = path.join(ROOT, 'work', 'local-decision-arms');
const ALPHA = 0.10;
const FLOOR = 0.005;

// Fixture header: Jev Banking77 probabilities from the named full corpus. DEV is
// seed 8, SAMPLE is seed 7, exactly as run.py:24-26; the separate committed arm
// files carry those id sets. Both groups sample the same Banking77 target frame.
const FRAME = Object.freeze({
  name: 'banking77-full-corpus-jev-1.13.0',
  source: 'work/choice-banking77/rows-full-jev.jsonl',
  targetPopulation: 'Banking77 full corpus',
  calibrationGroup: Object.freeze({ name: 'DEV-seed-8', targetPopulation: 'Banking77 full corpus' }),
  testGroup: Object.freeze({ name: 'SAMPLE-seed-7', targetPopulation: 'Banking77 full corpus' }),
});

function readJsonl(file) {
  return fs.readFileSync(file, 'utf8').split('\n').filter((line) => line.trim()).map((line) => JSON.parse(line));
}

function fixture() {
  const probabilities = readJsonl(path.join(B77, 'rows-full-jev.jsonl'));
  const devIds = new Set(readJsonl(path.join(ARMS, 'rows-clefflash-dev.jsonl')).map((row) => row.i));
  const sampleIds = new Set(readJsonl(path.join(ARMS, 'rows-clefflash.jsonl')).map((row) => row.i));
  const labels = [...new Set(probabilities.flatMap((row) => Object.keys(row.probabilities ?? {})))].sort();
  const map = (rows, group) => rows.map((row) => ({
    id: row.i,
    trueLabel: row.intent,
    probabilities: row.probabilities,
    samplingFrame: FRAME.name,
    group,
  }));
  return {
    labels,
    calibration: map(probabilities.filter((row) => devIds.has(row.i)), FRAME.calibrationGroup.name),
    test: map(probabilities.filter((row) => sampleIds.has(row.i)), FRAME.testGroup.name),
  };
}

function frameFor(targetPopulation = 'toy target') {
  return {
    name: 'toy-frame-v1',
    source: 'deterministic generated fixture',
    targetPopulation,
    calibrationGroup: { name: 'DEV', targetPopulation },
    testGroup: { name: 'SAMPLE', targetPopulation },
  };
}

function row(id, trueLabel, probabilities, group, samplingFrame = 'toy-frame-v1') {
  return { id, trueLabel, probabilities, group, samplingFrame };
}

// Independent log-gamma implementation for the test oracle. The implementation
// under test uses a recurrence around the beta-binomial mode instead.
function logGamma(z) {
  const coefficients = [
    0.99999999999980993, 676.5203681218851, -1259.1392167224028,
    771.32342877765313, -176.61502916214059, 12.507343278686905,
    -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7,
  ];
  if (z < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * z)) - logGamma(1 - z);
  const x = z - 1;
  let sum = coefficients[0];
  for (let i = 1; i < coefficients.length; i++) sum += coefficients[i] / (x + i);
  const t = x + 7.5;
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(sum);
}

function exactCoverageBand(nCalibration, nTest, alpha) {
  const l = Math.floor((nCalibration + 1) * alpha);
  const a = nCalibration + 1 - l;
  const b = l;
  const logBeta = (x, y) => logGamma(x) + logGamma(y) - logGamma(x + y);
  const weights = Array.from({ length: nTest + 1 }, (_, k) => Math.exp(
    logGamma(nTest + 1) - logGamma(k + 1) - logGamma(nTest - k + 1)
      + logBeta(k + a, nTest - k + b) - logBeta(a, b),
  ));
  const total = weights.reduce((sum, value) => sum + value, 0);
  const quantile = (target) => {
    let cumulative = 0;
    for (let k = 0; k < weights.length; k++) {
      cumulative += weights[k] / total;
      if (cumulative >= target) return k;
    }
    return nTest;
  };
  return { lowerCount: quantile(0.025), upperCount: quantile(0.975), confidence: 0.95 };
}

test('frozen Banking77 split refuses captured probability mass outside the fixed bound', () => {
  const data = fixture();
  assert.equal(data.calibration.length, 200);
  assert.equal(data.test.length, 600);
  assert.equal(new Set(data.calibration.map((item) => item.id)).size, 200);
  assert.equal(new Set(data.test.map((item) => item.id)).size, 600);
  assert.equal(data.calibration.some((item) => data.test.some((held) => held.id === item.id)), false);
  const invalidMass = (rows) => rows.filter((item) => {
    const total = Object.values(item.probabilities).reduce((sum, value) => sum + value, 0);
    return Math.abs(total - 1) > 1e-6;
  }).length;
  assert.equal(invalidMass(data.calibration), 14);
  assert.equal(invalidMass(data.test), 36);
  const result = splitConformalLac({ ...data, alpha: ALPHA, probabilityFloor: FLOOR, samplingFrame: FRAME });
  assert.equal(result.status, 'REFUSE');
  assert.equal(result.reason, 'invalid_probability_vector');
  assert.equal(result.coverage, undefined);
});

test('D5 synthetic arithmetic-only 200/600 split matches exact finite-sample coverage band', () => {
  // Synthetic arithmetic-only fixture; not observed-data coverage or a D5 measurement.
  const labels = ['a', 'b'];
  const samplingFrame = frameFor('synthetic target population');
  const makeRow = (id, group, index, goodCount) => {
    const trueLabel = index % 2 === 0 ? 'a' : 'b';
    const pTrue = index < goodCount ? 0.8 : 0.7;
    const probabilities = trueLabel === 'a' ? { a: pTrue, b: 1 - pTrue } : { a: 1 - pTrue, b: pTrue };
    return row(id, trueLabel, probabilities, group);
  };
  const calibration = Array.from({ length: 200 }, (_, i) => makeRow(`cal-${i}`, 'DEV', i, 190));
  const held = Array.from({ length: 600 }, (_, i) => makeRow(`held-${i}`, 'SAMPLE', i, 540));
  const result = splitConformalLac({ labels, calibration, test: held, alpha: ALPHA, probabilityFloor: FLOOR, samplingFrame });
  assert.equal(result.status, 'OK');
  assert.equal(result.nCalibration, 200);
  assert.equal(result.nTest, 600);
  assert.equal(result.calibrationRank, 181);
  assert.ok(Math.abs(result.threshold - 0.2) <= Number.EPSILON);
  assert.deepEqual(result.coverageBand, exactCoverageBand(200, 600, ALPHA));
  assert.equal(result.covered, 540);
  assert.ok(result.covered >= result.coverageBand.lowerCount);
  assert.ok(result.covered <= result.coverageBand.upperCount);
  assert.ok(Number.isFinite(result.meanSetSize));
  assert.ok(Number.isFinite(result.singletonShare));
});

test('LAC includes every label tied at q-hat', () => {
  const labels = ['a', 'b'];
  const calibration = [
    row('c1', 'a', { a: 0.9, b: 0.1 }, 'DEV'),
    row('c2', 'a', { a: 0.8, b: 0.2 }, 'DEV'),
    row('c3', 'a', { a: 0.8, b: 0.2 }, 'DEV'),
    row('c4', 'a', { a: 0.2, b: 0.8 }, 'DEV'),
  ];
  const held = [row('t1', 'b', { a: 0.2, b: 0.8 }, 'SAMPLE')];
  const result = splitConformalLac({ labels, calibration, test: held, alpha: 0.4, probabilityFloor: FLOOR, samplingFrame: frameFor() });
  assert.equal(result.status, 'OK');
  assert.ok(Math.abs(result.threshold - 0.2) <= Number.EPSILON);
  assert.deepEqual(result.predictionSets[0].labels, ['b']);
});

test('permuting calibration and test rows preserves ID-keyed prediction sets', () => {
  const labels = ['a', 'b'];
  const calibration = [
    row('c1', 'a', { a: 0.9, b: 0.1 }, 'DEV'),
    row('c2', 'b', { a: 0.2, b: 0.8 }, 'DEV'),
    row('c3', 'a', { a: 0.6, b: 0.4 }, 'DEV'),
    row('c4', 'b', { a: 0.7, b: 0.3 }, 'DEV'),
  ];
  const held = [
    row('t1', 'a', { a: 0.8, b: 0.2 }, 'SAMPLE'),
    row('t2', 'b', { a: 0.4, b: 0.6 }, 'SAMPLE'),
  ];
  const first = splitConformalLac({ labels, calibration, test: held, alpha: 0.2, probabilityFloor: FLOOR, samplingFrame: frameFor() });
  const permuted = splitConformalLac({ labels, calibration: [...calibration].reverse(), test: [...held].reverse(), alpha: 0.2, probabilityFloor: FLOOR, samplingFrame: frameFor() });
  const byId = (result) => Object.fromEntries(result.predictionSets.map((item) => [item.id, item.labels]));
  assert.deepEqual(byId(first), byId(permuted));
  assert.equal(first.coverage, permuted.coverage);
  assert.equal(first.meanSetSize, permuted.meanSetSize);
});

test('relabeling class IDs only relabels sets and preserves coverage and size', () => {
  const labels = ['a', 'b'];
  const calibration = [
    row('c1', 'a', { a: 0.9, b: 0.1 }, 'DEV'),
    row('c2', 'b', { a: 0.2, b: 0.8 }, 'DEV'),
    row('c3', 'a', { a: 0.6, b: 0.4 }, 'DEV'),
    row('c4', 'b', { a: 0.7, b: 0.3 }, 'DEV'),
  ];
  const held = [row('t1', 'a', { a: 0.8, b: 0.2 }, 'SAMPLE'), row('t2', 'b', { a: 0.4, b: 0.6 }, 'SAMPLE')];
  const first = splitConformalLac({ labels, calibration, test: held, alpha: 0.2, probabilityFloor: FLOOR, samplingFrame: frameFor() });
  const rename = (name) => (name === 'a' ? 'z' : 'y');
  const convert = (item) => row(item.id, rename(item.trueLabel), Object.fromEntries(Object.entries(item.probabilities).map(([label, p]) => [rename(label), p])), item.group);
  const relabeled = splitConformalLac({ labels: labels.map(rename), calibration: calibration.map(convert), test: held.map(convert), alpha: 0.2, probabilityFloor: FLOOR, samplingFrame: frameFor() });
  const back = (result) => Object.fromEntries(result.predictionSets.map((item) => [item.id, item.labels.map((label) => label === 'z' ? 'a' : 'b').sort()]));
  assert.deepEqual(back(relabeled), Object.fromEntries(first.predictionSets.map((item) => [item.id, [...item.labels].sort()])));
  assert.equal(first.coverage, relabeled.coverage);
  assert.equal(first.meanSetSize, relabeled.meanSetSize);
});

test('refuses undeclared exchangeability, overlapping IDs, and a different target population', () => {
  const labels = ['a', 'b'];
  const calibration = [row('same', 'a', { a: 0.8, b: 0.2 }, 'DEV')];
  const held = [row('test', 'b', { a: 0.2, b: 0.8 }, 'SAMPLE')];
  assert.equal(splitConformalLac({ labels, calibration, test: held, alpha: 0.1, probabilityFloor: FLOOR, samplingFrame: null }).status, 'REFUSE');
  assert.equal(splitConformalLac({ labels, calibration, test: [row('same', 'b', { a: 0.2, b: 0.8 }, 'SAMPLE')], alpha: 0.1, probabilityFloor: FLOOR, samplingFrame: frameFor() }).reason, 'overlapping_split_ids');
  const shifted = frameFor();
  shifted.testGroup.targetPopulation = 'different population';
  assert.equal(splitConformalLac({ labels, calibration, test: held, alpha: 0.1, probabilityFloor: FLOOR, samplingFrame: shifted }).reason, 'groups_not_from_same_target_population');
});

test('refuses malformed probability vectors before applying the probability floor', () => {
  const labels = ['a', 'b'];
  const held = [row('t1', 'a', { a: 0.7, b: 0.3 }, 'SAMPLE')];
  const cal = (probabilities) => [row('c1', 'a', probabilities, 'DEV')];
  for (const probabilities of [{ a: -0.01, b: 1.01 }, { a: Number.NaN, b: 0.5 }, { a: 0.7, b: 0.300002 }]) {
    const result = splitConformalLac({ labels, calibration: cal(probabilities), test: held, alpha: 0.1, probabilityFloor: FLOOR, samplingFrame: frameFor() });
    assert.equal(result.status, 'REFUSE');
    assert.equal(result.reason, 'invalid_probability_vector');
  }
});

test('coin-flip probabilities produce full prediction sets rather than a set-size pass', () => {
  const labels = ['a', 'b', 'c', 'd'];
  const uniform = { a: 0.25, b: 0.25, c: 0.25, d: 0.25 };
  const calibration = labels.map((label, index) => row(`c${index}`, label, uniform, 'DEV'));
  const held = [row('t1', 'a', uniform, 'SAMPLE')];
  const result = splitConformalLac({ labels, calibration, test: held, alpha: 0.2, probabilityFloor: FLOOR, samplingFrame: frameFor() });
  assert.equal(result.status, 'OK');
  assert.deepEqual(result.predictionSets[0].labels, labels);
  assert.equal(result.meanSetSize, labels.length);
});
