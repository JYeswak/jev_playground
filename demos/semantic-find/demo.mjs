#!/usr/bin/env node
// Riff on the official line-by-line search cookbook. Keyless by default: a
// fixture document stands in for the ToS text, and recorded overlap scores
// stand in for the Choice ranking plus the Noul existence check. One query is
// answered, one is not — the exists check is what tells them apart.
// NO-CLAIM: a fixture find is not a live search.
import { search } from "./find.mjs";

const ANSWERED = "Can I get a refund on a digital download?";

let failed = 0;
const a = search(ANSWERED);
const UNANSWERED = "What are the office holiday hours?";
console.log(`  points at ${a.best.id} (score=${a.best.score.toFixed(2)}): ${a.best.text}`);
console.log(`  exists=${a.exists.toFixed(2)} -> ${a.exists >= 0.5 ? "ANSWER" : "no answer"}`);
if (a.best.id !== "L03" || a.exists < 0.5) { console.error("MISS: answered query"); failed = 1; }

const b = search(UNANSWERED);
console.log(`query: ${UNANSWERED}`);
console.log(`  points at ${b.best.id} (score=${b.best.score.toFixed(2)}): ${b.best.text}`);
console.log(`  exists=${b.exists.toFixed(2)} -> ${b.exists >= 0.5 ? "ANSWER" : "no answer"}`);
if (b.exists >= 0.5) { console.error("MISS: unanswered query reads as answered"); failed = 1; }
process.exit(failed);
