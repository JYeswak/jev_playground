// cap3-tokens.mjs (jev-8c09): reproducible memory-tokens-per-turn measurement.
// Joins sidecar memory TEXT with main-log prune status on
// (instance, promptHash, memoryHash): enforced/cap3-pruned -> cut, else got.
// Usage: node work/jev-i20b/cap3-tokens.mjs <startISO> <endISO>
// Env overrides: JEV_MEMORY_FILTER_LOG_PATH / JEV_MEMORY_FILTER_SIDECAR_PATH.
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const [start, end] = process.argv.slice(2);
if (!start || !end) {
  console.error("usage: node work/jev-i20b/cap3-tokens.mjs <startISO> <endISO>");
  process.exit(2);
}
const mainPath = process.env.JEV_MEMORY_FILTER_LOG_PATH
  ?? join(homedir(), ".local", "state", "jev", "memory-filter.jsonl");
const fullPath = process.env.JEV_MEMORY_FILTER_SIDECAR_PATH
  ?? join(homedir(), ".local", "state", "jev", "memory-filter-full.jsonl");

const rowsOf = (p) => readFileSync(p, "utf8").split("\n")
  .filter(Boolean).map((l) => JSON.parse(l));

const main = new Map();
for (const r of rowsOf(mainPath)) {
  const ts = r.ts ?? "";
  if (ts < start || ts >= end) continue;
  main.set([r.instance, r.promptHash, r.memoryHash].join("\n"), r.status);
}
const turns = new Map();
for (const r of rowsOf(fullPath)) {
  const ts = r.ts ?? "";
  if (ts < start || ts >= end) continue;
  const t = Math.floor(((r.memory ?? "").length) / 4);
  const key = [r.instance, r.promptHash].join("\n");
  const st = main.get([r.instance, r.promptHash, r.memoryHash].join("\n")) ?? r.status;
  const slot = turns.get(key) ?? { got: 0, cut: 0 };
  if (st === "enforced" || st === "cap3-pruned" || r.decision === "prune") slot.cut += t;
  else slot.got += t;
  turns.set(key, slot);
}
let got = 0, cut = 0;
for (const v of turns.values()) { got += v.got; cut += v.cut; }
const out = {
  window: `${start}..${end}`,
  turns: turns.size,
  received: got,
  per_turn: turns.size ? Math.round((got / turns.size) * 10) / 10 : 0,
  cut,
};
console.log(JSON.stringify(out));
