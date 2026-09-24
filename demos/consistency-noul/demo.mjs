#!/usr/bin/env node
// Riff on the official self-consistency (noul) cookbook. Keyless: the review
// band runs on recorded Noul assessments so you can see the routing without
// spending a key.
//
// Questions, claim, and the 0.30-0.70 uncertainty band are the ones in
// docs-mirror/typesafe/cookbooks/consistency_noul_cookbook.md
// (14 Nouls over one borderline auto-insurance claim CLM-55029; below 0.30 is
// `no`, above 0.70 is `yes`, both boundaries inclusive `uncertain` and routed
// to human review — application logic over the returned probability, no new
// question, no second call).
// `node demos/consistency-noul/demo.mjs --live` repeats the 14-Noul battery
// through work/jev-client, model jev-1.13.0.

const LOW = 0.30;
const HIGH = 0.70;

// The band is the product: out-of-range or non-numeric never becomes yes/no.
function decide(p) {
  if (!Number.isFinite(p) || p < 0 || p > 1) return 'uncertain';
  if (p < LOW) return 'no';
  if (p > HIGH) return 'yes';
  return 'uncertain';
}

const QUESTIONS = {
  covered: 'Is the loss covered under the policy\'s collision coverage?',
  exclusion: 'Does a policy exclusion apply to this loss?',
  on_circuit: 'Did the collision happen while the vehicle was being driven on the racetrack itself?',
  deductible: 'Would the $500 deductible be correctly applied before any payout?',
  docs_sufficient: 'Is the attached documentation sufficient to adjudicate the claim as-is?',
  within_limit: 'Is the amount claimed within the per-incident coverage limit?',
  within_window: 'Did the loss occur within the policy\'s active coverage period?',
  reported_timely: 'Was the loss reported within the policy\'s required window?',
  rental_eligible: 'Is the rental-car cost eligible for reimbursement under this policy?',
  fraud_flag: 'Are there indicators that warrant a fraud review?',
  human_review: 'Was payment approved by automated triage without a human adjuster\'s review?',
  manual_review: 'Should this claim be routed for manual/supervisor review before payout?',
  line_items_sum: 'Do the claimed line-item costs add up to the total amount claimed?',
  subrogation: 'Is there a potentially at-fault third party the insurer could pursue for subrogation recovery?',
};

// The cookbook's borderline claim, verbatim from its "The state" section
// (docs-mirror/typesafe/cookbooks/consistency_noul_cookbook.md). The recorded REPEATS below
// are assessments of THIS claim, so the live lane must send it: before jev-s0f1 the live state
// was the id alone and every live answer judged an empty claim.
const CLAIM = {
  policy: {
    policy_id: 'AP-77413',
    policyholder: 'Dana M.',
    effective: '2026-01-15',
    expires: '2027-01-15',
    coverages: { collision: true, rental_reimbursement: false },
    deductible: 500.0,
    per_incident_limit: 10000.0,
    listed_drivers: ['Dana M.', 'Sam M.'],
    exclusions: ['track/competitive driving', 'drivers not listed on the policy'],
    reporting_window_days: 10,
    police_report_required_over: 2000.0,
  },
  claim: {
    claim_id: 'CLM-55029',
    incident_date: '2026-06-28',
    reported_date: '2026-07-04',
    driver: 'Sam M.',
    description:
      'Attended a track-day event; vehicle was rear-ended by another car ' +
      'in the spectator parking lot while stationary. Not on the circuit.',
    amount_claimed: 3250.0,
    line_items: [
      { item: 'rear bumper replacement', cost: 1700.0 },
      { item: 'paint + refinish', cost: 800.0 },
      { item: 'parking-sensor recalibration', cost: 450.0 },
      { item: 'rental car (6 days)', cost: 300.0 },
    ],
    documentation: ['repair estimate (PDF)', '8 damage photos'],
  },
  adjuster_notes: [
    {
      author: 'auto-triage',
      note: 'Collision coverage active. Approved. Pay full amount $3,250 to policyholder, 5-10 business days.',
    },
  ],
  claim_history: { claims_last_12mo: 2, prior_denied: 0 },
};

