#!/usr/bin/env node
/**
 * two-bit.mjs — admissibility gate before any new Jev seat is measured.
 *
 * Bit 1: is the label a function of the literal input tokens?
 * Bit 2: does a constant policy (always-keep, always-mid-tier, always-allow) score well?
 * A judge has a seat only when both are NO.
 *
 * Usage: node two-bit.mjs --candidate <name> [--registry <path>]
 * Exit 0: admitted (both NO). Exit 2: refused (either YES, or candidate
 * unknown/unset — refused, not measured). Exit 1: usage/registry error.
 */
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
function flag(name) {
  const i = args.indexOf(name);
  return i >= 0 && i + 1 < args.length ? args[i + 1] : null;
}

const candidate = flag("--candidate");
const registryPath =
  flag("--registry") ??
  resolve(dirname(fileURLToPath(import.meta.url)), "candidates.json");

if (!candidate) {
  console.error("usage: node two-bit.mjs --candidate <name> [--registry <path>]");
  process.exit(1);
}

let registry;
try {
  registry = JSON.parse(readFileSync(registryPath, "utf8"));
} catch (err) {
  console.error(`registry unreadable: ${registryPath}: ${err.message}`);
  process.exit(1);
}
if (!Array.isArray(registry)) {
  console.error("registry malformed: top level must be an array");
  process.exit(1);
}

const row = registry.find((r) => r?.name === candidate);
if (!row) {
  console.log(`candidate=${candidate} bit1=UNSET bit2=UNSET verdict=REFUSED (not in registry; record both bits, do not measure)`);
  process.exit(2);
}

for (const bit of ["bit1", "bit2"]) {
  if (row[bit] !== "YES" && row[bit] !== "NO") {
    console.log(`candidate=${candidate} ${bit}=${row[bit] ?? "UNSET"} verdict=REFUSED (bit unset; record it, do not measure)`);
    process.exit(2);
  }
}

console.log(`candidate=${candidate} bit1=${row.bit1} bit2=${row.bit2}`);
console.log(`evidence=${row.evidence ?? "(none recorded)"}`);
if (row.note) console.log(`note=${row.note}`);
if (row.bit1 === "NO" && row.bit2 === "NO") {
  console.log("verdict=ADMITTED (to measurement only; not certified)");
  process.exit(0);
}
console.log("verdict=REFUSED (no Jev seat; ship the cheap thing)");
process.exit(2);
