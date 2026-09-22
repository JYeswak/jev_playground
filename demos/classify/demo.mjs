#!/usr/bin/env node
// Riff on the official confidence-classification cookbook. Keyless by default:
// a six-group fixture taxonomy stands in for the 75 SIC groups, and recorded
// overlap margins stand in for the Choice confidence. A sure filing reports
// its group; an unsure one reports the parent division — nothing is dropped.
// NO-CLAIM: a fixture class is not a live label.
import { classify } from "./classify.mjs";

const FILINGS = [
  "Our bakery bakes bread with flour and yeast in a stone oven, selling pastry daily.",
  "The workshop cuts timber with saws and bores holes with drills.",
  "Risk audit of cheese stocks.",
];

let failed = 0;
for (const text of FILINGS) {
  const r = classify(text);
  console.log(`${r.level.padEnd(8)} ${r.label.padEnd(10)} conf=${r.confidence.toFixed(2)} (group ${r.group})  <-  ${text.slice(0, 48)}…`);
  if (!r.label || r.label === "unknown") failed = 1;
}
process.exit(failed);
