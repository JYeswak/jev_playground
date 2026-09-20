/**
 * A COMPUTED label for "does this change alter behaviour an existing caller depends on?"
 *
 * THE BOTTLENECK, per jev-fzw: the incumbent label is a mechanical proxy — any non-test
 * source edit counts as behaviour-changing. It called a MISS when the model correctly said
 * a NEW STANDALONE SCRIPT changes no caller's behaviour. The label was wrong, not the score.
 *
 * Seven hand-built results failed to transfer to real traffic tonight. The one measurement
 * that produced a reportable correctness number (§14c, dependency_freshness_lag) did so
 * because its truth was COMPUTED — exact semver comparison — not asserted. This applies that
 * lesson: the label is derived from the repository, so a second person running it gets the
 * same answer by construction rather than by agreeing with me.
 *
 * THE RULE, in one sentence a human can also apply:
 *   A change alters existing-caller behaviour iff it touches a file that something else in
 *   the repository already references, or that the repo invokes as an entry point.
 *
 * Decidable inputs only: the changed paths, whether any OTHER file names them, and whether
 * they are registered as an entry point (package.json omp.extensions / bin / scripts,
 * foundation/gates.d/*, .git/hooks/*).
 *
 * WHAT IT DELIBERATELY DOES NOT DO: judge whether the edit is semantically meaningful. A
 * comment-only edit to an imported file still counts as reachable. That is a known
 * over-count and it is stated rather than hidden — but it is a SMALLER over-count than
 * "every source edit", and it is the half that is computable.
 *
 * Run: node work/omp-jev-review/behaviour-label.mjs [N]
 */
import { execSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { basename } from 'node:path';

const SOURCE = /\.(ts|mjs|js|sh|py)$/;
// Aligned with measure-realdiffs.mjs so the comparison is like-for-like: it excludes test/
// DIRECTORIES and *.test.* FILES and docs/. Missing the second clause counted two test files
// as source on the first run.
const TEST_OR_DOC = /(^|\/)(test|tests|docs|fixtures)\/|\.test\./;

function sh(cmd) {
  return execSync(cmd, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
}

/** Entry points the repo invokes directly — reachable even with zero importers. */
function entryPoints() {
  const set = new Set();
  for (const line of sh('git ls-files').split('\n')) {
    if (!line) continue;
    if (line.startsWith('foundation/gates.d/')) set.add(line);
    if (line.startsWith('.git/hooks/')) set.add(line);
    if (basename(line) === 'package.json' && existsSync(line)) {
      try {
        const pkg = JSON.parse(readFileSync(line, 'utf8'));
        const dir = line.replace(/package\.json$/, '');
        for (const e of pkg?.omp?.extensions ?? []) set.add((dir + e.replace(/^\.\//, '')).replace(/\/+/g, '/'));
        for (const b of Object.values(pkg?.bin ?? {})) set.add((dir + String(b).replace(/^\.\//, '')).replace(/\/+/g, '/'));
      } catch {
        /* a malformed package.json is not an entry point claim */
      }
    }
  }
  return set;
}

const ENTRIES = entryPoints();

/**
 * Is `path` referenced by any OTHER tracked file? Searched by basename, because imports are
 * written relative and a full-path grep misses every real reference — the wrong-selector
 * failure this lane hit fourteen times.
 */
function referencedElsewhere(path) {
  const name = basename(path);
  let out = '';
  try {
    out = sh(`git grep -l --fixed-strings -- ${JSON.stringify(name)} | head -40`);
  } catch {
    return { referenced: false, by: [] };
  }
  // A .md mention is NOT a caller. Caught while first running this rule: it reported
  // "referenced by README.md", which is mention-vs-use — the same defect this lane has now
  // hit eighteen times, here inside the very rule written to fix a bad label. Only files that
  // can actually execute or import count.
  const by = out
    .split('\n')
    .filter((f) => f && f !== path && !TEST_OR_DOC.test(f) && !f.endsWith('.md') && SOURCE.test(f));
  return { referenced: by.length > 0, by: by.slice(0, 3) };
}

/** The computed label for one commit. */
export function labelCommit(sha) {
  const files = sh(`git show --name-only --format= ${sha}`).split('\n').filter(Boolean);
  const source = files.filter((f) => SOURCE.test(f) && !TEST_OR_DOC.test(f));

  const reasons = [];
  let behaviour = false;
  for (const f of source) {
    if (ENTRIES.has(f)) {
      behaviour = true;
      reasons.push(`${f}: registered entry point`);
      continue;
    }
    const { referenced, by } = referencedElsewhere(f);
    if (referenced) {
      behaviour = true;
      reasons.push(`${f}: referenced by ${by.join(', ')}`);
    } else {
      reasons.push(`${f}: NO caller and not an entry point`);
    }
  }
  if (source.length === 0) reasons.push('no non-test source files touched');

  return { sha: sha.slice(0, 8), sourceFiles: source.length, behaviour, mechanical: source.length > 0, reasons };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const n = Number(process.argv[2] ?? 14);
  const shas = sh(`git log --format=%H -${n} --no-merges`).split('\n').filter(Boolean);
  const rows = shas.map(labelCommit);

  let disagree = 0;
  console.log('sha       src  mechanical  computed  reason');
  for (const r of rows) {
    const d = r.behaviour !== r.mechanical;
    if (d) disagree += 1;
    console.log(
      `${r.sha}  ${String(r.sourceFiles).padStart(3)}  ${String(r.mechanical).padEnd(10)}  ${String(r.behaviour).padEnd(8)}  ${d ? 'DISAGREE  ' : ''}${r.reasons[0] ?? ''}`,
    );
  }
  console.log(`\ncommits ${rows.length} | disagreements with the mechanical proxy: ${disagree} (${((disagree / rows.length) * 100).toFixed(1)}%)`);
  console.log('Every disagreement is a commit the mechanical proxy called behaviour-changing');
  console.log('and that no existing caller can observe.');
}
