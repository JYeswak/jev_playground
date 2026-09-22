/**
 * run_shape.mjs — arm S of the jev-screen-shape unit (LIVE, spends credits).
 *
 * Drives the SHIPPED tool (`../.omp/tools/jev-screen.ts` execute()) over all
 * 662 bench texts. No question reconstruction, no alternate asker: the seam
 * under test is the tool itself. [test: offline shape untested; live N=662]
 *
 * Resume: rows-S-screen.jsonl is append-only; existing ids are skipped, so a
 * re-run spends only on missing rows. Refuses without TYPESAFE_API_KEY.
 */
import { readFileSync, appendFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import jevScreenTool from "../../.omp/tools/jev-screen.ts";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const BENCH = "/Users/josh/Developer/jev/jev-sec-bench/results/injection.json";
const OUT = join(HERE, "rows-S-screen.jsonl");
const CONCURRENCY = 8;

const apiKey = process.env.TYPESAFE_API_KEY;
if (!apiKey) {
  console.error("REFUSE: TYPESAFE_API_KEY is not set — no degraded run.");
  process.exit(2);
}

const bench = JSON.parse(readFileSync(BENCH, "utf8"));
const samples = bench.samples;
if (samples.length !== 662) {
  console.error(`REFUSE: corpus drift, ${samples.length} samples (bar: 662).`);
  process.exit(2);
}

const done = new Set();
if (existsSync(OUT)) {
  for (const line of readFileSync(OUT, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try {
      const r = JSON.parse(line);
      if (r.id) done.add(r.id);
    } catch { /* torn line: re-run covers it */ }
  }
}

const pi = { zod: { object: () => ({}), string: () => ({ min: () => ({}) }) } };
const tool = jevScreenTool(pi);

const pending = samples
  .map((s, i) => ({ id: `inj-${String(i).padStart(4, "0")}`, text: s.text }))
  .filter((r) => !done.has(r.id));
console.log(`rows: 662 total, ${done.size} present, ${pending.length} to call`);

let cursor = 0;
async function worker() {
  while (cursor < pending.length) {
    const row = pending[cursor++];
    const t0 = Date.now();
    try {
      const res = await tool.execute(`shape-${row.id}`, { text: row.text });
      const p = res?.details?.probability;
      appendFileSync(
        OUT,
        JSON.stringify({
          id: row.id,
          p: typeof p === "number" ? p : null,
          verdict: res?.details?.verdict ?? "review",
          reason: res?.details?.reason ?? null,
          latency_ms: Date.now() - t0,
        }) + "\n",
      );
    } catch (err) {
      appendFileSync(
        OUT,
        JSON.stringify({ id: row.id, error: String(err?.message ?? err) }) + "\n",
      );
    }
    if ((done.size + cursor) % 50 === 0) console.log(`...${done.size + cursor}/662`);
  }
}

await Promise.all(Array.from({ length: Math.min(CONCURRENCY, pending.length || 1) }, worker));
console.log(`COMPLETE -> ${OUT}`);
