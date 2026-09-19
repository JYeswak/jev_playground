// The measurement skillranker froze a contract for and never ran.
//
// Its tests/eval/ ships 12 labelled cases (`acceptable_additional_invocations_y`), a frozen 0/1/2
// loss table, an always-abstain negative control and a >= 0.90 top-1 precision promotion gate.
// Confirmed at origin/main today, 193 commits after our clone: `src/` still never reads that
// corpus, and the newer `expected_values.v1.json` is labelled
// "deterministic_contract_examples_not_measured_results". The contract is excellent and unused.
//
// WHAT THIS MEASURES, precisely: Jev's skill selection on skillranker's corpus under skillranker's
// loss table. It is NOT a measurement of skillranker the product -- that would require their
// binary and their prompt construction. It answers the question their contract was built to ask.
//
// PREREGISTERED BEFORE THE FIRST RUN (2026-09-19), taken from THEIR policy, not invented here:
//   - promotion gate: top-1 precision on positive cases >= 0.90 (their number)
//   - mean loss must beat the always-abstain negative control (their control)
//   Baselines computed earlier from the corpus alone, 5,000 trials: always-abstain 0.833,
//   coin-flip judge 1.011, uniform-pick 1.196, oracle 0.000. A coin flip scores WORSE than doing
//   nothing, so the corpus is discriminative and the bar is meaningful.
//
// PREVALENCE, per R28: 10 of 12 cases have a non-empty y. State it beside any score.
import { readFileSync } from 'node:fs';
import { TypeSafeClient, choice, noul } from '@typesafe-ai/sdk';
import { field } from '../oracle-kit/index.mjs';

const CORPUS = process.env.CORPUS ?? '~/Developer/skillranker-eval-probe/tests/eval/synthetic_cases.v1.jsonl';
const GATE = 0.90, ABSTAIN_CONTROL = 0.833;
const cases = readFileSync(CORPUS, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l));

// THEIR loss table, transcribed from tests/eval/evaluation_policy.v1.json.
const LOSS = {
  correct_recommendation_on_positive: 0,
  correct_no_match_abstention: 0,
  false_abstention_on_positive: 1,
  incorrect_recommendation_on_positive: 2,
  needless_recommendation_on_no_match: 2,
};

const client = new TypeSafeClient({ apiKey: process.env.TYPESAFE_API_KEY });
const NONE = '__none__';
let loss = 0, positives = 0, top1Correct = 0, abstains = 0;
const rows = [];

for (const c of cases) {
  const roster = c.visible_roster ?? [];
  const criteria = Object.fromEntries(roster.map((s) => [s.skill_id, `${s.usage_kind ?? 'skill'} — ${s.invocation_name}`]));
  criteria[NONE] = 'No listed skill genuinely helps; answer directly instead.';
  const r = await client.systemOne({
    state: { task: c.prompt_summary, constraints: c.current_constraints ?? '', already_loaded: c.already_available_references ?? [] },
    questions: {
      pick: choice('Which listed skill should the agent load next for this task, if any?', criteria),
      helpful: noul('Would loading any listed skill genuinely help here, versus answering directly?'),
    },
  });
  const pick = field(r.answers.pick, 'probabilities');
  const best = Object.entries(pick).sort((a, b) => b[1] - a[1])[0][0];
  const help = Number(field(r.answers.helpful, 'noul'));
  // ABSTAIN = the model picks __none__. Scored the way the product works: skillranker ranks with
  // a bounded Choice and does not gate on a second question.
  //
  // CORRECTED after a diagnostic run: the first version also required a `helpful` noul >= 0.5.
  // That noul read 0.07-0.48 on ALL 12 cases while the choice itself was confident (topP
  // 0.74-1.00), so my gate overrode every pick and produced a 92% abstain rate that measured my
  // question wording ("...versus answering directly", which biases downward), not Jev's ranking.
  // The noul is still reported below as a diagnostic, never as a gate.
  const abstained = best === NONE;
  const y = c.acceptable_additional_invocations_y ?? [];
  const yNonEmpty = y.length > 0;
  if (yNonEmpty) positives += 1;
  if (abstained) abstains += 1;

  let l, why;
  if (yNonEmpty && abstained) { l = LOSS.false_abstention_on_positive; why = 'false abstention'; }
  else if (yNonEmpty && y.includes(best)) { l = LOSS.correct_recommendation_on_positive; why = 'correct'; top1Correct += 1; }
  else if (yNonEmpty) { l = LOSS.incorrect_recommendation_on_positive; why = `wrong pick (${best})`; }
  else if (abstained) { l = LOSS.correct_no_match_abstention; why = 'correct abstention'; }
  else { l = LOSS.needless_recommendation_on_no_match; why = `needless (${best})`; }
  loss += l;
  rows.push({ helpfulP: help.toFixed(2), topP: Math.max(...Object.values(pick)).toFixed(2), case: c.case_id, kind: c.case_kind, pick: abstained ? 'ABSTAIN' : best, want: y.join(',') || '(none)', l, why });
  process.stderr.write('.');
}

const mean = loss / cases.length;
const precision = positives ? top1Correct / positives : NaN;
console.log(`\ncases=${cases.length}  positives=${positives} (prevalence ${(100 * positives / cases.length).toFixed(1)}%)  abstains=${abstains}`);
console.table(rows);
console.log(`mean loss = ${mean.toFixed(3)}   (their always-abstain control = ${ABSTAIN_CONTROL}, coin-flip = 1.011, oracle = 0.000)`);
console.log(`top-1 precision on positives = ${precision.toFixed(3)}   (their promotion gate = ${GATE})`);
const pass = precision >= GATE && mean < ABSTAIN_CONTROL;
console.log(`VERDICT: ${pass ? 'CLEARS their own promotion gate' : 'DOES NOT clear their gate'}`);
console.log(`NOTE: n=12 is their diagnostic_synthetic split; the repo forbids treating it as holdout evidence.`);
