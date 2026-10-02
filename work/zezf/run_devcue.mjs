#!/usr/bin/env node
// H2 dev replay (jev-zezf): predesc vs compute-time-cue arms, paired per dev row. 240 calls max.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/zezf/run_devcue.mjs
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { askJev } from "../../kit/src/client.ts";

const BASE = new URL(".", import.meta.url).pathname;
const devset = JSON.parse(readFileSync(join2(BASE, "..", "..", "var/agent-tmp/zezf/devset.json"), "utf8"));
function join2(a, ...p) { return p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a); }
const OUT = join2(BASE, "devcue.jsonl");
const CUE = " Judge only the command's own compute time from its text and arguments. Ignore queueing, waiting on locks, or unattended background aging.";

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { const o = JSON.parse(l); done.add(o.dev_id + o.arm); } catch { /* skip */ }
  }
}
console.log(`devset=${devset.length} done=${done.size}`);

for (const r of devset) {
  for (const arm of ["predesc", "cued"]) {
    if (done.has(r.dev_id + arm)) continue;
    const q = "Will this shell command run longer than 120 seconds? Answer for the full command including its arguments, not just the tool name." + (arm === "cued" ? CUE : "");
    let row;
    try {
      const res = await askJev({ model: "jev-1.13.0", state: { command: r.cmd, cwd: r.cwd }, questions: { longrun: q }, timeoutMs: 20000 });
      const h = createHash("sha256").update(r.cmd, "utf8").digest("hex").slice(0, 12);
      if (!res.ok) {
        if (/401|402|403/.test(res.reason + res.error)) { console.error(`STOP auth: ${res.reason}`); process.exit(3); }
        row = { dev_id: r.dev_id, arm, status: res.reason, pred: "short", latencyMs: res.latencyMs, model: res.model };
      } else {
        const n = res.scores.longrun;
        row = (typeof n === "number" && Number.isFinite(n))
          ? { dev_id: r.dev_id, arm, status: "scored", noul: n, pred: n >= 0.50 ? "long" : "short", latencyMs: res.latencyMs, model: res.model, ...(res.usage ? { usage: res.usage } : {}) }
          : { dev_id: r.dev_id, arm, status: "invalid", pred: "short", latencyMs: res.latencyMs, model: res.model };
      }
      row.row_hash = h;
    } catch (e) {
      row = { dev_id: r.dev_id, arm, status: "throw", pred: "short", error: String(e).slice(0, 120) };
    }
    appendFileSync(OUT, JSON.stringify(row) + "\n");
  }
}
console.log("devcue done");
