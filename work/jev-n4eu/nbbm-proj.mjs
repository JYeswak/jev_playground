// nbbm-verify projection: prerule match rate over recent gate-observe commands.
import { readFileSync } from "node:fs";
import { matchPrerule } from "/Users/josh/Developer/jev/.omp/hooks/post/jev-gate-observe.ts";

const rows = readFileSync("/Users/josh/.local/state/jev/gate-observe.jsonl", "utf8")
  .trim().split("\n").map((l) => JSON.parse(l));
const cmds = new Map();
for (const r of rows) {
  if (typeof r.cmd !== "string" || !r.cmd) continue;
  if (!cmds.has(r.cmd)) cmds.set(r.cmd, r.ts);
}
const now = Date.now();
const in24 = [...cmds.keys()].filter((c) => {
  const t = Date.parse(cmds.get(c));
  return now - t < 24 * 3600 * 1000;
});
const in7d = [...cmds.keys()].filter((c) => {
  const t = Date.parse(cmds.get(c));
  return now - t < 7 * 24 * 3600 * 1000;
});
const m24 = in24.filter((c) => matchPrerule(c) !== null);
const m7 = in7d.filter((c) => matchPrerule(c) !== null);
console.log(JSON.stringify({
  uniqueCmds: cmds.size, cmds24h: in24.length, cmds7d: in7d.length,
  matches24h: m24.length, matches7d: m7.length,
  perDay7d: (m7.length / 7).toFixed(2),
  matched: m7.slice(0, 10).map((c) => c.slice(0, 80)),
}));
