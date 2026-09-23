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

/**
 * Select-on-A / report-on-B, after `jev-phishing-bench/bench/protocol.py`.
 * The 2 000 emails are cut into two stratified halves at a fixed seed. Everything involving a
 * choice (best single signal, its threshold, combiner weights) is decided on half A only;
 * every published number comes from half B. A single-signal input cannot gain from selection:
 * `selectSingleSignal` returns it with `selected: false`.
 */

/** Deterministic PRNG so the split is a pure function of the seed. */
export function mulberry32(seed) {
  if (!Number.isInteger(seed)) throw new Error('mulberry32: integer seed required');
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Stratified halves: each class split in sorted-id order at a seeded permutation. */
export function stratifiedHalves(ids, labels, seed = 1) {
  if (ids.length !== labels.length) {
    throw new Error(`stratifiedHalves: ${ids.length} ids vs ${labels.length} labels`);
  }
  requireBoth(labels, 'stratifiedHalves');
  const rng = mulberry32(seed);
  const a = [], b = [];
  for (const cls of [true, false]) {
    const group = ids.filter((_, i) => labels[i] === cls).sort();
    const perm = group.map((id) => [rng(), id]).sort((x, y) => x[0] - y[0]).map(([, id]) => id);
    const half = Math.floor(perm.length / 2);
    a.push(...perm.slice(0, half));
    b.push(...perm.slice(half));
  }
  return { a, b };
}

/** Threshold on one score maximising accuracy. Mirrors protocol.py: candidates start at 0.5, ties keep the lowest. */
export function bestThreshold(y, s) {
  if (y.length !== s.length || y.length === 0) {
    throw new Error('bestThreshold: y and s must be non-empty and aligned');
  }
  const values = [...new Set(s)].sort((x, y) => x - y);
  if (values.length === 1) return 0.5;
  let bestT = 0.5, bestAcc = -1;
  for (const t of [0.5, ...values.slice(0, -1).map((v, k) => (v + values[k + 1]) / 2)].sort((x, y) => x - y)) {
    let hit = 0;
    for (let i = 0; i < y.length; i++) if ((s[i] >= t ? 1 : 0) === y[i]) hit++;
    const acc = hit / y.length;
    if (acc > bestAcc) { bestAcc = acc; bestT = t; }
  }
  return bestT;
}

/**
 * Pick the best single signal by AUROC on A, threshold it on A, report accuracy/AUROC on B.
 * `rows`: [{id, label: 0|1|bool, feats: {name: number}}]. With one signal there is nothing to
 * select: returns it with `selected: false` (the planted negative — no gain is possible).
 */
export function selectSingleSignal(rows, names, seed = 1) {
  if (!Array.isArray(names) || names.length === 0) throw new Error('selectSingleSignal: at least one signal name required');
  for (const r of rows) for (const n of names) {
    if (typeof r.feats?.[n] !== 'number' || Number.isNaN(r.feats[n])) {
      throw new Error(`selectSingleSignal: missing score for ${n} on ${r.id} — a missing field scores silence`);
    }
  }
  const ids = rows.map((r) => r.id);
  const labels = rows.map((r) => Boolean(r.label));
  const { a, b } = stratifiedHalves(ids, labels, seed);
  const inA = new Set(a), inB = new Set(b);
  const yA = rows.filter((r) => inA.has(r.id)).map((r) => Number(r.label));
  const yB = rows.filter((r) => inB.has(r.id)).map((r) => Number(r.label));
  const sA = (n) => rows.filter((r) => inA.has(r.id)).map((r) => r.feats[n]);
  const sB = (n) => rows.filter((r) => inB.has(r.id)).map((r) => r.feats[n]);
  let feature = names[0], bestAuc = -1;
  const aucA = {};
  for (const n of names) {
    const v = auc(sA(n), rows.filter((r) => inA.has(r.id)).map((r) => Boolean(r.label))).value;
    aucA[n] = v;
    if (v > bestAuc) { bestAuc = v; feature = n; }
  }
  const t = bestThreshold(yA, sA(feature));
  const predB = sB(feature).map((s) => (s >= t ? 1 : 0));
  const accB = predB.filter((p, i) => p === yB[i]).length / yB.length;
  const accA = sA(feature).filter((s, i) => (s >= t ? 1 : 0) === yA[i]).length / yA.length;
  return {
    seed, nA: a.length, nB: b.length, feature, threshold: t, selected: names.length > 1,
    accuracyA: accA, accuracyB: accB, aurocB: auc(sB(feature), rows.filter((r) => inB.has(r.id)).map((r) => Boolean(r.label))).value, aucA,
  };
}

/** Sigmoid. */
export function sigmoid(z) { return 1 / (1 + Math.exp(-z)); }

/**
 * Logistic combiner fit on A (bias term included, zero init, fixed schedule — deterministic).
 * Mirrors protocol.py's fit-weights-on-A step for small feature counts. Returns weights with bias first.
 */
export function fitLogistic(XA, yA, { iters = 2000, lr = 0.5 } = {}) {
  if (XA.length === 0) throw new Error('fitLogistic: empty training set');
  const d = XA[0].length;
  const w = new Array(d + 1).fill(0);
  for (let it = 0; it < iters; it++) {
    const grad = new Array(d + 1).fill(0);
    for (let i = 0; i < XA.length; i++) {
      let z = w[0];
      for (let j = 0; j < d; j++) z += w[j + 1] * XA[i][j];
      const err = sigmoid(z) - yA[i];
      grad[0] += err;
      for (let j = 0; j < d; j++) grad[j + 1] += err * XA[i][j];
    }
    for (let j = 0; j <= d; j++) w[j] -= (lr * grad[j]) / XA.length;
  }
  return w;
}

/** Score rows with weights from fitLogistic (bias first). */
export function scoreLogistic(w, X) {
  return X.map((row) => {
    let z = w[0];
    for (let j = 0; j < row.length; j++) z += w[j + 1] * row[j];
    return sigmoid(z);
  });
}
