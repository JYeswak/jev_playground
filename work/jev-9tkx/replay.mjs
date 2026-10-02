#!/usr/bin/env node
// jev-9tkx one-variable dev replay: base Noul question vs 3 redesigns on the
// committed dev slice (m959 44 clean keeps + s47b 30 drops + wb7j 96 drops).
// Reads: work/jev-m959/labels.json + sample_organic.json,
//   work/jev-9tkx/s47b-keys.json (hash refs only) joined to the local sidecar
//   (texts never copied out), work/jev-wb7j-lossdepth/heldout files.
// Writes: work/jev-9tkx/results.json (hashes + decisions + spend, NO raw text).
// Live jev-1.13.0, single calls per pair (stability 3.39%, no 3x per jev-li3w).
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { askJev } from "../../kit/src/client.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

const ROOT = "/Users/josh/Developer/jev";
const SIDECAR = join(homedir(), ".local", "state", "jev", "memory-filter-full.jsonl");
const OUTDIR = join(ROOT, "work", "jev-9tkx");
const MODEL = "jev-1.13.0";
const CUT = 0.5;

const BASE = "Memory: `memory`. Current request: `prompt`. Is this memory relevant to the current request?";
const VARIANTS = {
  base: BASE,
  usability: BASE + " Would acting on this memory change what you do next, or is it background you already have?",
  antiecho: BASE + " A memory that merely repeats the request is not relevant.",
  staleness: BASE + " Is this memory about the current task state, or a stale dispatch from an earlier turn? Only current state is relevant.",
};

function loadJSON(p) {
  return JSON.parse(readFileSync(join(ROOT, p), "utf8"));
}

function buildSlice() {
  const pairs = [];
  const labs = Object.fromEntries(loadJSON("work/jev-m959/labels.json").map((r) => [r.id, r]));
  const samp = Object.fromEntries(loadJSON("work/jev-m959/sample_organic.json").map((r) => [r.id, r]));
  const bad = new Set(["o01", "o03", "o14", "o15", "o30", "o40"]);
  for (const [id, l] of Object.entries(labs)) {
    if (bad.has(id)) continue;
    pairs.push({ id: "keep-" + id, prompt: samp[id].prompt, memory: samp[id].memory, expectKeep: l.label === "relevant" });
  }
  const blindKeys = loadJSON("work/jev-9tkx/s47b-keys.json");
  const side = readFileSync(SIDECAR, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  for (const [ph, mh] of blindKeys) {
    const hit = side.filter((r) => (r.promptHash || "").startsWith(ph) && (r.memoryHash || "").startsWith(mh));
    if (hit.length !== 1) throw new Error(`s47b join failed for ${ph}:${mh}`);
    pairs.push({ id: `drop-s47b-${ph}`, prompt: hit[0].prompt, memory: hit[0].memory, expectKeep: false, dropSet: "s47b" });
  }
  const readLines = (p) => readFileSync(join(ROOT, p), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const hl = Object.fromEntries(readLines("work/jev-wb7j-lossdepth/heldout-labels.jsonl").map((r) => [r.id, r.label]));
  const hs = Object.fromEntries(readLines("work/jev-wb7j-lossdepth/heldout-sample.jsonl").map((r) => [r.id, r]));
  for (const [id, label] of Object.entries(hl)) {
    if (label !== "IRRELEVANT" || !hs[id]) continue;
    pairs.push({ id: `drop-wb7j-${id}`, prompt: hs[id].prompt, memory: hs[id].memory, expectKeep: false, dropSet: "wb7j" });
  }
  return pairs;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  useInfisicalKey();
  const pairs = buildSlice();
  const nKeeps = pairs.filter((p) => !("dropSet" in p)).length;
  const nRel = pairs.filter((p) => !("dropSet" in p) && p.expectKeep).length;
  const nDrops = pairs.length - nKeeps;
  if (process.argv.includes("--dry-run")) {
    console.log(`dry slice: ${nKeeps} keeps (${nRel} relevant), ${nDrops} drops (${pairs.length} pairs)`);
    return;
  }
  console.log(`slice: ${nKeeps} keeps, ${nDrops} drops (${pairs.length} pairs x ${Object.keys(VARIANTS).length} variants)`);
  const results = { model: MODEL, variants: Object.keys(VARIANTS), pairs: [], spend: { calls: 0, inputTokens: 0 } };
  for (const [vi, vname] of Object.keys(VARIANTS).entries()) {
    let relKept = 0, kept = 0, dropped = 0, totalDrops = 0;
    for (const [pi, p] of pairs.entries()) {
      let noul = null, status = "scored";
      try {
        const res = await askJev({
          state: { prompt: p.prompt, memory: p.memory },
          questions: { rel: { instructions: VARIANTS[vname] } },
          model: MODEL, timeoutMs: 15000,
        });
        if (res.ok && typeof res.scores.rel === "number" && Number.isFinite(res.scores.rel)) {
          noul = res.scores.rel;
          results.spend.inputTokens += res.usage?.input_tokens ?? 0;
        } else {
          status = "invalid-keep";
        }
      } catch (e) {
        status = "fail_open";
      }
      results.spend.calls += 1;
      const decision = status === "scored" ? (noul < CUT ? "drop" : "keep") : "keep";
      if (!("dropSet" in p)) {
        if (decision === "keep") { kept++; if (p.expectKeep) relKept++; }
      } else {
        totalDrops++;
        if (decision === "drop") dropped++;
      }
      results.pairs.push({
        id: p.id, variant: vname, noul, decision, status,
        ph: createHash("sha256").update(p.prompt).digest("hex").slice(0, 12),
        mh: createHash("sha256").update(p.memory).digest("hex").slice(0, 12),
        promptChars: p.prompt.length, memChars: p.memory.length,
        expectKeep: p.expectKeep, ...(p.dropSet ? { dropSet: p.dropSet } : {}),
      });
      if ((vi * pairs.length + pi + 1) % 50 === 0) console.log(`  ${vi * pairs.length + pi + 1} calls done`);
      await sleep(100);
    }
    console.log(`${vname}: keep=${relKept}/${kept} drops=${dropped}/${totalDrops}`);
  }
  mkdirSync(OUTDIR, { recursive: true });
  writeFileSync(join(OUTDIR, "results.json"), JSON.stringify(results));
  console.log(`wrote results.json, calls=${results.spend.calls} inputTokens=${results.spend.inputTokens}`);
}

await main();
