/**
 * eww scorer: 32 pinned turns through the SHIPPED route questions (imported,
 * not copied), graded + prevalence-ordered. 32 live Jev calls, one request
 * each (both questions in parallel, as the extension asks them).
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     node work/omp-jev-route/score-32.mjs
 */
import { askJev } from '../jev-client/src/index.ts';
import { QUESTIONS } from './src/index.ts';
import { gradeQuestion } from '../jev-client/measure-kit.mjs';
import { TURNS } from './turns-32.mjs';

const THRESHOLD = 0.5;
const rows = [];
let errors = 0;
let model = null;
// TURNS truth keys are {heavyweight, mechanical}; question keys are
// {needs_heavyweight, mechanical}. Map explicitly — an undefined truth
// silently voids the whole column (gradeQuestion drops non-booleans).
const truthKey = (k) => (k === 'needs_heavyweight' ? 'heavyweight' : k);
for (const t of TURNS) {
  const r = await askJev({ state: { prompt: t.prompt }, questions: QUESTIONS, timeoutMs: 8000 });
  if (!r.ok) {
    rows.push({ id: t.id, cls: t.cls, error: `${r.reason}: ${r.error}` });
    errors += 1;
    continue;
  }
  model = r.model;
  const row = { id: t.id, cls: t.cls };
  for (const k of Object.keys(QUESTIONS)) {
    const s = r.scores[k];
    const said = s >= THRESHOLD;
    row[k] = { score: +s.toFixed(2), said, truth: t.truth[truthKey(k)], hit: said === t.truth[truthKey(k)] };
  }
  rows.push(row);
  console.log(`${t.id.padEnd(24)} ${t.cls.padEnd(12)} ` + Object.keys(QUESTIONS).map((k) => `${k.split('_')[0]}=${row[k].score}/${row[k].said ? 'T' : 'F'}/${row[k].truth ? 'T' : 'F'}/${row[k].hit ? 'HIT' : 'MISS'}`).join(' '));
}
console.log(`\nmodel: ${model} | transport errors: ${errors}`);
console.log('\nper question (near count BEFORE prevalence, §14e order):');
const verdicts = {};
for (const k of Object.keys(QUESTIONS)) {
  const samples = rows.filter((r) => r[k]).map((r) => ({ score: r[k].score, truth: r[k].truth }));
  const g = gradeQuestion(samples, THRESHOLD);
  verdicts[k] = g.verdict;
  console.log(`${k.padEnd(19)} ${g.correct}/${g.asked} | yes ${g.yes}/${g.asked} | best-const ${g.best}/${g.asked} | near ${g.near} | spread ${g.spread.toFixed(2)} | ${g.verdict}`);
}
console.log('\nby trap class:');
for (const cls of ['heavy-clear', 'mech-clear', 'trap-short', 'trap-long']) {
  for (const k of Object.keys(QUESTIONS)) {
    const ss = rows.filter((r) => r.cls === cls && r[k]);
    const hits = ss.filter((r) => r[k].hit).length;
    console.log(`  ${cls.padEnd(12)} ${k.split('_')[0]}: ${hits}/${ss.length}`);
  }
}
console.log(`\nverdicts: ${Object.entries(verdicts).map(([k, v]) => `${k}=${v}`).join(' ')}`);