// Recorded repeated Noul assessments of the cookbook's borderline claim
// (CLM-55029): 5 repeats x 14 questions. Run-to-run wobble is kept in on
// purpose: `covered` crosses 0.50 every which way yet never leaves `uncertain`
// (the band absorbs it), while `fraud_flag` and `subrogation` each cross an
// outer edge once — the band has edges of its own.
const REPEATS = [
  {
    covered: 0.47, exclusion: 0.57, on_circuit: 0.05, deductible: 0.88,
    docs_sufficient: 0.22, within_limit: 0.93, within_window: 0.96,
    reported_timely: 0.82, rental_eligible: 0.08, fraud_flag: 0.35,
    human_review: 0.90, manual_review: 0.78, line_items_sum: 0.97,
    subrogation: 0.74,
  },
  {
    covered: 0.51, exclusion: 0.60, on_circuit: 0.04, deductible: 0.91,
    docs_sufficient: 0.18, within_limit: 0.95, within_window: 0.97,
    reported_timely: 0.85, rental_eligible: 0.06, fraud_flag: 0.32,
    human_review: 0.92, manual_review: 0.81, line_items_sum: 0.98,
    subrogation: 0.69,
  },
  {
    covered: 0.44, exclusion: 0.55, on_circuit: 0.06, deductible: 0.86,
    docs_sufficient: 0.25, within_limit: 0.92, within_window: 0.95,
    reported_timely: 0.80, rental_eligible: 0.09, fraud_flag: 0.38,
    human_review: 0.89, manual_review: 0.75, line_items_sum: 0.96,
    subrogation: 0.76,
  },
  {
    covered: 0.53, exclusion: 0.62, on_circuit: 0.03, deductible: 0.90,
    docs_sufficient: 0.20, within_limit: 0.94, within_window: 0.96,
    reported_timely: 0.84, rental_eligible: 0.07, fraud_flag: 0.72,
    human_review: 0.91, manual_review: 0.80, line_items_sum: 0.97,
    subrogation: 0.71,
  },
  {
    covered: 0.48, exclusion: 0.53, on_circuit: 0.05, deductible: 0.89,
    docs_sufficient: 0.24, within_limit: 0.93, within_window: 0.97,
    reported_timely: 0.83, rental_eligible: 0.10, fraud_flag: 0.34,
    human_review: 0.93, manual_review: 0.77, line_items_sum: 0.98,
    subrogation: 0.73,
  },
];

// Headline-run band decisions: the fixture contract. Drift here exits 1.
const EXPECT = {
  covered: 'uncertain', exclusion: 'uncertain', on_circuit: 'no',
  deductible: 'yes', docs_sufficient: 'no', within_limit: 'yes',
  within_window: 'yes', reported_timely: 'yes', rental_eligible: 'no',
  fraud_flag: 'uncertain', human_review: 'yes', manual_review: 'yes',
  line_items_sum: 'yes', subrogation: 'yes',
};

function agreement(decisions) {
  const counts = new Map();
  for (const d of decisions) counts.set(d, (counts.get(d) ?? 0) + 1);
  const [top, n] = [...counts.entries()].reduce((a, b) => (b[1] > a[1] ? b : a));
  return { plurality: top, share: n / decisions.length };
}

function run(repeats) {
  return Object.keys(QUESTIONS).map((q) => {
    const nouls = repeats.map((r) => r[q]);
    const decisions = nouls.map(decide);
    const { plurality, share } = agreement(decisions);
    return { question: q, nouls, decisions, plurality, share };
  });
}

function show(rows, lane) {
  console.log(`consistency-noul demo [${lane}] — 14 Nouls x ${rows[0].nouls.length} repeats, band ${LOW.toFixed(2)}-${HIGH.toFixed(2)}\n`);
  console.log(`${'question'.padEnd(16)}${'nouls'.padEnd(36)}${'decisions'.padEnd(52)}plurality  agree`);
  for (const r of rows) {
    console.log(
      `${r.question.padEnd(16)}${r.nouls.map((n) => n.toFixed(2)).join(' ').padEnd(36)}${r.decisions.join(' | ').padEnd(52)}${r.plurality.padEnd(10)}${(r.share * 100).toFixed(0)}%`,
    );
  }
  const auto = rows.filter((r) => r.plurality !== 'uncertain').length;
  console.log(`\nautomatic: ${auto}/${rows.length} questions hold a non-uncertain plurality; the rest go to human review with probabilities visible.`);
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
  show(rows, 'fixture — recorded nouls, no key, no network');
  process.exit(0);
}

const { askJevBundle } = await import('../../work/jev-client/src/index.ts');
const NOUL_QUESTIONS = Object.fromEntries(
  Object.entries(QUESTIONS).map(([key, instructions]) => [key, { type: 'noul', instructions }]),
);
const liveRepeats = [];
for (let i = 0; i < 3; i++) {
  const r = await askJevBundle({
    state: { ...CLAIM, uid: `consistency-noul-demo-${Date.now()}-${i}` },
    questions: NOUL_QUESTIONS,
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
  const dist = {};
  for (const key of Object.keys(QUESTIONS)) {
    const a = r.answers[key];
    if (!a || typeof a.noul !== 'number') {
      console.error(`live call malformed: answer ${key} has no noul`);
      process.exit(1);
    }
    dist[key] = a.noul;
  }
  liveRepeats.push(dist);
}
show(run(liveRepeats), 'live');
