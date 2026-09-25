#!/usr/bin/env node
// Readout 5's live pass (bead jev-pvdp): the current and candidate gate wordings on the same rows.
//
//   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
//     node --experimental-strip-types work/gate-question-gap/live-pass-5.mjs --live
//
// Per row, two Jev calls on the same state: (A) the hook's own observe(), so the current flag is
// exactly the hook's (five frozen nouls, jev-1.13.0, max > 0.5); (B) askJev with the candidate's two
// added nouls (candidate.mjs ADDED) and the hook's STATE_CONTEXT. The candidate flag is A's five
// scores and B's two, max > 0.5. The raw command comes from the sidecar, sha-verified.
// It refuses before any call unless `readout5.py ready` exits 0 (extract committed, labels and
// adjudication committed, power met), --live is given, and TYPESAFE_API_KEY is in the environment.
// Rows accumulate in flags-5.partial.jsonl so a stopped pass resumes; flags-5.jsonl and
// flags-5-pass.json are written only when every row has both calls scored.
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { appendFileSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const EXTRACT = join(HERE, "extract-5.jsonl");
const PARTIAL = join(HERE, "flags-5.partial.jsonl");
const FLAGS = join(HERE, "flags-5.jsonl");
const RECEIPT = join(HERE, "flags-5-pass.json");
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
  refuse("NOT_RUN: readout 5's live pass makes two Jev calls per extract row; rerun with --live under `infisical run` once `readout5.py ready` exits 0");
}
const keyStatus = spawnSync(
  "python3",
  [join(HERE, "../../scripts/key-status.py")],
  { encoding: "utf8", env: process.env },
);
if (keyStatus.status !== 0) {
  refuse(keyStatus.stdout.trim() || keyStatus.stderr.trim(), keyStatus.status ?? 2);
}
const ready = spawnSync("python3", [join(HERE, "readout5.py"), "ready"], { encoding: "utf8" });
if (ready.status !== 0) refuse(`REFUSED: ${ready.stdout.trim() || ready.stderr.trim()}`, 1);
const key = process.env.TYPESAFE_API_KEY;

const rows = readJsonl(EXTRACT);
const raw = new Map();
for (const r of readJsonl(SIDECAR)) {
  if (sha(r.cmd) === r.cmdSha && !raw.has(r.cmdSha)) raw.set(r.cmdSha, r.cmd);
}
const missing = rows.filter((r) => !raw.has(r.cmdSha)).map((r) => r.i);
if (missing.length) refuse(`REFUSED: ${missing.length} extract rows have no sha-verified sidecar command: ${missing.slice(0, 20)}`, 1);

const { observe, MODEL } = await import("../../.omp/hooks/post/jev-gate-observe.ts");
const { askJev } = await import("../../kit/src/client.ts");
const { ADDED, CUT, STATE_CONTEXT } = await import("./candidate.mjs");
const done = new Map((existsSync(PARTIAL) ? readJsonl(PARTIAL) : []).map((r) => [r.i, r]));
const started = new Date().toISOString();
const todo = rows.filter((r) => !done.has(r.i));
console.error(`live pass 5: ${todo.length} rows to score (2 calls each), ${done.size} resumed, model ${MODEL}`);
let stopped = null;
for (const r of todo) {
  const command = raw.get(r.cmdSha);
  let current = null;
  await observe(
    { toolName: "bash", input: { command } },
    { append: async (_p, line) => { current = JSON.parse(line); }, appendSidecar: async () => {}, session: r.session, keyResolver: async () => key },
  );
  if (!isScored(current)) {
    stopped = { i: r.i, call: "current", status: current?.status ?? "no-row", error: current?.error ?? null };
    break;
  }
  const added = await askJev({ state: { command, context: STATE_CONTEXT }, questions: ADDED, model: MODEL, timeoutMs: 20000, apiKey: key });
  if (!added.ok) {
    stopped = { i: r.i, call: "candidate", status: added.reason ?? "error", error: added.error ?? null };
    break;
  }
  const addedProbs = added.scores ?? {};
  const all = [...Object.values(current.probs ?? {}), ...Object.values(addedProbs)].map(Number);
  const row = {
    i: r.i,
    cmdSha: r.cmdSha,
    current_flag: current.flag,
    current_probs: current.probs,
    added_probs: addedProbs,
    candidate_flag: Math.max(...all) > CUT,
    tokens: {
      current: current.tokens ?? null,
      added: added.usage ?? null,
    },
  };
  appendFileSync(PARTIAL, JSON.stringify(row) + "\n");
  done.set(r.i, row);
}
const scored = rows.map((r) => done.get(r.i)).filter(Boolean);
const input = scored.reduce((s, r) => s + (r.tokens.current?.input_tokens ?? 0) + (r.tokens.added?.input_tokens ?? 0), 0);
const summary = { scored: scored.length, rows: rows.length, calls: scored.length * 2, input_tokens: input, spend_usd: +(input * USD_PER_M_INPUT / 1e6).toFixed(6) };
if (stopped) refuse(`STOPPED at row ${stopped.i} (${stopped.call}): ${stopped.status} ${stopped.error ?? ""}; ${JSON.stringify(summary)}; rerun resumes`, 1);
writeFileSync(FLAGS, scored.map((r) => JSON.stringify(r)).join("\n") + "\n");
writeFileSync(RECEIPT, JSON.stringify({ lane: "live", model: MODEL, started, finished: new Date().toISOString(), ...summary }, null, 2) + "\n");
console.log(JSON.stringify({ flags: FLAGS, receipt: RECEIPT, ...summary }));
