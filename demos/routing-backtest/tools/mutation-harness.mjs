#!/usr/bin/env node
// Plant named mutations in the shipping code, assert the existing tests catch each one, restore.
//
// WHY. The lane's commit-subject enum has carried `mutation` as a verification level all session and
// it had been used ZERO times; every claim topped out at `test`. Jeff Emanuel's skillranker closes a
// bead with "Planted mutations: 7 of 7 caught by the intended tests ... Files were restored and
// compared", enumerating each mutation individually. A green suite proves the tests RAN. It does not
// prove they would have FAILED on a wrong answer, and that is the only property that makes a passing
// suite evidence for a stranger.
//
// This is not a coverage tool. Each mutation is a SPECIFIC WRONG BEHAVIOUR a reader might worry
// about: a boundary flipped from strict to inclusive, a sign inverted, a filter dropped, a
// denominator swapped. An escaped mutation names a real hole; it is reported, never smoothed over.
//
// CONSUMER: whoever is deciding whether to trust this demo's numbers, and `npm run mutate`.
// GATE: none — it reports. It is a measurement of the tests, published with them.
// OBSERVED DEFECT: this session shipped an arm that "passed by construction" (8-col fixture vs 9-col
//   schema), an assertion that could not observe the next change, a predicate satisfiable by
//   unrelated text, and a substring match that accepted a dollar amount as a percentage. Four
//   witnesses that could not fail. That is the class this measures.
// RETIREMENT: when a real mutation-testing tool runs in CI over this package, delete this file.
import { readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const MUTATIONS = [
  // Each: the file, the exact source span, its replacement, and what a reader fears.
  {
    id: 'tool-call-gate-inclusive',
    file: 'src/counterfactual.mjs',
    from: 'if (turn.toolCalls > policy.maxToolCalls) {',
    to: 'if (turn.toolCalls >= policy.maxToolCalls) {',
    fear: 'a turn at exactly the tool-call limit is wrongly excluded from cheap routing',
  },
  {
    id: 'prompt-budget-inverted',
    file: 'src/counterfactual.mjs',
    from: 'if (turn.promptTokens > policy.maxPromptTokens) {',
    to: 'if (turn.promptTokens < policy.maxPromptTokens) {',
    fear: 'the prompt-token budget admits exactly the turns it should reject',
  },
  {
    id: 'completion-budget-dropped',
    file: 'src/counterfactual.mjs',
    from: 'if (turn.completionTokens > policy.maxCompletionTokens) {',
    to: 'if (false) {',
    fear: 'the completion-token gate stops firing entirely, inflating cheap-eligible turns',
  },
  {
    id: 'missing-tokens-treated-as-routable',
    file: 'src/counterfactual.mjs',
    from: "return { cheapSufficient: false, reason: 'missing-token-counts' };",
    to: "return { cheapSufficient: true, reason: 'missing-token-counts' };",
    fear: 'turns with no token counts are priced as if they were routable',
  },
  {
    id: 'actual-spend-sign-flipped',
    file: 'src/counterfactual.mjs',
    from: 'if (actual !== null) actualSpend += actual;',
    to: 'if (actual !== null) actualSpend -= actual;',
    fear: 'the actual-spend accumulator inverts, so savings become a mirror of themselves',
  },
  {
    id: 'counterfactual-spend-not-accumulated',
    file: 'src/counterfactual.mjs',
    from: 'if (counterfactual !== null) counterfactualSpend += counterfactual;',
    to: 'if (counterfactual !== null) counterfactualSpend += 0;',
    fear: 'the counterfactual leg stays zero, making savings equal actual spend',
  },
  {
    id: 'unclassifiable-missing-spend-ignored',
    file: 'src/counterfactual.mjs',
    from: 'if (turn.classifiable && turn.actualSpend === null) {',
    to: 'if (false && turn.classifiable && turn.actualSpend === null) {',
    fear: 'a classifiable turn with no spend is silently counted rather than reported',
  },
];

function sha(p) {
  return createHash('sha256').update(readFileSync(p)).digest('hex').slice(0, 16);
}

function suiteFails() {
  try {
    execFileSync('npm', ['test'], { stdio: 'pipe' });
    return false; // suite passed -> the mutation ESCAPED
  } catch {
    return true; // suite failed -> the mutation was CAUGHT
  }
}

const files = [...new Set(MUTATIONS.map((m) => m.file))];
const before = Object.fromEntries(files.map((f) => [f, sha(f)]));
const originals = Object.fromEntries(files.map((f) => [f, readFileSync(f, 'utf8')]));

// A mutation harness whose baseline is already red proves nothing about any mutation.
if (suiteFails()) {
  console.error('BASELINE RED: the suite fails before any mutation. Nothing below would mean anything.');
  process.exit(2);
}
console.log('baseline: suite green');

let caught = 0;
const escaped = [];
for (const m of MUTATIONS) {
  const src = originals[m.file];
  const hits = src.split(m.from).length - 1;
  if (hits !== 1) {
    // A mutation that does not apply is not a pass. Stale spans are how this kind of harness rots.
    escaped.push({ ...m, note: `span appears ${hits} times, expected exactly 1 — MUTATION NOT APPLIED` });
    continue;
  }
  writeFileSync(m.file, src.replace(m.from, m.to));
  const detected = suiteFails();
  writeFileSync(m.file, src);
  if (detected) {
    caught += 1;
    console.log(`CAUGHT   ${m.id}`);
  } else {
    escaped.push(m);
    console.log(`ESCAPED  ${m.id}  — ${m.fear}`);
  }
}

// Restore-and-compare, the half that makes the run safe to have performed at all.
const dirty = files.filter((f) => sha(f) !== before[f]);
console.log('');
console.log(`mutations: ${caught}/${MUTATIONS.length} caught`);
console.log(`files restored byte-identical: ${dirty.length === 0 ? 'yes' : `NO — ${dirty.join(', ')}`}`);
for (const e of escaped) {
  console.log(`  HOLE ${e.id}: ${e.note ?? e.fear}`);
}
if (dirty.length) {
  console.error('RESTORE FAILED — source left mutated. Fix before committing anything.');
  process.exit(2);
}
process.exit(escaped.length ? 1 : 0);
