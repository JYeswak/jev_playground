#!/usr/bin/env node
// wbel cookbook two-request run (PREREG-cookbook.md). 2 calls/row, checkpointed.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/wbel/run_cook.mjs
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { askJevChoice, askJevBundle } from "../../kit/src/client.ts";
import { fitsQuestion, requestHash } from "../../kit/src/skill-veto.ts";

const BASE = new URL(".", import.meta.url).pathname;
const join2 = (a, ...p) => p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a);
const corpus = JSON.parse(readFileSync(join2(BASE, "replay-corpus.json"), "utf8"));
const short = JSON.parse(readFileSync(join2(BASE, "shortlists.json"), "utf8"));
const OUT = join2(BASE, "cook-rows.jsonl");

const R1_I = "Which of these skills, if any, is the right one to load to help with the user's latest request?";
const R2_I = "Exactly one of these skills is the right one to load for the user's latest request. Which one? Read what each actually does, not just its name.";

const ROOTS = [join(homedir(), ".claude", "skills"), join(homedir(), ".agents", "skills")];
async function describe(skill) {
  const segs = skill.split("/").filter(Boolean);
  const cands = [];
  for (const root of ROOTS) {
    cands.push(join(root, ...segs, "SKILL.md"));
    if (segs.length > 1) cands.push(join(root, segs[segs.length - 1], "SKILL.md"));
  }
  for (const f of cands) {
    try {
      const text = await readFile(f, "utf8");
      const m = /^description:\s*(.*?)\s*$/m.exec(text);
      const desc = m ? m[1].replace(/^["']|["']$/g, "") : "";
      const body = text.split("---").slice(2).join("---").trim().slice(0, 700);
      if (desc || body) return `${desc} — ${body}`.slice(0, 1200);
      return "";
    } catch { /* next */ }
  }
  return "";
}
const finiteDist = (p, ids) => {
  if (!p || typeof p !== "object") return false;
  let s = 0;
  for (const id of ids) {
    const v = p[id];
    if (typeof v !== "number" || !Number.isFinite(v) || v < 0) return false;
    s += v;
  }
  return Math.abs(s - 1) < 0.02;
};

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l).sample_id); } catch { /* skip */ }
  }
}
console.log(`corpus=${corpus.length} done=${done.size}`);
const authStop = (res) => {
  if (/401|402|403/.test((res.reason ?? "") + (res.error ?? ""))) { console.error(`STOP auth: ${res.reason}`); process.exit(3); }
};

for (const r of corpus) {
  if (done.has(r.sample_id)) continue;
  const row = { sample_id: r.sample_id, skill: r.skill, resolved: short[r.sample_id].resolved, reqHash: requestHash(r.request), model: "jev-1.13.0" };
  const t0 = Date.now();
  try {
    const names = short[r.sample_id].shortlist;
    const criteria = {};
    for (const n of names) criteria[n] = await describe(n);
    const r1 = await askJevChoice({ model: "jev-1.13.0", state: { request: r.request.slice(0, 2000) }, instructions: R1_I, classes: criteria, timeoutMs: 20000 });
    if (!r1.ok) { authStop(r1); throw new Error("r1-" + r1.reason); }
    const ranked = [...names].sort((a, b) => (r1.probabilities[b] ?? -1) - (r1.probabilities[a] ?? -1));
    const top3 = ranked.slice(0, 3);
    row.r1top3 = top3;
    const q = { which: { type: "choice", instructions: R2_I, criteria: Object.fromEntries(top3.map((n) => [n, criteria[n]])) } };
    for (const n of top3) q[`fits::${n}`] = { type: "noul", instructions: fitsQuestion(n, criteria[n]) };
    const r2 = await askJevBundle({ model: "jev-1.13.0", state: { request: r.request.slice(0, 2000) }, questions: q, timeoutMs: 20000 });
    if (!r2.ok) { authStop(r2); throw new Error("r2-" + r2.reason); }
    const w = r2.answers?.which;
    const probs = w?.probabilities ?? {};
    const wChoice = w?.choice;
    const fits = {};
    let fitsOk = true;
    const okChoice = typeof wChoice === "string" && top3.includes(wChoice) && finiteDist(probs, top3) && probs[wChoice] >= Math.max(...top3.map((n) => probs[n] ?? -1)) - 1e-6;
    for (const n of top3) {
      const f = r2.answers?.[`fits::${n}`]?.noul;
      if (typeof f !== "number" || !Number.isFinite(f)) { fitsOk = false; break; }
      fits[n] = f;
    }
    if (!okChoice || !fitsOk) throw new Error("r2-invalid");
    row.winner = wChoice;
    row.winner_p = probs[wChoice];
    row.fits = fits;
    row.best_fits = Math.max(...Object.values(fits));
    row.status = "scored";
    row.latencyMs = Date.now() - t0;
    for (const u of [r1.usage, r2.usage]) for (const k of ["input_tokens", "output_tokens"]) {
      if (u?.[k] != null) { row.usage = row.usage ?? { input_tokens: 0, output_tokens: 0 }; row.usage[k] += u[k]; }
    }
  } catch (e) {
    const msg = String(e).slice(0, 120);
    if (msg.startsWith("r1-") || msg.startsWith("r2-")) Object.assign(row, { status: msg.slice(0, 40), pred: "allow" });
    else Object.assign(row, { status: "invalid", pred: "allow" });
    row.latencyMs = Date.now() - t0;
  }
  appendFileSync(OUT, JSON.stringify(row) + "\n");
}
console.log("cook done");
