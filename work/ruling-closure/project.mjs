#!/usr/bin/env node
// project.mjs — render STATUS.tsv rows from ruling closures, with verification.
//
// Verifies every closure before rendering: receipt digest recomputed (same
// norm rule as emit/lane-status), live-monotonic inputs must carry as_of.
// Any violation REFUSES (exit 2) — a projection that passes a broken closure
// is the laundering this instrument exists to prevent.
//
// Diff mode (--diff STATUS.tsv) compares coverage WITHOUT rewriting: rows in
// the committed file with no closure are reported, never fabricated. Rows
// predating closures are history's finding, not a bug to paper over.
// --strict-diff turns uncovered rows into exit 2 (for the selftest arm).
//
// Usage:
//   node work/ruling-closure/project.mjs --dir DIR [--out rendered.tsv]
//     [--diff STATUS.tsv] [--strict-diff]
// Exit 0 rendered (report on stdout); 2 verification/diff failure.
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

function normDigest(buf) {
  const stripped = buf.toString("utf8").replace(/\s+$/, "");
  return createHash("sha256").update(stripped, "utf8").digest("hex").slice(0, 16);
}

function fail(msg) {
  console.error(`project: REFUSE — ${msg}`);
  process.exit(2);
}

const argv = process.argv.slice(2);
const get = (k) => {
  const i = argv.indexOf(k);
  return i === -1 ? null : argv[i + 1] ?? null;
};
const dir = get("--dir") ?? "work/ruling-closure/closures";
const out = get("--out");
const diffPath = get("--diff");
const strict = argv.includes("--strict-diff");

let files;
try {
  files = readdirSync(dir).filter((f) => f.endsWith(".closure.json")).sort();
} catch {
  fail(`closures dir unreadable: ${dir}`);
}
if (!files.length) fail(`no closures in ${dir} — an empty projection is not a pass`);

const rows = [];
for (const f of files) {
  let c;
  try { c = JSON.parse(readFileSync(join(dir, f), "utf8")); }
  catch { fail(`closure unparseable: ${f}`); }
  for (const k of ["candidate", "rung", "verdict", "author", "receipt"]) {
    if (c[k] === undefined || c[k] === null || c[k] === "") fail(`${f}: missing ${k}`);
  }
  let fresh;
  try { fresh = normDigest(readFileSync(c.receipt.path)); }
  catch { fail(`${f}: receipt unreadable: ${c.receipt.path}`); }
  if (fresh !== c.receipt.digest) {
    fail(`${f}: digest disagrees with receipt ${c.receipt.path} (closure ${c.receipt.digest} vs fresh ${fresh})`);
  }
  for (const inp of c.inputs ?? []) {
    if (inp.live && !inp.as_of) fail(`${f}: live-monotonic input without as_of: ${inp.path}`);
  }
  rows.push([c.candidate, String(c.rung ?? ""), String(c.score ?? ""),
    c.verdict, c.author, c.receipt.path, c.blocked_on ?? "",
    c.concur ?? "", c.receipt.digest, c.receipt_type ?? ""].join("\t"));
}

const rendered = `${rows.join("\n")}\n`;
if (out) writeFileSync(out, rendered);

let uncovered = [];
if (diffPath) {
  const have = new Set(rows.map((r) => r.split("\t")[0]));
  const committed = readFileSync(diffPath, "utf8").split("\n")
    .map((l) => l.split("\t")[0])
    .filter((c) => c && !c.startsWith("#") && c !== "candidate");
  uncovered = committed.filter((c) => !have.has(c));
  const extra = [...have].filter((c) => !committed.includes(c));
  console.log(`project: ${rows.length} closure(s) render; ${committed.length} committed row(s); uncovered (no closure): ${uncovered.length}${uncovered.length ? ` [${uncovered.join(", ")}]` : ""}; closures beyond committed file: ${extra.length}${extra.length ? ` [${extra.join(", ")}]` : ""}`);
} else {
  console.log(`project: ${rows.length} closure(s) rendered`);
}
if (strict && uncovered.length) fail(`${uncovered.length} committed row(s) without closure: ${uncovered.join(", ")}`);
