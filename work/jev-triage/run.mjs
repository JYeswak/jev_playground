/**
 * Fair rule-class triage: Choice + Noul on name/description/predicate/examples/numbers.
 *
 *   node work/jev-triage/run.mjs
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     node --experimental-strip-types work/jev-triage/run.mjs --live
 *
 * Budget live: 19 calls (Choice + Noul parallel per case).
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { askJevBundle } from "../jev-client/src/index.ts";
import {
  VERDICTS,
  baseline,
  baselineNoul,
  binaryShipConfusion,
  confusion,
  toState,
} from "./baseline.mjs";

const root = dirname(fileURLToPath(import.meta.url));
const { cases, choice_gold_mapping } = JSON.parse(
  readFileSync(join(root, "cases.json"), "utf8"),
);

export const CHOICE_INSTRUCTIONS =
  "Pick the mutually-exclusive triage verdict for this candidate rule class. You have the class name, a one-line description, the detection predicate, three real examples, and the measured numbers. SHIP = encode as a TTSR rule. REFUSE_TOO_RARE = fewer than 50 occurrences. REFUSE_NUISANCE = wallpaper OR the pattern is ordinary correct usage of the tool, not a defect. REFUSE_LOW_PRECISION = labelled FP above 0.30. UNDERPOWERED = cannot decide: one-session concentration, wrong observation channel, or tiny labelled_n.";

export const CHOICE_CLASSES = {
  SHIP: "Encode this class as a TTSR rule.",
  REFUSE_TOO_RARE: "Below the occurrence floor.",
  REFUSE_NUISANCE: "Wallpaper, or ordinary correct usage rather than a defect.",
  REFUSE_LOW_PRECISION: "Labelled false-positive rate above 0.30.",
  UNDERPOWERED: "Evidence cannot support ship-or-refuse.",
};

export const NOUL_INSTRUCTIONS =
  "this command shape is a DEFECT, not ordinary correct usage of the tool";

const NOUL_CRITERIA = {
  true: "The examples are a real defect worth warning an agent about.",
  false: "The examples are ordinary correct usage of the tool (or a file-path claim one ls settles).",
};

function printMatrix(title, { n, correct, matrix }) {
  const labels = VERDICTS;
  const hdr = labels.map((l) => l.replace("REFUSE_", "").slice(0, 8).padStart(8)).join(" ");
  console.log(`${title}  ${correct}/${n}`);
  console.log(`gold\\pred ${hdr}`);
  for (const g of labels) {
    const row = labels.map((p) => String(matrix[g][p]).padStart(8)).join(" ");
    console.log(`${g.replace("REFUSE_", "").slice(0, 8).padStart(8)} ${row}`);
  }
}

function noulPred(noul) {
  return noul >= 0.5;
}

// Single attempt per row. Retry is SDK-owned (askJevBundle `retry` option,
// default maxRetries 0); the hand-rolled 429/503/529 regex loop is deleted.
// A failed row records FAIL and the run continues — per-row isolation kept.
async function askOnce(opts) {
  return askJevBundle(opts);
}

const live = process.argv.includes("--live");
const scored = cases.map((c) => ({
  id: c.id,
  gold: c.gold,
  gold_noul: c.gold_noul,
  row_kind: c.row_kind,
  baseline: baseline(c),
  baseline_noul: baselineNoul(),
  state: toState(c),
}));

console.log(`cases=${scored.length}  lane=${live ? "live" : "offline"}`);
console.log(`choice_gold_mapping ${JSON.stringify(choice_gold_mapping)}`);
printMatrix(
  "baseline 5-way",
  confusion(scored.map((r) => ({ gold: r.gold, pred: r.baseline })), "pred"),
);
printBinary(
  "baseline SHIP vs rest",
  binaryShipConfusion(scored.map((r) => ({ gold: r.gold, pred: r.baseline })), "pred"),
);
console.log("baseline noul: UNANSWERABLE 19/19 (numeric predicate has no opinion on defect-vs-usage)");
const semantic = scored.filter((r) => r.row_kind === "semantic");
const arithmetic = scored.filter((r) => r.row_kind === "arithmetic");
console.log(
  `split semantic=${semantic.length} (noul gold false; baseline still SHIPS them) arithmetic=${arithmetic.length}`,
);
for (const r of semantic) {
  console.log(`  SEMANTIC ${r.id} gold_choice=${r.gold} gold_noul=${r.gold_noul} baseline_choice=${r.baseline}`);
}

if (!live) {
  console.log("live lane: NOT_RUN (pass --live under infisical run)");
  process.exit(0);
}

const BUDGET = cases.length;
console.log(
  `BUDGET calls=${BUDGET} (Choice+Noul parallel per case; not 38)  offline_insufficient=semantics not in the numbers`,
);

const questions = {
  verdict: { type: "choice", instructions: CHOICE_INSTRUCTIONS, criteria: CHOICE_CLASSES },
  defect: { type: "noul", instructions: NOUL_INSTRUCTIONS, criteria: NOUL_CRITERIA },
};

const liveRows = [];
let resolvedModel = null;
for (const row of scored) {
  const result = await askOnce({
    state: row.state,
    questions,
    model: "jev-1.13.0",
    timeoutMs: 20000,
  });
  resolvedModel = result.resolvedModel;
  const verdictAns = result.answers.verdict;
  const defectAns = result.answers.defect;
  const choice = verdictAns && typeof verdictAns === "object" ? verdictAns.choice : null;
  const confidence = verdictAns && typeof verdictAns === "object" ? verdictAns.confidence : null;
  const noul = defectAns && typeof defectAns === "object" ? defectAns.noul : null;
  if (typeof choice !== "string" || typeof noul !== "number") {
    console.log(`FAIL ${row.id} malformed answers`);
    liveRows.push({ ...row, ok: false, reason: "no-answers" });
    continue;
  }
  const rec = {
    id: row.id,
    gold: row.gold,
    gold_noul: row.gold_noul,
    row_kind: row.row_kind,
    baseline: row.baseline,
    jev: choice,
    confidence,
    noul,
    jev_noul: noulPred(noul),
    latencyMs: result.latencyMs,
    ok: true,
  };
  liveRows.push(rec);
  console.log(
    `${row.id} [${row.row_kind}] gold=${row.gold} base=${row.baseline} jev=${choice} conf=${Number(confidence).toFixed(3)} noul=${noul.toFixed(3)} gold_noul=${row.gold_noul}`,
  );
}

const jevOk = liveRows.filter((r) => r.ok && r.jev);
printMatrix(
  "jev 5-way",
  confusion(jevOk.map((r) => ({ gold: r.gold, pred: r.jev })), "pred"),
);
printBinary(
  "jev SHIP vs rest",
  binaryShipConfusion(jevOk.map((r) => ({ gold: r.gold, pred: r.jev })), "pred"),
);

function noulScore(rows) {
  const ok = rows.filter((r) => r.ok && typeof r.noul === "number");
  const correct = ok.filter((r) => r.jev_noul === r.gold_noul).length;
  return { n: ok.length, correct };
}

const noulAll = noulScore(jevOk);
const noulSem = noulScore(jevOk.filter((r) => r.row_kind === "semantic"));
const noulAri = noulScore(jevOk.filter((r) => r.row_kind === "arithmetic"));
console.log(`jev noul all ${noulAll.correct}/${noulAll.n}  (threshold 0.5)`);
console.log(`jev noul SEMANTIC ${noulSem.correct}/${noulSem.n}  ← seat under test`);
console.log(`jev noul ARITHMETIC ${noulAri.correct}/${noulAri.n}`);
console.log("baseline noul SEMANTIC UNANSWERABLE 0/3 (cannot answer)");

console.log("SEMANTIC ROWS");
for (const r of jevOk.filter((r) => r.row_kind === "semantic")) {
  const noulOk = r.jev_noul === r.gold_noul ? "noul-ok" : "noul-WRONG";
  console.log(
    `  ${r.id} gold_choice=${r.gold} jev_choice=${r.jev} gold_noul=${r.gold_noul} jev_noul=${r.jev_noul} noul=${r.noul.toFixed(3)} ${noulOk}`,
  );
}

const disagreements = jevOk.filter((r) => r.jev !== r.baseline);
console.log(`DISAGREEMENTS choice baseline-vs-jev ${disagreements.length}`);

const calibrated = [...jevOk].sort((a, b) => b.noul - a.noul);
console.log("noul calibration high→low; WRONG = jev_noul ≠ gold_noul");
for (const r of calibrated) {
  const mark = r.jev_noul === r.gold_noul ? "ok" : "WRONG";
  console.log(`  noul=${r.noul.toFixed(3)} ${mark} [${r.row_kind}] ${r.id}`);
}

const jevCorrect = jevOk.filter((r) => r.jev === r.gold).length;
const baseCorrect = scored.filter((r) => r.baseline === r.gold).length;
const seat =
  noulSem.correct > 0 && noulSem.n === 3 && noulSem.correct >= 2
    ? noulSem.correct === 3
      ? "EARNED"
      : "PARTIAL"
    : "NOT-EARNED";
console.log(
  `SEAT ${seat}  jev_choice ${jevCorrect}/${jevOk.length}  baseline_choice ${baseCorrect}/${scored.length}  jev_noul_semantic ${noulSem.correct}/${noulSem.n}  model=${resolvedModel ?? "UNMEASURED"}  calls=${jevOk.length}`,
);

function printBinary(title, b) {
  console.log(`${title}  ${b.correct}/${b.n}  TP=${b.tp} FP=${b.fp} TN=${b.tn} FN=${b.fn}`);
}

const receipt = {
  at: new Date().toISOString(),
  requested_model: "jev-1.13.0",
  resolved_model: resolvedModel,
  calls: jevOk.length,
  budget: BUDGET,
  choice_gold_mapping,
  jev_choice_correct: jevCorrect,
  baseline_choice_correct: baseCorrect,
  jev_noul_semantic: noulSem,
  jev_noul_arithmetic: noulAri,
  baseline_noul: "UNANSWERABLE",
  seat,
  rows: liveRows.map(({ state, baseline_noul, ...rest }) => rest),
};
const runDir = join(root, "runs");
mkdirSync(runDir, { recursive: true });
const out = join(runDir, `${new Date().toISOString().replaceAll(":", "").replaceAll(".", "")}.json`);
writeFileSync(out, JSON.stringify(receipt, null, 2));
console.log(`receipt ${out}`);
