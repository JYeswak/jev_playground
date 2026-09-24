#!/usr/bin/env node
// Readout 4's live gate pass (bead jev-9afl): score every extract-4 row with the hook's own observe().
//
//   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
//     node --experimental-strip-types work/gate-observe-dogfood/live-pass-4.mjs --live
//
// The flag is the hook's own: observe() from .omp/hooks/post/jev-gate-observe.ts, the same five
// frozen nouls, jev-1.13.0, and the same cut, fed the raw command from the sidecar (sha-verified
// against the extract). observe()'s log row goes to memory, and its sidecar append is a no-op.
// Without --live, or without TYPESAFE_API_KEY in the environment, it prints NOT_RUN and exits 2
// before any call; the key is read from the environment only, never from infisical by this script.
// Scored rows accumulate in flags-4.partial.jsonl, so a pass stopped by a 402 resumes without
// re-spending. flags-4.jsonl and flags-4-pass.json are written only when every row is scored.
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const EXTRACT = join(HERE, "extract-4.jsonl");
const PARTIAL = join(HERE, "flags-4.partial.jsonl");
const FLAGS = join(HERE, "flags-4.jsonl");
const RECEIPT = join(HERE, "flags-4-pass.json");
const SIDECAR = join(homedir(), ".local/state/jev/gate-observe-full.jsonl");
const USD_PER_M_INPUT = 0.042; // docs-mirror/typesafe/models.md: input tokens only, output free

const readJsonl = (path) => readFileSync(path, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const sha = (text) => createHash("sha256").update(text, "utf8").digest("hex");
const isScored = (row) => Boolean(row) && row.status === "scored";

function refuse(message, code = 2) {
  console.log(message);
  process.exit(code);
}

if (!process.argv.includes("--live")) {
  refuse("NOT_RUN: readout 4's live pass makes one Jev call per extract row; rerun with --live under `infisical run` to spend");
}
const key = process.env.TYPESAFE_API_KEY;
if (!key) {
  refuse("NOT_RUN reason=unconfigured: TYPESAFE_API_KEY is not in the environment (run under `infisical run --projectId=...`)");
}
if (existsSync(FLAGS)) refuse("REFUSED: flags-4.jsonl already exists; a second pass would overwrite the measured one", 1);

const rows = readJsonl(EXTRACT);
const raw = new Map();
for (const r of readJsonl(SIDECAR)) {
  if (sha(r.cmd) === r.cmdSha && !raw.has(r.cmdSha)) raw.set(r.cmdSha, r.cmd);
}
const missing = rows.filter((r) => !raw.has(r.cmdSha)).map((r) => r.i);
if (missing.length) refuse(`REFUSED: ${missing.length} extract rows have no sha-verified sidecar command: ${missing.slice(0, 20)}`, 1);

const { observe, MODEL } = await import("../../.omp/hooks/post/jev-gate-observe.ts");
const done = new Map((existsSync(PARTIAL) ? readJsonl(PARTIAL) : []).map((r) => [r.i, r]));
const started = new Date().toISOString();
const todo = rows.filter((r) => !done.has(r.i));
console.error(`live pass: ${todo.length} to score, ${done.size} resumed, model ${MODEL}`);
let stopped = null;
for (const r of todo) {
  let got = null;
  await observe(
    { toolName: "bash", input: { command: raw.get(r.cmdSha) } },
    {
      append: async (_path, line) => { got = JSON.parse(line); },
      appendSidecar: async () => {},
      session: r.session,
      keyResolver: async () => key,
    },
  );
  if (!isScored(got)) {
    stopped = { i: r.i, status: got?.status ?? "no-row", error: got?.error ?? null };
    break; // a 402 or any other failure stops the pass; the billing hold would refuse the rest anyway
  }
  const row = { i: r.i, cmdSha: r.cmdSha, status: got.status, flag: got.flag, probs: got.probs, latencyMs: got.latencyMs, tokens: got.tokens };
  appendFileSync(PARTIAL, JSON.stringify(row) + "\n");
  done.set(r.i, row);
}
const scored = rows.map((r) => done.get(r.i)).filter(Boolean);
const input = scored.reduce((s, r) => s + (r.tokens?.input_tokens ?? 0), 0);
const output = scored.reduce((s, r) => s + (r.tokens?.output_tokens ?? 0), 0);
const summary = { scored: scored.length, rows: rows.length, input_tokens: input, output_tokens: output, spend_usd: +(input * USD_PER_M_INPUT / 1e6).toFixed(6) };
if (stopped) refuse(`STOPPED at row ${stopped.i}: ${stopped.status} ${stopped.error ?? ""}; ${JSON.stringify(summary)}; rerun resumes from ${PARTIAL}`, 1);
writeFileSync(FLAGS, scored.map((r) => JSON.stringify(r)).join("\n") + "\n");
writeFileSync(RECEIPT, JSON.stringify({ lane: "live", model: MODEL, started, finished: new Date().toISOString(), ...summary, flagged: scored.filter((r) => r.flag).length }, null, 2) + "\n");
console.log(JSON.stringify({ flags: FLAGS, receipt: RECEIPT, ...summary }));
