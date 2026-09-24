#!/usr/bin/env node
/**
 * Bead jev-k9z.9, rubric arm: the shipped omp tool's path (rerank() from
 * work/nev-rerank/src/rank.ts with liveAsker from live.ts) on NevIR's 2,766 test questions.
 *
 *   node --experimental-strip-types work/rerank-nevir/tool.mjs --selftest     # no key, no network
 *   infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/rerank-nevir/tool.mjs {tool|tool-run2|tool-run3}
 *
 * Preregistration: docs/demos/upstream-repro/rerank-nevir-20260924.md. A dirty or uncommitted
 * preregistration refuses before any call (work/sr-adopt/phase_gate.py's require_bar).
 *
 * Each question gets its pair's two passages, raw text, in jev-rerank-bench's fixed order
 * (passage 1, passage 2) for both questions. Rows hold ids and scores only, no text. The
 * accounting, one-resume-pass and stop logic are work/rerank-tool-scifact/run.mjs's, imported.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { appendFileSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { liveAsker, LIVE_MODEL } from "../nev-rerank/src/live.ts";
import { requireSdkInstalled } from "../sdk/require-installed.mjs";
import { readRows, repairTail, runAll, scoreRanked, summarize, wrapFetch } from "../rerank-tool-scifact/run.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..");
export const RUNS = ["tool", "tool-run2", "tool-run3"];
export const PREREG = "docs/demos/upstream-repro/rerank-nevir-20260924.md";
export const rowsPath = (run) => join(HERE, `rows-${run}.jsonl`);
// The same two pins nevir.py reads: jev-rerank-bench@cd9a35b's question list, and NevIR's
// test split at HF revision 6263585072ce3b435ed09658613553fbf4e74184 (MIT).
export const CANDIDATES = join(ROOT, "jev-rerank-bench", "candidates", "nevir.jsonl");
export const CANDIDATES_SHA256 = "0c3acd0deda80e2cd9c31ed3b50e9fcef7380caa83f5b6cff313d7e441b92e07";
export const NEVIR_SHA256 = "5eb79ec32e82ff17ef6c2f47b75baca182013053ed74672d426bbc338af05d67";
const NEVIR_PATH = process.env.NEVIR_TEST ?? "/tmp/nevir/test.jsonl";

const sha256 = (buf) => createHash("sha256").update(buf).digest("hex");
function pinned(path, want) {
  const buf = readFileSync(path);
  if (sha256(buf) !== want) throw new Error(`${path} sha256 is not ${want}`);
  return buf.toString("utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
}

/** Questions in the bench's order: qid, pair, query, relevant doc, [d1, d2] and their raw text. */
export function loadNevir() {
  const text = new Map();
  for (const r of pinned(NEVIR_PATH, NEVIR_SHA256)) {
    text.set(`${r.id}-d1`, r.doc1);
    text.set(`${r.id}-d2`, r.doc2);
  }
  return pinned(CANDIDATES, CANDIDATES_SHA256).map((c) => {
    const docs = c.present.map((p) => p.did);
    return { qid: c.qid, pair: c.pair, query: c.query, rel: Object.keys(c.relevant)[0], docs, passages: docs.map((d) => text.get(d)) };
  });
}

/** One NevIR question through the shipped rerank() + asker. */
export const scoreQuestion = (q, run, attempt, asker) =>
  scoreRanked({ qid: q.qid, query: q.query, docs: q.docs, passages: q.passages }, run, attempt, asker);

function requireBar() {
  execFileSync(
    "python3",
    [
      "-c",
      "import sys; sys.path.insert(0, sys.argv[3]); from phase_gate import require_bar; require_bar(sys.argv[1], repo=sys.argv[2])",
      PREREG,
      ROOT,
      join(ROOT, "work", "sr-adopt"),
    ],
    { cwd: ROOT, stdio: ["ignore", "ignore", "inherit"] },
  );
}

