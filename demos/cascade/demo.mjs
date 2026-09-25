#!/usr/bin/env node
// Riff on the official SDE-cascade cookbook. Keyless by default: a cheap
// extraction stands in (schema-valid but wrong), and recorded per-field Nouls
// stand in for the verify call. Escalation is driven by the per-field battery
// only; the holistic overall head is displayed, never used.
// `node demos/cascade/demo.mjs --live` runs the cookbook's verify battery in
// one request (per-field Nouls plus the overall judge head) through
// work/jev-client, model jev-1.13.0.
// NO-CLAIM: a fixture cascade is not a live verification.
import { verify, THRESHOLD } from "./verify.mjs";

const live = process.argv.includes("--live");
let r = null;
if (live) {
  const { askJevBundle } = await import("../../kit/src/client.ts");
  const { FIELDS } = await import("./verify.mjs");
  const questions = {
    "__overall__::judge": {
      type: "noul",
      instructions: "Should this extracted record be escalated for human review?",
    },
  };
  for (const f of FIELDS) {
    questions[f.path] = {
      type: "noul",
      instructions: `Is the extracted ${f.path} '${f.value}' wrong against its spec (${f.spec})? Answer true when wrong.`,
    };
  }
  const res = await askJevBundle({
    model: "jev-1.13.0",
    state: { record: Object.fromEntries(FIELDS.map((f) => [f.path, f.value])) },
    questions,
    timeoutMs: 20000,
  });
  if (!res.ok) {
    console.error(`live call failed: ${res.reason} ${res.error}`);
    process.exit(2);
  }
  const heads = FIELDS.map((f) => ({ field: f.path, p: res.answers[f.path].noul }));
  const overall = res.answers["__overall__::judge"].noul;
  const escalations = heads.filter((h) => h.p >= THRESHOLD).map((h) => h.field);
  r = { heads, overall, escalate: escalations.length > 0, escalations };
} else {
  r = verify();
}
for (const h of r.heads) {
  console.log(`  ${h.field.padEnd(24)} p_wrong=${h.p.toFixed(2)} ${h.p >= THRESHOLD ? "ESCALATE" : "pass"}`);
}
console.log(`overall head: ${r.overall.toFixed(2)} (displayed, never gating)`);
console.log(`verdict: ${r.escalate ? `ESCALATE (${r.escalations.join(", ")})` : "accept"}`);
if (!r.escalate || !r.escalations.includes("location")) {
  console.error("MISS: wrong location field must escalate");
  process.exit(1);
}
