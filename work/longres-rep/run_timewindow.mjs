#!/usr/bin/env node
// Frozen 48-hour temporal replication. One request per row; SDK retries stay at zero.
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { askJevChoice } from "../../kit/src/client.ts";

const BASE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(BASE, "..", "..");
const CORPUS = join(BASE, "timewindow-corpus.json");
const OUT = join(BASE, "timewindow-rows.jsonl");
const CALIBRATION = join(ROOT, "work/jev-state-size/calibration-osworld-r3.tsv");
const MODEL = "jev-1.13.0";
const INPUT_USD_PER_MILLION = 0.042;
const SPEND_CAP_USD = 0.015;
const MAX_INPUT_TOKENS = Math.floor(SPEND_CAP_USD * 1_000_000 / INPUT_USD_PER_MILLION);
const MAX_CALLS = 200;
const TIMEOUT_MS = 20_000;
const FRAMING_RESERVE_BYTES = 128;
const INSTRUCTIONS = "This tool result just arrived. How should it be kept for the rest of the session?";
const CLASSES = {
  keep: "keep the full result: the task will need its specific details later",
  summarize: "keep only its gist: the general shape suffices; details will not be needed",
  drop: "discard it entirely: nothing in it will be needed again",
};

function compactBytes(value) {
  return Buffer.byteLength(JSON.stringify(value), "utf8");
}

function minimumBytesPerToken() {
  const lines = readFileSync(CALIBRATION, "utf8").trim().split("\n");
  const headers = lines[0].split("\t");
  const indexes = Object.fromEntries(headers.map((name, index) => [name, index]));
  const ratios = [];
  for (const line of lines.slice(1)) {
    const fields = line.split("\t");
    if (fields[indexes.outcome] !== "answered") continue;
    const tokens = Number(fields[indexes.input_tokens]);
    if (!Number.isFinite(tokens) || tokens <= 0) continue;
    const bytes = Number(fields[indexes.state_bytes]) + Number(fields[indexes.question_bytes]);
    if (Number.isFinite(bytes) && bytes > 0) ratios.push(bytes / tokens);
  }
  if (ratios.length === 0) throw new Error(`no answered calibration rows in ${CALIBRATION}`);
  return Math.min(...ratios);
}

function rowsFromCorpus(corpus) {
  if (corpus.status !== "READY") throw new Error(`corpus status is ${corpus.status}; refusing calls`);
  if (!Array.isArray(corpus.dev) || !Array.isArray(corpus.held) || corpus.dev.length !== 100 || corpus.held.length !== 100) {
    throw new Error("READY corpus must contain dev-100 and held-100");
  }
  const rows = [...corpus.dev, ...corpus.held];
  if (rows.length > MAX_CALLS) throw new Error(`corpus exceeds ${MAX_CALLS} calls`);
  const ids = new Set();
  for (const row of rows) {
    if (typeof row.sample_id !== "string" || ids.has(row.sample_id)) throw new Error("missing or duplicate sample_id");
    if (typeof row.head !== "string" || typeof row.tail !== "string" || typeof row.task !== "string") {
      throw new Error(`missing compact prompt fields for ${row.sample_id}`);
    }
    ids.add(row.sample_id);
  }
  return rows;
}

function stateFor(row) {
  return {
    result_head: row.head,
    result_tail: row.tail,
    task: row.task.slice(0, 500),
  };
}

function estimatedTokens(row, bytesPerToken) {
  const state = stateFor(row);
  const question = { instructions: INSTRUCTIONS, classes: CLASSES };
  const bytes = compactBytes(state) + compactBytes(question) + FRAMING_RESERVE_BYTES;
  return Math.ceil(bytes / bytesPerToken);
}

function loadCheckpoint(rows) {
  const expected = new Map(rows.map((row) => [row.sample_id, row]));
  const done = new Map();
  if (!existsSync(OUT)) return done;
  for (const [index, line] of readFileSync(OUT, "utf8").split("\n").entries()) {
    if (!line.trim()) continue;
    let record;
    try {
      record = JSON.parse(line);
    } catch {
      throw new Error(`invalid checkpoint JSON at line ${index + 1}; refusing a duplicate request`);
    }
    const sample = expected.get(record?.sample_id);
    if (!sample || record.model !== MODEL || record.source_path_sha256 !== sample.source_path_sha256 || record.full_result_sha256 !== sample.full_result_sha256) {
      throw new Error(`checkpoint row ${index + 1} does not match the pinned corpus`);
    }
    if (done.has(record.sample_id)) throw new Error(`duplicate checkpoint sample ${record.sample_id}`);
    done.set(record.sample_id, record);
  }
  return done;
}

function usageTokens(record) {
  const tokens = record?.usage?.input_tokens;
  return Number.isSafeInteger(tokens) && tokens >= 0 ? tokens : null;
}

