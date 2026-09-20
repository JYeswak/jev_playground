/**
 * Ground-truth measurement for the omp-jev-route questions.
 *
 * The extension writes confident-looking routing advice per turn. Nobody had checked the two
 * questions against known answers. This does that, following work/omp-jev-failure/measure.mjs:
 * each question must beat ITS OWN always-no / always-yes constant, and every near-threshold
 * verdict is flagged. Three identical runs report drift.
 *
 * Method: nine hand-built prompts whose tier WE know by construction. Heavy = multi-step
 * reasoning, unfamiliar code, or careful judgment. Light = mechanical or read-only. One is a
 * TRAP: "just bump the version" carries no evidence of difficulty in the prompt itself, so the
 * judgeable truth is light — a judge that says heavy there is hallucinating difficulty, not
 * perceiving it. (The extension sends state {prompt} only, so prompt-only evidence is the bar.)
 *
 * The questions are copied here rather than imported from src/index.ts on purpose: this file
 * has to keep reproducing the finding after degenerate questions are cut from the extension.
 *
 * Budget: 9 cases x 3 runs = 27 systemOne calls, both questions in one request each.
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     node work/omp-jev-route/measure.mjs
 */
import { askJev } from '../jev-client/src/index.ts';

const QUESTIONS = {
  needs_heavyweight:
    'Does this turn require multi-step reasoning, unfamiliar code, or careful judgment (as opposed to a mechanical edit)?',
  mechanical:
    'Is this turn a mechanical edit: a rename, format, move, config tweak, or other routine change?',
};

const H = { needs_heavyweight: true, mechanical: false };
const L = { needs_heavyweight: false, mechanical: true };

const CASES = [
  { name: 'heavy-port-auth', prompt: 'Port the auth layer to the new session model and keep both paths working during the migration.', truth: H },
  { name: 'heavy-flaky-test', prompt: 'Why is this test flaky across three services? It passes locally and fails in CI about one run in five.', truth: H },
  { name: 'heavy-rotate-tokens', prompt: 'Redesign the auth session boundary so refresh tokens rotate on every use.', truth: H },
  { name: 'heavy-debug-race', prompt: 'Two workers occasionally process the same job twice. Find the race in the claim path and fix it without serializing all claims.', truth: H },
  { name: 'light-typo', prompt: 'Fix this typo in a comment.', truth: L },
  { name: 'light-what-does', prompt: 'What does this function do?', truth: L },
  { name: 'light-rename', prompt: 'Rename this variable from `tmp` to `pendingCount` everywhere in this file.', truth: L },
  { name: 'light-format', prompt: 'Format this file with the project formatter.', truth: L },
  // TRAP: looks trivial, and on prompt-only evidence it IS trivial. Heavy in the world
  // (the version string is compiled into three artifacts) but the prompt says none of that.
  { name: 'trap-bump-version', prompt: 'Just bump the version to 2.4.1.', truth: L, trap: true },
];

const THRESHOLD = 0.5;
const RUNS = 3;
const KEYS = Object.keys(QUESTIONS);

const scores = Object.fromEntries(KEYS.map((k) => [k, Object.fromEntries(CASES.map((c) => [c.name, []]))]));
const rows = [];
const thin = [];
let errors = 0;

for (let run = 1; run <= RUNS; run++) {
  for (const testCase of CASES) {
    const result = await askJev({
      state: { prompt: testCase.prompt },
      questions: QUESTIONS,
      timeoutMs: 8000,
    });
    if (!result.ok) {
      rows.push(`run${run} ${testCase.name.padEnd(20)} ERROR ${result.reason} ${result.error}`);
      errors += 1;
      continue;
    }
    for (const key of KEYS) {
      const score = result.scores[key];
      if (typeof score !== 'number') continue;
      scores[key][testCase.name].push(score);
      if (run === 1) {
        const said = score >= THRESHOLD;
        const hit = said === testCase.truth[key];
        if (Math.abs(score - THRESHOLD) < 0.1) thin.push(`${testCase.name}/${key} @ ${score.toFixed(2)}`);
        rows.push(`${testCase.name.padEnd(20)} ${key.padEnd(10)} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(testCase.truth[key]).padEnd(5)} ${hit ? 'HIT' : 'MISS'}${testCase.trap ? ' (trap)' : ''}`);
      }
    }
  }
}

