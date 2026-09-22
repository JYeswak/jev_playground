#!/usr/bin/env node
// Riff on the official self-consistency cookbook. Keyless by default: the guard
// runs on recorded Choice assessments so you can see the routing without a key.
// `node demos/consistency/demo.mjs --live` repeats through work/jev-client.
//
// Questions, rubric, and the 0.60 automatic-action gate are the ones in
// docs-mirror/typesafe/cookbooks/consistency_choice_cookbook.md
// (8 Choices over one borderline post; below gate the result is `uncertain`
// and goes to human review).
//
// NO-CLAIM: a fixture consistency check shows the guard working. It is not a
// live agreement score — run --live (needs TYPESAFE_API_KEY) for real numbers.

// The guard is the product: argmax, abstain below gate, never invent a label.
const GATE = 0.60;

function decide(distribution) {
  const entries = Object.entries(distribution);
  if (entries.length === 0) return 'uncertain';
  if (!entries.every(([, p]) => Number.isFinite(p) && p >= 0 && p <= 1)) return 'uncertain';
  const [label, top] = entries.reduce((a, b) => (b[1] > a[1] ? b : a));
  return top >= GATE ? label : 'uncertain';
}

const QUESTIONS = {
  category: ['None', 'Harass', 'Hate', 'Violence', 'Spam', 'Sexual'],
  primary_risk: ['Harassment', 'Violence', 'LinkAbuse', 'AccountHistory', 'LowRisk'],
  target: ['None', 'Person', 'Group', 'Platform'],
  action: ['Allow', 'Warn', 'Remove', 'Strike', 'Escalate'],
  queue: ['Auto', 'General', 'Threat', 'Spam', 'TSLead'],
  link_handling: ['Allow', 'RmLink', 'Brigade', 'Escalate'],
  review_path: ['Auto', 'Human', 'Senior', 'Legal'],
  severity: ['None', 'Low', 'Medium', 'High'],
};

// Recorded repeated assessments of the cookbook's borderline post (P-88213):
// 5 repeats × 8 questions, per-label probabilities. Run-to-run wobble is kept
// in on purpose: `action` flips Remove/Escalate and one `link_handling` repeat
// falls below gate, so the table shows both a flip and an abstention.
const REPEATS = [
  {
    category: { None: 0.02, Harass: 0.71, Hate: 0.03, Violence: 0.18, Spam: 0.04, Sexual: 0.02 },
    primary_risk: { Harassment: 0.66, Violence: 0.20, LinkAbuse: 0.08, AccountHistory: 0.04, LowRisk: 0.02 },
    target: { None: 0.03, Person: 0.78, Group: 0.02, Platform: 0.17 },
    action: { Allow: 0.02, Warn: 0.10, Remove: 0.62, Strike: 0.08, Escalate: 0.18 },
    queue: { Auto: 0.04, General: 0.64, Threat: 0.16, Spam: 0.03, TSLead: 0.13 },
    link_handling: { Allow: 0.06, RmLink: 0.68, Brigade: 0.10, Escalate: 0.16 },
    review_path: { Auto: 0.05, Human: 0.72, Senior: 0.20, Legal: 0.03 },
    severity: { None: 0.01, Low: 0.09, Medium: 0.63, High: 0.27 },
  },
  {
    category: { None: 0.02, Harass: 0.68, Hate: 0.04, Violence: 0.21, Spam: 0.03, Sexual: 0.02 },
    primary_risk: { Harassment: 0.63, Violence: 0.23, LinkAbuse: 0.07, AccountHistory: 0.05, LowRisk: 0.02 },
    target: { None: 0.02, Person: 0.80, Group: 0.02, Platform: 0.16 },
    action: { Allow: 0.02, Warn: 0.08, Remove: 0.44, Strike: 0.07, Escalate: 0.39 },
    queue: { Auto: 0.03, General: 0.61, Threat: 0.19, Spam: 0.03, TSLead: 0.14 },
    link_handling: { Allow: 0.07, RmLink: 0.65, Brigade: 0.11, Escalate: 0.17 },
    review_path: { Auto: 0.04, Human: 0.70, Senior: 0.23, Legal: 0.03 },
    severity: { None: 0.01, Low: 0.08, Medium: 0.60, High: 0.31 },
  },
  {
    category: { None: 0.03, Harass: 0.70, Hate: 0.03, Violence: 0.19, Spam: 0.03, Sexual: 0.02 },
    primary_risk: { Harassment: 0.65, Violence: 0.21, LinkAbuse: 0.08, AccountHistory: 0.04, LowRisk: 0.02 },
    target: { None: 0.03, Person: 0.77, Group: 0.02, Platform: 0.18 },
    action: { Allow: 0.02, Warn: 0.09, Remove: 0.64, Strike: 0.09, Escalate: 0.16 },
    queue: { Auto: 0.04, General: 0.66, Threat: 0.15, Spam: 0.02, TSLead: 0.13 },
    link_handling: { Allow: 0.12, RmLink: 0.52, Brigade: 0.14, Escalate: 0.22 },
    review_path: { Auto: 0.05, Human: 0.69, Senior: 0.22, Legal: 0.04 },
    severity: { None: 0.01, Low: 0.10, Medium: 0.64, High: 0.25 },
  },
  {
    category: { None: 0.02, Harass: 0.72, Hate: 0.03, Violence: 0.17, Spam: 0.04, Sexual: 0.02 },
    primary_risk: { Harassment: 0.67, Violence: 0.19, LinkAbuse: 0.08, AccountHistory: 0.04, LowRisk: 0.02 },
    target: { None: 0.02, Person: 0.79, Group: 0.02, Platform: 0.17 },
    action: { Allow: 0.02, Warn: 0.11, Remove: 0.60, Strike: 0.08, Escalate: 0.19 },
    queue: { Auto: 0.05, General: 0.63, Threat: 0.17, Spam: 0.03, TSLead: 0.12 },
    link_handling: { Allow: 0.06, RmLink: 0.70, Brigade: 0.09, Escalate: 0.15 },
    review_path: { Auto: 0.06, Human: 0.71, Senior: 0.20, Legal: 0.03 },
    severity: { None: 0.01, Low: 0.09, Medium: 0.62, High: 0.28 },
  },
  {
    category: { None: 0.02, Harass: 0.69, Hate: 0.04, Violence: 0.20, Spam: 0.03, Sexual: 0.02 },
    primary_risk: { Harassment: 0.64, Violence: 0.22, LinkAbuse: 0.08, AccountHistory: 0.04, LowRisk: 0.02 },
    target: { None: 0.03, Person: 0.76, Group: 0.03, Platform: 0.18 },
    action: { Allow: 0.03, Warn: 0.09, Remove: 0.41, Strike: 0.08, Escalate: 0.39 },
    queue: { Auto: 0.04, General: 0.62, Threat: 0.18, Spam: 0.03, TSLead: 0.13 },
    link_handling: { Allow: 0.07, RmLink: 0.66, Brigade: 0.10, Escalate: 0.17 },
    review_path: { Auto: 0.05, Human: 0.73, Senior: 0.19, Legal: 0.03 },
    severity: { None: 0.01, Low: 0.08, Medium: 0.61, High: 0.30 },
  },
];

