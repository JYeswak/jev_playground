/**
 * Cost sample. The 219-call run discarded latencyMs and never read usage.
 * This does not rescore accuracy. N=8, first snippet-bearing rows, same wire
 * path as the scorer (liveAsker -> jev-client). Fetch is wrapped only to
 * copy usage off the response the client already parses.
 */
import { readFileSync } from "node:fs";
import { liveAsker } from "./src/live.ts";
import { passageId } from "./src/rank.ts";

const rows = readFileSync("work/nev-rerank/pairs.jsonl", "utf8")
  .trim()
  .split("\n")
  .map((line) => JSON.parse(line))
  .filter((row) => row.candidates.some((c) => c.snippet.length > 0))
  .slice(0, 8);

const captured = [];
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  const started = Date.now();
  const response = await realFetch(url, init);
  const text = await response.text();
  let usage = null;
  let model = null;
  try {
    const body = JSON.parse(text);
    usage = body.usage ?? null;
    model = body.model ?? null;
  } catch { /* client reports non-json */ }
  captured.push({ ms: Date.now() - started, status: response.status, usage, model });
  return { ok: response.ok, status: response.status, text: async () => text };
};

const INPUT_PER_M = 0.042;
let inputTokens = 0;
let outputTokens = 0;
const latencies = [];
for (const row of rows) {
  const passages = {};
  row.candidates.forEach((c, i) => {
    passages[passageId(i)] = c.snippet ? `${c.file}\n${c.snippet}` : c.file;
  });
  const answer = await liveAsker({ query: row.intent, passages });
  const cap = captured[captured.length - 1];
  latencies.push(cap?.ms ?? null);
  const usage = cap?.usage ?? {};
  inputTokens += Number(usage.input_tokens ?? usage.inputTokens ?? 0);
  outputTokens += Number(usage.output_tokens ?? usage.outputTokens ?? 0);
  console.log(JSON.stringify({
    id: row.id,
    ok: answer.ok,
    reason: answer.ok ? null : answer.reason,
    ms: cap?.ms ?? null,
    status: cap?.status ?? null,
    model: cap?.model ?? null,
    usage: cap?.usage ?? null,
    n_candidates: row.candidates.length,
  }));
}
latencies.sort((a, b) => a - b);
const cost = inputTokens * INPUT_PER_M / 1e6;
const per1k = rows.length ? (cost / rows.length) * 1000 : null;
console.log(JSON.stringify({
  n: rows.length,
  input_tokens: inputTokens,
  output_tokens: outputTokens,
  cost_usd: cost,
  cost_per_1k_requests: per1k,
  price: "$0.042/MTok input, output free, jev-rerank-bench/common.py read 2026-09-16",
  latency_ms_min: latencies[0],
  latency_ms_median: latencies[Math.floor(latencies.length / 2)],
  latency_ms_max: latencies[latencies.length - 1],
  note: "sample of 8, not the 219. The 219 discarded latency.",
}));
