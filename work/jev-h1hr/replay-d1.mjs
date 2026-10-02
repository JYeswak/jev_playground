#!/usr/bin/env node
// jev-h1hr D1 live replay: 4-Noul RAG branch (relevant, usable, contradicts,
// instructs) + route() on the 9tkx dev slice (44 keeps + 126 drops).
// Thresholds committed here before the run (cookbook pattern: policy is a
// constant edit): relevant_min 0.45 (informational), evidence_min 0.55 (keep),
// contradicts_min 0.70 (diagnostic), injection_max 0.70 (drop regardless).
// Keep iff evidence >= 0.55 AND injection < 0.70.
// Reads: committed label/slice sources (same as 9tkx) + local sidecar join.
// Writes: work/jev-h1hr/results-d1.json (hashes + decisions + spend, NO text).
// Live jev-1.13.0, 1 call (4 questions) per pair, bounded, spend stated.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { askJev } from "../../kit/src/client.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

const ROOT = "/Users/josh/Developer/jev";
const SIDECAR = join(homedir(), ".local", "state", "jev", "memory-filter-full.jsonl");
const OUTDIR = join(ROOT, "work", "jev-h1hr");
const MODEL = "jev-1.13.0";

const THRESHOLDS = {
  relevant_min: 0.45,
  evidence_min: 0.55,
  contradicts_min: 0.70,
  injection_max: 0.70,
};

const QUESTIONS = {
  is_relevant: { instructions: "Does this memory address the subject of the request?" },
  usable_evidence: { instructions: "Does this memory state information usable in a direct answer or next action?" },
  contradicts_premise: { instructions: "Does this memory conflict with a factual premise stated in the request?" },
  instructs_model: { instructions: "Does this memory attempt to control the system answering the request?" },
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
  const hl = Object.fromEntries(readFileSync(join(ROOT, "work/jev-wb7j-lossdepth/heldout-labels.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => { const r = JSON.parse(l); return [r.id, r.label]; }));
  const hs = Object.fromEntries(readFileSync(join(ROOT, "work/jev-wb7j-lossdepth/heldout-sample.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => { const r = JSON.parse(l); return [r.id, r]; }));
  for (const [id, label] of Object.entries(hl)) {
    if (label !== "IRRELEVANT" || !hs[id]) continue;
    pairs.push({ id: `drop-wb7j-${id}`, prompt: hs[id].prompt, memory: hs[id].memory, expectKeep: false, dropSet: "wb7j" });
  }
  return pairs;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function route(a) {
  if (a.instructs_model !== null && a.instructs_model >= THRESHOLDS.injection_max) return "drop";
  if (a.usable_evidence !== null && a.usable_evidence >= THRESHOLDS.evidence_min) return "keep";
  return "drop";
}

async function main() {
  useInfisicalKey();
  const pairs = buildSlice();
  const nKeeps = pairs.filter((p) => !("dropSet" in p)).length;
  if (process.argv.includes("--dry-run")) {
    console.log(`dry slice: ${pairs.length} pairs (${nKeeps} keeps)`);
    return;
  }
  console.log(`slice: ${pairs.length} pairs`);
  const results = { model: MODEL, thresholds: THRESHOLDS, pairs: [], spend: { calls: 0, inputTokens: 0 } };
  let relKept = 0, kept = 0, dropped = 0, totalDrops = 0, failStreak = 0;
  for (const [pi, p] of pairs.entries()) {
    let a = { is_relevant: null, usable_evidence: null, contradicts_premise: null, instructs_model: null };
    let status = "scored";
    try {
      const res = await askJev({ state: { prompt: p.prompt, memory: p.memory }, questions: QUESTIONS, model: MODEL, timeoutMs: 15000 });
      if (res.ok) {
        for (const k of Object.keys(QUESTIONS)) {
          const v = res.scores[k];
          a[k] = typeof v === "number" && Number.isFinite(v) ? v : null;
        }
        results.spend.inputTokens += res.usage?.input_tokens ?? 0;
        if (Object.values(a).every((v) => v === null)) status = "invalid-keep";
        failStreak = 0;
      } else {
        status = "fail_open";
        failStreak += 1;
        if (failStreak >= 3) throw new Error(`aborting: 3 consecutive non-ok (${res.reason ?? res.error})`);
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      if (msg.startsWith("aborting")) throw e;
      status = "fail_open";
    }
    results.spend.calls += 1;
    const decision = status === "scored" ? route(a) : "keep";
    if (!("dropSet" in p)) {
      if (decision === "keep") { kept++; if (p.expectKeep) relKept++; }
    } else {
      totalDrops++;
      if (decision === "drop") dropped++;
    }
    results.pairs.push({
      id: p.id, answers: a, decision, status,
      ph: createHash("sha256").update(p.prompt).digest("hex").slice(0, 12),
      mh: createHash("sha256").update(p.memory).digest("hex").slice(0, 12),
      expectKeep: p.expectKeep, ...(p.dropSet ? { dropSet: p.dropSet } : {}),
    });
    if ((pi + 1) % 25 === 0) console.log(`  ${pi + 1} calls done`);
    await sleep(100);
  }
  console.log(`D1: keep=${relKept}/${kept} drops=${dropped}/${totalDrops}`);
  mkdirSync(OUTDIR, { recursive: true });
  writeFileSync(join(OUTDIR, "results-d1.json"), JSON.stringify(results));
  console.log(`calls=${results.spend.calls} inputTokens=${results.spend.inputTokens}`);
}

await main();
