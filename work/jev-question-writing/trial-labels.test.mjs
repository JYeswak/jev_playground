// Offline smoke for the jev-vbh.2 question-writing loop's own artefacts.
// No key, no network, no Jev calls: label-file shape + verdict arithmetic
// on the RECORDED live scores (recomputed here by gradeQuestion, never re-run).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gradeQuestion, DEFAULT_THRESHOLD } from '../jev-client/measure-kit.mjs';

const dir = new URL('./', import.meta.url);
const load = (f) => JSON.parse(readFileSync(new URL(f, dir), 'utf8'));

// Labels must predate scoring: every truth boolean, names unique, state fields present.
test('pass4 labels: candidate key matches, 8 boolean truths, stated pin+available', () => {
  const labels = load('./pass4-labels.json');
  assert.equal(labels.candidate, 'dependency_freshness_lag');
  assert.equal(labels.cases.length, 8);
  const names = new Set();
  for (const c of labels.cases) {
    assert.equal(typeof c.truth, 'boolean', `${c.name} truth is not boolean`);
    assert.ok(typeof c.pin === 'string' && c.pin.length > 0, `${c.name} pin missing`);
    assert.ok(typeof c.available === 'string' && c.available.length > 0, `${c.name} available missing`);
    assert.ok(!names.has(c.name), `duplicate case ${c.name}`);
    names.add(c.name);
  }
});

test('pass5 labels: candidate key matches, 8 boolean truths, verbatim command', () => {
  const labels = load('./pass5-labels.json');
  assert.equal(labels.candidate, 'verification_weakened');
  assert.equal(labels.cases.length, 8);
  const names = new Set();
  for (const c of labels.cases) {
    assert.equal(typeof c.truth, 'boolean', `${c.name} truth is not boolean`);
    assert.ok(typeof c.command === 'string' && c.command.length > 0, `${c.name} command missing`);
    assert.ok(!names.has(c.name), `duplicate case ${c.name}`);
    names.add(c.name);
  }
});

test('pass7 labels: both candidates, 4 fresh boolean truths each', () => {
  const labels = load('./pass7-labels.json');
  const dep = labels.candidates.dependency_freshness_lag;
  const ver = labels.candidates.verification_weakened;
  assert.equal(dep.candidate, 'dependency_freshness_lag');
  assert.equal(ver.candidate, 'verification_weakened');
  for (const [key, group] of Object.entries({ dep, ver })) {
    assert.equal(group.cases.length, 4, `${key} is not 4 cases`);
    for (const c of group.cases) assert.equal(typeof c.truth, 'boolean', `${key}/${c.name} truth not boolean`);
  }
});

// RECORDED pass-4 scores (jev-1.13.0, 8 live calls; truths T,F,F,F,T,T,T,F
// in pass4-labels.json order). Recomputed, never re-run.
test('recorded pass-4 scores recompute to 8/8 DISCRIMINATES', () => {
  const truths = [true, false, false, false, true, true, true, false];
  const scores = [0.98, 0.01, 0.01, 0.01, 0.99, 0.98, 0.98, 0.12];
  const g = gradeQuestion(truths.map((truth, i) => ({ score: scores[i], truth })), DEFAULT_THRESHOLD);
  assert.equal(g.correct, 8);
  assert.equal(g.asked, 8);
  assert.equal(g.near, 0);
  assert.equal(g.verdict, 'DISCRIMINATES');
});

// RECORDED pass-5 scores (jev-1.13.0, 8 live calls; truths T,T,T,T,F,F,F,F).
test('recorded pass-5 scores recompute to 8/8 DISCRIMINATES', () => {
  const truths = [true, true, true, true, false, false, false, false];
  const scores = [0.88, 0.83, 0.80, 0.97, 0.06, 0.04, 0.03, 0.02];
  const g = gradeQuestion(truths.map((truth, i) => ({ score: scores[i], truth })), DEFAULT_THRESHOLD);
  assert.equal(g.correct, 8);
  assert.equal(g.asked, 8);
  assert.equal(g.near, 0);
  assert.equal(g.verdict, 'DISCRIMINATES');
});

// RECORDED pass-7 fresh-slice scores (jev-1.13.0, 4+4 live calls; truths T,T,F,F each).
// The ver 0.49 is the closest call on record: one tick under threshold, still a HIT.
test('recorded pass-7 scores recompute to 4/4 + 4/4 DISCRIMINATES', () => {
  const truths = [true, true, false, false];
  const dep = gradeQuestion([0.97, 0.98, 0.02, 0.02].map((score, i) => ({ score, truth: truths[i] })), DEFAULT_THRESHOLD);
  assert.equal(dep.correct, 4);
  assert.equal(dep.near, 0);
  assert.equal(dep.verdict, 'DISCRIMINATES');
  const ver = gradeQuestion([0.96, 0.94, 0.02, 0.49].map((score, i) => ({ score, truth: truths[i] })), DEFAULT_THRESHOLD);
  assert.equal(ver.correct, 4);
  assert.equal(ver.near, 1);
  assert.equal(ver.verdict, 'DISCRIMINATES');
});

// PLANTED NEGATIVE: recorded-score arms above would still pass if gradeQuestion
// degenerated to "high correct wins" — a constant verdict must stay DEGENERATE.
test('planted negative: constant scores stay DEGENERATE however high the raw count', () => {
  const samples = [
    { score: 0.9, truth: true }, { score: 0.85, truth: true }, { score: 0.8, truth: true },
    { score: 0.7, truth: false },
  ];
  const g = gradeQuestion(samples, DEFAULT_THRESHOLD);
  assert.equal(g.correct, 3);
  assert.equal(g.verdict, 'DEGENERATE');
});
