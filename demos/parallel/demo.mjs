#!/usr/bin/env node
// Riff on the official parallel-questions cookbook. Keyless by default: one
// short document plus four recorded answers stand in for the 13-question
// briefing over the GDPR article. Prints the whole briefing from one fixture
// request object — batching changes cost and speed, not answers.
// `node demos/parallel/demo.mjs --live` sends all four questions in one
// request through work/jev-client, model jev-1.13.0.
// NO-CLAIM: a fixture briefing is not a live judgment.
import { DOC, QUESTIONS, brief } from "./brief.mjs";

console.log(DOC);
console.log(`\n-- one request, ${Object.keys(QUESTIONS).length} questions`);
let failed = 0;
const live = process.argv.includes("--live");
let rows = null;
if (live) {
  const { askJevBundle } = await import("../../work/jev-client/src/index.ts");
  const res = await askJevBundle({ model: "jev-1.13.0", state: { document: DOC }, questions: QUESTIONS, timeoutMs: 30000 });
  if (!res.ok) {
    console.error(`live call failed: ${res.reason} ${res.error}`);
    process.exit(2);
  }
  rows = Object.entries(QUESTIONS).map(([id, q]) => {
    const a = res.answers[id];
    const answer = q.type === "noul" ? { type: "noul", noul: a.noul }
      : q.type === "choice" ? { type: "choice", choice: a.choice, confidence: a.confidence, probabilities: a.probabilities }
      : { type: "score", score: a.score, confidence: a.confidence };
    return { id, type: q.type, answer };
  });
} else {
  rows = brief();
}
for (const row of rows) {
  const a = row.answer;
  const shown = a.type === "noul" ? `noul=${a.noul}`
    : a.type === "choice" ? `choice=${a.choice} p=${a.probabilities[a.choice]}`
    : `score=${a.score} conf=${a.confidence}`;
  console.log(`  ${row.id.padEnd(14)} [${row.type}] ${shown}`);
  if (a === undefined) failed = 1;
}
const ids = rows.map((r) => r.id);
if (new Set(ids).size !== Object.keys(QUESTIONS).length) { console.error("coverage gap"); failed = 1; }
process.exit(failed);