console.log(rows.join('\n'));

// Drift: verdict flips and score spread across the three identical runs.
console.log('\ndrift across 3 identical runs:');
let flips = 0;
for (const testCase of CASES) {
  for (const key of KEYS) {
    const ss = scores[key][testCase.name];
    if (ss.length < 2) continue;
    const spread = Math.max(...ss) - Math.min(...ss);
    const verdicts = new Set(ss.map((s) => s >= THRESHOLD));
    if (verdicts.size > 1) flips += 1;
    console.log(`  ${testCase.name}/${key}: ${ss.map((s) => s.toFixed(2)).join(' ')} spread=${spread.toFixed(2)}${verdicts.size > 1 ? ' FLIP' : ''}`);
  }
}
console.log(`verdict flips: ${flips}`);

// Per-question verdicts on run 1. Rule, stated before running: DEGENERATE = same verdict on
// every case (a constant wearing a question's clothes). Otherwise it must beat the better of
// its own always-no / always-yes constants to DISCRIMINATE; beating neither is WEAK.
console.log('\nper question (must beat its own constant, not the coin flip):');
const verdicts = {};
for (const key of KEYS) {
  let correct = 0;
  let asked = 0;
  let yes = 0;
  let trueCount = 0;
  const all = [];
  for (const testCase of CASES) {
    const s = scores[key][testCase.name][0];
    if (typeof s !== 'number') continue;
    asked += 1;
    all.push(s);
    const said = s >= THRESHOLD;
    if (said) yes += 1;
    if (testCase.truth[key]) trueCount += 1;
    if (said === testCase.truth[key]) correct += 1;
  }
  const alwaysNo = asked - trueCount;
  const alwaysYes = trueCount;
  const spread = all.length ? Math.max(...all) - Math.min(...all) : 0;
  const constant = yes === 0 || yes === asked;
  const verdict = constant ? 'DEGENERATE' : (correct > Math.max(alwaysNo, alwaysYes) ? 'DISCRIMINATES' : 'WEAK');
  verdicts[key] = verdict;
  console.log(
    `${key.padEnd(19)} ${correct}/${asked} correct | said-yes ${yes}/${asked} | ` +
    `always-no ${alwaysNo}/${asked}, always-yes ${alwaysYes}/${asked} | ` +
    `spread ${spread.toFixed(2)} | ${verdict}`,
  );
  console.log(`${' '.repeat(19)} scores: ${all.map((s) => s.toFixed(2)).join(' ')}`);
}

const total = CASES.length * KEYS.length;
let hits = 0;
for (const testCase of CASES) {
  for (const key of KEYS) {
    const s = scores[key][testCase.name][0];
    if (typeof s === 'number' && (s >= THRESHOLD) === testCase.truth[key]) hits += 1;
  }
}
console.log(`\npooled agreement: ${hits}/${total} (coin flip: ${(total / 2).toFixed(1)})`);
console.log(`verdicts decided within 0.10 of ${THRESHOLD}: ${thin.length ? thin.join(', ') : 'none'}`);
console.log(`transport errors: ${errors}`);
console.log(`question verdicts: ${KEYS.map((k) => `${k}=${verdicts[k]}`).join(' ')}`);

console.log('\nNO-CLAIM: 9 hand-built prompts I wrote knowing the answer. Cases I author cannot');
console.log('establish accuracy on real turn traffic; cannot rule out that my phrasing made the');
console.log('heavy cases legible and the light cases trivially so; and the trap tests calibration');
console.log('to prompt-only evidence, not omniscience about the repo. This shows whether the');
console.log('questions are constants. It does not show they predict anything about real turns.');
