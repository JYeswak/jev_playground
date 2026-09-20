/**
 * measure-kit: the lane's standard question-measurement arithmetic, in one place.
 *
 * Every measure*.mjs tonight reimplemented the same table with drift: some printed the coin
 * flip, some the own-constant bar, only the later ones flagged near-threshold verdicts —
 * and that drift already produced one DISCRIMINATES the conductor had to correct to WEAK.
 * The gate this serves: no question-set verdict may be quoted without the own-constant bar
 * and the near-threshold count. Retirement: when measurement stops being how this lane
 * decides things.
 *
 * Verdict rule (settled tonight, stricter than the early units): for each question,
 *   DEGENERATE if it says the same thing on every case;
 *   else DISCRIMINATES iff correct > best_constant + near_threshold_count;
 *   else WEAK.
 * The near-threshold penalty exists because a verdict decided by 0.04 is a verdict the
 * threshold made, not the model. A kit standardises the arithmetic, not the cases.
 *
 * Pure core (gradeQuestion) is unit-tested with a fake asker; measure() drives live calls
 * through an injectable ask() defaulting to askJev.
 */
import { askJev } from './src/index.ts';

export const DEFAULT_THRESHOLD = 0.5;
export const NEAR_WINDOW = 0.1;

/**
 * Grade one question from run-1 samples. Pure; no I/O.
 * samples: [{score: number, truth: bool}]. Returns the standard row fields + verdict.
 */
export function gradeQuestion(samples, threshold = DEFAULT_THRESHOLD) {
  const valid = samples.filter((s) => typeof s.score === 'number' && typeof s.truth === 'boolean');
  const asked = valid.length;
  let correct = 0, yes = 0, trueCount = 0, near = 0;
  const scores = [];
  for (const s of valid) {
    const said = s.score >= threshold;
    scores.push(s.score);
    if (said) yes += 1;
    if (s.truth) trueCount += 1;
    if (said === s.truth) correct += 1;
    if (Math.abs(s.score - threshold) < NEAR_WINDOW) near += 1;
  }
  const alwaysNo = asked - trueCount;
  const alwaysYes = trueCount;
  const best = Math.max(alwaysNo, alwaysYes);
  const spread = scores.length ? Math.max(...scores) - Math.min(...scores) : 0;
  const constant = yes === 0 || yes === asked;
  const verdict = constant ? 'DEGENERATE' : (correct > best + near ? 'DISCRIMINATES' : 'WEAK');
  return { correct, asked, yes, trueCount, alwaysNo, alwaysYes, best, spread, near, scores, verdict };
}

const defaultAsk = (opts) => askJev(opts);

/**
 * Run the standard measurement.
 * cases: [{name, state, truth: {qkey: bool}}]. questions: {qkey: instructions}.
 * ask: async ({state, questions, timeoutMs}) -> {ok, scores?} — inject a fake in tests.
 * Prints the standard table; returns {perQuestion, flips, errors, rows}.
 */
export async function measure({ cases, questions, runs = 3, threshold = DEFAULT_THRESHOLD, timeoutMs = 8000, ask = defaultAsk }) {
  const keys = Object.keys(questions);
  const store = {};
  for (const c of cases) for (const k of keys) store[`${c.name}/${k}`] = [];
  const rows = [];
  const thin = [];
  let errors = 0;

  for (let run = 1; run <= runs; run++) {
    for (const c of cases) {
      const result = await ask({ state: c.state, questions, timeoutMs });
      if (!result.ok) {
        rows.push(`run${run} ${c.name}: ERROR ${result.reason} ${result.error}`);
        errors += 1;
        continue;
      }
      for (const k of keys) {
        const score = result.scores[k];
        if (typeof score !== 'number') continue;
        store[`${c.name}/${k}`].push(score);
        if (run === 1) {
          const truth = c.truth[k];
          const said = score >= threshold;
          if (Math.abs(score - threshold) < NEAR_WINDOW) thin.push(`${c.name}/${k} @ ${score.toFixed(2)}`);
          rows.push(`${c.name.padEnd(28)} ${k.padEnd(19)} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(truth).padEnd(5)} ${said === truth ? 'HIT' : 'MISS'}`);
        }
      }
    }
  }

  console.log(rows.join('\n'));

  let flips = 0;
  const driftLines = [];
  for (const c of cases) {
    for (const k of keys) {
      const ss = store[`${c.name}/${k}`];
      if (ss.length < 2) continue;
      const spread = Math.max(...ss) - Math.min(...ss);
      const v = new Set(ss.map((s) => s >= threshold));
      if (v.size > 1) flips += 1;
      driftLines.push(`  ${c.name}/${k}: ${ss.map((s) => s.toFixed(2)).join(' ')} spread=${spread.toFixed(2)}${v.size > 1 ? ' FLIP' : ''}`);
    }
  }
  console.log('\ndrift:');
  console.log(driftLines.join('\n'));
  console.log(`verdict flips: ${flips}`);

  console.log('\nper question (DISCRIMINATES requires correct > best_constant + near_threshold):');
  const perQuestion = {};
  for (const k of keys) {
    const samples = cases.map((c) => ({ score: store[`${c.name}/${k}`][0], truth: c.truth[k] }));
    const g = gradeQuestion(samples, threshold);
    perQuestion[k] = g;
    console.log(`${k.padEnd(19)} ${g.correct}/${g.asked} | yes ${g.yes}/${g.asked} | no-const ${g.alwaysNo}/${g.asked} yes-const ${g.alwaysYes}/${g.asked} | spread ${g.spread.toFixed(2)} | near ${g.near} | ${g.verdict}`);
    console.log(`${' '.repeat(19)} scores: ${g.scores.map((s) => s.toFixed(2)).join(' ')}`);
  }
  console.log(`\nnear-threshold verdicts (within ${NEAR_WINDOW} of ${threshold}): ${thin.length ? thin.join(', ') : 'none'}`);
  console.log(`transport errors: ${errors}`);
  return { perQuestion, flips, errors, rows };
}
