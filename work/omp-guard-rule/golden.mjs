#!/usr/bin/env node
// golden.mjs — replay the guard handler over the pinned fixture and compare.
//
// Volatile fields are scrubbed at replay (timestamp -> [TIMESTAMP],
// toolCallId -> [ID]), so the golden is exact over SHAPE AND classes.
// Live counts get structural treatment elsewhere; this file is exact by
// design. UPDATE_GOLDENS=1 regenerates golden-output.jsonl; otherwise the
// replayed output must byte-match it (git diff is the review gate; CI
// never auto-updates). See PROVENANCE.md.
import { readFileSync, writeFileSync } from "node:fs";

const FIXTURE = "work/omp-guard-rule/fixtures/session-pinned.jsonl";
const GOLDEN = "work/omp-guard-rule/golden-output.jsonl";

const { default: guardRule } = await import("./guard-rule.ts");
const rows = [];
let handler;
guardRule({ on: (ev, h) => { handler = h; }, appendEntry: async (t, r) => rows.push({ t, ...r }) }, {});

for (const line of readFileSync(FIXTURE, "utf8").split("\n")) {
  if (!line.trim()) continue;
  const ev = JSON.parse(line);
  await handler({ toolName: ev.toolName, toolCallId: ev.toolCallId, input: ev.input }, {});
}

const scrubbed = rows.map((r) => {
  const o = { ...r };
  if (o.timestamp) o.timestamp = "[TIMESTAMP]";
  if (o.toolCallId) o.toolCallId = "[ID]";
  return o;
});
const text = `${scrubbed.map((r) => JSON.stringify(r)).join("\n")}\n`;

if (process.env.UPDATE_GOLDENS === "1") {
  writeFileSync(GOLDEN, text);
  console.log(`golden: regenerated ${GOLDEN} (${scrubbed.length} rows)`);
  process.exit(0);
}

let expected;
try {
  expected = readFileSync(GOLDEN, "utf8");
} catch {
  console.error(`golden: MISSING ${GOLDEN} — run with UPDATE_GOLDENS=1 once, review the diff, commit it`);
  process.exit(2);
}
if (expected !== text) {
  console.error("golden: MISMATCH — replay output differs from frozen golden. git diff is the review gate; regenerate only deliberately with UPDATE_GOLDENS=1.");
  process.exit(3);
}
console.log(`golden: EXACT (${scrubbed.length} rows byte-match)`);
