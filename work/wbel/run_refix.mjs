#!/usr/bin/env node
// wbel fix rescore (PREREG-replay-fix.md): ONE variable — preceding work in state.
// --phase dev: rescore replay-corpus.json + replay-devctx.json -> replay-dev2.jsonl
// --phase fresh: score replay-fresh-corpus.json (preceding inline) -> replay-fresh-rows.jsonl
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/wbel/run_refix.mjs --phase dev
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { askJev } from "../../kit/src/client.ts";
import { fitsQuestion, decideVeto, requestHash } from "../../kit/src/skill-veto.ts";

const BASE = new URL(".", import.meta.url).pathname;
const join2 = (a, ...p) => p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a);
const phase = process.argv[process.argv.indexOf("--phase") + 1];
if (phase !== "dev" && phase !== "fresh") { console.error("need --phase dev|fresh"); process.exit(2); }

const idKey = phase === "dev" ? "sample_id" : "fresh_id";
const corpus = JSON.parse(readFileSync(join2(BASE, phase === "dev" ? "replay-corpus.json" : "replay-fresh-corpus.json"), "utf8"));
const ctx = phase === "dev" ? JSON.parse(readFileSync(join2(BASE, "replay-devctx.json"), "utf8")) : {};
const OUT = join2(BASE, phase === "dev" ? "replay-dev2.jsonl" : "replay-fresh-rows.jsonl");
import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
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

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l)[idKey]); } catch { /* skip */ }
  }
}
console.log(`phase=${phase} rows=${corpus.length} done=${done.size}`);

for (const r of corpus) {
  const id = r[idKey];
  if (done.has(id)) continue;
  const recent = phase === "dev" ? (ctx[id] ?? []) : (r.preceding ?? []);
  const desc = await describe(r.skill);
  const base = { [idKey]: id, skill: r.skill, reqHash: requestHash(r.request), recent_n: recent.length, model: "jev-1.13.0" };
  try {
    const res = await askJev({ model: "jev-1.13.0", state: { request: r.request.slice(0, 2000), recent_work: recent }, questions: { fits: fitsQuestion(r.skill, desc) }, timeoutMs: 20000 });
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
console.log("refix done");
