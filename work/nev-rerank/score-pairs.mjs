/**
 * Score the persisted grep->read pairs with one live systemOne call each.
 * Budget: one request per labelled row. Model jev-1.13.0. Approved 2026-09-21.
 *
 * Head-to-head on the same rows. A failed call is unscored, never a miss.
 * Unlabelled pairs are not in the file.
 */
import { appendFileSync, readFileSync, existsSync } from "node:fs";
import { rerank } from "./src/rank.ts";
import { liveAsker } from "./src/live.ts";

const PAIRS = "work/nev-rerank/pairs.jsonl";
const OUT = "work/nev-rerank/scores.jsonl";
const CONCURRENCY = 6;

const rows = readFileSync(PAIRS, "utf8").trim().split("\n").map((line) => JSON.parse(line));
const done = new Set();
if (existsSync(OUT)) {
  for (const line of readFileSync(OUT, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try { done.add(JSON.parse(line).id); } catch { /* skip a torn tail */ }
  }
}
const pending = rows.filter((row) => !done.has(row.id));
console.log(`rows=${rows.length} already=${done.size} pending=${pending.length}`);

async function askWithRetry(state) {
  let last = await liveAsker(state);
  for (let attempt = 0; attempt < 2 && !last.ok && (last.reason === "http" || last.reason === "transport"); attempt++) {
    await new Promise((resolve) => setTimeout(resolve, 800 * (attempt + 1)));
    last = await liveAsker(state);
  }
  return last;
}

async function scoreOne(row) {
  const passages = row.candidates.map((c) => (c.snippet ? `${c.file}\n${c.snippet}` : c.file));
  const query = row.intent.trim() || row.query;
  const result = await rerank(query, passages, askWithRetry);
  const top = result.ordered ? result.ranking[0] : null;
  const topFile = top ? row.candidates[top.index].file : null;
  return {
    id: row.id,
    label: row.label,
    label_rank: row.label_rank,
    n_candidates: row.candidates.length,
    snippet_chars: row.candidates.reduce((n, c) => n + c.snippet.length, 0),
    ordered: result.ordered,
    reason: result.reason ?? null,
    top_file: topFile,
    top_score: top && Number.isFinite(top.score) ? top.score : null,
    jev_top1: topFile === row.label,
    baseline_top1: row.label_rank === 1,
    scores: result.ordered ? result.ranking.map((r) => ({ file: row.candidates[r.index].file, score: r.score })) : [],
  };
}

let cursor = 0;
let finished = 0;
async function worker() {
  for (;;) {
    const i = cursor++;
    if (i >= pending.length) return;
    const row = pending[i];
    let record;
    try {
      record = await scoreOne(row);
    } catch (err) {
      record = {
        id: row.id,
        label: row.label,
        label_rank: row.label_rank,
        n_candidates: row.candidates.length,
        ordered: false,
        reason: "throw",
        error: err instanceof Error ? err.message : "throw",
        jev_top1: false,
        baseline_top1: row.label_rank === 1,
      };
    }
    appendFileSync(OUT, JSON.stringify(record) + "\n");
    finished += 1;
    if (finished % 20 === 0 || finished === pending.length) {
      console.log(`scored ${finished}/${pending.length} last=${record.id} ordered=${record.ordered} jev=${record.jev_top1}`);
    }
  }
}

await Promise.all(Array.from({ length: Math.min(CONCURRENCY, pending.length) }, () => worker()));
console.log("DONE");
