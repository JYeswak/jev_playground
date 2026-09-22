#!/usr/bin/env node
// Riff on the official SDE-cascade cookbook. Keyless by default: a cheap
// extraction stands in (schema-valid but wrong), and recorded per-field Nouls
// stand in for the verify call. Escalation is driven by the per-field battery
// only; the holistic overall head is displayed, never used.
// NO-CLAIM: a fixture cascade is not a live verification.
import { verify, THRESHOLD } from "./verify.mjs";

const r = verify();
for (const h of r.heads) {
  console.log(`  ${h.field.padEnd(24)} p_wrong=${h.p.toFixed(2)} ${h.p >= THRESHOLD ? "ESCALATE" : "pass"}`);
}
console.log(`overall head: ${r.overall.toFixed(2)} (displayed, never gating)`);
console.log(`verdict: ${r.escalate ? `ESCALATE (${r.escalations.join(", ")})` : "accept"}`);
if (!r.escalate || !r.escalations.includes("location")) {
  console.error("MISS: wrong location field must escalate");
  process.exit(1);
}
