#!/usr/bin/env node
// wbel enforcement replay (PREREG-replay.md): one fits-Noul per sampled organic row.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/wbel/run_replay.mjs
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { askJev } from "../../kit/src/client.ts";
import { fitsQuestion, decideVeto, requestHash } from "../../kit/src/skill-veto.ts";

const BASE = new URL(".", import.meta.url).pathname;
const join2 = (a, ...p) => p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a);
const corpus = JSON.parse(readFileSync(join2(BASE, "replay-corpus.json"), "utf8"));
const OUT = join2(BASE, "replay-rows.jsonl");

const ROOTS = [join(homedir(), ".claude", "skills"), join(homedir(), ".agents", "skills")];
async function describe(skill) {
  const { readFile } = await import("node:fs/promises");
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

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l).sample_id); } catch { /* skip */ }
  }
}
console.log(`corpus=${corpus.length} done=${done.size}`);

for (const r of corpus) {
  if (done.has(r.sample_id)) continue;
  const desc = await describe(r.skill);
  const base = { sample_id: r.sample_id, skill: r.skill, reqHash: requestHash(r.request), model: "jev-1.13.0" };
  try {
    const res = await askJev({ model: "jev-1.13.0", state: { request: r.request.slice(0, 2000) }, questions: { fits: fitsQuestion(r.skill, desc) }, timeoutMs: 20000 });
    if (!res.ok) {
      if (/401|402|403/.test((res.reason ?? "") + (res.error ?? ""))) { console.error(`STOP auth: ${res.reason}`); process.exit(3); }
      Object.assign(base, { status: res.reason, pred: "allow", latencyMs: res.latencyMs });
    } else {
      const n = res.scores?.fits;
      if (typeof n !== "number" || !Number.isFinite(n)) Object.assign(base, { status: "invalid", pred: "allow", latencyMs: res.latencyMs });
      else Object.assign(base, { status: "scored", noul: n, pred: decideVeto(n) ? "veto" : "allow", latencyMs: res.latencyMs, ...(res.usage ? { usage: res.usage } : {}) });
    }
  } catch (e) {
    Object.assign(base, { status: "throw", pred: "allow", error: String(e).slice(0, 120) });
  }
  appendFileSync(OUT, JSON.stringify(base) + "\n");
}
console.log("replay done");
