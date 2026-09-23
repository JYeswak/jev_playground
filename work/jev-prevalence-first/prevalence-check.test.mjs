/**
 * Offline test for checkPrevalence (jev-vbh.6, P2). Zero Jev calls.
 * Three arms: unanimous (DEGENERATE), skewed (DISCRIMINATES),
 * one-item-margin-with-near (WEAK).
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { checkPrevalence, checkChoice, checkLabelsOnly, checkUnlabeled, runSet } from './prevalence-check.mjs';

const CLI = join(dirname(fileURLToPath(import.meta.url)), 'prevalence-check.mjs');

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

test('choice set that loses to its majority class → WEAK, constant printed before verdict', () => {
  // 6 of 10 truths are "bash"; the model gets 5 right, so always-bash (6) wins.
  const truth = ['bash', 'bash', 'bash', 'bash', 'bash', 'bash', 'read', 'read', 'edit', 'edit'];
  const choice = ['bash', 'bash', 'bash', 'read', 'read', 'read', 'read', 'read', 'read', 'bash'];
  const pairs = truth.map((t, i) => ({ truth: t, choice: choice[i] }));
  const { lines, ret } = capture(() => checkChoice({ pairs }));
  orderHolds(lines);
  assert.match(lines[1], /always-bash 6\/10/);
  assert.equal(ret.correct, 5);
  assert.equal(ret.verdict, 'WEAK');
});

test('choice set that always answers one label → DEGENERATE even when it matches the majority', () => {
  const pairs = ['a', 'a', 'a', 'b'].map((t) => ({ truth: t, choice: 'a' }));
  const { ret } = capture(() => checkChoice({ pairs }));
  assert.equal(ret.verdict, 'DEGENERATE');
});

test('labels only: prints the bar to beat and defers the verdict', () => {
  const { lines, ret } = capture(() => checkLabelsOnly({ truths: ['BAD', 'BAD', 'BAD', 'OK', null] }));
  orderHolds(lines);
  assert.match(lines[1], /always-BAD 3\/4/, 'null truths are not counted');
  assert.equal(ret.verdict, 'DEFERRED');
});

test('unlabeled set: refuses, prints no constant and no verdict number', () => {
  const { lines, ret } = capture(() => checkUnlabeled({ rows: 5, field: 'label' }));
  orderHolds(lines);
  assert.match(lines[1], /NOT COMPUTABLE/);
  assert.doesNotMatch(lines[2], /\d+\/\d+/);
  assert.equal(ret.verdict, 'REFUSED');
});

function tmpFile(name, rows) {
  const dir = mkdtempSync(join(tmpdir(), 'prevalence-'));
  const p = join(dir, name);
  writeFileSync(p, name.endsWith('.json') ? JSON.stringify({ records: rows }) : rows.map((r) => JSON.stringify(r)).join('\n') + '\n');
  return p;
}

test('labels joined from a second file by id reach the binary check', () => {
  const scores = tmpFile('s.jsonl', [{ id: 'a', p: 0.9 }, { id: 'b', p: 0.1 }, { id: 'c', p: 0.2 }]);
  const labels = tmpFile('l.jsonl', [{ id: 'a', label: 1 }, { id: 'b', label: 0 }, { id: 'c', label: 0 }]);
  const { ret } = capture(() => runSet({ file: scores, score: 'p', labels, id: 'id', truth: 'label', threshold: 0.5 }));
  assert.equal(ret.asked, 3);
  assert.equal(ret.correct, 3);
});

test('CLI exit codes: 0 discriminates, 3 weak, 2 unlabeled, 64 usage', () => {
  const good = tmpFile('g.jsonl', [
    { p: 0.9, y: 1 }, { p: 0.9, y: 1 }, { p: 0.9, y: 1 }, { p: 0.1, y: 0 }, { p: 0.1, y: 0 }, { p: 0.1, y: 0 },
  ]);
  const weak = tmpFile('w.jsonl', [
    { c: 'a', y: 'a' }, { c: 'b', y: 'a' }, { c: 'b', y: 'a' }, { c: 'a', y: 'b' },
  ]);
  const unlabeled = tmpFile('u.json', [{ cmd: 'ls' }, { cmd: 'pwd' }]);
  const run = (args) => spawnSync(process.execPath, [CLI, ...args], { encoding: 'utf8' }).status;
  assert.equal(run([good, '--score', 'p', '--truth', 'y']), 0);
  assert.equal(run([weak, '--choice', 'c', '--truth', 'y']), 3);
  assert.equal(run([unlabeled, '--truth', 'label']), 2);
  assert.equal(run([good, '--score', 'p', '--choice', 'c', '--truth', 'y']), 64);
});
