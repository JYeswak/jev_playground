#!/usr/bin/env node
// jev-9n6h control: re-score flipped pairs with SAME-TIME single calls.
// If singles-now agree with bundle (not recorded), the gap is time-noise.
// Reads work/jev-9n6h/results.json + sidecar joins. Writes stdout only.
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { askJev } from "../../kit/src/client.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

const ROOT = "/Users/josh/Developer/jev";
const STATE = join(homedir(), ".local", "state", "jev");
const MODEL = "jev-1.13.0";
const CUT = 0.5;
const BASE = "Memory: `memory`. Current request: `prompt`. Is this memory relevant to the current request?";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  useInfisicalKey();
  const res = JSON.parse(readFileSync(join(ROOT, "work/jev-9n6h/results.json"), "utf8"));
  const main = readFileSync(join(STATE, "memory-filter.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const full = readFileSync(join(STATE, "memory-filter-full.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const byKey = new Map();
  for (const r of full) byKey.set(r.promptHash + ":" + r.memoryHash, r);
  let agreeBundle = 0, agreeRecorded = 0, n = 0, tok = 0;
  for (const t of res.turns) {
    if (!t.flips.length) continue;
    const rows = main.filter((r) => r.instance === t.instance && r.promptHash.startsWith(t.promptHash) && r.status === "scored");
    const first = byKey.get(rows[0].promptHash + ":" + rows[0].memoryHash);
    const prompt = first.prompt;
    for (const f of t.flips) {
      const idx = parseInt(f.key.slice(1), 10);
      const rr = rows[idx];
      const mem = byKey.get(rr.promptHash + ":" + rr.memoryHash).memory;
      const ans = await askJev({ state: { prompt, memory: mem }, questions: { rel: { instructions: BASE } }, model: MODEL, timeoutMs: 15000 });
      if (!ans.ok) { console.log(`${t.instance}/${f.key} single FAILED`); continue; }
      tok += ans.usage?.input_tokens ?? 0;
      const dec = ans.scores.rel < CUT ? "drop" : "keep";
      const bdec = f.bundled;
      const rdec = f.recorded;
      if (dec === bdec) agreeBundle++;
      if (dec === rdec) agreeRecorded++;
      n++;
      console.log(`${t.instance}/${f.key}: single-now=${dec}(${ans.scores.rel.toFixed(2)}) recorded=${rdec} bundled=${bdec}`);
      await sleep(200);
    }
  }
  console.log(`control: ${n} pairs, singles agree with BUNDLE ${agreeBundle}/${n}, with RECORDED ${agreeRecorded}/${n}, tokens ${tok}`);
}

await main();
