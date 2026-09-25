/**
 * Real-diff measurement for omp-jev-review.
 *
 * Every measurement in this lane so far used cases the measurer authored knowing the answers.
 * This one uses REAL COMMITS from this repository, and — the part that matters — labels them
 * from MECHANICALLY CHECKABLE properties of the diff rather than from my judgement:
 *
 *   behaviour = the diff modifies a non-test source line (.ts/.mjs/.sh outside test/ and docs/)
 *   boundary  = the diff touches a path or line dealing with keys, auth, permissions or secrets
 *
 * Both labels are computed by the script from `git show`, not typed in by a human. I cannot
 * tilt them toward the answer I want, which is the flaw in every prior set here: a docs-only
 * commit CANNOT be labelled behaviour-true no matter what I think of it.
 *
 * That trade is deliberate. The labels are cruder than a careful human read — a source edit
 * that changes only a comment counts as behaviour-true — so a MISS here may be the label being
 * blunt rather than the model being wrong. Every miss is printed with its diff stat so the
 * reader can judge which.
 *
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-review/measure-realdiffs.mjs
 */
import { execFileSync } from 'node:child_process';
import { askJev } from '../../kit/src/client.ts';
import { gradeQuestion } from '../jev-client/measure-kit.mjs';

const COUNT = Number(process.env.REVIEW_MEASURE_N ?? 14);
const THRESHOLD = 0.5;
const MAX_DIFF = 12000;

const QUESTIONS = {
  behaviour: 'Does this change alter behaviour that an existing caller depends on?',
  boundary: 'Does this change touch a security, permission, or authentication boundary?',
};

const SECURITY = /(api[_-]?key|apikey|secret|token|auth|password|credential|permission|chmod|infisical|TYPESAFE_API_KEY)/i;

const git = (...args) => execFileSync('git', args, { encoding: 'utf8', maxBuffer: 1024 * 1024 * 32 });
const shas = git('log', '--format=%H', `-${COUNT}`, '--no-merges').trim().split('\n');

const cases = [];
for (const sha of shas) {
  const subject = git('show', '-s', '--format=%s', sha).trim();
  const files = git('show', '--name-only', '--format=', sha).trim().split('\n').filter(Boolean);
  const diff = git('show', '--format=', sha);
  if (diff.trim().length === 0) continue;

  // changed lines only, so an unchanged security line elsewhere in the file cannot label it
  const changed = diff.split('\n').filter((line) => /^[+-]/.test(line) && !/^[+-]{3}/.test(line));

  const sourceFiles = files.filter(
    (f) => /\.(ts|mjs|js|sh|py)$/.test(f) && !/(^|\/)test\//.test(f) && !/\.test\./.test(f) && !f.startsWith('docs/'),
  );
  const behaviour = sourceFiles.length > 0;
  const boundary = sourceFiles.length > 0 && changed.some((line) => SECURITY.test(line));

  cases.push({ sha: sha.slice(0, 8), subject, files: files.length, sourceFiles: sourceFiles.length, diff: diff.slice(0, MAX_DIFF), truth: { behaviour, boundary } });
}

console.log(`real commits scored: ${cases.length}  (labels computed from the diff, not typed)\n`);

const tally = {};
const misses = [];
for (const key of Object.keys(QUESTIONS)) tally[key] = { correct: 0, yes: 0, truthYes: 0, scores: [], truths: [] };

for (const testCase of cases) {
  const result = await askJev({ state: { subject: testCase.subject, diff: testCase.diff }, questions: QUESTIONS, timeoutMs: 8000 });
  if (!result.ok) {
    console.log(`${testCase.sha} ERROR ${result.reason}: ${result.error}`);
    continue;
  }
  for (const key of Object.keys(QUESTIONS)) {
    const score = result.scores[key];
    if (typeof score !== 'number') continue;
    const said = score >= THRESHOLD;
    const truth = testCase.truth[key];
    tally[key].scores.push(score);
    tally[key].truths.push(truth);
    if (said) tally[key].yes += 1;
    if (truth) tally[key].truthYes += 1;
    if (said === truth) tally[key].correct += 1;
    else misses.push(`${key.padEnd(10)} ${testCase.sha} score=${score.toFixed(2)} said=${said} truth=${truth} files=${testCase.files} src=${testCase.sourceFiles} :: ${testCase.subject.slice(0, 64)}`);
  }
}

const n = cases.length;
for (const [key, t] of Object.entries(tally)) {
  const g = gradeQuestion(t.scores.map((s, i) => ({ score: s, truth: t.truths[i] })), THRESHOLD);
  const best = g.best, spread = g.spread, near = g.near, verdict = g.verdict;
  console.log(`${key.padEnd(10)} ${g.correct}/${n} | said-yes ${g.yes}/${n} | truth-yes ${g.trueCount}/${n} | best constant ${best}/${n} | spread ${spread.toFixed(2)} | near-threshold ${near} | ${verdict}`);
}

if (misses.length) {
  console.log('\nmisses, with diff size so a blunt label can be told from a wrong answer:');
  for (const m of misses) console.log('  ' + m);
}
console.log('\nNO-CLAIM: labels are mechanical proxies. `behaviour` treats any non-test source');
console.log('edit as behaviour-changing, so a comment-only source edit is labelled true and a');
console.log('correct model answer scores as a MISS. Read the miss list before trusting a total.');
