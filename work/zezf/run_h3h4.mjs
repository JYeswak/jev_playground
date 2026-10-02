#!/usr/bin/env node
// H3/H4 live run (PREREG-H3H4.md). --phase dev|held. Checkpointed by phase+design+row id.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/zezf/run_h3h4.mjs --phase dev
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { askJev, askJevChoice } from "../../kit/src/client.ts";

const BASE = new URL(".", import.meta.url).pathname;
const join2 = (a, ...p) => p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a);
const phase = process.argv[process.argv.indexOf("--phase") + 1];
if (phase !== "dev" && phase !== "held") { console.error("need --phase dev|held"); process.exit(2); }

const H3_Q = "This shell command runs for longer than 120 seconds, judging by its full command text including all arguments, not just the tool name.";
const H4_I = "How long will this shell command run, judging by its full command text including all arguments, not just the tool name?";
const H4_C = { long: "runs for longer than 120 seconds", short: "finishes in 120 seconds or less" };

const rows = phase === "dev"
  ? JSON.parse(readFileSync(join2(BASE, "..", "..", "var/agent-tmp/zezf/devset.json"), "utf8"))
      .map((r) => ({ id: r.dev_id, cmd: r.cmd, cwd: r.cwd, label: r.label }))
  : JSON.parse(readFileSync(join2(BASE, "sample_h3h4.json"), "utf8"))
      .map((r) => ({ id: r.sample_id, cmd: r.cmd, cwd: r.cwd, label: r.label }));
const OUT = join2(BASE, phase === "dev" ? "h3h4dev.jsonl" : "h3h4held.jsonl");
let cuts = {};
if (phase === "held") cuts = JSON.parse(readFileSync(join2(BASE, "cuts_h3h4.json"), "utf8"));

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { const o = JSON.parse(l); done.add(o.phase + o.design + o.id); } catch { /* skip */ }
  }
}
console.log(`phase=${phase} rows=${rows.length} done=${done.size}`);

const authStop = (res) => {
  if (/401|402|403/.test((res.reason ?? "") + (res.error ?? ""))) { console.error(`STOP auth: ${res.reason}`); process.exit(3); }
};
const h = (cmd) => createHash("sha256").update(cmd ?? "", "utf8").digest("hex").slice(0, 12);

for (const r of rows) {
  for (const design of ["h3", "h4"]) {
    if (done.has(phase + design + r.id)) continue;
    const base = { phase, design, id: r.id, row_hash: h(r.cmd), label: r.label, model: "jev-1.13.0" };
    try {
      if (design === "h3") {
        const res = await askJev({ model: "jev-1.13.0", state: { command: r.cmd, cwd: r.cwd }, questions: { fits: H3_Q }, timeoutMs: 20000 });
        if (!res.ok) { authStop(res); Object.assign(base, { status: res.reason, pred: "short", latencyMs: res.latencyMs }); }
        else {
          const n = res.scores?.fits;
          if (typeof n !== "number" || !Number.isFinite(n)) Object.assign(base, { status: "invalid", pred: "short", latencyMs: res.latencyMs });
          else {
            Object.assign(base, { status: "scored", noul: n, latencyMs: res.latencyMs, ...(res.usage ? { usage: res.usage } : {}) });
            if (phase === "held") base.pred = n >= cuts.h3 ? "long" : "short";
          }
        }
      } else {
        const res = await askJevChoice({ model: "jev-1.13.0", state: { command: r.cmd, cwd: r.cwd }, instructions: H4_I, classes: H4_C, timeoutMs: 20000 });
        if (!res.ok) { authStop(res); Object.assign(base, { status: res.reason, pred: "short", latencyMs: res.latencyMs }); }
        else {
          const p = res.probabilities?.long;
          if (typeof p !== "number" || !Number.isFinite(p)) Object.assign(base, { status: "invalid", pred: "short", latencyMs: res.latencyMs });
          else {
            Object.assign(base, { status: "scored", choice: res.choice, p_long: p, latencyMs: res.latencyMs, ...(res.usage ? { usage: res.usage } : {}) });
            if (phase === "held") base.pred = p >= cuts.h4 ? "long" : "short";
          }
        }
      }
    } catch (e) {
      Object.assign(base, { status: "throw", pred: "short", error: String(e).slice(0, 120) });
    }
    appendFileSync(OUT, JSON.stringify(base) + "\n");
  }
}
console.log("h3h4 done");