let corpus;
try {
  corpus = JSON.parse(readFileSync(CORPUS, "utf8"));
} catch {
  throw new Error("frozen corpus is not valid JSON");
}
const rows = rowsFromCorpus(corpus);
const bytesPerToken = minimumBytesPerToken();
const estimates = new Map(rows.map((row) => [row.sample_id, estimatedTokens(row, bytesPerToken)]));
const estimatedTotal = [...estimates.values()].reduce((sum, tokens) => sum + tokens, 0);
if (estimatedTotal > MAX_INPUT_TOKENS) {
  throw new Error(`calibrated input-token upper estimate ${estimatedTotal} exceeds spend cap ${MAX_INPUT_TOKENS}`);
}

const mode = process.argv.slice(2);
if (mode.length === 1 && mode[0] === "--preflight") {
  console.log(JSON.stringify({
    status: "READY",
    model: MODEL,
    rows: rows.length,
    calls_cap: MAX_CALLS,
    estimated_input_tokens: estimatedTotal,
    estimated_spend_usd: Number((estimatedTotal * INPUT_USD_PER_MILLION / 1_000_000).toFixed(6)),
    spend_cap_usd: SPEND_CAP_USD,
    timeout_ms: TIMEOUT_MS,
    retries: 0,
  }));
  process.exit(0);
}
if (mode.length !== 1 || mode[0] !== "--live") {
  throw new Error("use --preflight for keyless checks or --live for the bounded live run");
}

const done = loadCheckpoint(rows);
let reservedTokens = 0;
for (const row of rows) {
  const previous = done.get(row.sample_id);
  if (!previous) continue;
  reservedTokens += usageTokens(previous) ?? estimates.get(row.sample_id);
}
if (reservedTokens > MAX_INPUT_TOKENS) throw new Error("checkpointed usage exceeds spend cap");
console.log(`rows=${rows.length} done=${done.size} estimate_tokens=${estimatedTotal}`); // ubs:ignore — aggregate counts and estimates only; no request state or user text

for (let index = 0; index < rows.length; index++) {
  const row = rows[index];
  if (done.has(row.sample_id)) continue;
  const estimate = estimates.get(row.sample_id);
  const remaining = rows.slice(index).reduce(
    (sum, candidate) => sum + (done.has(candidate.sample_id) ? 0 : estimates.get(candidate.sample_id)),
    0,
  );
  if (reservedTokens + remaining > MAX_INPUT_TOKENS) {
    console.error(`STOP spend preflight: reserved=${reservedTokens} remaining_estimate=${remaining}`);
    process.exitCode = 4;
    break;
  }

  const base = {
    sample_id: row.sample_id,
    source_path_sha256: row.source_path_sha256,
    full_result_sha256: row.full_result_sha256,
    model: MODEL,
  };
  let result;
  try {
    result = await askJevChoice({
      model: MODEL,
      state: stateFor(row),
      instructions: INSTRUCTIONS,
      classes: CLASSES,
      timeoutMs: TIMEOUT_MS,
    });
  } catch {
    const record = { ...base, status: "throw", pred: "keep", latencyMs: null };
    appendFileSync(OUT, `${JSON.stringify(record)}\n`, "utf8");
    done.set(row.sample_id, record);
    reservedTokens += estimate;
    console.error("STOP: request threw; checkpointed KEEP and did not retry");
    process.exitCode = 3;
    break;
  }
  let record;
  if (!result.ok) {
    record = { ...base, status: result.reason, pred: "keep", latencyMs: result.latencyMs };
  } else if (result.model !== MODEL) {
    record = { ...base, status: "model-mismatch", pred: "keep", latencyMs: result.latencyMs };
  } else {
    record = {
      ...base,
      status: "scored",
      choice: result.choice,
      probabilities: result.probabilities,
      confidence: result.confidence,
      latencyMs: result.latencyMs,
      ...(result.usage ? { usage: result.usage } : {}),
    };
  }
  appendFileSync(OUT, `${JSON.stringify(record)}\n`, "utf8");
  done.set(row.sample_id, record);
  reservedTokens += usageTokens(record) ?? estimate;

  const failure = !result.ok ? `${result.reason} ${result.error}` : "";
  if (!result.ok && (failure.includes("401") || failure.includes("402") || failure.includes("403"))) {
    console.error(`STOP authorization/billing: ${result.reason}`);
    process.exitCode = 3;
    break;
  }
  if (!result.ok && result.reason === "unconfigured") {
    console.error("STOP: no Jev API key configured; no further requests");
    process.exitCode = 3;
    break;
  }
  if (record.status === "model-mismatch") {
    console.error("STOP: response model did not match the pinned model");
    process.exitCode = 3;
    break;
  }
}
console.log(`checkpoint_rows=${done.size} reserved_input_tokens=${reservedTokens}`); // ubs:ignore — aggregate counts and actual usage only; no request state or user text
