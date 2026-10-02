#!/usr/bin/env node
// zezf live run (PREREG.md): one Noul per sampled held-out row. 300 calls max.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/zezf/run_long.mjs
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { askJev } from "../../kit/src/client.ts";

const BASE = new URL(".", import.meta.url).pathname;
const sample = JSON.parse(readFileSync(join2(BASE, "..", "..", "var/agent-tmp/zezf/sample.json"), "utf8"));
function join2(a, ...p) { return p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a); }
const OUT = join2(BASE, "longrows.jsonl");

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l).sample_id); } catch { /* skip */ }
  }
}
console.log(`sample=${sample.length} done=${done.size}`);

for (const r of sample) {
  if (done.has(r.sample_id)) continue;
  const q = "Will this shell command run longer than 120 seconds? Answer for the full command including its arguments, not just the tool name.";
  let row;
  try {
    const res = await askJev({ model: "jev-1.13.0", state: { command: r.cmd, cwd: r.cwd }, questions: { longrun: q }, timeoutMs: 20000 });
    const h = createHash("sha256").update(r.cmd, "utf8").digest("hex").slice(0, 12);
    const tok = (r.cmd.trim().split(/\s+/)[0] ?? "").split("/").pop() ?? "";
    if (!res.ok) {
      if (/401|402|403/.test(res.reason + res.error)) { console.error(`STOP auth: ${res.reason}`); process.exit(3); }
      row = { sample_id: r.sample_id, row_hash: h, first_token: tok, status: res.reason, pred: "short", latencyMs: res.latencyMs, model: res.model };
    } else {
      const n = res.scores.longrun;
      row = (typeof n === "number" && Number.isFinite(n))
        ? { sample_id: r.sample_id, row_hash: h, first_token: tok, status: "scored", noul: n, pred: n >= 0.50 ? "long" : "short", latencyMs: res.latencyMs, model: res.model, ...(res.usage ? { usage: res.usage } : {}) }
        : { sample_id: r.sample_id, row_hash: h, first_token: tok, status: "invalid", pred: "short", latencyMs: res.latencyMs, model: res.model };
    }
  } catch (e) {
    row = { sample_id: r.sample_id, status: "throw", pred: "short", error: String(e).slice(0, 120) };
  }
  appendFileSync(OUT, JSON.stringify(row) + "\n");
}
console.log("longrows done");
