#!/usr/bin/env node
// One budgeted live Jev call. Verifies the API contract and prints the decoded response.
//
// Run ONLY through Infisical so the key never lands in the tree, a file, or a shell history entry:
//
//   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod -- \
//     node scripts/jev-probe.mjs
//
// The key is read from the environment and NEVER printed, logged, or echoed — not even a prefix.
// Request and response shapes are taken from the vendored clone read-only, not from memory:
//   skillranker/docs/jev-endpoint-contract.md  (origin + exactly one /v1/systemone join)
//   skillranker/src/jev/client.rs:148          (Authorization header, Accept: application/json)
//   skillranker/src/jev/codec.rs:67-149        (Request{model,state,questions}, Question::Noul|Choice)
//   skillranker/src/config.rs:25               (model "jev-latest")
// OFFLINE LANE FIRST, per AGENTS.md §8. --replay decodes a recorded response and makes NO network
// call, so the probe's decode path is exercised with no key and the live lane is an explicit choice
// rather than the only mode. The fixture is a real captured response with no credential in it.
const replay = process.argv.includes('--replay');
if (replay) {
  const { readFileSync } = await import('node:fs');
  const path = 'docs/demos/jev-probe/probe-response-20260918.json';
  let decoded;
  try {
    decoded = JSON.parse(readFileSync(new URL(`../${path}`, import.meta.url), 'utf8'));
  } catch (error) {
    // A missing or corrupt fixture must SAY SO. Silently falling through to the live lane would
    // turn an offline run into a paid call, which is the opposite of what --replay promises.
    console.error(`REPLAY FAILED: ${path} unreadable or not JSON — ${error.message}`);
    process.exit(2);
  }
  console.log(`REPLAY ${path} — no network call, live lane NOT_RUN`);
  console.log(JSON.stringify(decoded, null, 2));
  process.exit(0);
}

const key = process.env.TYPESAFE_API_KEY ?? process.env.TYPE_SAFE_AI_KEY;
if (!key) {
  console.error('ERROR no key in env. Run under: infisical run --projectId=<id> --env=prod -- node scripts/jev-probe.mjs');
  process.exit(2);
}

const url = 'https://api.typesafe.ai/v1/systemone';
const body = {
  model: 'jev-latest',
  // The state is the evidence the model judges. Deliberately a claim this lane can check itself.
  // EVERY FIGURE BELOW IS BOUND TO A COMMITTED RECEIPT, because pane 3's grade
  // (docs/demos/duel-2/runs/probe-grade-20260918T144541Z.json) found the earlier version citing
  // "the 4619-session/488724-turn census [with] no located receipt — the script's own numbers are an
  // unopened control." That is my modal failure, citing a number without binding its control,
  // arriving inside the probe built to test claims. The receipt is now in the tree and named here.
  state: {
    census_receipt: 'docs/demos/jev-probe/census-20260918.json',
    census_receipt_norm_sha256_16: 'af6c682c26014b69',
    census_producer: 'demos/usage-shape/bin/shape.mjs --json over ~/.claude/projects, 2026-09-18',
    finding: 'Across 4619 local agent sessions and 488724 billed turns, 98.878% of all tokens are '
      + 'cache-read context re-sent on every turn; model output is 0.140% of tokens.',
    question_context: 'A team is deciding whether to build a cheaper-model router to cut spend.',
  },
  questions: {
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
  },
};

// BOUNDED. ubs flagged the unbounded fetch and it was right: a stalled request against a PAID API
// with no signal hangs until the process is killed, and the vendored client bounds every exchange by
// an owned deadline for exactly this reason (skillranker/docs/jev-transport.md). 20 s is the budget.
const started = Date.now();
let res;
let text;
try {
  res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(20_000),
  });
  text = await res.text();
} catch (error) {
  // A timeout or transport failure is a REPORTED outcome, not a crash with a stack for the reader.
  console.error(`PROBE FAILED after ${Date.now() - started} ms: ${error.name}: ${error.message}`);
  process.exit(1);
}
const ms = Date.now() - started;

console.log(`HTTP ${res.status} in ${ms} ms`);
// Never echo request headers. Response body only.
try {
  console.log(JSON.stringify(JSON.parse(text), null, 2).slice(0, 4000));
} catch {
  console.log(text.slice(0, 2000));
}
process.exit(res.ok ? 0 : 1);
