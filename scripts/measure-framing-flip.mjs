#!/usr/bin/env node
// Does the lane's HEADLINE lesson still reproduce?
//
// README: "Withhold that shape and ask the same two questions, and the verdict flips:
//          router_pays moves from 0.21 to 0.59 and the lever it picks drops from 0.75 to 0.49."
//
// That flip was measured ONCE, in 2026-09-18, and no runner was ever committed, so it has never
// been re-checked. This script runs BOTH arms N times each against the live API and prints the
// two distributions side by side. It changes exactly ONE thing between arms: whether the measured
// usage shape is present in `state`. Questions are byte-identical across arms.
//
// Usage:
//   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod -- \
//     node scripts/measure-framing-flip.mjs [N]
//
// NO-CLAIM: one machine, one network, one moment. Enough to say whether a published point
// estimate reproduces; not enough to publish a new point estimate in its place.

const key = process.env.TYPESAFE_API_KEY;
if (!key) {
  console.error('ERROR no key in env. Run under: infisical run --projectId=... -- node scripts/measure-framing-flip.mjs');
  process.exit(2);
}
const N = Number(process.argv[2] || 10);
// Lane-sanctioned caller (943158c): SDK-owned wire, our failure taxonomy.
// askJevBundle passes the MIXED Noul+Choice battery through unmodified.
import { askJevBundle } from '../work/jev-client/src/index.ts';

// IDENTICAL in both arms. If these differ, the experiment measures nothing.
const questions = {
  router_pays: {
    type: 'noul',
    instructions: 'Would building a cheaper-model router, which substitutes a cheaper model for '
      + 'the same set of turns, meaningfully reduce this team\'s token spend?',
    criteria: { true: 'it would meaningfully reduce spend', false: 'it would not' },
  },
  top_lever: {
    type: 'choice',
    instructions: 'Which single lever should this team attack first?',
    criteria: {
      fewer_turns: 'reduce the number of turns, since each re-sends the whole context',
      cheaper_model: 'substitute a cheaper model on the same turns',
      shorter_output: 'ask the model for less output',
      shorter_prompts: 'write shorter prompts',
    },
  },
};

const context = 'A team is deciding whether to build a cheaper-model router to cut spend.';

// WITH: the measured shape is in the state. WITHOUT: the same request minus that one field.
const withState = {
  census_receipt: 'docs/demos/jev-probe/census-20260918.json',
  census_receipt_norm_sha256_16: 'af6c682c26014b69',
  census_producer: 'demos/usage-shape/bin/shape.mjs --json over ~/.claude/projects, 2026-09-18',
  finding: 'Across 4619 local agent sessions and 488724 billed turns, 98.878% of all tokens are '
    + 'cache-read context re-sent on every turn; model output is 0.140% of tokens.',
  question_context: context,
};
const withoutState = { question_context: context };

async function one(state) {
  // Fail-stop preserved: any failure throws and aborts the experiment —
  // a partial distribution presented as complete would be the lie here.
  const r = await askJevBundle({
    state, questions,
    model: 'jev-1.13.0', // pinned: jev-latest is a moving model.
    apiKey: key, timeoutMs: 20000,
  });
  if (!r.ok) throw new Error(`Invalid Jev answer: ${r.reason} ${r.error}`);
  const pays = r.answers?.router_pays;
  const lever = r.answers?.top_lever;
  if (!pays || typeof pays.noul !== 'number') throw new Error('Invalid Jev answer: router_pays.noul missing');
  if (!lever || typeof lever.choice !== 'string') throw new Error('Invalid Jev answer: top_lever.choice missing');
  return {
    router_pays: pays.noul,
    top_lever: lever.choice,
    lever_conf: lever.probabilities?.[lever.choice],
  };
}

function summarise(label, rows) {
  const v = rows.map((r) => r.router_pays).sort((a, b) => a - b);
  const levers = {};
  for (const r of rows) levers[r.top_lever] = (levers[r.top_lever] || 0) + 1;
  console.log(`${label.padEnd(16)} n=${v.length}  router_pays min ${v[0]} median ${v[Math.floor(v.length / 2)]} max ${v[v.length - 1]}`);
  console.log(`${' '.repeat(16)} top_lever ${JSON.stringify(levers)}`);
  return v;
}

const withRows = [];
const withoutRows = [];
for (let i = 0; i < N; i++) {
  withRows.push(await one(withState));
  withoutRows.push(await one(withoutState));
}

console.log(`\nframing flip, ${N} paired calls per arm, ${new Date().toISOString()}\n`);
const a = summarise('WITH shape', withRows);
const b = summarise('WITHOUT shape', withoutRows);

// The published claim is a DIRECTION plus two points. Report on both separately: a direction can
// survive while its point estimates rot, and conflating the two is how a stale number keeps a
// true lesson looking verified.
const medA = a[Math.floor(a.length / 2)];
const medB = b[Math.floor(b.length / 2)];
console.log(`\ndirection: withholding the shape moves router_pays ${medA} -> ${medB} (${medB > medA ? 'UP, as published' : 'NOT up — published direction does not reproduce'})`);
console.log(`published points: 0.21 -> 0.59. Runs at or below 0.21 in WITH arm: ${a.filter((x) => x <= 0.21).length}/${a.length}; at or above 0.59 in WITHOUT arm: ${b.filter((x) => x >= 0.59).length}/${b.length}`);
