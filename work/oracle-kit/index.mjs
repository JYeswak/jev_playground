// oracle-kit — the shared scorer for this lane's oracles.
//
// EXTRACTED, NOT PRE-BUILT. docs/demos/ORACLE-PROGRAM.md §7 parked this until the same scorer had
// been hand-rolled three times, because premature extraction is the ceremony. That trigger has now
// fired legitimately: work/compaction-proof, work/router-spec and work/bicameral-gate each carry
// their own copy, and `ripwire . --quality-delta` gates on the duplication.
//
// Every function here exists because a hand-rolled version of it produced a WRONG NUMBER today:
//   auc()        -- a constant score yields an all-ties AUC of exactly 0.500, which is
//                   indistinguishable from a real null. Three router runs reported that.
//   requireBoth()-- a degenerate label (one class empty) yields NaN. The gate arm hit this.
//   field()      -- reading `.distribution` instead of `.probabilities` returns undefined and
//                   scores silence. This is why it THROWS instead of defaulting.
//   feasibility()-- an oracle with no arm that ought to pass cannot tell a broken harness from a
//                   real null. A perfect judge failed an impossible bar before this rule existed.

/** Mann-Whitney AUC. Ties count half. Throws rather than returning NaN on a degenerate label. */
export function auc(scores, labels) {
  requireBoth(labels, 'auc');
  if (scores.length !== labels.length) {
    throw new Error(`auc: ${scores.length} scores vs ${labels.length} labels`);
  }
  if (scores.some((s) => typeof s !== 'number' || Number.isNaN(s))) {
    throw new Error('auc: non-numeric score — a missing field scores silence');
  }
  const A = scores.filter((_, i) => labels[i]);
  const B = scores.filter((_, i) => !labels[i]);
  let wins = 0, ties = 0;
  for (const a of A) for (const b of B) { if (a > b) wins++; else if (a === b) ties++; }
  const value = (wins + 0.5 * ties) / (A.length * B.length);
  // A perfectly constant score is not a measurement; it is a harness defect wearing a null's face.
  const constant = new Set(scores).size === 1;
  return { value, constant, nPos: A.length, nNeg: B.length };
}

/** A label set must contain both classes or nothing can be measured against it. */
export function requireBoth(labels, who = 'oracle') {
  const pos = labels.filter(Boolean).length;
  if (pos === 0 || pos === labels.length) {
    throw new Error(`${who}: degenerate label — ${pos}/${labels.length} positive. Both classes required.`);
  }
}

/** Read an answer field by the names the SDK actually uses. See docs/demos/SDK-SURFACE.md. */
export function field(answer, kind) {
  const v = kind === 'noul' ? answer?.noul
    : kind === 'probabilities' ? answer?.probabilities
      : kind === 'score' ? answer?.score
        : answer?.[kind];
  if (v === undefined) {
    throw new Error(`field: no '${kind}' on ${JSON.stringify(answer)} — there is no .probability or .distribution in this SDK`);
  }
  return v;
}

/**
 * Run an oracle only if its feasibility arm passes.
 * `armScores`/`armLabels` must be a near-deterministic label the pipeline MUST be able to detect.
 * Returns null when the harness is blind, so the caller reports a broken instrument, not a verdict.
 */
export function feasibility(armScores, armLabels, bar = 0.8) {
  const a = auc(armScores, armLabels);
  const ok = a.value >= bar && !a.constant;
  return { ok, auc: a.value, bar, constant: a.constant };
}

/** Expected calibration error of the top answer. Reported alongside accuracy, never instead of it. */
export function ece(confidences, corrects, bins = 10) {
  if (confidences.length !== corrects.length) throw new Error('ece: length mismatch');
  const buckets = new Map();
  confidences.forEach((c, i) => {
    const b = Math.min(Math.floor(c * bins), bins - 1);
    if (!buckets.has(b)) buckets.set(b, []);
    buckets.get(b).push([c, corrects[i] ? 1 : 0]);
  });
  const n = confidences.length;
  let total = 0;
  for (const v of buckets.values()) {
    const meanC = v.reduce((s, [c]) => s + c, 0) / v.length;
    const meanA = v.reduce((s, [, a]) => s + a, 0) / v.length;
    total += (v.length / n) * Math.abs(meanA - meanC);
  }
  return total;
}

/**
 * The anytime-valid e-process from asupersync/src/lab/oracle/eprocess.rs:224-238, reproduced
 * exactly: e_t = e_{t-1} * max(1e-15, 1 + lambda*(x - p0)), reject at e >= 1/alpha.
 * Type-I error is controlled under OPTIONAL STOPPING by Ville's inequality, so it stays valid
 * however many times you look.
 */
export function eProcess(observations, { lambda = 0.5, p0 = 0.5, alpha = 0.05, max = 1e15 } = {}) {
  let e = 1;
  for (const x of observations) {
    e = Math.min(e * Math.max(1e-15, 1 + lambda * ((x ? 1 : 0) - p0)), max);
  }
  return { e, reject: e >= 1 / alpha, threshold: 1 / alpha };
}
