import { readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { askJev } from "../../kit/src/client.ts";

/**
 * pack-nuisance-run.mts — bind-rate Jev judge, 75 rows.
 *
 * One Noul per sampled real edit. State = edit path + excerpt + the full
 * doctrine body of that type (read from the rule file at runtime, never
 * transcribed). Question: at least one clause would CHANGE this edit
 * (live gap), not merely share its topic; already-followed advice is inert.
 * Thresholds REPORTED at t in {0.5,0.7,0.9}, never selected. By-product:
 * Jev-vs-hand agreement. BUDGET <=75 live calls, jev-1.13.0, 20s timeout.
 */
const BINDS = "work/skills-vein/pack-nuisance-binds-20260920.jsonl";
const LABELS = "work/skills-vein/pack-nuisance-labels-20260920.json";
const OUT = "work/skills-vein/pack-nuisance-results-20260920.jsonl";
const RULES: Record<string, string> = {
  rs: "/Users/josh/.agents/rules/ft-rs-doctrine.md",
  sh: "/Users/josh/.agents/rules/ft-sh-doctrine.md",
  md: "/Users/josh/.agents/rules/ft-md-doctrine.md",
};
function doctrineOf(t: string): string {
  const raw = readFileSync(RULES[t], "utf8");
  return raw.replace(/^---\n[\s\S]*?\n---\n/, "").trim();
}

function instructionsFor(): string {
  return [
    `Statement: at least one clause of the doctrine would CHANGE the edit`,
    `described in state — the edit has a live gap the clause covers. A clause`,
    `the edit already follows, or that shares only vocabulary with the edit,`,
    `is INERT and does not count. True means: binds (would change the edit).`,
    `False means: inert (would change nothing).`,
  ].join(" ");
}

const THRESHOLDS = [0.5, 0.7, 0.9];
const mode = process.argv[2] ?? "--fake";

type Row = { type: string; session: string; path: string; excerpt: string };

async function main(): Promise<void> {
  if (mode === "--fake") {
    const realFetch = globalThis.fetch;
    let n = 0;
    globalThis.fetch = (async () => {
      n += 1;
      const noul = n % 2 === 0 ? 0.9 : 0.1;
      return new Response(JSON.stringify({ answers: { relevant: { noul } } }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }) as typeof fetch;
    const r = await askJev({
      state: { probe: true },
      questions: { relevant: instructionsFor() },
      model: "jev-1.13.0",
      timeoutMs: 20000,
      apiKey: "fake-offline-proof",
    });
    globalThis.fetch = realFetch;
    if (!r.ok || typeof r.scores["relevant"] !== "number") {
      console.log(`FAKE-FAIL ${JSON.stringify(r)}`);
      process.exit(1);
    }
    console.log(`FAKE-OK noul=${r.scores["relevant"]}`);
    return;
  }
  if (mode !== "--live") {
    console.log("usage: --fake | --live");
    process.exit(2);
  }
  const rows: Row[] = readFileSync(BINDS, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((l) => JSON.parse(l) as Row);
  let labels: Record<string, string[]> = {};
  try {
    labels = JSON.parse(readFileSync(LABELS, "utf8")) as Record<string, string[]>;
  } catch {
    labels = {};
  }
  console.log(`BUDGET rows=${rows.length} mode=--live model=jev-1.13.0`);
  const key = (r: Row): string => `${r.type}||${r.session}||${r.path}`;
  writeFileSync(OUT, "");
  let ok = 0;
  let fail = 0;
  for (const r of rows) {
    const res = await askJev({
      state: { path: r.path, edit: r.excerpt.slice(0, 2000), doctrine: doctrineOf(r.type) },
      questions: { relevant: instructionsFor() },
      model: "jev-1.13.0",
      timeoutMs: 20000,
    });
    if (res.ok) {
      ok += 1;
      appendFileSync(
        OUT,
        JSON.stringify({ key: key(r), type: r.type, noul: res.scores["relevant"], latencyMs: res.latencyMs, model: res.model }) + "\n",
      );
    } else {
      fail += 1;
      appendFileSync(OUT, JSON.stringify({ key: key(r), type: r.type, error: res.reason }) + "\n");
    }
  }
  console.log(`LIVE-DONE ok=${ok} fail=${fail}`);
  const out = readFileSync(OUT, "utf8").split("\n").filter(Boolean)
    .map((l) => JSON.parse(l) as { key: string; type: string; noul?: number });
  const lab = out.filter((r) => typeof r.noul === "number" && r.key in labels);
  console.log(`labeled_rows=${lab.length}`);
  const pos = lab.filter((r) => (labels[r.key] as string[]).length > 0).length;
  console.log(`hand_bind_rate=${(pos / lab.length).toFixed(4)}`);
  for (const t of THRESHOLDS) {
    const jp = lab.filter((r) => (r.noul as number) >= t);
    const tp = jp.filter((r) => (labels[r.key] as string[]).length > 0).length;
    const agree = lab.filter(
      (r) => (((r.noul as number) >= t) ? 1 : 0) === ((labels[r.key] as string[]).length > 0 ? 1 : 0),
    ).length;
    console.log(
      `t=${t} jev_pos=${jp.length} jev_precision=${jp.length > 0 ? (tp / jp.length).toFixed(4) : "NA"} agreement=${(agree / lab.length).toFixed(4)}`,
    );
  }
}

await main();
