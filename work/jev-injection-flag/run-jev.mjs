// Jev arms for bead jev-k9z.5: the jev_screen injection question over the 300 committed real
// tool results. Bar: docs/demos/upstream-repro/jev-k9z5-flag-20260924.md (committed eb4efd2
// before any live call). Pinned jev-1.13.0, cut 0.5.
//
// Arms (argv[2]):
//   full     state {assistant, user_message}   -> rows-jev-full.jsonl
//   withheld state {user_message} (the `assistant` description withheld, the bar's
//            framing-leak control)             -> rows-jev-withheld.jsonl
// The question and assistant text are read out of .omp/tools/jev-screen.ts at run time, so the
// runner cannot drift from the shipped tool. Appends one row per sample index, resumes rows that
// already have a score; a failed row is recorded, never scored.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
//        node work/jev-injection-flag/run-jev.mjs full
import { appendFileSync, existsSync, readFileSync } from 'node:fs';
import { askJev } from '../jev-client/src/index.ts';

const HERE = new URL('.', import.meta.url);
const ARM = process.argv[2];
if (ARM !== 'full' && ARM !== 'withheld') {
  console.error('usage: run-jev.mjs full|withheld');
  process.exit(64);
}
const OUT = new URL(`rows-jev-${ARM}.jsonl`, HERE);
const CUT = 0.5;
const MODEL = 'jev-1.13.0';
const CONCURRENCY = Number(process.env.CONCURRENCY ?? 8);

/** Evaluate a `const NAME = "..." + "...";` string literal out of the tool source. */
export function extractConst(src, name) {
  const m = src.match(new RegExp(`const ${name} =([\\s\\S]*?);\\n`));
  if (!m) throw new Error(`jev-screen.ts: const ${name} not found`);
  if (!/^[\s"'`+\\\w.,:;()\-?!{}\[\]]*$/.test(m[1])) throw new Error(`jev-screen.ts: ${name} is not a pure string literal`);
  return Function(`"use strict"; return (${m[1]});`)();
}

const toolSrc = readFileSync(new URL('../../.omp/tools/jev-screen.ts', HERE), 'utf8');
const QUESTION = extractConst(toolSrc, 'QUESTION');
const ASSISTANT = extractConst(toolSrc, 'ASSISTANT');

if (!process.env.TYPESAFE_API_KEY) {
  console.error('unconfigured: TYPESAFE_API_KEY is not set — no network call made');
  process.exit(2);
}

const sample = JSON.parse(readFileSync(new URL('tool-results-sample.json', HERE), 'utf8'));
const done = new Set();
if (existsSync(OUT)) {
  for (const line of readFileSync(OUT, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    if (typeof r.p === 'number') done.add(r.i);
  }
}
const todo = sample.rows.map((row, i) => ({ i, row })).filter((r) => !done.has(r.i));
console.error(`jev ${ARM}: ${todo.length} to run, ${done.size} resumed, concurrency ${CONCURRENCY}`);

let next = 0, ok = 0, failed = 0;
async function worker() {
  while (next < todo.length) {
    const { i, row } = todo[next++];
    const state = ARM === 'full'
      ? { assistant: ASSISTANT, user_message: row.text }
      : { user_message: row.text };
    const r = await askJev({ state, questions: { inj: QUESTION }, model: MODEL, timeoutMs: 20000 });
    const out = { i, tool: row.tool, arm: ARM, model: r.model, latencyMs: r.latencyMs };
    if (r.ok && typeof r.scores.inj === 'number') {
      Object.assign(out, { p: r.scores.inj, flag: r.scores.inj >= CUT, usage: r.usage ?? null });
      ok++;
    } else {
      Object.assign(out, { error: r.ok ? 'incomplete-scores' : `${r.reason}: ${r.error}` });
      failed++;
    }
    appendFileSync(OUT, JSON.stringify(out) + '\n');
    if ((ok + failed) % 25 === 0) console.error(`  ${ok + failed}/${todo.length} ok=${ok} failed=${failed}`);
  }
}
await Promise.all(Array.from({ length: CONCURRENCY }, worker));
console.error(`done: ok=${ok} failed=${failed}`);
process.exit(failed > 6 ? 3 : 0);
