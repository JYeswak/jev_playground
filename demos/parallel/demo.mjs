#!/usr/bin/env node
// Riff on the official parallel-questions cookbook. Keyless by default: one
// short document plus four recorded answers stand in for the 13-question
// briefing over the GDPR article. Prints the whole briefing from one fixture
// request object — batching changes cost and speed, not answers.
// NO-CLAIM: a fixture briefing is not a live judgment.
import { DOC, QUESTIONS, brief } from "./brief.mjs";

console.log(DOC);
console.log(`\n-- one request, ${Object.keys(QUESTIONS).length} questions`);
let failed = 0;
for (const row of brief()) {
  const a = row.answer;
  const shown = a.type === "noul" ? `noul=${a.noul}`
    : a.type === "choice" ? `choice=${a.choice} p=${a.probabilities[a.choice]}`
    : `score=${a.score} conf=${a.confidence}`;
  console.log(`  ${row.id.padEnd(14)} [${row.type}] ${shown}`);
  if (a === undefined) failed = 1;
}
const ids = brief().map((r) => r.id);
if (new Set(ids).size !== Object.keys(QUESTIONS).length) { console.error("coverage gap"); failed = 1; }
process.exit(failed);
