/**
 * pass5-run.mjs — jev-vbh.2 Pass 5: SECOND candidate (control-weakening
 * PRESENCE family), live measurement on OBSERVED facts.
 * Reads pass5-labels.json (labelled BEFORE any Jev call), sends each case ONCE
 * via the sanctioned askJev, grades with gradeQuestion. Prints HIT/MISS rows +
 * the rule-computed verdict word. 8 live Jev calls total.
 */
import { readFileSync } from 'node:fs';
import { askJev } from '../../kit/src/client.ts';
import { gradeQuestion, DEFAULT_THRESHOLD } from '../jev-client/measure-kit.mjs';
import { CANDIDATE_QUESTION_2, buildCommandState } from './trial.mjs';

const labels = JSON.parse(readFileSync(new URL('./pass5-labels.json', import.meta.url), 'utf8'));
const key = CANDIDATE_QUESTION_2.key;
if (key !== labels.candidate) throw new Error(`candidate mismatch: ${key} vs ${labels.candidate}`);

const samples = [];
let model = null;
let calls = 0;
for (const c of labels.cases) {
  const state = buildCommandState({ command: c.command });
  // eslint-disable-next-line no-await-in-loop
  const result = await askJev({ state, questions: { [key]: CANDIDATE_QUESTION_2.instructions } });
  calls += 1;
  if (!result.ok) throw new Error(`askJev failed on ${c.name}: ${result.reason} ${result.error}`);
  model = result.model;
  const score = result.scores[key];
  const truth = c.truth;
  const said = score >= DEFAULT_THRESHOLD;
  samples.push({ score, truth });
  console.log(`${c.name.padEnd(42)} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(truth).padEnd(5)} ${said === truth ? 'HIT' : 'MISS'}`);
}

const g = gradeQuestion(samples, DEFAULT_THRESHOLD);
console.log(`\n${key} ${g.correct}/${g.asked} | yes ${g.yes}/${g.asked} | no-const ${g.alwaysNo}/${g.asked} yes-const ${g.alwaysYes}/${g.asked} | spread ${g.spread.toFixed(2)} | near ${g.near} | ${g.verdict}`);
console.log(`scores: ${g.scores.map((s) => s.toFixed(2)).join(' ')}`);
console.log(`calls: ${calls} | model: ${model} | threshold: ${DEFAULT_THRESHOLD}`);
