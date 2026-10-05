import { readFileSync, appendFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { createHash } from "node:crypto";
import { join } from "node:path";
import { askJev } from "../../kit/src/client.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

const ROOT = "/Users/josh/Developer/jev";
const STATE = join(homedir(), ".local/state/jev");
const MODEL = "jev-1.13.0";
const CUT = 0.5;
const CAP = 291;
const OUT = join(ROOT, "work/jev-li3w/rows.jsonl");
const FROZEN = join(ROOT, "work/jev-li3w/frozen-pairs.jsonl");
const MISSING = join(ROOT, "work/jev-li3w/not-run.jsonl");
const INPUT = "Memory: `memory`. Current request: `prompt`. Is this memory relevant to the current request?";
const main = readFileSync(join(STATE, "memory-filter.jsonl"), "utf8").split("\n").filter(Boolean).map(JSON.parse);
const counts = new Map();
for (const row of main) if (row.status === "scored" && ["drop", "keep"].includes(row.decision)) {
  const key = `${row.promptHash}:${row.memoryHash}`;
  counts.set(key, (counts.get(key) ?? 0) + 1);
}
const sourcePairs = [...counts].filter(([, n]) => n >= 2).map(([key]) => key).sort();
if (sourcePairs.length !== 126) throw new Error(`repeat census mismatch: ${sourcePairs.length}`);
const payloads = new Map();
for (const line of readFileSync(join(STATE, "memory-filter-full.jsonl"), "utf8").split("\n")) {
  if (!line) continue;
  const row = JSON.parse(line);
  if (row.schema !== "jev-memory-filter-full.v1" || typeof row.prompt !== "string" || typeof row.memory !== "string") continue;
  const key = `${row.promptHash}:${row.memoryHash}`;
  if (sourcePairs.includes(key) && !payloads.has(key)) payloads.set(key, row);
}
for (const key of payloads.keys()) {
  const { promptHash, memoryHash, prompt, memory } = payloads.get(key);
  const sha = (text) => createHash("sha256").update(text, "utf8").digest("hex");
  if (sha(prompt) !== promptHash || sha(memory) !== memoryHash) throw new Error("payload hash mismatch");
}
const pairs = sourcePairs.filter((key) => payloads.has(key));
const missing = sourcePairs.filter((key) => !payloads.has(key));
if (pairs.length !== 97 || missing.length !== 29 || pairs.length * 3 !== CAP) throw new Error(`payload coverage mismatch: ${pairs.length}/${sourcePairs.length}`);
if (process.argv.includes("--freeze")) {
  const encode = (key) => { const [promptHash, memoryHash] = key.split(":"); return JSON.stringify({ promptHash, memoryHash }); };
  writeFileSync(FROZEN, pairs.map(encode).join("\n") + "\n");
  writeFileSync(MISSING, missing.map((key) => JSON.stringify({ ...JSON.parse(encode(key)), status: "NOT_RUN", reason: "No exact prompt/memory payload row in memory-filter-full.v1" })).join("\n") + "\n");
  console.log(JSON.stringify({ frozenPairs: pairs.length, notRunPairs: missing.length, requestsMax: CAP }));
  process.exit(0);
}
const frozen = readFileSync(FROZEN, "utf8").split("\n").filter(Boolean).map(JSON.parse).map((r) => `${r.promptHash}:${r.memoryHash}`);
if (JSON.stringify(frozen) !== JSON.stringify(pairs)) throw new Error("available payload set differs from committed frozen set");
if (readFileSync(OUT, "utf8").trim()) throw new Error("result ledger is not empty");
let calls = 0, inputTokens = 0;
for (const key of pairs) {
  const { promptHash, memoryHash, prompt, memory } = payloads.get(key);
  for (let round = 1; round <= 3; round++) {
    if (calls >= CAP) throw new Error("hard call cap reached");
    const result = await askJev({ state: { prompt, memory }, questions: { rel: { instructions: INPUT } }, model: MODEL, timeoutMs: 15000 });
    calls++;
    if (!result.ok) {
      const auth = /HTTP (401|402|403)/.exec(result.error);
      appendFileSync(OUT, JSON.stringify({ promptHash, memoryHash, round, status: "error", errorClass: result.reason, authStatus: auth?.[1] ?? null, model: result.model, latencyMs: result.latencyMs, inputTokens: null }) + "\n", { mode: 0o600 });
      console.log(JSON.stringify({ calls, round, status: "error", errorClass: result.reason, authStatus: auth?.[1] ?? null }));
      if (auth) process.exit(2);
      process.exit(1);
    }
    const noul = result.scores.rel;
    const row = { promptHash, memoryHash, round, status: "scored", noul, decision: noul < CUT ? "drop" : "keep", model: result.model, latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null };
    appendFileSync(OUT, JSON.stringify(row) + "\n", { mode: 0o600 });
    inputTokens += result.usage?.input_tokens ?? 0;
    console.log(JSON.stringify({ calls, round, status: row.status, model: row.model, latencyMs: row.latencyMs, inputTokens: row.inputTokens }));
  }
}
console.log(JSON.stringify({ calls, inputTokens, spendUsd: inputTokens * 0.042 / 1000000, cap: CAP }));
