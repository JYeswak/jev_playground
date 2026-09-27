#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve } from "node:path";
import { askJevBundle } from "../../kit/src/client.ts";

const ROOT = resolve(new URL("../..", import.meta.url).pathname);
const PREREG = resolve(ROOT, "work/jev-41c6/prereg.md");
const REACH = resolve(ROOT, "work/jev-41c6/reachability.json");
const IDS = resolve(ROOT, "work/jev-oioo/h1-dev-items.jsonl");
const STATES = resolve(ROOT, "var/agent-tmp/jev-oioo/states.jsonl");
const BASELINE = resolve(ROOT, "work/jev-oioo/live-results.jsonl");
const OUT = resolve(ROOT, "work/jev-41c6/live-rows.jsonl");
const RECEIPT = resolve(ROOT, "work/jev-41c6/receipt.json");
const MODEL = "jev-1.13.0";
const RATE = 0.042;

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");
const text = async (path) => readFile(path, "utf8");
const parseJsonl = (value) => value.split("\n").filter(Boolean).map(JSON.parse);
const jsonl = (rows) => `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`;

function combination(n, k) {
  if (k < 0 || k > n) return 0n;
  k = Math.min(k, n - k);
  let out = 1n;
  for (let i = 1; i <= k; i += 1) out = (out * BigInt(n - k + i)) / BigInt(i);
  return out;
}

function exactMcNemarP(b, c) {
  const n = b + c;
  if (n === 0) return 1;
  const limit = Math.min(b, c);
  let numerator = 0n;
  for (let i = 0; i <= limit; i += 1) numerator += combination(n, i);
  const denominator = 1n << BigInt(n);
  return Math.min(1, (2 * Number(numerator)) / Number(denominator));
}

function usageFields(usage) {
  if (!usage || typeof usage !== "object") return null;
  const input = Number(usage.input_tokens);
  const output = Number(usage.output_tokens);
  if (!Number.isFinite(input) || !Number.isFinite(output)) return null;
  return { input_tokens: input, output_tokens: output };
}

function summarize(rows) {
  const valid = rows.filter((row) => row.h2_status === "scored" && row.baseline_status === "scored");
  const h2Correct = valid.filter((row) => row.h2_prediction === row.gold).length;
  const baselineCorrect = valid.filter((row) => row.baseline_prediction === row.gold).length;
  const h2Only = valid.filter((row) => row.h2_prediction === row.gold && row.baseline_prediction !== row.gold).length;
  const baselineOnly = valid.filter((row) => row.h2_prediction !== row.gold && row.baseline_prediction === row.gold).length;
  const p = exactMcNemarP(h2Only, baselineOnly);
  const invalid = rows.length - valid.length;
  const usage = rows.map((row) => row.usage).filter(Boolean);
const usageRows = rows.filter((row) => row.usage);
const usageComplete = usageRows.length === rows.length;
const inputTokens = usageRows.reduce((sum, item) => sum + item.usage.input_tokens, 0);
const outputTokens = usageRows.reduce((sum, item) => sum + item.usage.output_tokens, 0);
  return {
    requested: rows.length,
    valid_paired: valid.length,
    invalid: invalid,
    h2_correct: h2Correct,
    h2_accuracy: valid.length ? h2Correct / valid.length : null,
    baseline_correct: baselineCorrect,
    baseline_accuracy: valid.length ? baselineCorrect / valid.length : null,
    h2_only_correct: h2Only,
    baseline_only_correct: baselineOnly,
    mcnemar_exact_two_sided_p: p,
    refusal_rate: rows.length ? invalid / rows.length : null,
    pass_bar: valid.length > 0 && h2Correct > baselineCorrect && p < 0.05 && h2Only > baselineOnly && invalid / rows.length <= 0.05,
usage_complete: usageComplete,
usage_rows: usageRows.length,
usage_missing_rows: rows.length - usageRows.length,
input_tokens: inputTokens,
output_tokens: outputTokens,
spend_usd: inputTokens * RATE / 1_000_000,
  };
}

const preregBytes = await readFile(PREREG);
const idsBytes = await readFile(IDS);
const stateBytes = await readFile(STATES);
const reach = JSON.parse(await text(REACH));
const preregSha = sha256(preregBytes);
if (reach.prereg_sha256 !== preregSha) throw new Error("reach receipt does not bind current prereg");
if (reach.dev_id_manifest_sha256 !== sha256(idsBytes)) throw new Error("reach receipt does not bind ID manifest");
if (reach.state_source_sha256 !== sha256(stateBytes)) throw new Error("reach receipt does not bind state source");
if (reach.status !== "REACHABLE" || reach.mode !== "mcnemar") throw new Error("reach receipt is not REACHABLE/mcnemar");

