// Reusable skill-router EVAL CONTRACT process.
//
// Mirrors Dicklesworthstone/skillranker tests/eval @ bb52b8f25:
//   frozen 0/1/2 loss, always-abstain + coin-flip controls, ≥0.90 top-1 gate.
// WHAT THIS SCORES: a judge's pick (or abstain) against their labelled Y under
// their loss table. It is NOT a measurement of skillranker the product — that
// requires their `sr` binary. measured_product stays false unless a binary path
// is actually invoked (this module never invokes one).
//
// PREREGISTERED, taken from THEIR policy, not invented here:
//   top-1 precision on positives ≥ 0.90 is an explicit FAIL, not a soft note.
//   diagnostic_synthetic cannot promote even at precision 1.0.
//
// The second-gate defect (a `helpful` noul that forced 11/12 abstentions) is
// not reproduced. Abstain is only `__none__` or a roster too small to ask.

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
export const CONTRACT_DIR = join(here, 'contract');
export const PLANTED_FIXTURE = join(here, 'fixtures', 'planted-wrong-pick.jsonl');

export const NONE = '__none__';
export const PICK_INSTRUCTIONS =
  'Which listed skill should the agent load next for this task, if any?';
export const ABSTAIN_CRITERION = 'No listed skill genuinely helps; answer directly instead.';
export const TOP1_GATE = 0.90;
export const EVAL_SCHEMA = 'jev.skillranker-eval.score.v1';

export const LOSS = {
  correct_recommendation_on_positive: 0,
  correct_no_match_abstention: 0,
  false_abstention_on_positive: 1,
  incorrect_recommendation_on_positive: 2,
  needless_recommendation_on_no_match: 2,
  operationally_unavailable_on_attempted_case: 2,
};

export function loadJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

export function loadJsonl(path) {
  return readFileSync(path, 'utf8')
    .split('\n')
    .filter((line) => line.trim())
    .map((line, i) => {
      try {
        return JSON.parse(line);
      } catch (err) {
        throw new Error(`${path}:${i + 1} is not JSON: ${err.message}`);
      }
    });
}

export function loadPolicy(dir = CONTRACT_DIR) {
  return loadJson(join(dir, 'evaluation_policy.v1.json'));
}

export function loadExpected(dir = CONTRACT_DIR) {
  return loadJson(join(dir, 'expected_values.v1.json'));
}

export function loadCases(dir = CONTRACT_DIR) {
  return loadJsonl(join(dir, 'synthetic_cases.v1.jsonl'));
}

export function loadPlanted(path = PLANTED_FIXTURE) {
  return loadJsonl(path);
}

/** Refuse a drifted loss table rather than score against a remembered one. */
export function assertFrozenLoss(policy = loadPolicy()) {
  const theirs = policy?.loss_policy?.loss_values;
  if (!theirs || typeof theirs !== 'object') {
    throw new Error('policy has no loss_policy.loss_values');
  }
  for (const [key, value] of Object.entries(LOSS)) {
    if (theirs[key] !== value) {
      throw new Error(`loss table drift on ${key}: contract=${theirs[key]} frozen=${value}`);
    }
  }
  const gate = policy?.promotion_requirements?.top_one_precision?.minimum_rate;
  if (gate !== TOP1_GATE) {
    throw new Error(`promotion gate drift: contract=${gate} frozen=${TOP1_GATE}`);
  }
  return theirs;
}

export function rosterOf(c) {
  return Array.isArray(c.visible_roster) ? c.visible_roster : [];
}

export function yOf(c) {
  return Array.isArray(c.acceptable_additional_invocations_y)
    ? c.acceptable_additional_invocations_y
    : [];
}

export function rosterIds(c) {
  return rosterOf(c).map((s) => s.skill_id);
}

/**
 * Criteria map a hook and this harness both send. Empty roster → only `__none__`,
 * which is fewer than two labels: do not call Jev (askJevChoice refuses). That
 * is the installable≠exportable hole on the overflow case: Y names a skill that
 * is not in the exported roster, so the judge cannot pick it.
 */
export function criteriaFromRoster(roster) {
  const criteria = {};
  for (const skill of roster ?? []) {
    const id = skill.skill_id;
    if (!id) continue;
    const kind = skill.usage_kind ?? 'skill';
    const name = skill.invocation_name ?? id;
    criteria[id] = `${kind} — ${name}`;
  }
  criteria[NONE] = ABSTAIN_CRITERION;
  return criteria;
}

