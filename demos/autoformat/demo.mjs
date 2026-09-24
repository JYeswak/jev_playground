#!/usr/bin/env node
// Riff on the official structure-recovery cookbook. Keyless by default: a
// fixture memo stands in for the gist text, and deterministic stitch/classify
// rules stand in for the two per-line question passes. Prints the recovered
// markdown.
// `node demos/autoformat/demo.mjs --live` runs the cookbook's two requests
// through work/jev-client, model jev-1.13.0: pass 1 asks one mid-sentence
// Noul per adjacent non-blank pair (join iff p >= 0.5) in a single request;
// pass 2 asks one Choice per stitched block in a second request. Blank lines
// stay in code, never sent — like the cookbook. Rendering still copies input
// text verbatim; the model never rewrites a word.
// NO-CLAIM: a fixture format is not a live rewrite.
import { recover } from "./recover.mjs";

const live = process.argv.includes("--live");
let r = null;
if (live) {
  const { askJevBundle } = await import("../../work/jev-client/src/index.ts");
  const { RAW, render } = await import("./recover.mjs");
  const tag = (i) => `L${String(i).padStart(2, "0")}`;
  const state1 = RAW.map((t, i) => `${tag(i)}| ${t}`).join("\n");
  const pairIdx = RAW.map((_, i) => i).filter((i) => i > 0 && RAW[i] !== "");
  const q1 = {};
  for (const i of pairIdx) {
    q1[`join_${tag(i)}`] = {
      type: "noul",
      instructions: `Does line ${tag(i)} pick up mid-sentence, continuing a sentence left unfinished at the end of line ${tag(i - 1)}?`,
    };
  }
  const s1 = await askJevBundle({ model: "jev-1.13.0", state: state1, questions: q1, timeoutMs: 30000 });
  if (!s1.ok) {
    console.error(`live call failed: ${s1.reason} ${s1.error}`);
    process.exit(2);
  }
  const stitched = [];
  RAW.forEach((text, i) => {
    if (text === "") { stitched.push({ text: "", gap: true }); return; }
    const prev = stitched.length ? stitched[stitched.length - 1] : null;
    const p = i > 0 && RAW[i] !== "" ? s1.answers[`join_${tag(i)}`].noul : 0;
    if (prev && !prev.gap && p >= 0.5) {
      prev.text += " " + text;
      prev.joins = (prev.joins || 0) + 1;
    } else {
      stitched.push({ text, gap: false });
    }
  });
  const blocks = stitched.filter((b) => !(b.gap && b.text === ""));
  const state2 = blocks.map((b, i) => `B${String(i).padStart(3, "0")}| ${b.text}`).join("\n");
  const KINDS = ["heading", "paragraph", "list_item", "code", "quote", "callout"];
  const q2 = {};
  blocks.forEach((b, i) => {
    if (b.text === "") return;
    const id = `B${String(i).padStart(3, "0")}`;
    q2[`type_${id}`] = {
      type: "choice",
      // Name the block: every question sees the whole state, so an unnamed "this block" was the
      // same question N times and got one answer for all blocks (jev-lcf).
      instructions: `What kind of content is block ${id}?`,
      criteria: {
        heading: "a short title naming a section",
        paragraph: "ordinary running prose",
        list_item: "one item of a list",
        code: "a command or code to run literally",
        quote: "quoted text from elsewhere",
        callout: "a note, tip, or warning set apart from the main text",
      },
    };
  });
  const s2 = await askJevBundle({ model: "jev-1.13.0", state: state2, questions: q2, timeoutMs: 30000 });
  if (!s2.ok) {
    console.error(`live call failed: ${s2.reason} ${s2.error}`);
    process.exit(2);
  }
  const toKind = { heading: "heading", paragraph: "paragraph", list_item: "list", code: "code", quote: "paragraph", callout: "warning" };
  const kinds = blocks.map((b, i) => (b.text === "" ? "blank" : toKind[s2.answers[`type_B${String(i).padStart(3, "0")}`].choice]));
  const judged = blocks.map((b, i) => ({ ...b, kind: kinds[i] }));
  r = { blocks: judged, markdown: render(judged), joins: judged.reduce((n, b) => n + (b.joins || 0), 0) };
} else {
  r = recover();
}
console.log(r.markdown);
console.log(`\n-- joins=${r.joins} blocks=${r.blocks.filter((b) => b.kind !== "blank").length}`);
const must = ["## Migration", "## What changes", "```", "bun run build", "> the old pipeline", "- back up"];
const missing = must.filter((s) => !r.markdown.includes(s));
if (missing.length) {
  process.exit(1);
}
