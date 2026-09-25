/**
 * Hybrid: numeric predicate decides arithmetic; Jev Noul vetoes only survivors.
 *
 *   node work/jev-triage/hybrid.mjs
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     node --experimental-strip-types work/jev-triage/hybrid.mjs --live
 *
 * Budget: one Noul per numeric-SHIP class that has no cached noul.
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { askJev } from "../../kit/src/client.ts";
import {
  baseline,
  binaryShipConfusion,
  confusion,
  hybridVerdict,
  shipPredicate,
  toState,
} from "./baseline.mjs";

const root = dirname(fileURLToPath(import.meta.url));
const base = JSON.parse(readFileSync(join(root, "cases.json"), "utf8"));
const extra = JSON.parse(readFileSync(join(root, "extra-cases.json"), "utf8"));
const classify = JSON.parse(readFileSync(join(root, "r-classify.json"), "utf8"));
const prior = JSON.parse(readFileSync(join(root, "runs/2026-09-20T221837415Z.json"), "utf8"));

const cases = [...base.cases, ...extra.cases];
const noulCache = Object.fromEntries(prior.rows.map((r) => [r.id, r.noul]));

const NOUL_Q = {
  defect:
    "this command shape is a DEFECT, not ordinary correct usage of the tool",
};

const live = process.argv.includes("--live");

const survivors = cases.filter((c) => shipPredicate(c));
const needCall = survivors.filter((c) => noulCache[c.id] == null);
console.log(
  `BUDGET calls=${needCall.length}  survivors=${survivors.length}/${cases.length}  cached=${survivors.length - needCall.length}  reason=noul veto only on numeric SHIP`,
);
console.log(
  `PART1 semantic_callable=${classify.n_semantic_callable} not_a_class=${classify.n_not_a_class} honest_share=${classify.honest_share}`,
);
if (needCall.length) {
  console.log(`need_call ${needCall.map((c) => c.id).join(",")}`);
}

async function fillNoul() {
  if (!live) {
    if (needCall.length) {
      console.log(`live lane: NOT_RUN; ${needCall.length} survivors lack noul`);
    }
    return;
  }
  for (const c of needCall) {
    const r = await askJev({
      state: toState(c),
      questions: NOUL_Q,
      model: "jev-1.13.0",
      timeoutMs: 20000,
    });
    if (!r.ok) {
      console.log(`FAIL ${c.id} ${r.reason} ${r.error}`);
      continue;
    }
    noulCache[c.id] = r.scores.defect;
    console.log(`LIVE ${c.id} noul=${r.scores.defect.toFixed(3)}`);
  }
}

function scoreAt(t) {
  const rows = [];
  let calls = 0;
  for (const c of cases) {
    const noul = noulCache[c.id] ?? null;
    const h = hybridVerdict(c, noul, t);
    if (h.missing) continue;
    if (h.called) calls += 1;
    rows.push({
      id: c.id,
      gold: c.gold,
      gold_noul: c.gold_noul,
      row_kind: c.row_kind,
      baseline: baseline(c),
      noul,
      hybrid: h.verdict,
      veto: h.veto,
      called: h.called,
    });
  }
  const binH = binaryShipConfusion(rows.map((r) => ({ gold: r.gold, pred: r.hybrid })), "pred");
  const binB = binaryShipConfusion(rows.map((r) => ({ gold: r.gold, pred: r.baseline })), "pred");
  const fiveH = confusion(rows.map((r) => ({ gold: r.gold, pred: r.hybrid })), "pred");
  const fiveB = confusion(rows.map((r) => ({ gold: r.gold, pred: r.baseline })), "pred");
  const sem = rows.filter((r) => r.row_kind === "semantic");
  const semH = sem.filter((r) => r.hybrid === r.gold).length;
  const semB = sem.filter((r) => r.baseline === r.gold).length;
  const noulSem = sem.filter((r) => typeof r.noul === "number");
  const noulSemOk = noulSem.filter((r) => (r.noul >= t) === r.gold_noul).length;
  return { t, n: rows.length, calls, binH, binB, fiveH, fiveB, semN: sem.length, semH, semB, noulSem: { n: noulSem.length, correct: noulSemOk }, rows };
}

await fillNoul();

const scored = scoreAt(0.5);
console.log(`n=${scored.n}  hybrid@0.5 ${scored.binH.correct}/${scored.binH.n} TP=${scored.binH.tp} FP=${scored.binH.fp} FN=${scored.binH.fn}`);
console.log(`          baseline     ${scored.binB.correct}/${scored.binB.n} TP=${scored.binB.tp} FP=${scored.binB.fp} FN=${scored.binB.fn}`);
console.log(`          5-way hybrid ${scored.fiveH.correct}/${scored.fiveH.n}  baseline ${scored.fiveB.correct}/${scored.fiveB.n}`);
console.log(`          semantic choice hybrid ${scored.semH}/${scored.semN}  baseline ${scored.semB}/${scored.semN}`);
console.log(`          noul semantic @0.5 ${scored.noulSem.correct}/${scored.noulSem.n}`);

console.log("SEMANTIC rows @0.5");
for (const r of scored.rows.filter((x) => x.row_kind === "semantic")) {
  console.log(
    `  ${r.id} gold=${r.gold} base=${r.baseline} hybrid=${r.hybrid} noul=${r.noul ?? "NA"} veto=${r.veto}`,
  );
}

const sweep = [];
for (let i = 0; i <= 20; i++) {
  const t = i / 20;
  const s = scoreAt(t);
  sweep.push({
    t,
    correct: s.binH.correct,
    fp: s.binH.fp,
    fn: s.binH.fn,
    tp: s.binH.tp,
    semH: s.semH,
    noulSem: s.noulSem.correct,
  });
}
console.log("calibration t  correct fp fn semH noulSemOk");
for (const s of sweep) {
  console.log(
    `  t=${s.t.toFixed(2)}  ${s.correct}/${scored.n}  FP=${s.fp} FN=${s.fn}  sem=${s.semH} noul=${s.noulSem}`,
  );
}
sweep.sort((a, b) => b.correct - a.correct || a.fn - b.fn || a.fp - b.fp);
const best = sweep[0];
console.log(`BEST_T ${best.t} correct=${best.correct}/${scored.n} FP=${best.fp} FN=${best.fn}`);

const beatsBoth =
  scored.binH.correct > scored.binB.correct && scored.semH > scored.semB;
console.log(
  `SEAT ${beatsBoth ? "EARNED" : "NOT-EARNED-AS-REPLACEMENT"}  hybrid_beats_numeric_binary=${scored.binH.correct > scored.binB.correct}  hybrid_beats_semantic=${scored.semH > scored.semB}`,
);
console.log(
  `COST 1 noul per numeric-SHIP candidate; this set ${survivors.length} calls if cold, ${needCall.length} this run; mining pipeline = paid call only after hits/rate/FP/concentration pass`,
);

const receipt = {
  at: new Date().toISOString(),
  n: scored.n,
  semantic_callable: classify.n_semantic_callable,
  budget_this_run: needCall.length,
  survivors: survivors.map((c) => c.id),
  noulCache,
  hybrid_0_5: {
    binary: scored.binH,
    five: { correct: scored.fiveH.correct, n: scored.fiveH.n },
    semantic: { correct: scored.semH, n: scored.semN },
  },
  baseline: {
    binary: scored.binB,
    five: { correct: scored.fiveB.correct, n: scored.fiveB.n },
    semantic: { correct: scored.semB, n: scored.semN },
  },
  best_t: best,
  sweep,
  mapping: base.choice_gold_mapping,
};
const runDir = join(root, "runs");
mkdirSync(runDir, { recursive: true });
const out = join(runDir, `hybrid-${new Date().toISOString().replaceAll(":", "").replaceAll(".", "")}.json`);
writeFileSync(out, JSON.stringify(receipt, null, 2));
console.log(`receipt ${out}`);
