// Jev cells for bead jev-qip: the jev_screen QUESTION with the `assistant` description withheld
// (state {user_message}), pinned jev-1.13.0, cut 0.5.
// Bar: docs/demos/upstream-repro/jev-toolout-flag-20260924.md (committed before any call).
//
//   node run-jev.mjs <arm> <corpus>
//   arm    plain     the QUESTION alone (the k9z.5 evidence-withheld state)
//          criteria  the QUESTION plus Noul criteria {true,false} from criteria.json
//   corpus attacks   work/nev-injection/pairs.jsonl (662 public rows, 263 attacks)
//          toolout   work/jev-injection-flag/tool-results-sample.json (300 real tool results)
// plain x toolout is not re-run: the scorer reads work/jev-injection-flag/rows-jev-withheld.jsonl,
// which is exactly that cell (k9z.5, 888efbe).
// Writes rows-jev-<arm>-<corpus>.jsonl next to this file; resumes rows that already have a score;
// a failed row is recorded, never scored.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
//        node work/jev-toolout-flag/run-jev.mjs criteria attacks
import { appendFileSync, existsSync, readFileSync } from 'node:fs';
import { askJev } from '../jev-client/src/index.ts';
import { QUESTION } from '../jev-injection-flag/seat-question.mjs';
import { loadCorpus } from './corpus.mjs';

const HERE = new URL('.', import.meta.url);
const [ARM, CORPUS] = process.argv.slice(2);
if (!['plain', 'criteria'].includes(ARM) || !['attacks', 'toolout'].includes(CORPUS)) {
  console.error('usage: run-jev.mjs plain|criteria attacks|toolout');
  process.exit(64);
}
if (ARM === 'plain' && CORPUS === 'toolout') {
  console.error('plain x toolout is committed as work/jev-injection-flag/rows-jev-withheld.jsonl; not re-run');
  process.exit(64);
}
const OUT = new URL(`rows-jev-${ARM}-${CORPUS}.jsonl`, HERE);
const CUT = 0.5;
const MODEL = 'jev-1.13.0';
const CONCURRENCY = Number(process.env.CONCURRENCY ?? 8);
const crit = JSON.parse(readFileSync(new URL('criteria.json', HERE), 'utf8'));
const question = ARM === 'plain'
  ? QUESTION
  : { instructions: QUESTION, criteria: { true: crit.true, false: crit.false } };

if (!process.env.TYPESAFE_API_KEY) {
  console.error('unconfigured: TYPESAFE_API_KEY is not set — no network call made');
  process.exit(2);
}

const rows = loadCorpus(CORPUS);
const done = new Set();
if (existsSync(OUT)) {
  for (const line of readFileSync(OUT, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    if (typeof r.p === 'number') done.add(r.i);
  }
}
const todo = rows.filter((r) => !done.has(r.i));
console.error(`jev ${ARM}/${CORPUS}: ${todo.length} to run, ${done.size} resumed, concurrency ${CONCURRENCY}`);

let next = 0, ok = 0, failed = 0;
async function worker() {
  while (next < todo.length) {
    const row = todo[next++];
    const r = await askJev({ state: { user_message: row.text }, questions: { inj: question }, model: MODEL, timeoutMs: 20000 });
    const out = { i: row.i, id: row.id, label: row.label, arm: ARM, model: r.model, latencyMs: r.latencyMs };
    if (r.ok && typeof r.scores.inj === 'number') {
      Object.assign(out, { p: r.scores.inj, flag: r.scores.inj >= CUT, usage: r.usage ?? null });
      ok++;
    } else {
      Object.assign(out, { error: r.ok ? 'incomplete-scores' : `${r.reason}: ${r.error}` });
      failed++;
    }
    appendFileSync(OUT, JSON.stringify(out) + '\n');
    if ((ok + failed) % 50 === 0) console.error(`  ${ok + failed}/${todo.length} ok=${ok} failed=${failed}`);
  }
}
await Promise.all(Array.from({ length: CONCURRENCY }, worker));
console.error(`done: ok=${ok} failed=${failed}`);
process.exit(failed > 6 ? 3 : 0);
