#!/usr/bin/env node
// Riff on the official function-calling cookbook. Keyless by default: a fixture
// spec with two functions stands in for spec.json, and recorded overlap scores
// stand in for the per-argument Choice/Noul questions. Prints the typed call
// each command dispatches to, with the call confidence (least-certain judgment).
// NO-CLAIM: a fixture dispatch is not a live tool call.
import { dispatch } from "./dispatch.mjs";

const COMMANDS = [
  "plot AAPL candles with a 20 bar moving average",
  "plot TSLA",
  "quote NVDA",
];

let failed = 0;
for (const text of COMMANDS) {
  const r = dispatch(text);
  console.log(`call: ${r.tool}(${Object.entries(r.args).map(([k, v]) => `${k}=${v}`).join(", ")})  confidence=${r.confidence.toFixed(2)}  <-  ${text.slice(0, 50)}`);
  if (!r.tool) { failed = 1; }
}
process.exit(failed);
