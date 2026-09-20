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
// (askJev reached only through measure-kit now.)

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
// Ported to measure-kit (P3-36): same cases, same questions, same trap note, same NO-CLAIM.
// Only the table arithmetic moved — verdicts now carry the near-threshold penalty.
import { measure } from '../jev-client/measure-kit.mjs';

const out = await measure({
  cases: CASES.map((c) => ({ name: c.name + (c.trap ? ' (trap)' : ''), state: { prompt: c.prompt }, truth: c.truth })),
  questions: QUESTIONS,
  runs: 3,
  threshold: 0.5,
  timeoutMs: 8000,
});

const total = CASES.length * Object.keys(QUESTIONS).length;
let hits = 0;
for (const k of Object.keys(QUESTIONS)) hits += out.perQuestion[k].correct;
console.log(`\npooled agreement: ${hits}/${total} (coin flip: ${(total / 2).toFixed(1)})`);
console.log(`question verdicts: ${Object.keys(QUESTIONS).map((k) => `${k}=${out.perQuestion[k].verdict}`).join(' ')}`);

console.log('\nNO-CLAIM: 9 hand-built prompts I wrote knowing the answer. Cases I author cannot');
console.log('establish accuracy on real turn traffic; cannot rule out that my phrasing made the');
console.log('heavy cases legible and the light cases trivially so; and the trap tests calibration');
console.log('to prompt-only evidence, not omniscience about the repo. This shows whether the');
console.log('questions are constants. It does not show they predict anything about real turns.');
