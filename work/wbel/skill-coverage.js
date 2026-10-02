#!/usr/bin/env node
// jev-wbel coverage census: skill loads in pane sessions vs shadow rows.
// Run: node work/wbel/skill-coverage.js (plain JS, no TS). Writes coverage.json.
// Glob (state it): ~/.omp/agent/sessions/-Developer-jev*/ + profile roots, *.jsonl,
// events with timestamp >= BASELINE. Aggregates only, no raw text.
import { readdirSync, statSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";

const BASELINE = Date.parse("2026-10-02T07:08:00Z");
const FAKE = ["/tmp/", "/var/folders/", "/private-tmp", "/private/var/folders"];
const isSkillRead = (p) => {
  if (typeof p !== "string" || !p) return false;
  if (FAKE.some((x) => p.startsWith(x))) return false;
  if (p.startsWith("skill://")) {
    const rest = p.slice("skill://".length);
    return rest.length > 0 && !rest.includes("..");
  }
  return p.includes("SKILL.md");
};

const roots = [join(homedir(), ".omp", "agent", "sessions")];
try {
  for (const p of readdirSync(join(homedir(), ".omp", "profiles")))
    roots.push(join(homedir(), ".omp", "profiles", p, "agent", "sessions"));
} catch { /* no profiles */ }

const files = [];
for (const r of roots) {
  let slugs = [];
  try { slugs = readdirSync(r).filter((s) => s.startsWith("-Developer-jev")); } catch { continue; }
  for (const s of slugs) {
    let names = [];
    try { names = readdirSync(join(r, s)).filter((n) => n.endsWith(".jsonl") && !n.startsWith(".")); } catch { continue; }
    for (const n of names) {
      const fp = join(r, s, n);
      try { if (statSync(fp).mtimeMs >= BASELINE) files.push(fp); } catch { /* skip */ }
    }
  }
}

const loads = [];
const toolNames = {};
for (const fp of files) {
  let text = "";
  try { text = readFileSync(fp, "utf8"); } catch { continue; }
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    let o;
    try { o = JSON.parse(line); } catch { continue; }
    const t = Date.parse(o.timestamp ?? "");
    if (Number.isNaN(t) || t < BASELINE) continue;
    const m = o.message;
    if (!m || m.role !== "assistant" || !Array.isArray(m.content)) continue;
    for (const b of m.content) {
      if (!b || b.type !== "toolCall") continue;
      toolNames[b.name] = (toolNames[b.name] ?? 0) + 1;
      if (b.name === "read" && isSkillRead(b.arguments?.path))
        loads.push({ session: fp.split("/").pop().slice(-40), ts: o.timestamp, path: b.arguments.path });
      if (b.name === "skill")
        loads.push({ session: fp.split("/").pop().slice(-40), ts: o.timestamp, path: `<skill-tool:${JSON.stringify(b.arguments).slice(0, 120)}>` });
    }
  }
}

let shadow = [];
try {
  shadow = readFileSync(join(homedir(), ".local", "state", "jev", "skill-veto-shadow.jsonl"), "utf8")
    .split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
} catch { /* no log */ }

const out = {
  baseline: "2026-10-02T07:08:00Z (b6ea4d1c)",
  glob: "~/.omp/agent/sessions/-Developer-jev*/ + profiles/*/agent/sessions/-Developer-jev*/",
  candidateFiles: files.length,
  skillLoads: loads,
  toolDistribution: Object.fromEntries(Object.entries(toolNames).sort((a, b) => b[1] - a[1]).slice(0, 15)),
  shadowRows: shadow.length,
};
writeFileSync(join(import.meta.dirname, "coverage.json"), JSON.stringify(out, null, 1) + "\n");
console.log(`files=${files.length} skillLoads=${loads.length} shadowRows=${shadow.length}`);
for (const l of loads) console.log(`load ${l.ts} ${l.session} ${l.path}`);
