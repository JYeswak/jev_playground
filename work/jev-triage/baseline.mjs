/** Deterministic rule-class triage. The predicate the dispatch named, plus a
 *  5-way cascade so a confusion matrix has a class for every non-ship.
 *
 *  SHIP iff hits>=50 AND rate<=5 AND (FP<=0.30 OR unlabelled) AND concentration<0.5
 *  Missing rate / FP / concentration do not fail their clause (unmeasured ≠ failing).
 *
 *  Cascade (first match): hits<50 → TOO_RARE; rate>5 → NUISANCE; labelled FP>0.30 →
 *  LOW_PRECISION; concentration>=0.5 → UNDERPOWERED; else SHIP.
 */
export const VERDICTS = [
  "SHIP",
  "REFUSE_TOO_RARE",
  "REFUSE_NUISANCE",
  "REFUSE_LOW_PRECISION",
  "UNDERPOWERED",
];

export function shipPredicate(c) {
  if (c.hits < 50) return false;
  if (c.rate != null && c.rate > 5) return false;
  if (c.FP != null && c.FP > 0.3) return false;
  if (
    c.concentration_top_session_share != null &&
    c.concentration_top_session_share >= 0.5
  ) {
    return false;
  }
  return true;
}

export function baseline(c) {
  if (c.hits < 50) return "REFUSE_TOO_RARE";
  if (c.rate != null && c.rate > 5) return "REFUSE_NUISANCE";
  if (c.FP != null && c.FP > 0.3) return "REFUSE_LOW_PRECISION";
  if (
    c.concentration_top_session_share != null &&
    c.concentration_top_session_share >= 0.5
  ) {
    return "UNDERPOWERED";
  }
  return "SHIP";
}

export function toState(c) {
  return {
    name: c.name,
    description: c.description,
    predicate: c.predicate,
    examples: c.examples,
    hits: c.hits,
    N: c.N,
    rate: c.rate,
    FP: c.FP,
    labelled_n: c.labelled_n,
    seed: c.seed,
    concentration_top_session_share: c.concentration_top_session_share,
    corpus_is_authored_by_us: c.corpus_is_authored_by_us,
    is_defect_or_routing: c.is_defect_or_routing,
  };
}

/** Numeric predicate cannot answer "is this ordinary correct usage?". */
export function baselineNoul() {
  return { answerable: false, reason: "noul asks semantics; the numeric predicate has no opinion" };
}

/** Numeric first. Jev noul vetoes only survivors. Missing noul on a survivor is not a silent ship in live scoring. */
export function hybridVerdict(c, noul, t = 0.5) {
  if (!shipPredicate(c)) {
    return { verdict: baseline(c), called: false, veto: false };
  }
  if (noul == null || typeof noul !== "number") {
    return { verdict: null, called: true, veto: false, missing: true };
  }
  if (noul < t) {
    return { verdict: "REFUSE_NUISANCE", called: true, veto: true };
  }
  return { verdict: "SHIP", called: true, veto: false };
}

export function confusion(rows, predKey, goldKey = "gold") {
  const labels = VERDICTS;
  const matrix = Object.fromEntries(
    labels.map((a) => [a, Object.fromEntries(labels.map((b) => [b, 0]))]),
  );
  let correct = 0;
  for (const row of rows) {
    const gold = row[goldKey];
    const pred = row[predKey];
    if (!labels.includes(gold) || !labels.includes(pred)) continue;
    matrix[gold][pred] += 1;
    if (gold === pred) correct += 1;
  }
  return { n: rows.length, correct, matrix };
}

export function binaryShipConfusion(rows, predKey, goldKey = "gold") {
  let tp = 0, fp = 0, tn = 0, fn = 0;
  for (const row of rows) {
    const goldShip = row[goldKey] === "SHIP";
    const predShip = row[predKey] === "SHIP";
    if (goldShip && predShip) tp += 1;
    else if (!goldShip && predShip) fp += 1;
    else if (!goldShip && !predShip) tn += 1;
    else fn += 1;
  }
  return { n: rows.length, tp, fp, tn, fn, correct: tp + tn };
}
