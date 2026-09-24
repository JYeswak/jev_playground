// Jev arm for bead jev-32z: the frozen gate questions over 300 real routine jev commands.
// Bar and adjudication rule: docs/demos/upstream-repro/bicameral-gate-real-traffic-20260923.md,
// committed at 5432635 before this file ran. Pinned jev-1.13.0. Appends one row per command to
// real-rows-jev.jsonl and resumes rows that already have scores; a failed row is recorded, never
// scored. Run: infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node work/bicameral-gate/real-traffic.mjs [out.jsonl]
// The optional argument (jev-24e) writes a re-run to a new file; the call path is unchanged.
import { appendFileSync, existsSync, readFileSync } from 'node:fs';
import { askJev } from '../jev-client/src/index.ts';
import { CUT, RISK, STATE_CONTEXT } from './questions.mjs';

const HERE = new URL('.', import.meta.url);
const OUT = process.argv[2] ?? new URL('real-rows-jev.jsonl', HERE);
const sample = JSON.parse(readFileSync(new URL('real-sample.json', HERE), 'utf8'));
const CONCURRENCY = Number(process.env.CONCURRENCY ?? 8);

if (!process.env.TYPESAFE_API_KEY) {
  console.error('unconfigured: TYPESAFE_API_KEY is not set — no network call made');
  process.exit(2);
}

const questions = {
  ...Object.fromEntries(Object.entries(RISK).map(([k, q]) => [k, q.instructions])),
  mentions_git: 'Does this command text contain the word git?',
};

const done = new Set();
if (existsSync(OUT)) {
  for (const line of readFileSync(OUT, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    if (r.scores) done.add(r.i);
  }
}
const todo = sample.commands.map((command, i) => ({ i, command })).filter((r) => !done.has(r.i));
console.error(`jev arm: ${todo.length} to run, ${done.size} resumed, concurrency ${CONCURRENCY}`);

let next = 0, ok = 0, failed = 0;
async function worker() {
  while (next < todo.length) {
    const { i, command } = todo[next++];
    const r = await askJev({
      state: { command, context: STATE_CONTEXT },
      questions,
      model: 'jev-1.13.0',
      timeoutMs: 20000,
    });
    const row = { i, command, model: r.model, latencyMs: r.latencyMs };
    if (r.ok) {
      const risk = Math.max(...Object.keys(RISK).map((k) => r.scores[k]));
      Object.assign(row, { scores: r.scores, risk, flag: risk > CUT, usage: r.usage ?? null });
      ok++;
    } else {
      Object.assign(row, { error: `${r.reason}: ${r.error}` });
      failed++;
    }
    appendFileSync(OUT, JSON.stringify(row) + '\n');
    if ((ok + failed) % 25 === 0) console.error(`  ${ok + failed}/${todo.length} ok=${ok} failed=${failed}`);
  }
}
await Promise.all(Array.from({ length: CONCURRENCY }, worker));
console.error(`done: ok=${ok} failed=${failed}`);
process.exit(failed > 6 ? 3 : 0);
