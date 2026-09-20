/**
 * pass7-run.mjs — jev-vbh.2 Pass 7: fresh-slice cross-check of BOTH surviving
 * candidates on NEW cases neither has seen. Reads pass7-labels.json (labelled
 * BEFORE any Jev call), sends each case ONCE via the sanctioned askJev, grades
 * each candidate with gradeQuestion. Prints HIT/MISS rows + rule verdicts.
 * 8 live Jev calls total (4 + 4).
 */
import { readFileSync } from 'node:fs';
import { askJev } from '../jev-client/src/index.ts';
import { gradeQuestion, DEFAULT_THRESHOLD } from '../jev-client/measure-kit.mjs';
import { CANDIDATE_QUESTION, CANDIDATE_QUESTION_2, buildState, buildCommandState } from './trial.mjs';

const labels = JSON.parse(readFileSync(new URL('./pass7-labels.json', import.meta.url), 'utf8'));

const samplesDep = [];
let model = null;
let calls = 0;
const keyDep = CANDIDATE_QUESTION.key;
if (keyDep !== labels.candidates.dependency_freshness_lag.candidate) throw new Error('dep candidate mismatch');
for (const c of labels.candidates.dependency_freshness_lag.cases) {
  const state = buildState({ pin: c.pin, available: c.available, context: c.context });
  // eslint-disable-next-line no-await-in-loop
  const result = await askJev({ state, questions: { [keyDep]: CANDIDATE_QUESTION.instructions } });
  calls += 1;
  if (!result.ok) throw new Error(`askJev failed on ${c.name}: ${result.reason} ${result.error}`);
  model = result.model;
  const score = result.scores[keyDep];
  const said = score >= DEFAULT_THRESHOLD;
  samplesDep.push({ score, truth: c.truth });
  console.log(`${c.name.padEnd(42)} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(c.truth).padEnd(5)} ${said === c.truth ? 'HIT' : 'MISS'}`);
}
const gDep = gradeQuestion(samplesDep, DEFAULT_THRESHOLD);
console.log(`\n${keyDep} ${gDep.correct}/${gDep.asked} | yes ${gDep.yes}/${gDep.asked} | no-const ${gDep.alwaysNo}/${gDep.asked} yes-const ${gDep.alwaysYes}/${gDep.asked} | spread ${gDep.spread.toFixed(2)} | near ${gDep.near} | ${gDep.verdict}`);
console.log(`scores: ${gDep.scores.map((s) => s.toFixed(2)).join(' ')}`);

const samplesVer = [];
const keyVer = CANDIDATE_QUESTION_2.key;
if (keyVer !== labels.candidates.verification_weakened.candidate) throw new Error('ver candidate mismatch');
for (const c of labels.candidates.verification_weakened.cases) {
  const state = buildCommandState({ command: c.command });
  // eslint-disable-next-line no-await-in-loop
  const result = await askJev({ state, questions: { [keyVer]: CANDIDATE_QUESTION_2.instructions } });
  calls += 1;
  if (!result.ok) throw new Error(`askJev failed on ${c.name}: ${result.reason} ${result.error}`);
  model = result.model;
  const score = result.scores[keyVer];
  const said = score >= DEFAULT_THRESHOLD;
  samplesVer.push({ score, truth: c.truth });
  console.log(`${c.name.padEnd(42)} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(c.truth).padEnd(5)} ${said === c.truth ? 'HIT' : 'MISS'}`);
}
const gVer = gradeQuestion(samplesVer, DEFAULT_THRESHOLD);
console.log(`\n${keyVer} ${gVer.correct}/${gVer.asked} | yes ${gVer.yes}/${gVer.asked} | no-const ${gVer.alwaysNo}/${gVer.asked} yes-const ${gVer.alwaysYes}/${gVer.asked} | spread ${gVer.spread.toFixed(2)} | near ${gVer.near} | ${gVer.verdict}`);
console.log(`scores: ${gVer.scores.map((s) => s.toFixed(2)).join(' ')}`);
console.log(`calls: ${calls} | model: ${model} | threshold: ${DEFAULT_THRESHOLD}`);
