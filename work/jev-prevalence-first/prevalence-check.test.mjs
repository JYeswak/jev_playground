/**
 * Offline test for checkPrevalence (jev-vbh.6, P2). Zero Jev calls.
 * Three arms: unanimous (DEGENERATE), skewed (DISCRIMINATES),
 * one-item-margin-with-near (WEAK).
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { checkPrevalence } from './prevalence-check.mjs';

// Capture printed lines so the test proves the order, not just the verdict.
function capture(fn) {
  const lines = [];
  const orig = console.log;
  console.log = (...a) => lines.push(a.join(' '));
  try {
    const ret = fn();
    return { lines, ret };
  } finally {
    console.log = orig;
  }
}

function orderHolds(lines) {
  assert.match(lines[0], /^near-threshold:/, 'near-threshold count prints FIRST');
  assert.match(lines[1], /^own-constant:/, 'own-constant bar prints SECOND');
  assert.match(lines[2], /^verdict:/, 'verdict prints LAST');
}

test('unanimous set: constant 1.0 → DEGENERATE', () => {
  const samples = [
    { score: 0.9, truth: true },
    { score: 0.85, truth: true },
    { score: 0.95, truth: true },
    { score: 0.8, truth: true },
  ];
  const { lines, ret } = capture(() => checkPrevalence({ samples }));
  orderHolds(lines);
  assert.match(lines[1], /majority share 100\.0%/, 'constant is 1.0');
  assert.equal(ret.verdict, 'DEGENERATE');
});

test('skewed set: correct beats best + near → DISCRIMINATES', () => {
  const samples = [
    { score: 0.9, truth: true },
    { score: 0.85, truth: true },
    { score: 0.9, truth: true },
    { score: 0.8, truth: true },
    { score: 0.2, truth: false },
    { score: 0.25, truth: false },
  ];
  const { lines, ret } = capture(() => checkPrevalence({ samples }));
  orderHolds(lines);
  assert.equal(ret.correct, 6);
  assert.equal(ret.best, 4);
  assert.equal(ret.near, 0);
  assert.equal(ret.verdict, 'DISCRIMINATES');
});

test('one-item margin with near: correct <= best + near → WEAK', () => {
  // best-constant 4/6 (always-no), correct 5/6 — a one-item margin — but
  // near = 2, so 5 <= 4 + 2 and the threshold owns the margin: WEAK.
  const samples = [
    { score: 0.9, truth: true },
    { score: 0.55, truth: true }, // near, correct yes
    { score: 0.2, truth: false },
    { score: 0.15, truth: false },
    { score: 0.45, truth: false }, // near, correct no
    { score: 0.8, truth: false }, // the one MISS: said yes, truth no
  ];
  const { lines, ret } = capture(() => checkPrevalence({ samples }));
  orderHolds(lines);
  assert.equal(ret.correct, 5);
  assert.equal(ret.best, 4);
  assert.equal(ret.near, 2);
  assert.equal(ret.verdict, 'WEAK');
});
