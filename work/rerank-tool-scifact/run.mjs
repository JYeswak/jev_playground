#!/usr/bin/env node
/**
 * Bead jev-k9z.7: the shipped omp tool jev_rerank on BEIR SciFact.
 *
 *   node work/rerank-tool-scifact/run.mjs --selftest            # no key, no network
 *   infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node work/rerank-tool-scifact/run.mjs {tool|tool-run2|tool-run3}
 *
 * Measures the code path .omp/tools/jev-rerank.ts runs: rerank() from
 * work/nev-rerank/src/rank.ts with liveAsker from work/nev-rerank/src/live.ts, passed
 * as-is. Nothing here restates the rubric, the question, or the expected-level reduction.
 * Preregistration: docs/demos/upstream-repro/rerank-tool-scifact-prereg-20260924.md.
 *
 * Passages go to the tool in BM25 order as `${title}\n${text}`. One row per query and
 * attempt, ids and scores only: no query or passage text is written (the corpus license
 * decision in rerank-beir-scifact-20260924.md). globalThis.fetch is wrapped to count HTTP
 * requests, statuses and the server's usage.input_tokens per query; the tool's own return
 * value carries none of these. The wrapper changes no request and no response.
 *
 * After the first pass, queries whose row came back ordered=false get exactly one more
 * attempt (attempt 2). A key/SDK/billing refusal stops dispatch and exits 4.
 */