const idRows = parseJsonl(idsBytes.toString("utf8"));
if (idRows.length !== 200 || new Set(idRows.map((row) => row.id)).size !== 200) throw new Error("expected 200 unique dev IDs");
const statesById = new Map(parseJsonl(stateBytes.toString("utf8")).map((row) => [row.id, row.state]));
const baselineById = new Map(parseJsonl(await text(BASELINE)).map((row) => [row.id, row]));
for (const item of idRows) {
  const state = statesById.get(item.id);
  const baseline = baselineById.get(item.id);
  if (!state || !Array.isArray(state.evidence) || state.evidence.length !== 5) throw new Error(`state missing five evidence sentences: ${item.id}`);
  if (Object.hasOwn(state, "label") || Object.hasOwn(state, "gold") || Object.hasOwn(state, "source_claim_id")) throw new Error(`gold leaked into state: ${item.id}`);
  if (!baseline || baseline.jev?.status !== "scored") throw new Error(`baseline missing: ${item.id}`);
}

const existing = await (async () => {
  try { return parseJsonl(await text(OUT)); } catch { return []; }
})();
const rowsById = new Map(existing.map((row) => [row.id, row]));
const questions = {};
for (let j = 0; j < 5; j += 1) {
  questions[`support_${j}`] = {
    type: "noul",
    instructions: `Does evidence sentence ${j} support the claim?`,
    criteria: {
      true: "The sentence states the claim or directly implies that it is true",
      false: "The sentence contradicts the claim or does not address what the claim asserts",
    },
  };
  questions[`contradict_${j}`] = {
    type: "noul",
    instructions: `Does evidence sentence ${j} contradict the claim?`,
    criteria: {
      true: "The sentence states information incompatible with the claim",
      false: "The sentence does not state information incompatible with the claim",
    },
  };
}

const orphanId = idRows[0].id;
const orphanBaseline = baselineById.get(orphanId);
rowsById.set(orphanId, { id: orphanId, gold: orphanBaseline.gold, baseline_status: orphanBaseline.jev.status, baseline_prediction: orphanBaseline.jev.supported ? "SUPPORTS" : "REFUTES", h2_status: "invalid", reason: "orphaned_api_call_lost_before_checkpoint_due_to_runner_validation_bug", orphaned_api_call: true, model: MODEL, usage: null, latency_ms: null });
for (const item of idRows) {
  if (rowsById.has(item.id)) continue;
  const baseline = baselineById.get(item.id);
  const state = statesById.get(item.id);
  const started = Date.now();
  const answer = await askJevBundle({ state, questions, model: MODEL, timeoutMs: 10000, retry: { maxRetries: 0 } });
  const row = {
    id: item.id,
    gold: baseline.gold,
    baseline_status: baseline.jev.status,
    baseline_prediction: baseline.jev.supported ? "SUPPORTS" : "REFUTES",
    h2_status: answer.ok ? "scored" : "invalid",
    latency_ms: answer.latencyMs ?? (Date.now() - started),
    model: answer.ok ? answer.model : MODEL,
    usage: answer.ok ? usageFields(answer.usage) : null,
  };
  if (answer.ok) {
    const scores = {};
    for (const [name, value] of Object.entries(answer.answers)) {
const raw = typeof value === "number" ? value : value && typeof value === "object" ? value.noul : undefined;
      if (typeof raw !== "number" || !Number.isFinite(raw) || raw < 0 || raw > 1) throw new Error(`validated answer escaped numeric bounds: ${item.id}/${name}`);
      scores[name] = raw;
    }
    const supportHit = [0, 1, 2, 3, 4].some((j) => scores[`support_${j}`] > 0.5);
    const contradictHit = [0, 1, 2, 3, 4].some((j) => scores[`contradict_${j}`] > 0.5);
    row.scores = scores;
    row.support_hit = supportHit;
    row.contradict_hit = contradictHit;
    row.h2_prediction = supportHit && !contradictHit ? "SUPPORTS" : "REFUTES";
  } else {
    row.error = answer.error;
    row.reason = answer.reason;
    if (["billing-hold"].includes(answer.reason) || /(?:401|402|403)/.test(answer.error ?? "")) {
      row.stop_reason = "hard_failure";
      rowsById.set(item.id, row);
      await writeFile(OUT, jsonl([...rowsById.values()]));
      throw new Error(`hard Jev failure on ${item.id}: ${answer.reason}`);
    }
  }
  rowsById.set(item.id, row);
  await writeFile(OUT, jsonl([...rowsById.values()]));
}

const rows = idRows.map((item) => rowsById.get(item.id));
const stats = summarize(rows);
const receipt = {
  status: stats.invalid === 0 ? "LIVE_COMPLETE" : "LIVE_COMPLETE_WITH_INVALID",
  created_at: new Date().toISOString(),
  model: MODEL,
  comparator: "none",
  prereg_sha256: preregSha,
  dev_id_manifest_sha256: sha256(idsBytes),
  state_source_sha256: sha256(stateBytes),
rows: rows.length,
orphaned_api_calls: rows.filter((row) => row.orphaned_api_call).map((row) => row.id),
  stats,
};
await writeFile(RECEIPT, `${JSON.stringify(receipt, null, 2)}\n`);
console.log(JSON.stringify(receipt, null, 2));
