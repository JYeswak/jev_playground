#!/usr/bin/env node
// D8 live: citation-check Choice on verifier triples, reusing demos/citation
// question shape + kit askJevChoice. Bounded: 300 calls max.
import { readFileSync, existsSync, appendFileSync } from "node:fs";
import { execSync } from "node:child_process";
import { askJevChoice } from "../../kit/src/client.ts";

const ITEMS = JSON.parse(readFileSync(new URL("./d8.live.json", import.meta.url), "utf8"));
const OUT = new URL("./d8.receipt.jsonl", import.meta.url);
const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l).n); } catch {}
  }
}
const classes = {
  supports: "The section states the claim or directly implies that it is true",
  contradicts: "The section states the opposite of the claim or implies it is false",
  says_nothing: "The section does not address what the claim asserts, either way",
};
function excerpt(art) {
  if (/^[\w.\-]*\/[\w.\-/]*\.[\w]+$/.test(art)) {
    const p = art.startsWith("/") ? art : `/Users/josh/Developer/jev/${art}`;
    if (existsSync(p)) {
      try { return readFileSync(p, "utf8").slice(0, 1200); } catch { return null; }
    }
    return null;
  }
  if (/^[0-9a-f]{7,40}$/.test(art)) {
    try {
      return execSync(`git show -s --format=%s ${art}`, { encoding: "utf8", timeout: 15000 }).slice(0, 400);
    } catch { return null; }
  }
  return null;
}
let calls = 0;
for (let n = 0; n < ITEMS.length; n++) {
  if (done.has(n)) continue;
  if (calls >= 300) break;
  const it = ITEMS[n];
  const section = excerpt(it.artifact);
  if (section === null) {
    appendFileSync(OUT, JSON.stringify({ n, answer: it.verdict, choice: "fabricated", auto: true, status: "no-call" }) + "\n");
    continue;
  }
  const r = await askJevChoice({
    state: { claim: it.claim, section },
    instructions: "How does the section relate to the claim?",
    classes,
    model: "jev-1.13.0",
    timeoutMs: 20000,
  });
  if (!r.ok) {
    if (/401|402|403/.test(`${r.reason} ${r.error}`)) { console.error("STOP auth"); break; }
    appendFileSync(OUT, JSON.stringify({ n, answer: it.verdict, status: "error", reason: r.reason }) + "\n");
    continue;
  }
  calls++;
  appendFileSync(OUT, JSON.stringify({ n, answer: it.verdict, choice: r.choice, confidence: r.confidence, status: "ok" }) + "\n");
}
console.log(`calls_this_run=${calls}`);
