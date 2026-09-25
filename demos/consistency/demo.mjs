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

// The cookbook's rubric, verbatim from "The rubric: 8 `Choice` questions": per question the
// instructions and each label's description (its Choice criteria). The live lane sends exactly
// this; before jev-t6yt it sent "Pick the single most applicable label for <key>." with no label
// descriptions, so the model saw bare label names like `RmLink` and `TSLead`.
const RUBRIC = {
  category: [
    'What is the single most applicable content-policy category for this post?',
    {
      None: 'No policy violation of any kind.',
      Harass: 'Insults or demeans a person, with no threat of harm and no protected-class attack.',
      Hate: 'Attacks a person or group over a protected characteristic (race, religion, gender, ...).',
      Violence: 'Makes a credible threat of harm or incites violence against someone.',
      Spam: 'Unsolicited promotion or link spam, with no personal attack.',
      Sexual: 'Sexual or adult content.',
    },
  ],
  primary_risk: [
    'What is the primary moderation risk that should drive triage for this post?',
    {
      Harassment: 'Personal attack or targeted abuse is the main risk.',
      Violence: 'A threat of harm or intimidation is the main risk.',
      LinkAbuse: 'External-link or off-platform coordination risk is the main risk.',
      AccountHistory: 'Prior account history or repeat behavior is the main risk.',
      LowRisk: 'No meaningful moderation risk is present.',
    },
  ],
  target: [
    'Who or what is the content primarily directed at?',
    {
      None: 'Not directed at anyone in particular.',
      Person: 'Directed at one specific individual.',
      Group: 'Directed at a protected group or class.',
      Platform: 'Directed at the community or platform itself, not a person.',
    },
  ],
  action: [
    'What enforcement action should be taken on this post?',
    {
      Allow: 'Leave the post up with no action.',
      Warn: 'Leave the post up but attach a warning label.',
      Remove: 'Remove the post, but do not penalize the account.',
      Strike: 'Remove the post and add a strike to the account.',
      Escalate: 'Take no automated action; hold for a human decision.',
    },
  ],
  queue: [
    'Which single moderation queue should own this post?',
    {
      Auto: 'Auto-resolve; no human queue needed.',
      General: 'General moderation queue.',
      Threat: 'Threat / violence response queue.',
      Spam: 'Spam and platform-abuse queue.',
      TSLead: 'Trust-and-safety lead / senior queue.',
    },
  ],
  link_handling: [
    'How should any external link or off-platform invite in the post be handled?',
    {
      Allow: 'Leave the link in place.',
      RmLink: 'Strip or disable the link but keep the post.',
      Brigade: 'Treat the link as coordinated brigading and action it as abuse.',
      Escalate: 'Send the link to a specialist to assess before acting.',
    },
  ],
  review_path: [
    'Who should make the final call on this post?',
    {
      Auto: 'Automated action; no human review.',
      Human: 'A frontline human moderator makes the call.',
      Senior: 'A senior or specialist reviewer is required.',
      Legal: 'Route to legal or law-enforcement escalation.',
    },
  ],
  severity: [
    'What is the overall severity of this post?',
    {
      None: 'No violation.',
      Low: 'Rude or dismissive, but essentially harmless.',
      Medium: 'Personal harassment with no clearly credible threat.',
      High: 'Harassment together with a threat that could be read as credible.',
    },
  ],
};

// Label sets per question, in the cookbook's order (what the recorded lane checks against).
const QUESTIONS = Object.fromEntries(Object.entries(RUBRIC).map(([key, [, criteria]]) => [key, Object.keys(criteria)]));

// The cookbook's borderline post, verbatim from its "The state" section
// (docs-mirror/typesafe/cookbooks/consistency_choice_cookbook.md). The recorded REPEATS below
// are assessments of THIS post, so the live lane must send it: before jev-s0f1 the live state
// was the id alone and every live answer judged an empty post.
const POST = {
  post_id: 'P-88213',
  author: { user_id: 'u/4471', account_age_days: 38, prior_strikes: 1, followers: 210 },
  context: {
    surface: 'public reply',
    in_reply_to: 'another user defending a game patch',
    community: 'r/gamedebates',
  },
  content: {
    text:
      'Are you seriously this dense? Anyone who defends that patch is a complete clown and ' +
      "should be embarrassed to even post here. People like you are what's ruining this " +
      "community and honestly you need to be dealt with. Come say it to my face, invite's " +
      "right here. Keep it up and I'll end your whole channel.",
    has_link: true,
    link_domain: 'discord.gg',
    language: 'en',
  },
  reports: { user_reports: 4, report_reasons: ['harassment', 'spam', 'threat'] },
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

const { askJevBundle } = await import('../../kit/src/client.ts');
// The cookbook's system_one call: Choice(instructions, criteria) per rubric question.
const CHOICE_QUESTIONS = Object.fromEntries(
  Object.entries(RUBRIC).map(([key, [instructions, criteria]]) => [key, { type: 'choice', instructions, criteria }]),
);
const liveRepeats = [];
for (let i = 0; i < 3; i++) {
  const r = await askJevBundle({
    // The cookbook's state shape: {uid, post}, the post nested, not spread (jev-t6yt).
    state: { uid: `consistency-demo-${Date.now()}-${i}`, post: POST },
    questions: CHOICE_QUESTIONS,
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
    if (!a || typeof a.probabilities !== 'object') {
      console.error(`live call malformed: answer ${key} has no probabilities`);
      process.exit(1);
    }
    dist[key] = a.probabilities;
  }
  liveRepeats.push(dist);
}
show(run(liveRepeats), 'live');