export function canAskChoice(criteria) {
  return Object.keys(criteria).length >= 2;
}

export function stateFromCase(c) {
  return {
    task: c.prompt_summary ?? '',
    constraints: c.current_constraints ?? '',
    already_loaded: c.already_available_references ?? [],
  };
}

export function offeredY(c) {
  const ids = new Set(rosterIds(c));
  return yOf(c).filter((id) => ids.has(id));
}

/** Y nonempty but none of Y is in the exported roster. */
export function installableNotOffered(c) {
  const y = yOf(c);
  if (y.length === 0) return false;
  if (offeredY(c).length > 0) return false;
  const relevant = c.visible_roster_summary?.relevant_skill_id;
  return relevant ? y.includes(relevant) : true;
}

/**
 * Score one decision against Y. Mutual exclusion: exactly one loss class.
 * Fail-safe for a missing pick is abstain (loss 1 on a positive, 0 on no-match),
 * never a fabricated skill id. An attempted operational failure is loss 2.
 */
export function scoreDecision({ y = [], pick = null, unavailable = false } = {}) {
  if (unavailable) {
    return {
      loss: LOSS.operationally_unavailable_on_attempted_case,
      why: 'operational unavailable',
      class: 'operationally_unavailable_on_attempted_case',
    };
  }
  const labels = Array.isArray(y) ? y : [];
  const yNonEmpty = labels.length > 0;
  const abstained = pick == null || pick === NONE;
  if (yNonEmpty && abstained) {
    return { loss: LOSS.false_abstention_on_positive, why: 'false abstention', class: 'false_abstention_on_positive' };
  }
  if (yNonEmpty && labels.includes(pick)) {
    return { loss: LOSS.correct_recommendation_on_positive, why: 'correct', class: 'correct_recommendation_on_positive' };
  }
  if (yNonEmpty) {
    return {
      loss: LOSS.incorrect_recommendation_on_positive,
      why: `wrong pick (${pick})`,
      class: 'incorrect_recommendation_on_positive',
    };
  }
  if (abstained) {
    return { loss: LOSS.correct_no_match_abstention, why: 'correct abstention', class: 'correct_no_match_abstention' };
  }
  return {
    loss: LOSS.needless_recommendation_on_no_match,
    why: `needless (${pick})`,
    class: 'needless_recommendation_on_no_match',
  };
}

export function argmax(probabilities) {
  if (!probabilities || typeof probabilities !== 'object') {
    throw new Error("argmax: probabilities missing (there is no .distribution)");
  }
  const entries = Object.entries(probabilities);
  if (entries.length === 0) throw new Error('argmax: empty probabilities');
  entries.sort((a, b) => b[1] - a[1]);
  return { pick: entries[0][0], topP: entries[0][1] };
}

export function summarize(rows) {
  const n = rows.length;
  const positives = rows.filter((r) => r.yNonEmpty);
  const top1Correct = positives.filter((r) => r.class === 'correct_recommendation_on_positive').length;
  const loss = rows.reduce((s, r) => s + r.loss, 0);
  const precision = positives.length ? top1Correct / positives.length : NaN;
  return {
    n,
    positives: positives.length,
    prevalence: n ? positives.length / n : 0,
    top1Correct,
    precision,
    meanLoss: n ? loss / n : NaN,
    totalLoss: loss,
    abstains: rows.filter((r) => r.abstained).length,
    falseAbstentions: rows.filter((r) => r.class === 'false_abstention_on_positive').length,
    wrongPicks: rows.filter((r) => r.class === 'incorrect_recommendation_on_positive').length,
    needless: rows.filter((r) => r.class === 'needless_recommendation_on_no_match').length,
    unavailable: rows.filter((r) => r.class === 'operationally_unavailable_on_attempted_case').length,
    holes: rows.filter((r) => r.installableNotOffered).length,
  };
}

/**
 * Promotion / precision gate. ≥0.90 is an explicit FAIL (exit 2 on --score/--live).
 * diagnostic_synthetic cannot promote even when the rate clears — their forbidden_use.
 */
