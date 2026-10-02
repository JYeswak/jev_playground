#!/usr/bin/env node
// j0er-annotate replay (PREREG-annotate.md): frozen web+inj evaluators over organic
// non-jev toolResults. 2 calls/row max. Checkpointed by sample_id.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- node --experimental-strip-types work/j0er-annotate/run_replay.mjs
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { makeWebscreenHandler } from "../../.omp/hooks/post/jev-webscreen.ts";
import { makeInjectionShadowHandler } from "../../.omp/hooks/post/jev-injection-shadow.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

const BASE = new URL(".", import.meta.url).pathname;
const join2 = (a, ...p) => p.reduce((x, y) => x.replace(/\/$/, "") + "/" + y.replace(/^\//, ""), a);
const corpus = JSON.parse(readFileSync(join2(BASE, "corpus.json"), "utf8"));
const OUT = join2(BASE, "replay-rows.jsonl");
const WEBDUP = join2(BASE, "web-dup.jsonl");
process.env.JEV_WEBSCREEN_SHADOW_PATH = WEBDUP;

useInfisicalKey();
const injCaptured = [];
const web = makeWebscreenHandler({});
const inj = makeInjectionShadowHandler({
  enforce: false,
  screenLocalRead: true,
  append: async (_path, line) => { injCaptured.push(JSON.parse(line)); },
});

const countLines = () => {
  if (!existsSync(WEBDUP)) return 0;
  const t = readFileSync(WEBDUP, "utf8");
  return t.split("\n").filter((l) => l.trim()).length;
};
const webRowsSince = (n) => {
  if (!existsSync(WEBDUP)) return [];
  const all = readFileSync(WEBDUP, "utf8").split("\n").filter((l) => l.trim());
  return all.slice(n).map((l) => JSON.parse(l));
};

const done = new Set();
if (existsSync(OUT)) {
  for (const l of readFileSync(OUT, "utf8").split("\n")) {
    if (!l.trim()) continue;
    try { done.add(JSON.parse(l).sample_id); } catch { /* skip */ }
  }
}
console.log(`corpus=${corpus.length} done=${done.size}`);
const authStop = (s) => {
  if (/401|402|403/.test(s)) { console.error("STOP auth in row"); process.exit(3); }
};

for (const r of corpus) {
  if (done.has(r.sample_id)) continue;
  const t0 = Date.now();
  const event = { toolName: r.tool, content: [{ type: "text", text: r.text }] };
  const row = { sample_id: r.sample_id, tool: r.tool, slug: r.slug, model: "jev-1.13.0" };
  const wb0 = countLines();
  const ij0 = injCaptured.length;
  try {
    await web(event);
    await inj(event);
  } catch (e) {
    row.handler_throw = String(e).slice(0, 100);
  }
  const wNew = webRowsSince(wb0);
  const iNew = injCaptured.slice(ij0);
  row.web_writes = wNew.length;
  row.inj_writes = iNew.length;
  const w = wNew[0] ?? null;
  const j = iNew[0] ?? null;
  if (w) {
    row.web = { status: w.status, flagged: w.flagged ?? 0, topScore: w.topScore ?? null, latencyMs: w.latencyMs ?? null, reason: w.reason ?? null };
    if (w.input_tokens != null) row.usage = { input_tokens: w.input_tokens, output_tokens: w.output_tokens ?? 0 };
    authStop(w.reason ?? "");
  }
  if (j) {
    row.inj = { status: j.status, score: j.score ?? null, flag: j.flag ?? null, latencyMs: j.latencyMs ?? null, reason: j.reason ?? null };
    if (j.usage?.input_tokens != null) {
      row.usage = row.usage ?? { input_tokens: 0, output_tokens: 0 };
      row.usage.input_tokens += j.usage.input_tokens;
      row.usage.output_tokens += j.usage.output_tokens ?? 0;
    }
    authStop(j.reason ?? "");
  }
  const wFlag = (w && (w.flagged ?? 0) > 0) || false;
  const iFlag = !!(j && j.flag === true);
  row.flagged = wFlag || iFlag;
  row.screened = !!((w && w.status === "ok") || (j && j.status === "scored"));
  row.latencyMs = Date.now() - t0;
  appendFileSync(OUT, JSON.stringify(row) + "\n");
}
console.log("replay done");
