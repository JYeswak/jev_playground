// Does jev-model-router's TIER choice predict how hard a turn actually was?
//
// The mod routes subagent model and main-loop EFFORT (routeMainModel defaults off, which our own
// +90.2% finding endorses). So the question is not "does it save money" -- it is "does the tier
// it picks carry information about the work the turn turned out to need?"
//
// GROUND TRUTH, deterministic and not supplied by the model: the number of tool calls the turn
// actually made. A prompt that ended up costing >= HARD_CALLS tool calls was hard work; one that
// ended in < EASY_CALLS was mechanical. Both are read from the transcript AFTER the fact, so the
// judge cannot see them.
//
// WIN CONDITION, PREREGISTERED HERE BEFORE THE FIRST RUN (2026-09-19):
//   ADOPT the tier signal if, over >= 60 real prompts,
//     (a) AUC(tier_rank vs hard-turn) >= 0.70, AND
//     (b) it beats a PROMPT-LENGTH-ONLY baseline by >= 0.05 AUC.
//   (b) exists because length is the dumb baseline that has already beaten a model twice today.
// FEASIBILITY ARM: the same scorer is run on a label the pipeline must be able to detect --
// "did this prompt mention a file path" -- which is near-deterministic from the text. If that
// arm does not clear 0.80, the harness is blind and NO verdict about the router is reported.
import { readFileSync } from 'node:fs';
// Lane-sanctioned caller (943158c): askJevBundle passes the MIXED
// Choice+Score+Noul battery through unmodified. No hand-rolled POST,
// no private client.
import { askJevBundle } from '../../kit/src/client.ts';
import { auc as kitAuc, field } from '../oracle-kit/index.mjs';

const HARD_CALLS = 5, EASY_CALLS = 2, AUC_BAR = 0.70, MARGIN_BAR = 0.05, ARM_BAR = 0.80;
const rows = readFileSync(process.argv[2], 'utf8').split('\n').filter(Boolean)
  .map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);

// A turn = a user prompt, then every tool call until the next user prompt.
const turns = [];
let cur = null;
for (const r of rows) {
  const m = r.message; if (!m) continue;
  const parts = Array.isArray(m.content) ? m.content : [];
  // omp stores EVERY role's content as a parts array; a user prompt is its concatenated text.
  if (m.role === 'user') {
    const text = parts.filter(p => p?.type === 'text').map(p => p.text).join('\n').trim();
    if (text) { if (cur) turns.push(cur); cur = { prompt: text.slice(0, 2000), calls: 0 }; }
  } else if (cur) {
    cur.calls += parts.filter(p => p?.type === 'toolCall').length;
  }
}
if (cur) turns.push(cur);
const usable = turns.filter(t => t.prompt.length > 20 && (t.calls >= HARD_CALLS || t.calls < EASY_CALLS));
console.log(`turns=${turns.length}  usable=${usable.length}  hard=${usable.filter(t => t.calls >= HARD_CALLS).length}`);
if (usable.length < 20) { console.log('SKIP: too few usable turns in this session'); process.exit(0); }

// BALANCED DRAW, declared before measuring: the raw pool is ~10:1 hard:easy, and an imbalanced
// denominator lets a weak signal look strong. Take every easy turn and an equal number of hard
// ones, evenly spaced through the session so the draw is not front-loaded.
const CAP = Number(process.env.CAP ?? 60);
const easies = usable.filter(t => t.calls < EASY_CALLS);
const hards = usable.filter(t => t.calls >= HARD_CALLS);
const per = Math.min(easies.length, hards.length, Math.floor(CAP / 2));
const pick = (arr, k) => Array.from({ length: k }, (_, i) => arr[Math.floor(i * arr.length / k)]);
const sample = [...pick(easies, per), ...pick(hards, per)];
const hard = sample.map(t => t.calls >= HARD_CALLS);
const hasPath = sample.map(t => /[\w-]+\/[\w./-]+|\.\w{2,4}\b/.test(t.prompt));   // feasibility arm label

const auc = (scores, labels) => kitAuc(scores, labels).value;

const TIERS = { mechanical: 'Mechanical and local: a rename, a small edit, a lookup.',
                ordinary: 'Ordinary engineering: a normal feature or fix.',
                hard: 'Hard or high-stakes: design, debugging, or something risky.' };
const tierRank = [], armScore = [];
for (const t of sample) {
  const r = await askJevBundle({
    model: 'jev-1.13.0', // pinned: the previous code sent no model (SDK default moves).
    state: { task: t.prompt },
    questions: {
      tier: { type: 'choice', instructions: 'How hard is this task?', criteria: TIERS },
      effort: { type: 'score', instructions: 'How much step-by-step reasoning does this need?', criteria: ['none', 'a little', 'a lot', 'extensive'] },
      mentions_file: { type: 'noul', instructions: 'Does this task text mention a specific file or path?' },
    },
    apiKey: process.env.TYPESAFE_API_KEY,
    timeoutMs: 20000,
  });
  if (!r.ok && r.reason === 'unconfigured') {
    console.log('SKIP: unconfigured (TYPESAFE_API_KEY unset) — no network attempted');
    process.exit(2);
  }
  if (!r.ok) throw new Error(`Invalid Jev answer: ${r.reason} ${r.error}`);
  // The field is `probabilities`, NOT `distribution`. Using the wrong name yields a constant 0
  // score and therefore an all-ties AUC of exactly 0.500 -- which is what three bogus REJECT runs
  // reported before this was caught. Fail loudly instead of scoring silence.
  const d = field(r.answers.tier, 'probabilities');
  // rank = expected tier index, so the whole distribution is used rather than the argmax alone
  tierRank.push((d.ordinary ?? 0) * 1 + (d.hard ?? 0) * 2);
  armScore.push(Number(field(r.answers.mentions_file, 'noul')));
  process.stderr.write('.');
}
const lenBaseline = sample.map(t => t.prompt.length);
const aTier = auc(tierRank, hard), aLen = auc(lenBaseline, hard), aArm = auc(armScore, hasPath);
console.log(`\nn=${sample.length}`);
console.log(`FEASIBILITY ARM  mentions-a-path AUC=${aArm.toFixed(3)}  (bar ${ARM_BAR})`);
if (!(aArm >= ARM_BAR)) { console.log('HARNESS BLIND -- no verdict about the router is reported.'); process.exit(0); }
console.log(`tier   AUC=${aTier.toFixed(3)}   length-baseline AUC=${aLen.toFixed(3)}   margin=${(aTier - aLen).toFixed(3)}`);
console.log(`VERDICT: ${aTier >= AUC_BAR && (aTier - aLen) >= MARGIN_BAR ? 'ADOPT tier signal' : 'REJECT -- does not clear the preregistered bar'}`);