async function live(run) {
  if (!RUNS.includes(run)) throw new Error(`run must be one of ${RUNS.join(", ")}`);
  requireBar();
  const questions = loadNevir();
  wrapFetch();
  const path = rowsPath(run);
  repairTail(path);
  const existing = readRows(path);
  const t0 = Date.now();
  const { stopped } = await runAll({
    run,
    cands: questions,
    existing,
    write: (row) => appendFileSync(path, JSON.stringify(row) + "\n"),
    log: (m) => console.error(m),
    score: (q, attempt) => scoreQuestion(q, run, attempt, liveAsker),
  });
  const s = summarize(readRows(path));
  console.log(
    `${run} model=${LIVE_MODEL} start=${new Date(t0).toISOString()} end=${new Date().toISOString()} ` +
      `wall_s=${((Date.now() - t0) / 1000).toFixed(1)} questions=${s.queries}/${questions.length} ` +
      `unordered_after_resume=${s.unordered.length} http_calls=${s.calls} input_tokens=${s.tin}`,
  );
  if (stopped) {
    console.log(`STOPPED: ${stopped}. No further calls were dispatched.`);
    return 4;
  }
  return s.queries === questions.length ? 0 : 3;
}

async function selftest() {
  requireSdkInstalled();
  const bad = [];
  const check = (ok, msg) => ok || bad.push(msg);
  const qs = [
    { qid: "9-1-q1", pair: "9-1", query: "query one", docs: ["9-1-d1", "9-1-d2"], passages: ["alpha body", "beta body"] },
    { qid: "9-1-q2", pair: "9-1", query: "query two", docs: ["9-1-d1", "9-1-d2"], passages: ["alpha body", "beta body"] },
  ];
  const hadKey = Object.hasOwn(process.env, "TYPESAFE_API_KEY");
  const prev = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  const origFetch = globalThis.fetch;
  let net = 0;
  globalThis.fetch = async () => {
    net += 1;
    throw new Error("selftest: network is forbidden");
  };
  try {
    // 1. A fake asker that prefers p02: rows map pNN back to NevIR doc ids, and carry no text.
    const seen = [];
    const fake = async (state) => {
      seen.push(state);
      return { ok: true, scores: { p01: 0.2, p02: 0.9 } };
    };
    const rows = [];
    await runAll({ run: "selftest", cands: qs, existing: [], write: (r) => rows.push(r), score: (q, a) => scoreQuestion(q, "selftest", a, fake) });
    check(rows.length === 2 && rows.every((r) => r.ordered && r.attempt === 1), "fake asker: two ordered rows");
    check(rows.every((r) => r.ranking.map((x) => x.doc).join() === "9-1-d2,9-1-d1"), "ranking maps p02 back to the d2 id");
    check(seen.every((st) => st.passages.p01 === "alpha body" && st.passages.p02 === "beta body"), "passages go in fixed d1, d2 order, raw text");
    check(!JSON.stringify(rows).includes("body") && !JSON.stringify(rows).includes("query "), "rows carry no text");
    // 2. The shipped liveAsker with no key: ordered=false unconfigured, 0 HTTP calls, dispatch stops.
    const rows2 = [];
    const r2 = await runAll({ run: "selftest", cands: qs, existing: [], write: (r) => rows2.push(r), score: (q, a) => scoreQuestion(q, "selftest", a, liveAsker) });
    check(rows2.length >= 1 && rows2.every((r) => !r.ordered && r.reason === "unconfigured" && r.calls === 0), "missing key: unconfigured, zero calls");
    check(r2.stopped?.startsWith("unconfigured"), "missing key: dispatch stops");
    check(net === 0, "no network call");
    // 3. The real NevIR file, when present: 2,766 questions, 1,383 pairs, two passages each.
    try {
      const all = loadNevir();
      check(all.length === 2766 && new Set(all.map((q) => q.pair)).size === 1383, "NevIR: 2,766 questions over 1,383 pairs");
      check(all.every((q) => q.passages.length === 2 && q.docs[0].endsWith("-d1") && q.docs[1].endsWith("-d2")), "NevIR: d1 then d2 for every question");
    } catch (err) {
      bad.push(`NevIR data: ${err.message}`);
    }
  } finally {
    globalThis.fetch = origFetch;
    if (hadKey) process.env.TYPESAFE_API_KEY = prev;
    else delete process.env.TYPESAFE_API_KEY;
  }
  for (const b of bad) console.log(`SELFTEST RED: ${b}`);
  console.log(bad.length ? "SELFTEST FAIL" : "SELFTEST PASS: id mapping, fixed passage order, no text in rows, keyless = unconfigured with 0 calls and a stop, NevIR shape");
  return bad.length ? 1 : 0;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const arg = process.argv[2];
  if (arg === "--selftest") process.exitCode = await selftest();
  else if (arg) process.exitCode = await live(arg);
  else {
    console.error(`usage: tool.mjs --selftest | ${RUNS.join(" | ")}`);
    process.exitCode = 2;
  }
}