import { AsyncLocalStorage } from "node:async_hooks";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { appendFileSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { rerank } from "../nev-rerank/src/rank.ts";
import { liveAsker, LIVE_MODEL } from "../nev-rerank/src/live.ts";
import { requireSdkInstalled } from "../sdk/require-installed.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
export const CANDIDATES = join(HERE, "..", "rerank-scifact", "candidates.jsonl");
export const CANDIDATES_SHA256 = "2cf3a9a96a12253a76095f5505dc475dcae5eb64b5dd29b2ed36de9290fe83e8";
export const ZIP_SHA256 = "536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165";
const ZIP_PATH = process.env.BEIR_SCIFACT_ZIP ?? "/tmp/beir-scifact/scifact.zip";
export const RUNS = ["tool", "tool-run2", "tool-run3"];
export const DEPTH = 20;
// Queries in flight; liveAsker is sequential within a query and the shipped path does not
// retry (maxRetries 0). 4 keeps the request rate under the documented 1,200 requests/minute
// (docs-mirror/typesafe/models.md:14) unless a call returns in under 200 ms.
const CONCURRENCY = 4;
const STOP_REASONS = new Set(["unconfigured", "sdk-missing", "billing-hold"]);

export const rowsPath = (run) => join(HERE, `rows-${run}.jsonl`);
const sha256 = (buf) => createHash("sha256").update(buf).digest("hex");

export function loadCandidates() {
  const buf = readFileSync(CANDIDATES);
  if (sha256(buf) !== CANDIDATES_SHA256) throw new Error(`candidates.jsonl sha256 is not ${CANDIDATES_SHA256}`);
  const rows = buf.toString("utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
  for (const r of rows) if (r.cands.length !== DEPTH) throw new Error(`qid ${r.qid}: ${r.cands.length} candidates`);
  return rows;
}

/** Same bytes run.py:101-124 reads; refuses on a sha mismatch. */
export function loadText() {
  const zip = readFileSync(ZIP_PATH);
  const digest = sha256(zip);
  if (digest !== ZIP_SHA256) throw new Error(`scifact.zip sha256 ${digest} != ${ZIP_SHA256}`);
  const member = (name) =>
    execFileSync("unzip", ["-p", ZIP_PATH, name], { maxBuffer: 64 * 1024 * 1024 })
      .toString("utf8")
      .split("\n")
      .filter((l) => l.trim())
      .map((l) => JSON.parse(l));
  const corpus = new Map(member("scifact/corpus.jsonl").map((d) => [d._id, d]));
  const queries = new Map(member("scifact/queries.jsonl").map((q) => [q._id, q.text]));
  return { corpus, queries };
}

/** The frozen passage string: title, newline, text. */
export const passageString = (doc) => `${doc.title ?? ""}\n${doc.text ?? ""}`;

/** Per-query HTTP accounting. Installed once; a no-op outside a query context. */
const ctxStore = new AsyncLocalStorage();
let fetchWrapped = false;
export function wrapFetch() {
  if (fetchWrapped) return;
  fetchWrapped = true;
  const orig = globalThis.fetch;
  globalThis.fetch = async (...args) => {
    const ctx = ctxStore.getStore();
    if (!ctx) return orig(...args);
    ctx.calls += 1;
    let res;
    try {
      res = await orig(...args);
    } catch (err) {
      ctx.status.transport = (ctx.status.transport ?? 0) + 1;
      throw err;
    }
    ctx.status[res.status] = (ctx.status[res.status] ?? 0) + 1;
    try {
      const body = await res.clone().json();
      const tin = body?.usage?.input_tokens;
      if (typeof tin === "number" && Number.isFinite(tin)) ctx.inputTokens += tin;
      if (typeof body?.model === "string") ctx.models.add(body.model);
    } catch {
      // non-JSON body: the shipped client classifies it; we only count the request
    }
    return res;
  };
}

/** One rerank() over `passages` (in `docs` order) with the HTTP accounting. work/rerank-nevir reuses it. */
export async function scoreRanked({ qid, query, docs, passages }, run, attempt, asker) {
  const ctx = { calls: 0, status: {}, inputTokens: 0, models: new Set() };
  const t0 = performance.now();
  const res = await ctxStore.run(ctx, () => rerank(query, passages, asker));
  const wallMs = Math.round(performance.now() - t0);
  return {
    qid,
    run,
    attempt,
    ordered: res.ordered,
    reason: res.reason ?? null,
    calledModel: res.calledModel,
    truncated: res.truncated,
    ranking: res.ranking.map((r) => ({ doc: docs[r.index], score: Number.isFinite(r.score) ? r.score : null })),
    wallMs,
    ts: new Date().toISOString(),
    calls: ctx.calls,
    status: ctx.status,
    inputTokens: ctx.inputTokens,
    models: [...ctx.models].sort(),
  };
}

export async function scoreQuery(cand, text, run, attempt, asker) {
  const docs = cand.cands.map(([d]) => d);
  const passages = docs.map((d) => passageString(text.corpus.get(d)));
  return scoreRanked({ qid: cand.qid, query: text.queries.get(cand.qid), docs, passages }, run, attempt, asker);
}

/** Drop one trailing partial line left by a crash. Never deletes the file. */
export function repairTail(path) {
  if (!existsSync(path)) return;
  const text = readFileSync(path, "utf8");
  if (text === "" || text.endsWith("\n")) return;
  writeFileSync(path, text.slice(0, text.lastIndexOf("\n") + 1));
}

export function readRows(path) {
  if (!existsSync(path)) return [];
  return readFileSync(path, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
}

/** Bounded pool over queries. Stops dispatching once `stop()` is true. */
async function pool(items, worker, stop) {
  let next = 0;
  const lanes = Array.from({ length: Math.min(CONCURRENCY, items.length) }, async () => {
    while (next < items.length && !stop()) {
      const item = items[next++];
      await worker(item);
    }
  });
  await Promise.all(lanes);
}

/**
 * One run: first pass over queries with no attempt-1 row, then one resume pass over
 * queries whose attempt-1 row is ordered=false and that have no attempt-2 row.
 * `write(row)` persists; `existing` is the rows already on disk.
 */
export async function runAll({
  run,
  cands,
  text,
  asker,
  write,
  existing = [],
  log = () => {},
  score = (cand, attempt) => scoreQuery(cand, text, run, attempt, asker),
}) {
  const has = (attempt) => new Set(existing.filter((r) => r.attempt === attempt).map((r) => r.qid));
  let stopped = null;
  const stop = () => stopped !== null;
  const worker = (attempt) => async (cand) => {
    const row = await score(cand, attempt);
    write(row);
    existing.push(row);
    if (STOP_REASONS.has(row.reason) || row.status["402"]) stopped ??= `${row.reason ?? "http"} at qid ${row.qid}`;
    if (!row.ordered) log(`attempt ${attempt} qid ${row.qid} ordered=false reason=${row.reason}`);
  };
  const done1 = has(1);
  const first = cands.filter((c) => !done1.has(c.qid));
  log(`${run}: first pass ${first.length} queries (${done1.size} already on disk)`);
  await pool(first, worker(1), stop);
  if (!stopped) {
    const done2 = has(2);
    const failed1 = new Set(existing.filter((r) => r.attempt === 1 && !r.ordered).map((r) => r.qid));
    const second = cands.filter((c) => failed1.has(c.qid) && !done2.has(c.qid));
    log(`${run}: resume pass ${second.length} queries`);
    await pool(second, worker(2), stop);
  }
  return { stopped };
}

export function summarize(rows) {
  const latest = new Map();
  for (const r of rows) if (!latest.has(r.qid) || r.attempt > latest.get(r.qid).attempt) latest.set(r.qid, r);
  const unordered = [...latest.values()].filter((r) => !r.ordered).map((r) => r.qid);
  const calls = rows.reduce((s, r) => s + r.calls, 0);
  const tin = rows.reduce((s, r) => s + r.inputTokens, 0);
  return { queries: latest.size, unordered, calls, tin };
}

async function live(run) {
  if (!RUNS.includes(run)) throw new Error(`run must be one of ${RUNS.join(", ")}`);
  const cands = loadCandidates();
  const text = loadText();
  wrapFetch();
  const path = rowsPath(run);
  repairTail(path);
  const existing = readRows(path);
  const t0 = Date.now();
  const startIso = new Date(t0).toISOString();
  const { stopped } = await runAll({
    run,
    cands,
    text,
    asker: liveAsker,
    existing,
    write: (row) => appendFileSync(path, JSON.stringify(row) + "\n"),
    log: (m) => console.error(m),
  });
  const s = summarize(readRows(path));
  console.log(
    `${run} model=${LIVE_MODEL} start=${startIso} end=${new Date().toISOString()} wall_s=${((Date.now() - t0) / 1000).toFixed(1)} ` +
      `queries=${s.queries}/${cands.length} unordered_after_resume=${s.unordered.length} [${s.unordered.join(",")}] ` +
      `http_calls=${s.calls} input_tokens=${s.tin}`,
  );
  if (stopped) {
    console.log(`STOPPED: ${stopped}. No further calls were dispatched.`);
    return 4;
  }
  return s.queries === cands.length ? 0 : 3;
}

async function selftest() {
  // Arm 4 runs the shipped liveAsker through the SDK. A missing install is the named
  // prerequisite (npm ci --prefix work/sdk) that run-registered-suites.py reads as SKIP.
  requireSdkInstalled();
  const bad = [];
  const check = (ok, msg) => {
    if (!ok) bad.push(msg);
  };
  const cands = loadCandidates().slice(0, 2);
  // Synthetic text: the selftest reads no corpus and no network.
  const corpus = new Map();
  for (const c of cands) for (const [d] of c.cands) corpus.set(d, { title: `T${d}`, text: `body ${d}` });
  const text = { corpus, queries: new Map(cands.map((c) => [c.qid, `query ${c.qid}`])) };
  const prev = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  const origFetch = globalThis.fetch;
  let netCalls = 0;
  globalThis.fetch = async () => {
    netCalls += 1;
    throw new Error("selftest: network is forbidden");
  };
  try {
    wrapFetch();
    // 1. Injected fake asker: reverse BM25 order by score. Proves id->doc mapping and row shape.
    const seen = [];
    const fake = async (state) => {
      seen.push(state);
      const ids = Object.keys(state.passages);
      return { ok: true, scores: Object.fromEntries(ids.map((id, i) => [id, (i + 1) / ids.length])) };
    };
    const rows = [];
    const r1 = await runAll({ run: "selftest", cands, text, asker: fake, write: (r) => rows.push(r) });
    check(!r1.stopped && rows.length === 2, "fake asker: two rows, not stopped");
    for (const [k, c] of cands.entries()) {
      const row = rows.find((r) => r.qid === c.qid);
      const bm25 = c.cands.map(([d]) => d);
      check(row?.ordered === true && row.attempt === 1, `fake asker qid ${c.qid}: ordered attempt 1`);
      check(JSON.stringify(row.ranking.map((x) => x.doc)) === JSON.stringify([...bm25].reverse()), `qid ${c.qid}: ranking maps ids back to docs`);
      check(row.calls === 0, `qid ${c.qid}: fake asker made no HTTP call`);
      check(!JSON.stringify(row).includes("body ") && !JSON.stringify(row).includes("query "), `qid ${c.qid}: row carries no text`);
      const st = seen[k];
      check(st.passages.p01 === `T${bm25[0]}\nbody ${bm25[0]}` && Object.keys(st.passages).length === DEPTH, `qid ${c.qid}: passages in BM25 order as title\\ntext`);
    }
    // 2. Resume: an asker that fails the first attempt of every query gets exactly one more try.
    let tries = 0;
    const flaky = async (state) => (++tries <= 2 ? { ok: false, reason: "http" } : fake(state));
    const rows2 = [];
    await runAll({ run: "selftest", cands, text, asker: flaky, write: (r) => rows2.push(r) });
    check(rows2.length === 4 && rows2.filter((r) => r.attempt === 2 && r.ordered).length === 2, "resume: one retry per ordered=false query");
    check(rows2.filter((r) => r.attempt === 1).every((r) => !r.ordered && r.ranking.map((x) => x.doc).join() === cands.find((c) => c.qid === r.qid).cands.map(([d]) => d).join()), "ordered=false returns BM25 order");
    // 3. Shipped liveAsker with no key: ordered=false reason=unconfigured, no throw, no HTTP, run stops.
    const rows3 = [];
    let threw = false;
    let r3;
    try {
      r3 = await runAll({ run: "selftest", cands, text, asker: liveAsker, write: (r) => rows3.push(r) });
    } catch {
      threw = true;
    }
    check(!threw, "missing key: no throw");
    check(rows3.length >= 1 && rows3.every((r) => r.ordered === false && r.reason === "unconfigured" && r.calls === 0), "missing key: ordered=false reason=unconfigured, zero HTTP calls");
    check(r3?.stopped?.startsWith("unconfigured"), "missing key: dispatch stops");
    // 4. Shipped liveAsker through a fake transport: counts 20 calls and usage per query.
    process.env.TYPESAFE_API_KEY = "test-key";
    const answer = JSON.stringify({
      answers: { score: { type: "score", score: 3, confidence: 0.9, legend: { 0: "a", 1: "b", 2: "c", 3: "d" }, probabilities: { 0: 0.1, 1: 0.1, 2: 0.2, 3: 0.6 } } },
      usage: { input_tokens: 7, output_tokens: 1 },
      model: "jev-selftest",
    });
    globalThis.fetch = origFetch; // restore, then re-wrap over a fake transport
    fetchWrapped = false;
    globalThis.fetch = async () => new Response(answer, { status: 200, headers: { "content-type": "application/json" } });
    wrapFetch();
    const rows4 = [];
    await runAll({ run: "selftest", cands, text, asker: liveAsker, write: (r) => rows4.push(r) });
    check(rows4.length === 2 && rows4.every((r) => r.ordered && r.calls === DEPTH && r.inputTokens === 7 * DEPTH && r.status["200"] === DEPTH), "fake transport: 20 calls, 140 tokens, 20x200 per query");
    check(rows4.every((r) => r.models.join() === "jev-selftest"), "fake transport: response model recorded");
    check(rows4.every((r) => r.ranking.every((x) => x.score !== null && x.score >= 0 && x.score <= 1)), "fake transport: scores in [0,1]");
    check(netCalls === 0, "no real network call");
  } finally {
    globalThis.fetch = origFetch;
    if (prev === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = prev;
  }
  for (const b of bad) console.log(`SELFTEST RED: ${b}`);
  console.log(bad.length ? "SELFTEST FAIL" : "SELFTEST PASS: fake asker 2 queries, id->doc mapping, no text in rows, one resume per failure, missing key = ordered=false/unconfigured with 0 calls and no throw, fake transport counts 20 calls and usage");
  return bad.length ? 1 : 0;
}

// Imported by work/rerank-nevir/tool.mjs: dispatch only when run as the script.
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const arg = process.argv[2];
  if (arg === "--selftest") process.exitCode = await selftest();
  else if (arg) process.exitCode = await live(arg);
  else {
    console.error("usage: run.mjs --selftest | tool | tool-run2 | tool-run3");
    process.exitCode = 2;
  }
}