export function applyPromotionGate(summary, { split = 'diagnostic_synthetic' } = {}) {
  const failures = [];
  const precision = summary.precision;
  if (!(typeof precision === 'number' && !Number.isNaN(precision) && precision >= TOP1_GATE)) {
    failures.push({
      code: 'TOP1_BELOW_GATE',
      message: `top-1 precision ${precision} < ${TOP1_GATE}`,
      got: precision,
      need: TOP1_GATE,
    });
  }
  if (split === 'diagnostic_synthetic') {
    failures.push({
      code: 'SPLIT_FORBIDS_PROMOTION',
      message: 'diagnostic_synthetic cannot promote (their contract forbids it)',
    });
  }
  if (summary.positives < 150) {
    failures.push({
      code: 'COHORT_TOO_SMALL',
      message: `positives ${summary.positives} < 150 (their relevance_cohort minimum)`,
      got: summary.positives,
      need: 150,
    });
  }
  const ratePass = !failures.some((f) => f.code === 'TOP1_BELOW_GATE');
  return {
    ratePass,
    promotable: failures.length === 0,
    fail: !ratePass,
    failures,
  };
}

export function toEvalRow(c, decision, extra = {}) {
  const y = yOf(c);
  const abstained = extra.unavailable ? false : decision.class?.includes('abstention') || extra.pick === NONE || extra.pick == null;
  return {
    schema: EVAL_SCHEMA,
    case_id: c.case_id,
    kind: c.case_kind,
    split: c.split ?? null,
    pick: extra.unavailable ? null : (extra.pick ?? NONE),
    y,
    yNonEmpty: y.length > 0,
    abstained: extra.unavailable ? false : abstained,
    loss: decision.loss,
    why: decision.why,
    class: decision.class,
    roster_ids: rosterIds(c),
    y_in_roster: offeredY(c),
    installableNotOffered: installableNotOffered(c),
    judge: extra.judge ?? 'injected',
    lane: extra.lane ?? 'offline',
    measured_product: extra.measured_product === true,
    binary_path: extra.binary_path ?? null,
    model: extra.model ?? null,
    topP: extra.topP ?? null,
    t: extra.t ?? new Date().toISOString(),
  };
}

export function scoreCase(c, pick, extra = {}) {
  const decision = scoreDecision({ y: yOf(c), pick, unavailable: extra.unavailable === true });
  return toEvalRow(c, decision, { ...extra, pick });
}

