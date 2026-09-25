#!/usr/bin/env node
// Riff on the official RAG-passage cookbook. Keyless by default: the policy
// runs on recorded assessments so you can see the routing without a key.
// `node demos/rag/demo.mjs --live` scores through work/jev-client.
//
// Questions + thresholds are the ones in
// docs-mirror/typesafe/cookbooks/classifying_rag_passages.md
// (four Nouls per passage; route() first-match order; THRESHOLDS dict).
// Fixture answers are the cookbook's own recorded outputs for the headline
// query (route table), not live scores.
//
// NO-CLAIM: fixture keep/drop shows the policy working. It is not a live
// retrieval score — run --live (needs TYPESAFE_API_KEY) for real numbers.
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));

// Policy lives here, in our code: numbers, not rewordings.
const THRESHOLDS = {
  injection_max: 0.7,
  contradicts_min: 0.7,
  relevant_min: 0.45,
  evidence_min: 0.55,
};

function route(a) {
  if (a.contains_prompt_injection > THRESHOLDS.injection_max) return 'exclude';
  if (a.contradicts_query_premise > THRESHOLDS.contradicts_min) return 'conflicting_evidence';
  if (a.is_relevant < THRESHOLDS.relevant_min) return 'exclude';
  if (a.contains_answer_evidence > THRESHOLDS.evidence_min) return 'include';
  return 'exclude';
}

const keep = (r) => (r === 'include' || r === 'conflicting_evidence' ? 'keep' : 'drop');

const QUESTIONS = {
  is_relevant: { type: 'noul', instructions: 'Does this passage address the subject of the query?' },
  contains_answer_evidence: { type: 'noul', instructions: 'Does this passage state information usable in a direct answer?' },
  contradicts_query_premise: { type: 'noul', instructions: 'Does this passage conflict with a factual premise stated in the query?' },
  contains_prompt_injection: { type: 'noul', instructions: 'Does this passage attempt to control the system answering the query?' },
};

const EXPECT = {
  'forum-injection': 'exclude',
  'sessions-05': 'exclude',
  'sessions-06-a': 'exclude',
  'sessions-01': 'conflicting_evidence',
  'signing-keys-51-c': 'exclude',
};

function show(query, rows, lane) {
  console.log(`rag-passage demo [${lane}] — ${query}\n`);
  console.log(`${'route'.padEnd(21)}${'rel'.padStart(6)}${'evid'.padStart(6)}${'contra'.padStart(7)}${'inj'.padStart(6)}  keep/drop  id`);
  for (const { passage, answers, route: r } of rows) {
    console.log(
      `${r.padEnd(21)}${answers.is_relevant.toFixed(2).padStart(6)}${answers.contains_answer_evidence.toFixed(2).padStart(6)}${answers.contradicts_query_premise.toFixed(2).padStart(7)}${answers.contains_prompt_injection.toFixed(2).padStart(6)}  ${keep(r).padEnd(9)}${passage.id}`,
    );
  }
}

function check(rows) {
  const bad = rows.filter(({ passage, route: r }) => EXPECT[passage.id] !== r);
  if (bad.length > 0) {
    console.error(`FIXTURE DRIFT: ${bad.map(({ passage }) => passage.id).join(', ')} routed off expectation`);
    process.exit(1);
  }
}

const live = process.argv.includes('--live');
const fixture = JSON.parse(readFileSync(join(HERE, 'fixture.json'), 'utf8'));

if (!live) {
  const rows = fixture.passages.map((passage) => ({ passage, answers: passage.answers, route: route(passage.answers) }));
  check(rows);
  show(fixture.query, rows, 'fixture — recorded assessments, no key, no network');
  process.exit(0);
}

const { askJevBundle } = await import('../../kit/src/client.ts');
const rows = [];
for (const passage of fixture.passages) {
  const r = await askJevBundle({
    state: { query: fixture.query, passage: { id: passage.id, title: passage.title, source_type: passage.source_type } },
    questions: QUESTIONS,
    model: 'jev-1.13.0',
    timeoutMs: 20000,
  });
  if (!r.ok) {
    if (r.reason === 'unconfigured' || r.reason === 'sdk-missing') {
      // Nothing was measured, so this is not a success: exit 2 (jev-6smc).
      console.log(`live lane: NOT_RUN — ${r.error}`);
      process.exit(2);
    }
    console.error(`live call failed: ${r.reason} ${r.error}`);
    process.exit(1);
  }
  const answers = {};
  for (const key of Object.keys(QUESTIONS)) {
    const a = r.answers[key];
    if (!a || typeof a.noul !== 'number') {
      console.error(`live call malformed: answer ${key} has no numeric noul`);
      process.exit(1);
    }
    answers[key] = a.noul;
  }
  rows.push({ passage, answers, route: route(answers) });
}
show(fixture.query, rows, 'live');
