#!/usr/bin/env node
// D9 veto live run (jev-hj5t, PREREG-d9.md). One fits-Noul per sampled held-out row.
// Usage: infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node work/skills-breadth/run_veto.mjs
// Appends work/skills-breadth/receipt.jsonl rows (hashes/decisions/spend, no raw text).
import { readFileSync, appendFileSync, existsSync } from "node:fs";

import { homedir } from "node:os";
import { join } from "node:path";
import { askJev } from "../../kit/src/client.ts";

const BASE = new URL(".", import.meta.url).pathname;
const sample = JSON.parse(readFileSync(join(BASE, "..", "..", "var/agent-tmp/skills-breadth/sample.json"), "utf8"));
const OUT = join(BASE, "receipt.jsonl");

const ros = {};
for (const d of (await import("node:fs")).readdirSync(join(homedir(), ".claude", "skills"), { withFileTypes: true })) {
  if (!d.isDirectory()) continue;
  try {
    const t = readFileSync(join(homedir(), ".claude", "skills", d.name, "SKILL.md"), "utf8");
    const nm = (/^name:\s*(.*?)\s*$/m.exec(t) || [])[1] || d.name;
    const ds = (/^description:\s*(.*?)\s*$/m.exec(t) || [])[1] || "";
    ros[nm.replace(/^["']|["']$/g, "")] = ds.replace(/^["']|["']$/g, "");
  } catch { /* skip */ }
}

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l).sample_id); } catch { /* skip */ }
  }
}
console.log(`sample=${sample.length} done=${done.size} roster=${Object.keys(ros).length}`);

let stops = 0;
for (const r of sample) {
  if (done.has(r.sample_id)) continue;
  const desc = ros[r.top1] ?? "";
  const q = `Does the skill '${r.top1}' do the specific thing the user's request asks for? It is described as: ${desc}`;
  const t0 = Date.now();
  let row;
  try {
    const res = await askJev({ model: "jev-1.13.0", state: { request: r.prompt }, questions: { fits: q }, timeoutMs: 20000 });
    if (!res.ok) {
      if (/401|402|403/.test(res.error + res.reason)) { console.error(`STOP auth: ${res.reason} ${res.error}`); stops++; break; }
      row = { sample_id: r.sample_id, status: res.reason, veto: false, latencyMs: res.latencyMs, model: res.model };
    } else {
      const noul = res.scores.fits;
      row = Number.isFinite(noul)
        ? { sample_id: r.sample_id, status: "scored", noul, veto: noul < 0.40, latencyMs: res.latencyMs, model: res.model, ...(res.usage ? { usage: res.usage } : {}) }
        : { sample_id: r.sample_id, status: "invalid", veto: false, latencyMs: res.latencyMs, model: res.model };
    }
  } catch (e) {
    row = { sample_id: r.sample_id, status: "throw", veto: false, error: String(e).slice(0, 120) };
  }
  row.wallMs = Date.now() - t0;
  appendFileSync(OUT, JSON.stringify(row) + "\n");
  if (stops) break;
}
console.log("receipt rows appended; stop-auth=" + stops);
