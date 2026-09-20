/**
 * random-judge — Delta 3 mechanism (Wave B §6 Pass 5 of P1-P12): the chance
 * floor any judge must beat, plus the own-constant baseline.
 *
 * randomBaseline: seeded no-signal judge. Shuffles the observed truth labels
 * (Fisher-Yates under a deterministic mulberry32 PRNG) and scores the
 * permutation against truth. On a skewed set this lands near the majority
 * rate — chance, not skill — which is exactly the point: a real judge that
 * cannot beat this number has found no signal.
 *
 * ownConstant: majority-label accuracy — answering the majority every time.
 * The commit-judge receipt is the standing example of why this bar bites:
 * 30/31 correct but yes on 31/31 against a 30/31 always-yes constant means
 * the question never beat its own constant.
 *
 * Both pure, offline, dependency-free. No Jev calls, no network, no I/O.
 * cases: array of bare labels OR objects holding the label under `truthKey`.
 */

/** Default seed — pinned so the chance floor is reproducible across runs. */
export const DEFAULT_SEED = 20260920;

/** Deterministic PRNG (mulberry32). Seed any uint32; same seed → same stream. */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Extract the truth label from a bare value or a { [truthKey]: label } case. */
function truthOf(c, truthKey) {
  if (c !== null && typeof c === "object" && truthKey in c) return c[truthKey];
  return c;
}

/**
 * No-signal random judge: seeded shuffle of the observed truth labels.
 *
 * @param {object} args
 * @param {Array<unknown>} args.cases - bare labels or objects
 * @param {string} [args.truthKey="truth"] - label field for object cases
 * @param {number} [args.seed=DEFAULT_SEED] - PRNG seed; same seed → identical output
 * @returns {{ predicted: unknown[], accuracy: number }}
 */
export function randomBaseline({ cases = [], truthKey = "truth", seed = DEFAULT_SEED } = {}) {
  const list = Array.isArray(cases) ? cases : [];
  const truths = list.map((c) => truthOf(c, truthKey));
  const predicted = truths.slice();
  const rand = mulberry32(seed);
  for (let i = predicted.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [predicted[i], predicted[j]] = [predicted[j], predicted[i]];
  }
  let correct = 0;
  for (let i = 0; i < truths.length; i++) {
    if (predicted[i] === truths[i]) correct += 1;
  }
  return { predicted, accuracy: truths.length === 0 ? 0 : correct / truths.length };
}

/**
 * Own-constant baseline: accuracy of always answering the majority label.
 *
 * @param {object} args
 * @param {Array<unknown>} args.cases - bare labels or objects
 * @param {string} [args.truthKey="truth"] - label field for object cases
 * @returns {{ label: unknown, accuracy: number, count: number, total: number }}
 *   label: majority label (first-seen wins ties); accuracy: its share.
 */
export function ownConstant({ cases = [], truthKey = "truth" } = {}) {
  const list = Array.isArray(cases) ? cases : [];
  const counts = new Map();
  for (const c of list) {
    const t = truthOf(c, truthKey);
    counts.set(t, (counts.get(t) ?? 0) + 1);
  }
  let label = undefined;
  let count = 0;
  for (const [t, n] of counts) {
    if (n > count) {
      label = t;
      count = n;
    }
  }
  return { label, accuracy: list.length === 0 ? 0 : count / list.length, count, total: list.length };
}
