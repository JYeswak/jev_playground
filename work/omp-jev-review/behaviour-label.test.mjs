/**
 * Tests for the computed behaviour label (jev-fzw).
 *
 * The acceptance is "a rule a second person would apply the same way". These pin the
 * decisions that make that true — a rule whose answers depend on taste is the bottleneck
 * the bead exists to remove.
 *
 * Run: node --test work/omp-jev-review/behaviour-label.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { labelCommit } from './behaviour-label.mjs';
import { execSync } from 'node:child_process';

const sh = (c) => execSync(c, { encoding: 'utf8' }).trim();

test('the label is deterministic — same commit, same answer', () => {
  const sha = sh('git log --format=%H -1 --no-merges');
  assert.deepEqual(labelCommit(sha), labelCommit(sha), 'a second run must agree with the first');
});

test('PLANTED NEGATIVE: a docs-only commit is not behaviour-changing', () => {
  // SELECTOR DEFECT, fixed 2026-09-20 after the non-author review made it fail:
  // `git log -- docs/ ':!work/'` selects commits that MENTION docs/, not commits touching
  // ONLY docs/. The first matching commit also touched work/jev-score-register/, so the
  // premise ("this commit is docs-only") was false and the assertion was testing nothing.
  // It passed for hours purely by luck of which commit was newest — a live-history query in
  // a test is a moving target, the same defect class as quoting an unpinned denominator.
  // Now the premise is VERIFIED rather than assumed: scan recent commits and use the first
  // whose file list is genuinely all-docs, and skip honestly if none exists.
  const shas = sh('git log --format=%H -60 --no-merges').split('\n').filter(Boolean);
  const docsOnly = shas.find((s) => {
    const files = sh(`git show --name-only --format= ${s}`).split('\n').filter(Boolean);
    return files.length > 0 && files.every((f) => f.startsWith('docs/'));
  });
  if (!docsOnly) return; // genuinely none in range; not a failure of the rule
  const row = labelCommit(docsOnly);
  assert.equal(row.behaviour, false, `docs-only commit ${row.sha} must not be behaviour-changing`);
});

test('PLANTED NEGATIVE: a .md mention is not a caller', () => {
  // The first version of this rule reported "referenced by README.md" and counted it.
  // That is mention-vs-use, the defect this lane has hit eighteen times.
  const row = labelCommit(sh('git log --format=%H -1 --no-merges -- work/omp-harm-rule/organic-fires.mjs'));
  const mdReason = row.reasons.find((r) => /referenced by [^:]*\.md/.test(r));
  assert.equal(mdReason, undefined, `a .md file was counted as a caller: ${mdReason}`);
});

test('a registered entry point counts as reachable even with zero importers', () => {
  const row = labelCommit(sh('git log --format=%H -1 --no-merges -- foundation/gates.d/'));
  if (row.sourceFiles === 0) return;
  assert.equal(row.behaviour, true, 'gates.d stages are invoked by the glob and are entry points');
});

test('the row always carries a reason — a bare verdict is not a label', () => {
  const row = labelCommit(sh('git log --format=%H -1 --no-merges'));
  assert.ok(Array.isArray(row.reasons) && row.reasons.length > 0);
  for (const r of row.reasons) assert.match(r, /entry point|referenced by|NO caller|no non-test source/);
});

test('mechanical and computed are both reported, so disagreement stays visible', () => {
  const row = labelCommit(sh('git log --format=%H -1 --no-merges'));
  assert.equal(typeof row.mechanical, 'boolean');
  assert.equal(typeof row.behaviour, 'boolean');
});
