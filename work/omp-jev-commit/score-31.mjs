/**
 * Unit 2: score 31 real commits through real Jev, join with human labels, kit verdict.
 * Truth in labels-31.json (read from diffs BEFORE any score was seen).
 * 31 calls, three noul questions each, one request per commit.
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     node --experimental-strip-types work/omp-jev-commit/score-31.mjs
 */
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { askJev } from '../../kit/src/client.ts';
import { gradeQuestion } from '../jev-client/measure-kit.mjs';

const labels = JSON.parse(readFileSync(new URL('./labels-31.json', import.meta.url), 'utf8')).commits;
const QUESTIONS = {
  describes: 'Does the commit message accurately describe what this diff actually changes?',
  overstates: 'Does the message claim work, results, or verification that the diff does not contain?',
  omits: 'Does the diff contain a significant change the message never mentions?',
};
const KEYS = Object.keys(QUESTIONS);
const all = [];
for (const c of labels) {
  const message = execFileSync('git', ['log', '-1', '--format=%B', c.sha], { encoding: 'utf8' });
  const diff = execFileSync('git', ['show', '--format=', c.sha], { encoding: 'utf8' }).slice(0, 12000);
  const r = await askJev({ state: { message, diff }, questions: QUESTIONS, timeoutMs: 8000 });
  if (!r.ok) { all.push({ sha: c.sha.slice(0, 7), error: `${r.reason}: ${r.error}` }); continue; }
  const row = { sha: c.sha.slice(0, 7) };
  for (const k of KEYS) {
    const s = r.scores[k];
    const said = s >= 0.5;
    row[k] = { score: +s.toFixed(2), said, truth: c[k], hit: said === c[k] };
  }
  all.push(row);
  console.log(`${row.sha} ` + KEYS.map((k) => `${k}=${row[k].score}/${row[k].said ? 'T' : 'F'}/${row[k].truth ? 'T' : 'F'}/${row[k].hit ? 'HIT' : 'MISS'}`).join(' '));
}
console.log('\nkit verdicts (rule: DISCRIMINATES iff correct > best_constant + near):');
for (const k of KEYS) {
  const samples = all.filter((r) => r[k]).map((r) => ({ score: r[k].score, truth: r[k].truth }));
  const g = gradeQuestion(samples);
  console.log(`${k.padEnd(11)} ${g.correct}/${g.asked} | yes ${g.yes}/${g.asked} | best-const ${g.best}/${g.asked} | near ${g.near} | spread ${g.spread.toFixed(2)} | ${g.verdict}`);
}
const errs = all.filter((r) => r.error);
console.log(`transport errors: ${errs.length}`);
