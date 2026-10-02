#!/usr/bin/env node
// Dev one-variable: full description (cross-root + body head 700) vs prereg description-only.
// Paired per-row on devset.json (non-held sessions). 82 calls max. Receipt devvar.jsonl.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/skills-breadth/run_devvar.mjs
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { askJev } from "../../kit/src/client.ts";

const BASE = new URL(".", import.meta.url).pathname;
const devset = JSON.parse(readFileSync(join(BASE, "..", "..", "var/agent-tmp/skills-breadth/devset.json"), "utf8"));
const OUT = join(BASE, "devvar.jsonl");

const ROOTS = [join(homedir(), ".claude", "skills"), join(homedir(), ".agents", "skills")];
function skillFiles(skill) {
  const segs = skill.split("/").filter(Boolean);
  const out = [];
  for (const root of ROOTS) {
    out.push(join(root, ...segs, "SKILL.md"));
    if (segs.length > 1) out.push(join(root, segs[segs.length - 1], "SKILL.md"));
  }
  return out;
}
function readFull(skill) {
  for (const f of skillFiles(skill)) {
    try {
      const t = readFileSync(f, "utf8");
      const d = (/^description:\s*(.*?)\s*$/m.exec(t) || [])[1] || "";
      const body = t.split("---").slice(2).join("---").trim().slice(0, 700);
      return { desc: d.replace(/^["']|["']$/g, ""), body };
    } catch { /* next */ }
  }
  return { desc: "", body: "" };
}
function readDescOnly(skill) {
  // prereg arm replica: ~/.claude/skills only, description frontmatter only
  const f = join(homedir(), ".claude", "skills", skill.split("/").pop(), "SKILL.md");
  try {
    const t = readFileSync(f, "utf8");
    return (/^description:\s*(.*?)\s*$/m.exec(t) || [])[1]?.replace(/^["']|["']$/g, "") ?? "";
  } catch { return ""; }
}

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { const o = JSON.parse(l); done.add(o.dev_id + o.arm); } catch { /* skip */ }
  }
}

async function askOnce(prompt, skill, text) {
  const q = `Does the skill '${skill}' do the specific thing the user's request asks for? It is described as: ${text}`;
  try {
    const res = await askJev({ model: "jev-1.13.0", state: { request: prompt.slice(0, 2000) }, questions: { fits: q }, timeoutMs: 20000 });
    if (!res.ok) {
      if (/401|402|403/.test(res.reason + res.error)) { console.error("STOP auth"); process.exit(3); }
      return { status: res.reason, noul: null };
    }
    const n = res.scores.fits;
    return { status: "scored", noul: n, usage: res.usage, latencyMs: res.latencyMs };
  } catch (e) {
    return { status: "throw", noul: null };
  }
}

for (const r of devset) {
  for (const arm of ["predesc", "fulldesc"]) {
    if (done.has(r.dev_id + arm)) continue;
    const text = arm === "predesc" ? readDescOnly(r.top1) : (() => { const f = readFull(r.top1); return `${f.desc} — ${f.body}`; })();
    const a = await askOnce(r.prompt, r.top1, text);
    appendFileSync(OUT, JSON.stringify({ dev_id: r.dev_id, arm, status: a.status, noul: a.noul ?? null, veto: a.noul !== null && a.noul !== undefined && a.noul < 0.40, ...(a.usage ? { usage: a.usage } : {}), ...(a.latencyMs ? { latencyMs: a.latencyMs } : {}) }) + "\n");
  }
}
console.log("devvar done");
