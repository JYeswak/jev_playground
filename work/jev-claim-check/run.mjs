// Live dogfood arm for bead jev-sp5. Drives the SHIPPED tool (.omp/tools/jev-claim-check.ts,
// default live asker) over every case in cases.jsonl, so the measured thing is the tool itself.
// Bar: docs/demos/upstream-repro/jev-claim-check-20260924.md, committed before this runs.
// Appends one row per case to rows.jsonl; a case that already has a verdict is not re-asked.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
//        node work/jev-claim-check/run.mjs
// Re-score with no key: python3 work/jev-claim-check/score.py
import { appendFileSync, existsSync, readFileSync } from "node:fs";
import mod from "../../.omp/tools/jev-claim-check.ts";

const HERE = new URL(".", import.meta.url);
const ROWS = new URL("rows.jsonl", HERE);
const VERDICTS = new Set(["supported", "unsupported", "unsure"]);

if (!process.env.TYPESAFE_API_KEY) {
  console.error("TYPESAFE_API_KEY unset: run under infisical run (see header). No call made.");
  process.exit(2);
}

const factory = typeof mod === "function" ? mod : mod.default;
const pi = { zod: { object: (s) => s, string: () => ({ min: () => ({}) }) } };
const tool = factory(pi);

const cases = readFileSync(new URL("cases.jsonl", HERE), "utf8").trim().split("\n").map((l) => JSON.parse(l));
const done = new Set();
if (existsSync(ROWS)) {
  for (const line of readFileSync(ROWS, "utf8").trim().split("\n").filter(Boolean)) {
    const r = JSON.parse(line);
    if (VERDICTS.has(r.verdict)) done.add(r.id);
  }
}

let failed = 0;
for (const c of cases) {
  if (done.has(c.id)) continue;
  const r = await tool.execute(c.id, { claim: c.claim, evidence: c.evidence });
  const d = r.details;
  const row = {
    id: c.id,
    truth: c.truth,
    verdict: d.verdict,
    probability: d.probability,
    confidence: d.confidence,
    reason: d.reason,
    latencyMs: d.latencyMs,
    usage: d.usage,
    at: new Date().toISOString(),
  };
  appendFileSync(ROWS, JSON.stringify(row) + "\n");
  if (!VERDICTS.has(d.verdict)) failed += 1;
  console.log(`${c.id}\t${d.verdict}\t${d.probability ?? "-"}`);
}
console.log(failed ? `${failed} case(s) without a verdict; rerun to resume` : "all cases answered");
process.exit(failed ? 3 : 0);