// Headline-run gated decisions: the fixture contract. Drift here exits 1.
const EXPECT = {
  category: 'Harass',
  primary_risk: 'Harassment',
  target: 'Person',
  action: 'Remove',
  queue: 'General',
  link_handling: 'RmLink',
  review_path: 'Human',
  severity: 'Medium',
};

function agreement(question, decisions) {
  const counts = new Map();
  for (const d of decisions) counts.set(d, (counts.get(d) ?? 0) + 1);
  const [top, n] = [...counts.entries()].reduce((a, b) => (b[1] > a[1] ? b : a));
  return { plurality: top, share: n / decisions.length };
}

function run(repeats) {
  const rows = [];
  for (const q of Object.keys(QUESTIONS)) {
    const decisions = repeats.map((r) => decide(r[q]));
    const { plurality, share } = agreement(q, decisions);
    rows.push({ question: q, decisions, plurality, share });
  }
  return rows;
}

function show(rows, lane) {
  console.log(`consistency demo [${lane}] — 8 Choices × ${REPEATS.length} repeats, gate ${GATE.toFixed(2)}\n`);
  console.log(`${'question'.padEnd(14)}${'decisions'.padEnd(44)}plurality  agree`);
  for (const r of rows) {
    console.log(
      `${r.question.padEnd(14)}${r.decisions.join(' | ').padEnd(44)}${r.plurality.padEnd(10)}${(r.share * 100).toFixed(0)}%`,
    );
  }
  const auto = rows.filter((r) => r.plurality !== 'uncertain').length;
  console.log(`\nautomatic: ${auto}/${rows.length} questions hold a gated plurality; the rest go to human review.`);
}

function check(rows) {
  const bad = rows.filter((r) => EXPECT[r.question] !== r.decisions[0]);
  if (bad.length > 0) {
    console.error(`FIXTURE DRIFT: ${bad.map((r) => r.question).join(', ')} decided off expectation`);
    process.exit(1);
  }
}

const live = process.argv.includes('--live');
if (!live) {
  const rows = run(REPEATS);
  check(rows);
  show(rows, 'fixture — recorded assessments, no key, no network');
  process.exit(0);
}

const { askJevBundle } = await import('../../work/jev-client/src/index.ts');
const CHOICE_QUESTIONS = Object.fromEntries(
  Object.entries(QUESTIONS).map(([key, labels]) => [
    key,
    { type: 'choice', instructions: `Pick the single most applicable label for ${key}.`, criteria: Object.fromEntries(labels.map((l) => [l, null])) },
  ]),
);
const liveRepeats = [];
for (let i = 0; i < 3; i++) {
  const r = await askJevBundle({
    state: { post_id: 'P-88213', uid: `consistency-demo-${Date.now()}-${i}` },
    questions: CHOICE_QUESTIONS,
    model: 'jev-1.13.0',
    timeoutMs: 20000,
  });
  if (!r.ok) {
    if (r.reason === 'unconfigured') {
      console.log('live lane: NOT_RUN — TYPESAFE_API_KEY is not set (see .env.example)');
      process.exit(0);
    }
    console.error(`live call failed: ${r.reason} ${r.error}`);
    process.exit(1);
  }
  const dist = {};
  for (const key of Object.keys(QUESTIONS)) {
    const a = r.answers[key];
    if (!a || typeof a.probabilities !== 'object') {
      console.error(`live call malformed: answer ${key} has no probabilities`);
      process.exit(1);
    }
    dist[key] = a.probabilities;
  }
  liveRepeats.push(dist);
}
show(run(liveRepeats), 'live');
