#!/usr/bin/env node
// longres Choice run (PREREG-longres.md): keep/summarize/drop per long result. 200 max.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/longres/run_choice.mjs
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { askJevChoice } from "../../kit/src/client.ts";
import { createHash } from "node:crypto";

const BASE = new URL(".", import.meta.url).pathname;
const join2 = (a, ...p) => p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a);
const corpus = JSON.parse(readFileSync(join2(BASE, process.env.LONGRES_CORPUS ?? "corpus.json"), "utf8"));
const rows = [...corpus.dev, ...corpus.held];
const OUT = join2(BASE, process.env.LONGRES_OUT ?? "choice-rows.jsonl");

const INSTR = "This tool result just arrived. How should it be kept for the rest of the session?";
const CLASSES = {
  keep: "keep the full result: the task will need its specific details later",
  summarize: "keep only its gist: the general shape suffices, details will not be needed",
  drop: "discard it entirely: nothing in it will be needed again",
};

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l).sample_id); } catch { /* skip */ }
  }
}
console.log(`rows=${rows.length} done=${done.size}`);

for (const r of rows) {
  if (done.has(r.sample_id)) continue;
  const h = createHash("sha256").update(r.head + r.tail, "utf8").digest("hex").slice(0, 12);
  const base = { sample_id: r.sample_id, win_sha: h, model: "jev-1.13.0" };
  const state = { result_head: r.head, result_tail: r.tail, task: (r.task ?? "").slice(0, 500) };
  try {
    const res = await askJevChoice({ model: "jev-1.13.0", state, instructions: INSTR, classes: CLASSES, timeoutMs: 20000 });
    if (!res.ok) {
      if (/401|402|403/.test((res.reason ?? "") + (res.error ?? ""))) { console.error(`STOP auth: ${res.reason}`); process.exit(3); }
      Object.assign(base, { status: res.reason, pred: "keep", latencyMs: res.latencyMs });
    } else {
      Object.assign(base, { status: "scored", choice: res.choice, probabilities: res.probabilities, confidence: res.confidence, latencyMs: res.latencyMs, ...(res.usage ? { usage: res.usage } : {}) });
    }
  } catch (e) {
    Object.assign(base, { status: "throw", pred: "keep", error: String(e).slice(0, 120) });
  }
  appendFileSync(OUT, JSON.stringify(base) + "\n");
}
console.log("choice done");
