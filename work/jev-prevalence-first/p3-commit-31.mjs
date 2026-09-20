/**
 * P3: re-ordered Unit-2 output (jev-vbh.6) — near, constant, verdict.
 *
 * Truth: work/omp-jev-commit/labels-31.json (committed; read from diffs BEFORE
 *   scores were seen — receipt lines 4-5 of commit-judge-31-20260919.md).
 * Scores: EMBEDDED per-case scores transcribed from the LIVE re-run
 *   /tmp/score31-rerun.log lines 2-32 (31 keyed Jev calls, 0 transport errors,
 *   run 2026-09-20). This supersedes the first-run receipt transcription
 *   (commit 0befea4): the re-run is authoritative and the numbers moved —
 *   see DRIFT FINDING below. Zero Jev calls in THIS script (scores are
 *   recorded, not fetched).
 */
import { readFileSync } from 'node:fs';
import { checkPrevalence } from './prevalence-check.mjs';

const labels = JSON.parse(
  readFileSync(new URL('../omp-jev-commit/labels-31.json', import.meta.url), 'utf8'),
).commits;
const truth = Object.fromEntries(labels.map((c) => [c.sha.slice(0, 7), c]));
const short = (c) => c.sha.slice(0, 7);

// Embedded: [sha7, describes, overstates, omits] from /tmp/score31-rerun.log:2-32.
const RECORDED = [
  ['4639b9f', 0.71, 0.41, 0.13], ['ee6ddf5', 0.68, 0.39, 0.13],
  ['1d4e0c8', 0.85, 0.62, 0.27], ['dc2016c', 0.79, 0.29, 0.17],
  ['963c237', 0.91, 0.72, 0.39], ['bdd1c9a', 0.66, 0.78, 0.25],
  ['74d27ad', 0.83, 0.84, 0.22], ['d1f251c', 0.52, 0.44, 0.51],
  ['0d36407', 0.56, 0.68, 0.63], ['033d61f', 0.85, 0.59, 0.19],
  ['b3551a9', 0.86, 0.75, 0.21], ['14f5c9c', 0.73, 0.25, 0.40],
  ['bb50501', 0.81, 0.73, 0.29], ['c4b4352', 0.88, 0.48, 0.19],
  ['7e34898', 0.86, 0.64, 0.26], ['3097181', 0.86, 0.63, 0.11],
  ['79333f7', 0.79, 0.20, 0.33], ['a69d16d', 0.87, 0.34, 0.22],
  ['2e19de8', 0.92, 0.30, 0.09], ['4cbc7b5', 0.80, 0.25, 0.31],
  ['ea71898', 0.88, 0.21, 0.14], ['455e3e2', 0.87, 0.43, 0.33],
  ['959c321', 0.88, 0.82, 0.33], ['1143dec', 0.80, 0.18, 0.22],
  ['cbd1d60', 0.90, 0.58, 0.51], ['48f834b', 0.86, 0.15, 0.28],
  ['3c43d62', 0.73, 0.36, 0.34], ['d2e815c', 0.80, 0.71, 0.28],
  ['83e9055', 0.74, 0.33, 0.18], ['1f1cf55', 0.53, 0.64, 0.22],
  ['48eecdf', 0.77, 0.21, 0.50],
];
const bySha = new Map(RECORDED.map((r) => [r[0], r]));
if (bySha.size !== 31 || !labels.every((c) => bySha.has(short(c)))) {
  throw new Error('recorded-score coverage gap: every labeled sha needs a log line');
}
const samplesFor = (key, idx) => labels.map((c) => ({ score: bySha.get(short(c))[idx], truth: c[key] }));

console.log('P3 re-ordered Unit-2 output (truth: labels-31.json; scores: /tmp/score31-rerun.log:2-32)');
const sets = [['describes', samplesFor('describes', 1)], ['overstates', samplesFor('overstates', 2)], ['omits', samplesFor('omits', 3)]];
for (const [name, samples] of sets) {
  console.log(`--- ${name} ---`);
  checkPrevalence({ samples });
}
console.log('--- reconciliation vs rerun kit lines (log :34-37) ---');
console.log('describes: log 30/31 yes 31/31 best 30 near 3 DEGENERATE — see above');
console.log('overstates: log 17/31 yes 14/31 best 31 near 6 WEAK — see above');
console.log('omits: log 28/31 yes 4/31 best 30 near 4 WEAK — see above');
console.log('DRIFT FINDING: 48eecdf omits 0.49 MISS (first run, receipt :17-19) → 0.50 HIT');
console.log('  (rerun). The receipt\'s emblematic near-miss flipped on re-run: a threshold-made');
console.log('  verdict rotting in one day. Per §14e (commit-learnings-20260919 §§14-14e: 197/400');
console.log('  rows within ±0.10 of 0.50 — half the verdicts made by the threshold, not Jev),');
console.log('  near-threshold rows must be re-measured, never quoted from a prior run.');
