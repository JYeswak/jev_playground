/**
 * Ground-truth measurement for the omp-jev-rerank questions.
 *
 * The extension's first live run disagreed with ground truth on 2 of 3 questions. That was n=1,
 * so it settles nothing — this settles it over cases where WE know the answer by construction.
 *
 * Method: run real greps against this repo, build each candidate list twice —
 *   ORDERED   : the definition line first, then call sites
 *   SHUFFLED  : the definition buried in the middle
 * and a NOISE case where most hits are genuinely irrelevant.
 * Ground truth is known for each arm, so every question has a right answer.
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-rerank/measure.mjs
 */
import { askJev } from '../jev-client/src/index.ts';

const QUESTIONS = {
  definitional: 'Do the first three candidates contain the definition or primary implementation, rather than call sites and tests?',
  ordered: 'Are these candidates already ordered with the most relevant to the stated intent first?',
  noise: 'Is more than half of this candidate list irrelevant to the stated intent?',
};

const DEF = 'work/jev-client/src/index.ts:41: export async function askJev(options: AskOptions): Promise<JevResult> {';
const CALLS = Array.from({ length: 14 }, (_u, i) => `work/omp-jev-review/src/index.ts:${60 + i}:   const result = await askJev({`);
const JUNK = Array.from({ length: 14 }, (_u, i) => `docs/notes/file${i}.md:${i}: the word askJev appears in this prose but nothing is defined or called`);

const CASES = [
  { name: 'ordered-def-first', intent: 'find where askJev is defined', candidates: [DEF, ...CALLS], truth: { definitional: true, ordered: true, noise: false } },
  { name: 'buried-def', intent: 'find where askJev is defined', candidates: [...CALLS.slice(0, 7), DEF, ...CALLS.slice(7)], truth: { definitional: false, ordered: false, noise: false } },
  { name: 'mostly-noise', intent: 'find where askJev is defined', candidates: [DEF, ...JUNK], truth: { definitional: true, ordered: true, noise: true } },
  { name: 'all-noise', intent: 'find where askJev is defined', candidates: JUNK, truth: { definitional: false, ordered: false, noise: true } },
];

const THRESHOLD = 0.5;
let correct = 0;
let total = 0;
const rows = [];

for (const testCase of CASES) {
  const result = await askJev({
    state: { intent: testCase.intent, candidates: testCase.candidates.map((line, i) => `${i}: ${line}`) },
    questions: QUESTIONS,
    timeoutMs: 6000,
  });
  if (!result.ok) {
    rows.push(`${testCase.name}: ERROR ${result.reason} ${result.error}`);
    continue;
  }
  for (const key of Object.keys(QUESTIONS)) {
    const score = result.scores[key];
    if (typeof score !== 'number') continue;
    const said = score >= THRESHOLD;
    const truth = testCase.truth[key];
    const hit = said === truth;
    total += 1;
    if (hit) correct += 1;
    rows.push(`${testCase.name.padEnd(18)} ${key.padEnd(13)} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(truth).padEnd(5)} ${hit ? 'HIT' : 'MISS'}`);
  }
}

console.log(rows.join('\n'));
console.log(`\nagreement with ground truth: ${correct}/${total}`);
console.log(`a coin flip on ${total} items is ${(total / 2).toFixed(1)}`);
console.log('NO-CLAIM: 4 hand-built cases against one repo. This bounds nothing about real search traffic.');
