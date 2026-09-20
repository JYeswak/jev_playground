/**
 * prevalence-check: the prevalence-first skill's enforcement point (jev-vbh.6, P2).
 *
 * The skill = prevalence cell + near-threshold column printed BEFORE any verdict.
 * Order is enforced in code, not by convention:
 *   pass 1 — near-threshold count, printed FIRST;
 *   pass 2 — own-constant bar (majority share), printed SECOND;
 *   pass 3 — gradeQuestion verdict, computed LAST via measure-kit (never hand-claimed).
 * A drift assertion refuses to print a verdict if local arithmetic ever diverges
 * from the kit again (the drift that already cost this lane one corrected verdict).
 *
 * Pure except for console output. Zero Jev calls.
 */
import { gradeQuestion, DEFAULT_THRESHOLD, NEAR_WINDOW } from '../jev-client/measure-kit.mjs';

export { DEFAULT_THRESHOLD, NEAR_WINDOW };

export function checkPrevalence({ samples, threshold = DEFAULT_THRESHOLD }) {
  const valid = samples.filter((s) => typeof s.score === 'number' && typeof s.truth === 'boolean');

  // Pass 1 FIRST: prevalence cell — near-threshold count before anything else.
  let near = 0;
  for (const s of valid) {
    if (Math.abs(s.score - threshold) < NEAR_WINDOW) near += 1;
  }
  console.log(`near-threshold: ${near}/${valid.length} (window ±${NEAR_WINDOW} around ${threshold})`);

  // Pass 2 SECOND: own-constant bar — what always-answering-the-majority scores.
  const trueCount = valid.filter((s) => s.truth).length;
  const alwaysYes = trueCount;
  const alwaysNo = valid.length - trueCount;
  const best = Math.max(alwaysYes, alwaysNo);
  const majority = alwaysYes >= alwaysNo ? 'yes' : 'no';
  const share = valid.length ? `${((best / valid.length) * 100).toFixed(1)}%` : 'n/a';
  console.log(`own-constant: always-${majority} ${best}/${valid.length} (majority share ${share})`);

  // Pass 3 LAST: the verdict is computed here, after both lines above are printed.
  const g = gradeQuestion(samples, threshold);
  if (g.near !== near) {
    throw new Error(`drift: local near ${near} !== kit near ${g.near} — fix the duplication, print nothing`);
  }
  if (g.best !== best) {
    throw new Error(`drift: local best ${best} !== kit best ${g.best} — fix the duplication, print nothing`);
  }
  console.log(`verdict: ${g.correct}/${g.asked} vs best-constant ${g.best} + near ${g.near} → ${g.verdict}`);
  return g;
}
