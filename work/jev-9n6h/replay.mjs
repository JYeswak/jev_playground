#!/usr/bin/env node
// jev-9n6h bundle replay: one request with N Noul questions vs recorded
// per-memory single calls on 8 recorded recall turns.
// Reads: memory-filter.jsonl/.jsonl sidecar (local-only; texts joined by hash).
// Writes: work/jev-9n6h/results.json (hashes + decisions + spend, NO raw text).
// Live jev-1.13.0, 1 call per turn (8 calls), bounded, spend stated.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { askJev } from "../../kit/src/client.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

const ROOT = "/Users/josh/Developer/jev";
const STATE = join(homedir(), ".local", "state", "jev");
const OUTDIR = join(ROOT, "work", "jev-9n6h");
const MODEL = "jev-1.13.0";
const CUT = 0.5;
const TURNS = [
  ["8f2d3656", "79bc81c8cfb2"],
  ["8f2d3656", "ec4ee0c2cf9a"],
  ["d94fbbc2", "c3d3964e5015"],
  ["8f2d3656", "ba24fca3f776"],
  ["d94fbbc2", "14e2b450002c"],
  ["250a7b42", "700c529feabc"],
  ["6367a728", "a0c4ef5decef"],
  ["d94fbbc2", "f6b295c3c541"],
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  useInfisicalKey();
  const main = readFileSync(join(STATE, "memory-filter.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const full = readFileSync(join(STATE, "memory-filter-full.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const byKey = new Map();
  for (const r of full) byKey.set(r.promptHash + ":" + r.memoryHash, r);
  const results = { model: MODEL, turns: [], spend: { calls: 0, inputTokens: 0 } };
  for (const [inst, ph] of TURNS) {
    const rows = main.filter((r) => r.instance === inst && r.promptHash.startsWith(ph) && r.status === "scored");
    if (rows.length < 15) throw new Error(`turn ${inst}/${ph} has ${rows.length} rows`);
    const first = byKey.get(rows[0].promptHash + ":" + rows[0].memoryHash);
    const prompt = first.prompt;
    const state = { prompt };
    const questions = {};
    const items = [];
    rows.forEach((r, i) => {
      const f = byKey.get(r.promptHash + ":" + r.memoryHash);
      const key = "m" + i;
      state[key] = f.memory;
      questions[key] = { instructions: `Memory: \`${key}\`. Current request: \`prompt\`. Is this memory relevant to the current request?` };
      items.push({ key, memoryHash: r.memoryHash, recordedNoul: r.noul, recordedDecision: r.decision, inputTokens: r.inputTokens, latencyMs: r.latencyMs });
    });
    const reqBytes = JSON.stringify({ state, questions }).length;
    const t0 = Date.now();
    const res = await askJev({ state, questions, model: MODEL, timeoutMs: 30000 });
    const wall = Date.now() - t0;
    results.spend.calls += 1;
    if (!res.ok) throw new Error(`bundle call failed: ${res.error}`);
    results.spend.inputTokens += res.usage?.input_tokens ?? 0;
    let agree = 0, flips = [];
    for (const it of items) {
      const n = res.scores[it.key];
      const okNum = typeof n === "number" && Number.isFinite(n);
      const dec = okNum ? (n < CUT ? "drop" : "keep") : "keep";
      if (dec === it.recordedDecision) agree++;
      else flips.push({ key: it.key, recorded: it.recordedDecision, bundled: dec, noul: n });
    }
    const baseTok = items.reduce((s, it) => s + (it.inputTokens || 0), 0);
    const baseWall = Math.max(...items.map((it) => it.latencyMs || 0));
    results.turns.push({
      instance: inst, promptHash: ph, n: items.length,
      agree, flips, baseInputTokens: baseTok,
      bundleInputTokens: res.usage?.input_tokens ?? null,
      baseWallMaxMs: baseWall, bundleWallMs: wall, reqBytes,
    });
    console.log(`${inst}/${ph}: agree ${agree}/${items.length} baseTok ${baseTok} bundleTok ${res.usage?.input_tokens ?? "?"} wall ${wall}ms (base max ${baseWall}ms) reqBytes ${reqBytes}`);
    await sleep(500);
  }
  mkdirSync(OUTDIR, { recursive: true });
  writeFileSync(join(OUTDIR, "results.json"), JSON.stringify(results));
  console.log(`calls=${results.spend.calls} inputTokens=${results.spend.inputTokens}`);
}

await main();