export function runAlwaysAbstain(cases, extra = {}) {
  const rows = cases.map((c) => scoreCase(c, NONE, { ...extra, judge: 'always-abstain' }));
  return { rows, summary: summarize(rows) };
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function actionSpace(c) {
  const ids = rosterIds(c);
  return ids.length ? [...ids, NONE] : [NONE];
}

/** Exact expected loss of uniform pick over roster ∪ {__none__}. */
export function expectedCoinFlipLoss(cases) {
  let total = 0;
  for (const c of cases) {
    const options = actionSpace(c);
    const n = options.length;
    let e = 0;
    for (const pick of options) {
      e += scoreDecision({ y: yOf(c), pick }).loss;
    }
    total += e / n;
  }
  return total / cases.length;
}

export function runCoinFlip(cases, { trials = 5000, seed = 1, extra = {} } = {}) {
  const rng = mulberry32(seed);
  const means = [];
  let lastRows = [];
  for (let t = 0; t < trials; t++) {
    const rows = cases.map((c) => {
      const options = actionSpace(c);
      const pick = options[Math.floor(rng() * options.length)];
      return scoreCase(c, pick, { ...extra, judge: 'coin-flip', seed, trial: t });
    });
    lastRows = rows;
    means.push(summarize(rows).meanLoss);
  }
  const mean = means.reduce((s, x) => s + x, 0) / means.length;
  const variance = means.reduce((s, x) => s + (x - mean) ** 2, 0) / means.length;
  return {
    rows: lastRows,
    summary: { ...summarize(lastRows), trials, seed, sampledMean: mean, sampledSd: Math.sqrt(variance) },
    expected: expectedCoinFlipLoss(cases),
  };
}

/**
 * Planted wrong pick. Must score 2. A weakened loss table (wrong pick → 0 or 1)
 * makes this throw — that is the RED arm.
 */
export function runPlanted(cases = loadPlanted()) {
  const rows = [];
  for (const c of cases) {
    const pick = c.planted_pick;
    if (!pick) throw new Error(`${c.case_id}: planted_pick missing`);
    const row = scoreCase(c, pick, { judge: 'planted', lane: 'offline' });
    const expected = c.expected_loss;
    if (expected !== undefined && row.loss !== expected) {
      throw new Error(
        `PLANTED NEGATIVE DID NOT RED: ${c.case_id} pick=${pick} loss=${row.loss} expected=${expected}`,
      );
    }
    if (row.loss !== 2) {
      throw new Error(`PLANTED NEGATIVE DID NOT RED: ${c.case_id} wrong pick scored ${row.loss}, want 2`);
    }
    rows.push(row);
  }
  return { rows, summary: summarize(rows), red: true };
}

/** Map their expected_values.v1.json decision names onto scoreDecision. */
export function scoreExpectedExample(ex) {
  if (ex.decision === 'unavailable_operational_failure') {
    return scoreDecision({ y: [], pick: null, unavailable: true });
  }
  if (ex.decision === 'ranked_in_y') return scoreDecision({ y: ['IN_Y'], pick: 'IN_Y' });
  if (ex.decision === 'ranked_not_in_y') return scoreDecision({ y: ['X'], pick: 'WRONG' });
  if (ex.decision === 'ranked_any_skill') return scoreDecision({ y: [], pick: 'ANY' });
  if (ex.decision === 'abstain') return scoreDecision({ y: ex.y_nonempty ? ['X'] : [], pick: NONE });
  throw new Error(`unknown expected-values decision: ${ex.decision}`);
}

export function verifyExpectedValues(expected = loadExpected()) {
  const mismatches = [];
  for (const ex of expected.loss_examples ?? []) {
    const got = scoreExpectedExample(ex);
    if (got.loss !== ex.loss) {
      mismatches.push({ example_id: ex.example_id, got: got.loss, want: ex.loss });
    }
  }
  const aa = expected.always_abstain_counterexample;
  if (aa?.cohort) {
    const total = aa.cohort.reduce((s, row) => s + (row.y_nonempty ? 1 : 0), 0);
    const mean = total / aa.cohort.length;
    const want = aa.expected.always_abstain_total_loss;
    if (total !== want) mismatches.push({ example_id: 'always_abstain_total', got: total, want });
    if (Math.abs(mean - aa.expected.always_abstain_mean_loss) > 1e-9) {
      mismatches.push({ example_id: 'always_abstain_mean', got: mean, want: aa.expected.always_abstain_mean_loss });
    }
  }
  if (mismatches.length) {
    throw new Error(`expected_values mismatch: ${JSON.stringify(mismatches)}`);
  }
  return { ok: true, examples: (expected.loss_examples ?? []).length };
}

/**
 * The judge shape an omp skill-router hook must call. Same state, same
 * instructions, same `__none__` abstain option. Never a second noul gate.
 * `ask` is injected: ({ state, instructions, classes }) => { ok, choice, ... }.
 */
export async function judgeSkillPick({ roster, task, constraints = '', already_loaded = [], ask, model = null }) {
  if (typeof ask !== 'function') throw new Error('judgeSkillPick: ask is required (injectable)');
  const criteria = criteriaFromRoster(roster);
  const state = { task, constraints, already_loaded };
  if (!canAskChoice(criteria)) {
    return {
      pick: NONE,
      abstained: true,
      asked: false,
      reason: 'roster_too_small_to_ask',
      probabilities: { [NONE]: 1 },
      topP: 1,
      confidence: null,
      model,
      state,
      criteria,
    };
  }
  const result = await ask({ state, instructions: PICK_INSTRUCTIONS, classes: criteria });
  if (!result || result.ok === false) {
    return {
      pick: NONE,
      abstained: true,
      asked: true,
      unavailable: true,
      reason: result?.reason ?? 'ask_failed',
      probabilities: null,
      topP: null,
      confidence: null,
      model: result?.model ?? model,
      state,
      criteria,
    };
  }
  const { pick, topP } = argmax(result.probabilities);
  return {
    pick,
    abstained: pick === NONE,
    asked: true,
    unavailable: false,
    reason: null,
    probabilities: result.probabilities,
    topP,
    confidence: result.confidence ?? null,
    model: result.model ?? model,
    state,
    criteria,
  };
}

export function exportJsonl(path, rows) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${rows.map((r) => JSON.stringify(r)).join('\n')}${rows.length ? '\n' : ''}`);
  return { path, n: rows.length };
}
