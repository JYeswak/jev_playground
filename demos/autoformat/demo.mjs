#!/usr/bin/env node
// Riff on the official structure-recovery cookbook. Keyless by default: a
// fixture memo stands in for the gist text, and deterministic stitch/classify
// rules stand in for the two per-line question passes. Prints the recovered
// markdown. NO-CLAIM: a fixture format is not a live rewrite.
import { recover } from "./recover.mjs";

const r = recover();
console.log(r.markdown);
console.log(`\n-- joins=${r.joins} blocks=${r.blocks.filter((b) => b.kind !== "blank").length}`);
const must = ["## Migration", "## What changes", "```", "bun run build", "> the old pipeline", "- back up"];
const missing = must.filter((s) => !r.markdown.includes(s));
if (missing.length) {
  process.exit(1);
}
