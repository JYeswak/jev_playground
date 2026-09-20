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

/**
 * Absence is a claim and must be proven against the record's own keys.
 *
 * Written after the EIGHTH wrong-selector failure in one session (NEGATIVE_EVIDENCE R33 and its
 * correction): a join was attempted, it returned nothing, and "the artifact cannot attribute its
 * fires" was PUBLISHED — while the field sat on the row the whole time under a name nobody
 * dumped. The same shape produced `.distribution` vs `.probabilities` (a constant 0.500 across
 * three runs), `.probability` vs `.noul`, and a `"role": "toolResult"` grep whose spacing matched
 * zero files.
 *
 * Eight repetitions means the written rule is not the fix. This is the mechanical one:
 * you cannot report a field missing without having been shown what IS present.
 *
 * @throws with the full key list whenever the field is absent — so the error message itself is
 *         the key dump the caller failed to run.
 */
export function requireKey(record, key, who = 'record') {
  if (record === null || typeof record !== 'object') {
    throw new Error(`${who}: not an object (${typeof record}); cannot claim '${key}' is absent`);
  }
  if (!(key in record)) {
    throw new Error(`${who}: no '${key}'. Keys present: [${Object.keys(record).sort().join(', ')}]`);
  }
  return record[key];
}

/** Non-throwing counterpart: returns the value and the key list, so absence is always reported WITH evidence. */
export function inspectKey(record, key) {
  const keys = (record && typeof record === 'object') ? Object.keys(record).sort() : [];
  return { present: keys.includes(key), value: record?.[key], keys };
}

/**
 * Skillranker 0/1/2 decision loss. A scoring rule for {recommend, abstain}:
 *   correct pick / correct abstain → 0
 *   false abstain on a positive    → 1
 *   wrong pick / needless pick     → 2
 *
 * Lifted from work/skillranker-eval (their frozen evaluation_policy.v1.json).
 * Always-abstain mean loss equals nPos/n; without the false-abstain cell, silence wins.
 */
export function decisionLoss({ yNonEmpty, abstained, pickInY }) {
  if (yNonEmpty && abstained) return 1;
  if (yNonEmpty && pickInY) return 0;
  if (yNonEmpty) return 2;
  if (abstained) return 0;
  return 2;
}

/** Mean of decisionLoss (or a substitute table) over rows. */
export function meanDecisionLoss(rows, lossFn = decisionLoss) {
  if (!Array.isArray(rows) || rows.length === 0) {
    throw new Error('meanDecisionLoss: empty rows — an empty scan set is not a measurement');
  }
  let total = 0;
  for (const row of rows) total += lossFn(row);
  return total / rows.length;
}

/**
 * PLANTED-INVALID table: charges only wrong *emissions*. Silence costs 0.
 * Always-abstain then scores 0 and "wins". A gate that uses this table is broken.
 */
export function emissionOnlyLoss({ yNonEmpty, abstained, pickInY }) {
  if (abstained) return 0;
  if (yNonEmpty && pickInY) return 0;
  return 2;
}

/** Answer fields the installed SDK actually declares. See docs/demos/SDK-SURFACE.md. */
export const SDK_ANSWER_FIELDS = Object.freeze([
  'noul', 'choice', 'confidence', 'probabilities', 'score', 'legend', 'type',
]);

export const FORBIDDEN_SELECTORS = Object.freeze(['distribution', 'probability']);

/** Refuse a selector the SDK does not declare. Silent defaulting is how AUC 0.500 was fabricated. */
export function assertSdkSelector(kind) {
  if (FORBIDDEN_SELECTORS.includes(kind)) {
    throw new Error(`selector '${kind}' is not in the SDK — there is no .probability or .distribution`);
  }
  if (!SDK_ANSWER_FIELDS.includes(kind)) {
    throw new Error(`selector '${kind}' is not a declared SDK answer field`);
  }
  return kind;
}

/**
 * A Choice decision must not be overridden by a second noul.
 * The skillranker `helpful` ≥ 0.5 gate moved mean loss 0.750 → 0.167 by forcing abstention
 * (math-and-next-level-20260919.md §1.1 / §4(d)). That is a selector bug, not a model result.
 */
export function refuseInventedNoulGate(opts = {}) {
  if (opts && Object.prototype.hasOwnProperty.call(opts, 'helpfulNoul')) {
    throw new Error('invented noul gate: a choice decision must not be overridden by a second noul (SDK-SURFACE / skillranker second-gate defect)');
  }
}
