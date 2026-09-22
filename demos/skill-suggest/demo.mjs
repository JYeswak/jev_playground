#!/usr/bin/env node
// Riff on the official skill-suggestion cookbook. Keyless by default: a tiny
// fixture roster stands in for the 182-skill Hermes catalog, and recorded
// overlap scores stand in for the two TypeSafe calls (rank-all, then verify
// the top three with a gate). Fixture suggestions are not a live ranking.
// NO-CLAIM: nothing here calls Jev; see INJECTION-FLAG-RESULT.md for a measured seat.
import { suggest, ROSTER } from "./suggest.mjs";

const TASKS = [
  "Cut many iPhone takes of a lip-synced performance into a music video locked to a clean master track.",
  "Black-box sensitive content in a macOS screen recording before upload.",
  "Post this to Mastodon.",
];

let failed = 0;
for (const text of TASKS) {
  const r = suggest(text, ROSTER);
  if (r.skill) console.log(`suggest: ${r.skill}  (score=${r.score.toFixed(2)})  <-  ${text.slice(0, 60)}…`);
  else console.log(`suggest: nothing (best=${r.best.toFixed(2)} below gate)  <-  ${text.slice(0, 60)}…`);
}
if (TASKS.length !== 3) { console.error("fixture changed shape"); failed = 1; }
process.exit(failed);
