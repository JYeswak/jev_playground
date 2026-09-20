#!/usr/bin/env node
// emit.mjs — write ONE ruling-closure JSON at ruling time.
//
// CREATION GATE, answered:
//   1. CONSUMER — the ruling author, at ruling time; work/ruling-closure/project.mjs
//      (renders STATUS.tsv from closures); scripts/selftest-ruling-closure.sh
//      (stage 80 discovers it by glob — no new stage).
//   2. GATE — one JSON per ruling carrying verdict + receipt digest + falsifier +
//      pinned inputs + guard exit codes. Missing required field REFUSES (exit 2);
//      a closure that cannot name its evidence is not a closure.
//   3. DEFECT — OBSERVED, three same-turn-update failures plus one RED, all tonight:
//      STATUS.tsv fell behind its receipts three separate times (parallel hand-edits);
//      a digest pointed at a live file (NEGATIVE_EVIDENCE.md) and took the lane RED;
//      README counts went stale twice while the repository moved. Every one is a
//      consistency failure between parts of what should be one object (see
//      alignment-operating-model-20260920.md). Five hand-maintained artifacts
//      per ruling drift; one object per ruling cannot drift from itself.
//   4. RETIREMENT — when STATUS.tsv is generated from closures rather than edited
//      (project.mjs exists for exactly this); then emit is the only writer.
//
// WHAT IT DELIBERATELY DOES NOT DO: it does not judge the ruling (verdict is
// recorded, never second-guessed), and it does not fetch live sources — an
// as_of timestamp is asserted by the author for live-monotonic inputs, and a
// missing as_of on a --live-input REFUSES rather than guessing.
//
// Digest rule REUSED from scripts/lane-status.sh (never a second hashing rule):
// strip trailing whitespace bytes, sha256, first 16 hex.
//
// Usage:
//   node work/ruling-closure/emit.mjs --candidate C --rung N --verdict V --author A \
//     --receipt PATH --falsifier PATH --falsifier-sha S --falsifier-fired yes|no \
//     [--input PATH]... [--live-input PATH --as-of TS]... \
//     [--guard name=rc]... --out DIR
// Writes DIR/<candidate>.closure.json. Exit 0 wrote it; 2 refused.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

function normDigest(buf) {
  const stripped = buf.toString("utf8").replace(/\s+$/, "");
  return createHash("sha256").update(stripped, "utf8").digest("hex").slice(0, 16);
}

function fail(msg) {
  console.error(`emit: REFUSE — ${msg}`);
  process.exit(2);
}

const argv = process.argv.slice(2);
const get = (k) => {
  const i = argv.indexOf(k);
  return i === -1 ? null : argv[i + 1] ?? null;
};
const getAll = (k) => {
  const out = [];
  for (let i = 0; i < argv.length; i++) if (argv[i] === k && argv[i + 1]) out.push(argv[i + 1]);
  return out;
};

const candidate = get("--candidate");
const rung = get("--rung");
const verdict = get("--verdict");
const author = get("--author");
const receipt = get("--receipt");
const falsifier = get("--falsifier");
const falsifierSha = get("--falsifier-sha");
const fired = get("--falsifier-fired");
const outDir = get("--out") ?? "work/ruling-closure/closures";

for (const [name, v] of [["--candidate", candidate], ["--rung", rung],
    ["--verdict", verdict], ["--author", author], ["--receipt", receipt],
    ["--falsifier", falsifier], ["--falsifier-sha", falsifierSha],
    ["--falsifier-fired", fired]]) {
  if (!v) fail(`missing required ${name}`);
}
if (!["yes", "no"].includes(fired)) fail("--falsifier-fired must be yes|no");
if (!/^[1-5]$/.test(rung)) fail("--rung must be 1-5");

let receiptDigest;
try {
  receiptDigest = normDigest(readFileSync(receipt));
} catch {
  fail(`receipt unreadable: ${receipt}`);
}
const falsifierDigest = (() => {
  try { return normDigest(readFileSync(falsifier)); } catch { return null; }
})();
// Optional projection fields (for project.mjs → STATUS.tsv columns). Historical
// rows predate closures, so these default empty rather than fabricate.
for (const k of ["--score", "--blocked-on", "--concur", "--receipt-type"]) {
  const i = argv.indexOf(k);
  if (i !== -1 && !argv[i + 1]) fail(`${k} needs a value (pass "" explicitly for empty)`);
}
const score = get("--score") ?? "";
const blockedOn = get("--blocked-on") ?? "";
const concur = get("--concur") ?? "";
const receiptType = get("--receipt-type") ?? "measurement";
const inputs = [];
for (const p of getAll("--input")) {
  let d;
  try { d = normDigest(readFileSync(p)); } catch { fail(`input unreadable: ${p}`); }
  inputs.push({ path: p, sha: d, live: false, as_of: null });
}
const liveInputs = getAll("--live-input");
const asOf = get("--as-of");
if (liveInputs.length && !asOf) fail("--live-input without --as-of (live sources need timestamps, never guesses)");
for (const p of liveInputs) inputs.push({ path: p, sha: null, live: true, as_of: asOf });

const guards = {};
for (const g of getAll("--guard")) {
  const m = g.match(/^([a-z0-9_-]+)=(\d+)$/i);
  if (!m) fail(`--guard must be name=rc, got: ${g}`);
  guards[m[1]] = Number(m[2]);
}

const closure = {
  candidate, rung: Number(rung), verdict, author,
  score, blocked_on: blockedOn, concur, receipt_type: receiptType,
  receipt: { path: receipt, digest: receiptDigest },
  falsifier: { path: falsifier, commit_sha: falsifierSha, fired: fired === "yes", digest: falsifierDigest },
  inputs, guards,
  emitted_at: new Date().toISOString(),
};

mkdirSync(outDir, { recursive: true });
const dest = join(outDir, `${candidate}.closure.json`);
writeFileSync(dest, `${JSON.stringify(closure, null, 1)}\n`);
console.log(`emit: wrote ${dest}`);
