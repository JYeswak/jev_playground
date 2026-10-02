#!/usr/bin/env node
// L3 for D9 shadow veto (jev-wbel). Two fresh omp --mode=rpc sessions from the repo root.
// Bar (bead comment, predeclared): session A (unrelated ask + beads skill read) logs
// wouldVeto=true for plan-to-beads; session B (beads ask + beads read) logs
// wouldVeto=false; both reads succeed. Exit 0 iff all hold, 1 otherwise, 2 without a key.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node work/skills-breadth/l3-veto.mjs
import { spawn } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const LOG = join(homedir(), ".local", "state", "jev", "skill-veto-shadow.jsonl");

if (!process.env.TYPESAFE_API_KEY) {
  console.error("TYPESAFE_API_KEY unset: run under infisical run. No session started.");
  process.exit(2);
}

const PROMPT_A = "What is 17*23? Also read skill://plan-to-beads/SKILL.md and quote its description field exactly.";
const PROMPT_B = "I need to break a feature into tracked beads. Read skill://plan-to-beads/SKILL.md and tell me its first step.";

function readLog() {
  if (!existsSync(LOG)) return [];
  return readFileSync(LOG, "utf8").split("\n").filter(Boolean).map((l) => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function runSession(prompt, maxMs) {
  return new Promise((resolve) => {
    const frames = [];
    const child = spawn("omp", ["--mode=rpc", "--max-time=240"], { cwd: ROOT, env: { ...process.env } });
    let buf = "";
    child.stdout.on("data", (d) => {
      buf += d.toString();
      let idx;
      while ((idx = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, idx).trim();
        buf = buf.slice(idx + 1);
        if (!line) continue;
        try { frames.push(JSON.parse(line)); } catch { frames.push({ _raw: line.slice(0, 160) }); }
        const last = frames[frames.length - 1];
      }
    });
    child.stdin.write(JSON.stringify({ id: "p1", type: "negotiate_protocol", protocolVersion: 2 }) + "\n");
    child.stdin.write(JSON.stringify({ id: "s1", type: "prompt", message: prompt }) + "\n");
    child.on("close", (code) => { clearTimeout(timer); resolve({ code, frames }); });
  });
}

const before = readLog().length;
console.log(`shadow rows before: ${before}`);

const a = await runSession(PROMPT_A, 250000);
const rowsA = mid.slice(before).filter((r) => String(r.skill).startsWith("plan-to-beads"));
const readOkA = a.frames.some((f) => JSON.stringify(f).includes("plan-to-beads"));
console.log(`A: frames=${a.frames.length} readSeen=${readOkA} vetoRows=${rowsA.length} veto=${rowsA.map((r) => r.wouldVeto).join(",")}`);

const b = await runSession(PROMPT_B, 250000);
const rowsB = after.slice(mid.length).filter((r) => String(r.skill).startsWith("plan-to-beads"));
const readOkB = b.frames.some((f) => JSON.stringify(f).includes("plan-to-beads"));
console.log(`B: frames=${b.frames.length} readSeen=${readOkB} vetoRows=${rowsB.length} veto=${rowsB.map((r) => r.wouldVeto).join(",")}`);

const passA = rowsA.length >= 1 && rowsA.some((r) => r.wouldVeto === true);
const passB = rowsB.length >= 1 && rowsB.every((r) => r.wouldVeto === false);
const ok = passA && passB && readOkA && readOkB;
console.log(`A-veto=${passA} B-silent=${passB} A-read=${readOkA} B-read=${readOkB} -> ${ok ? "L3 BAR MET" : "L3 BAR MISSED"}`);
process.exit(ok ? 0 : 1);
