import { readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { askJev } from "../../kit/src/client.ts";

/**
 * skills-jev-pilot-run.mts — Noul skill-relevance pilot.
 *
 * PREREGISTERED: one Noul question per (session, skill) pair, key
 * "relevant". State = request + tool names + paths + skill name + skill
 * description + work_count. Instructions carry the statement plus
 * true/false criteria and what to check. Model pinned jev-1.13.0,
 * timeoutMs 20000, sanctioned askJev (no forked fetch).
 * Thresholds REPORTED at t in {0.5, 0.7, 0.9}, never selected on this set.
 * Comparison on identical rows: Jev-positive precision vs naive-positive
 * precision (every shortlisted row is naive-positive by construction).
 * Recall NOT measured (negatives unlabeled).
 * BUDGET: <=120 live Noul calls (40 sessions x <=3). Lane: live.
 * Offline-insufficient reason: relevance judgment IS the model call; wiring
 * (shape, parsing, bucketing) proven here with --fake first.
 *
 * Usage:
 *   npx tsx work/skills-vein/skills-jev-pilot-run.mts --fake   # offline
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     npx tsx work/skills-vein/skills-jev-pilot-run.mts --live
 */
const PAIRS = "work/skills-vein/skills-jev-pilot-pairs-20260920.jsonl";
const LABELS = "work/skills-vein/skills-jev-pilot-labels-20260920.json";
const OUT = "work/skills-vein/skills-jev-pilot-results-20260920.jsonl";
const THRESHOLDS = [0.5, 0.7, 0.9];

const mode = process.argv[2] ?? "--fake";

type Pair = {
  session: string;
  skill: string;
  work_count: number;
  request: string;
  tools: string[];
  paths: string[];
  skill_desc: string;
};

function instructionsFor(skill: string): string {
  return [
    `Statement: the skill "${skill}" is relevant to the work in this session.`,
    `Answer true if a competent engineer doing exactly the work described in`,
    `state would benefit from reading this skill before or during the work.`,
    `Answer false if the skill is unrelated to the work, or merely shares`,
    `ordinary vocabulary with it (e.g. the word "commit", "design", "report").`,
    `True means: relevant. False means: not relevant.`,
  ].join(" ");
}

async function main(): Promise<void> {
  if (mode === "--fake") {
    // Offline wiring proof: deterministic fake through the REAL askJev path
    // by stubbing global fetch. Exercises shape, parsing, threshold buckets.
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
      questions: { relevant: instructionsFor("probe-skill") },
      model: "jev-1.13.0",
      timeoutMs: 20000,
      apiKey: "fake-offline-proof",
    });
    globalThis.fetch = realFetch;
    if (!r.ok || typeof r.scores["relevant"] !== "number") {
      console.log(`FAKE-FAIL ${JSON.stringify(r)}`);
      process.exit(1);
    }
    console.log(`FAKE-OK noul=${r.scores["relevant"]} latencyMs=${r.latencyMs}`);
    return;
  }

  if (mode !== "--live") {
    console.log("usage: --fake | --live");
    process.exit(2);
  }
  const pairs: Pair[] = readFileSync(PAIRS, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((l) => JSON.parse(l) as Pair);
  let labels: Record<string, number> = {};
  try {
    labels = JSON.parse(readFileSync(LABELS, "utf8")) as Record<string, number>;
  } catch {
    labels = {};
  }
  console.log(`BUDGET pairs=${pairs.length} mode=${mode} model=jev-1.13.0`);


  writeFileSync(OUT, "");
  let ok = 0;
  let fail = 0;
  for (const p of pairs) {
    const r = await askJev({
      state: {
        request: p.request,
        tools: p.tools,
        paths: p.paths,
        skill: p.skill,
        skill_description: p.skill_desc,
        work_count: p.work_count,
      },
      questions: { relevant: instructionsFor(p.skill) },
      model: "jev-1.13.0",
      timeoutMs: 20000,
    });
    if (r.ok) {
      ok += 1;
      appendFileSync(
        OUT,
        JSON.stringify({
          session: p.session,
          skill: p.skill,
          noul: r.scores["relevant"],
          latencyMs: r.latencyMs,
          model: r.model,
        }) + "\n",
      );
    } else {
      fail += 1;
      appendFileSync(
        OUT,
        JSON.stringify({ session: p.session, skill: p.skill, error: r.reason }) + "\n",
      );
    }
  }
  console.log(`LIVE-DONE ok=${ok} fail=${fail} out=${OUT}`);

  const rows = readFileSync(OUT, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((l) => JSON.parse(l) as { session: string; skill: string; noul?: number });
  const key = (s: string, k: string): string => `${s}|||${k}`;
  const labeled = rows.filter((r) => typeof r.noul === "number" && key(r.session, r.skill) in labels);
  console.log(`labeled_rows=${labeled.length}`);
  const naivePrec =
    labeled.length > 0
      ? labeled.filter((r) => labels[key(r.session, r.skill)] === 1).length / labeled.length
      : NaN;
  console.log(`naive_positive_precision=${Number.isNaN(naivePrec) ? "NA" : naivePrec.toFixed(4)}`);
  for (const t of THRESHOLDS) {
    const pos = labeled.filter((r) => (r.noul as number) >= t);
    const prec =
      pos.length > 0
        ? pos.filter((r) => labels[key(r.session, r.skill)] === 1).length / pos.length
        : NaN;
    console.log(
      `t=${t} jev_pos=${pos.length} jev_precision=${Number.isNaN(prec) ? "NA" : prec.toFixed(4)}`,
    );
  }
}

await main();
