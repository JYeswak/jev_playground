#!/usr/bin/env node
// Chief router: one Choice call routes a job to research, write, or review.
// Keyless by default on recorded verdicts; --live calls Jev through
// work/jev-client askJevChoice. Riffed from Movez's "Jev Engineering" guide
// step 4 (research/write/review queues + confidence gate).
//
// CONFIDENCE_BAR = 0.85 is MOVEZ'S number, not measured here. Their guide
// recommends it as a starting production gate and says to tune it on your
// own labeled workflow examples. Nothing below was tuned: the bar is a
// constant in our code, changeable under review.
//
// The gate: a confident research/write pick routes to that worker. Anything
// else — low confidence, a review pick, a malformed answer — routes to
// review. Low confidence NEVER routes to a worker; review is the safe
// default, and review capacity (not thresholds) is what a overload shows.
//
// NO-CLAIM: a fixture route is not a live handoff. No speed or cost claim
// appears here: not 200x, not $0.042 — those are the guide author's
// numbers on their workload, unmeasured in this tree.
const CLASSES = {
  research: 'Collect missing evidence for the goal before anything is drafted.',
  write: 'Draft from evidence already in hand; nothing material is missing.',
  review: 'Goal unclear, out of scope, work complete, or needs a human glance.',
};

// Movez's production gate, labeled as theirs (see header). Tune on labels.
const CONFIDENCE_BAR = 0.85;

const WORKERS = new Set(['research', 'write']);

function route(choice, confidence) {
  if (WORKERS.has(choice) && typeof confidence === 'number' && confidence >= CONFIDENCE_BAR) {
    return choice;
  }
  return 'review';
}

const INSTRUCTIONS = 'Which job should handle this work next: research, write, or review?';

const JOBS = [
  {
    id: 'vendor-outage',
    goal: 'Explain why checkout webhooks failed between 02:00 and 03:00.',
    completedWork: 'Nothing yet: no logs pulled, no timeline, no cause.',
    recorded: { choice: 'research', confidence: 0.93 },
  },
  {
    id: 'refund-draft',
    goal: 'Answer the billing complaint with a refund confirmation.',
    completedWork: 'Refund issued (receipt r-881), policy section identified.',
    recorded: { choice: 'write', confidence: 0.91 },
  },
  {
    id: 'vague-ask',
    goal: 'Look into the slow thing from yesterday.',
    completedWork: 'No logs, no service name, no time window.',
    recorded: { choice: 'write', confidence: 0.61 },
  },
  {
    id: 'done-review',
    goal: 'Confirm the migration runbook is complete and signed off.',
    completedWork: 'All steps checked, sign-off requested from the owner.',
    recorded: { choice: 'review', confidence: 0.88 },
  },
];

const EXPECT = {
  'vendor-outage': 'research',
  'refund-draft': 'write',
  'vague-ask': 'review',
  'done-review': 'review',
};

function show(rows, lane) {
  console.log(`chief router [${lane}]\n`);
  console.log(`${'destination'.padEnd(13)}${'choice'.padStart(9)}${'conf'.padStart(7)}  job`);
  for (const { job, choice, confidence, destination } of rows) {
    console.log(`${destination.padEnd(13)}${choice.padStart(9)}${confidence.toFixed(2).padStart(7)}  ${job.id}`);
  }
}

function check(rows) {
  const bad = rows.filter(({ job, destination }) => EXPECT[job.id] !== destination);
  if (bad.length > 0) {
    console.error(`FIXTURE DRIFT: ${bad.map(({ job }) => job.id).join(', ')} routed off expectation`);
    process.exit(1);
  }
}

const live = process.argv.includes('--live');

if (!live) {
  const rows = JOBS.map((job) => {
    const destination = route(job.recorded.choice, job.recorded.confidence);
    return { job, choice: job.recorded.choice, confidence: job.recorded.confidence, destination };
  });
  check(rows);
  show(rows, 'fixture — recorded verdicts, no key, no network');
  process.exit(0);
}

const { askJevChoice } = await import('../../work/jev-client/src/index.ts');
const rows = [];
for (const job of JOBS) {
  const r = await askJevChoice({
    state: { goal: job.goal, completedWork: job.completedWork },
    instructions: INSTRUCTIONS,
    classes: CLASSES,
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
  rows.push({ job, choice: r.choice, confidence: r.confidence, destination: route(r.choice, r.confidence) });
}
show(rows, 'live');
