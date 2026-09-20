/**
 * §10 demo: persona golden/trap pattern + the three missing mechanisms.
 *
 * Golden rows (judge-scored 1-5, GROUNDING) joined to corpus-source records via
 * joinOutcomes; a trap row that answers is TRAP-LEAK; ownConstant + randomBaseline
 * computed over the golden verdicts. Toy data demonstrates MECHANICS only — the
 * claim is that the three mechanisms compose with the adopted pattern, not that
 * these toy verdicts transfer anywhere.
 *
 * Run: node work/jev-persona-eval/demo.mjs
 */
import { joinOutcomes } from '../jev-eval-honesty/outcome-join.mjs';
import { randomBaseline, ownConstant } from '../jev-eval-honesty/random-judge.mjs';

// Golden rows as the adopted pattern shapes them: brace-free judge lines parsed
// to verdicts, each joined to the corpus record that holds its answer.
const goldenRows = [
  '{"customType": "persona-eval.decision.v1", "data": {"kind": "golden_scored", "toolCallId": "g1", "grounding": 5, "source": "corpus-a"}}',
  '{"customType": "persona-eval.decision.v1", "data": {"kind": "golden_scored", "toolCallId": "g2", "grounding": 4, "source": "corpus-a"}}',
  '{"customType": "persona-eval.decision.v1", "data": {"kind": "golden_scored", "toolCallId": "g3", "grounding": 2, "source": "corpus-b"}}',
  '{"customType": "persona-eval.decision.v1", "data": {"kind": "trap_answered", "toolCallId": "t1", "grounding": 1}}',
];
const corpusSources = [
  '{"customType": "persona-corpus.v1", "data": {"kind": "source", "toolCallId": "g1", "corpus": "corpus-a"}}',
  '{"customType": "persona-corpus.v1", "data": {"kind": "source", "toolCallId": "g2", "corpus": "corpus-a"}}',
  '{"customType": "persona-corpus.v1", "data": {"kind": "source", "toolCallId": "g3", "corpus": "corpus-b"}}',
];

const join = joinOutcomes({ rows: goldenRows, expectKey: ['kind'], idKey: 'toolCallId' });
console.log(`join: matched=${join.matched.length} zeroHit=${join.zeroHit}`);
const leaks = join.matched.filter((m) => m.verdict === 'trap_answered');
console.log(`TRAP-LEAK rows: ${leaks.length} (${leaks.map((m) => m.id).join(',') || 'none'})`);
const sources = joinOutcomes({ rows: corpusSources, expectKey: ['kind'], idKey: 'toolCallId' });
console.log(`corpus-source join: matched=${sources.matched.length}`);

// Verdicts binarised the adopted way (grounding >= 4 counts as grounded);
// constant + chance baselines over the golden verdicts.
const cases = [
  { name: 'g1', truth: true }, { name: 'g2', truth: true }, { name: 'g3', truth: false },
];
const oc = ownConstant({ cases, truthKey: 'truth' });
console.log(`ownConstant: ${oc.label}=${oc.accuracy} (${oc.count}/${oc.total})`);
const rb = randomBaseline({ cases, truthKey: 'truth', seed: 20260920 });
console.log(`randomBaseline: accuracy=${rb.accuracy}`);
console.log('prevalence: golden truth 2/3 grounded — UNKNOWN population; toy set, mechanics only');
