#!/usr/bin/env node
// Single-session shadow probe: one fresh RPC session reads a skill; prints new shadow rows.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/skills-breadth/probe-one.mjs "<prompt>"
import { spawn } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const LOG = join(homedir(), ".local", "state", "jev", "skill-veto-shadow.jsonl");
const prompt = process.argv[2] ?? "Break this into tracked beads. Read skill://plan-to-beads/SKILL.md and tell me its first step.";

if (!process.env.TYPESAFE_API_KEY) {
  console.error("TYPESAFE_API_KEY unset: run under infisical run.");
  process.exit(2);
}
const before = existsSync(LOG) ? readFileSync(LOG, "utf8").split("\n").filter(Boolean).length : 0;

await new Promise((resolve) => {
  const child = spawn("omp", ["--mode=rpc", "--max-time=180"], { cwd: ROOT, env: { ...process.env } });
  let buf = "";
  child.stdout.on("data", (d) => {
    buf += d.toString();
    let idx;
    while ((idx = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, idx).trim();
      buf = buf.slice(idx + 1);
      if (!line) continue;
      try {
        const f = JSON.parse(line);
        if (f.type === "agent_end") { try { child.stdin.end(); } catch {} }
      } catch { /* keep */ }
    }
  });
  child.stderr.on("data", () => {});
  const timer = setTimeout(() => { try { child.kill("SIGKILL"); } catch {} }, 200000);
  child.stdin.write(JSON.stringify({ id: "p1", type: "negotiate_protocol", protocolVersion: 2 }) + "\n");
  child.stdin.write(JSON.stringify({ id: "s1", type: "prompt", message: prompt }) + "\n");
  child.on("close", () => { clearTimeout(timer); resolve(); });
});

const rows = existsSync(LOG) ? readFileSync(LOG, "utf8").split("\n").filter(Boolean) : [];
console.log(`rows before=${before} after=${rows.length}`);
for (const l of rows.slice(before)) console.log(l.slice(0, 400));
