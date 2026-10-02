#!/usr/bin/env node
// vendor-paste live run (PREREG-vendor.md): one Noul per sampled window. 320 max.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/vendor-paste/run_vendor.mjs
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { askJev } from "../../kit/src/client.ts";

const BASE = new URL(".", import.meta.url).pathname;
const join2 = (a, ...p) => p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a);
const sample = JSON.parse(readFileSync(join2(BASE, "sample.json"), "utf8"));
const rows = [...sample.dev, ...sample.held];
const OUT = join2(BASE, "vendor-rows.jsonl");
const Q = "This pasted code is vendored third-party code, not code written for this repository. Judge only the code text, not any file path.";

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l).sample_id); } catch { /* skip */ }
  }
}
console.log(`rows=${rows.length} done=${done.size}`);

for (const r of rows) {
  if (done.has(r.sample_id)) continue;
  const h = createHash("sha256").update(r.window, "utf8").digest("hex").slice(0, 12);
  const base = { sample_id: r.sample_id, split: r.label === undefined ? "?" : (r.sample_id[0] === "d" ? "dev" : "held"), win_sha: h, model: "jev-1.13.0" };
  try {
    const res = await askJev({ model: "jev-1.13.0", state: { code: r.window.slice(0, 4000) }, questions: { vendored: Q }, timeoutMs: 20000 });
    if (!res.ok) {
      if (/401|402|403/.test((res.reason ?? "") + (res.error ?? ""))) { console.error(`STOP auth: ${res.reason}`); process.exit(3); }
      Object.assign(base, { status: res.reason, pred: "own", latencyMs: res.latencyMs, model: res.model });
    } else {
      const n = res.scores?.vendored;
      if (typeof n !== "number" || !Number.isFinite(n)) Object.assign(base, { status: "invalid", pred: "own", latencyMs: res.latencyMs, model: res.model });
      else Object.assign(base, { status: "scored", noul: n, latencyMs: res.latencyMs, model: res.model, ...(res.usage ? { usage: res.usage } : {}) });
    }
  } catch (e) {
    Object.assign(base, { status: "throw", pred: "own", error: String(e).slice(0, 120) });
  }
  appendFileSync(OUT, JSON.stringify(base) + "\n");
}
console.log("vendor done");
