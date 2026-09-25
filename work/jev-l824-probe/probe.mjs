import { readFile, writeFile } from "node:fs/promises";
import { performance } from "node:perf_hooks";
import { askJev } from "../../kit/src/client.ts";

const MODEL = "jev-1.13.0";
const CALLS = 20;
const CONCURRENCY = 16;
const state = JSON.parse(await readFile(new URL("./state.json", import.meta.url), "utf8"));
const questions = {
  relevance: "Does this state contain useful information for a coding agent searching this repository?",
};

function percentile(values, p) {
  if (!values.length) return null;
  const ordered = [...values].sort((a, b) => a - b);
  const index = (ordered.length - 1) * p;
  const lower = Math.floor(index);
  const upper = Math.min(lower + 1, ordered.length - 1);
  return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower);
}

async function oneCall() {
  const started = performance.now();
  const result = await askJev({ state, questions, model: MODEL, timeoutMs: 10000 });
  return {
    ok: result.ok,
    model: result.model,
    latencyMs: result.latencyMs,
    wallMs: performance.now() - started,
    usage: result.ok ? result.usage ?? null : null,
    reason: result.ok ? null : result.reason,
  };
}

async function sequential() {
  const started = performance.now();
  const results = [];
  for (let index = 0; index < CALLS; index += 1) results.push(await oneCall());
  return { concurrency: 1, wallMs: performance.now() - started, results };
}

async function concurrent() {
  const started = performance.now();
  const results = Array(CALLS);
  let next = 0;
  async function worker() {
    while (true) {
      const index = next++;
      if (index >= CALLS) return;
      results[index] = await oneCall();
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCY }, () => worker()));
  return { concurrency: CONCURRENCY, wallMs: performance.now() - started, results };
}

function summarize(run) {
  const successful = run.results.filter((result) => result.ok);
  const latencies = successful.map((result) => result.latencyMs);
  const wallLatencies = run.results.map((result) => result.wallMs);
  const inputTokens = successful.reduce((sum, result) => sum + (result.usage?.input_tokens ?? 0), 0);
  return {
    concurrency: run.concurrency,
    wallMs: run.wallMs,
    calls: run.results.length,
    successes: successful.length,
    failures: run.results.length - successful.length,
    failureReasons: Object.fromEntries(
      Object.entries(Object.groupBy(run.results.filter((result) => !result.ok), (result) => result.reason))
        .map(([reason, values]) => [reason, values.length]),
    ),
    callLatencyMs: { p50: percentile(latencies, 0.5), p95: percentile(latencies, 0.95) },
    wallPerCallMs: { p50: percentile(wallLatencies, 0.5), p95: percentile(wallLatencies, 0.95) },
    inputTokens,
    spendUsd: inputTokens * 0.042 / 1_000_000,
  };
}

const sequentialRun = await sequential();
const concurrentRun = await concurrent();
const report = {
  model: MODEL,
  callsPerArm: CALLS,
  concurrentArmLimit: CONCURRENCY,
  stateSource: { path: state.source_path, sha256: state.source_sha256, byteLength: state.byte_length },
  question: questions,
  sequential: summarize(sequentialRun),
  concurrent16: summarize(concurrentRun),
  boundary: "This is a transport/queue smoke on one committed non-authored state, not an accuracy or ranking result.",
};
await writeFile(new URL("./live-report.json", import.meta.url), JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify(report, null, 2));
