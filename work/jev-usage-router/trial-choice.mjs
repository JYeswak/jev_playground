#!/usr/bin/env node
/**
 * trial-choice: the usage router's one Choice on real, non-authored goals (jev-vbh.4).
 *
 * Sends the exact request src/router.mjs sends (CRITERIA, INSTRUCTIONS, routeState) for a pinned,
 * stratified sample of goals-2026-09-25.jsonl, three repeats each, then prints every decision and
 * the preregistered measurements (docs/demos/upstream-repro/usage-router-trial-choice-prereg-20260925.md).
 * No ruling is written.
 *
 * Usage:
 *   infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/jev-usage-router/trial-choice.mjs [--limit N] [--out FILE]
 * Exit: 0 run complete, 2 NOT_RUN (no key), 3 refused (key not OK, corpus hash mismatch, or a
 * 401/402 stop), 1 any other error.
 */
import { createHash, timingSafeEqual } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { appendFileSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { askJevChoice } from '../../kit/src/client.ts';
import { CRITERIA, INSTRUCTIONS, routeState } from './src/router.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
export const MODEL = 'jev-1.13.0';
export const FLOOR = 0.55;
export const SEED = 20260925;
export const REPEATS = 3;
export const GOALS = path.join(HERE, 'goals-2026-09-25.jsonl');
export const GOALS_SHA256 = '0d6445dd0e39fa9c7a61e27fc537832aaabf5d268c87a83d60496f1e73a3fd12';
const OFF_LOCAL = new Set(['research', 'browser']);

/** mulberry32: the preregistered seeded generator. */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** All non-local goals, plus as many local goals, drawn by a seeded Fisher-Yates over file order. */
export function sampleGoals(goals, seed = SEED) {
  const offLocal = goals.filter((g) => g.label !== 'local');
  const local = goals.filter((g) => g.label === 'local');
  const rand = mulberry32(seed);
  const order = local.slice();
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  const picked = order.slice(0, offLocal.length);
  return [...offLocal, ...picked].sort((x, y) => x.i - y.i);
}

/** The router's policy: act on the choice at or above the floor, otherwise abstain as bypass. */
export function policyAction(answer, floor = FLOOR) {
  if (!answer.ok) return null;
  return answer.confidence >= floor ? answer.choice : 'bypass';
}

const BROWSER_WORDS = /\b(browser|click|screenshot|booking|book a)\b/i;
const RESEARCH_WORDS = /https?:\/\/|\b(web|search|online|internet|arxiv|leaderboard|published|latest|look up|google|browse|website|download)\b/i;

/** The preregistered lexical baseline. */
export function lexicalRoute(goal) {
  if (BROWSER_WORDS.test(goal)) return 'browser';
  if (RESEARCH_WORDS.test(goal)) return 'research';
  return 'local';
}

/** Most frequent action over repeats; ties go to the first repeat's action. */
export function majority(actions) {
  const counts = new Map();
  for (const a of actions) counts.set(a, (counts.get(a) ?? 0) + 1);
  let best = actions[0];
  for (const [a, n] of counts) if (n > counts.get(best)) best = a;
  return best;
}

function rate(num, den) {
  return den ? num / den : null;
}

/** Recall, false-route rate and prevalence precision for one per-goal action map. */
export function routeStats(goals, actionOf, prevalence) {
  const offGoals = goals.filter((g) => g.label !== 'local');
  const localGoals = goals.filter((g) => g.label === 'local');
  const recall = rate(offGoals.filter((g) => OFF_LOCAL.has(actionOf(g))).length, offGoals.length);
  const falseRoute = rate(localGoals.filter((g) => OFF_LOCAL.has(actionOf(g))).length, localGoals.length);
  const precision =
    recall === null || falseRoute === null || recall * prevalence + falseRoute * (1 - prevalence) === 0
      ? null
      : (recall * prevalence) / (recall * prevalence + falseRoute * (1 - prevalence));
  const shortOff = offGoals.filter((g) => g.short);
  const shortSafe = shortOff.filter((g) => OFF_LOCAL.has(actionOf(g)) || actionOf(g) === 'bypass').length;
  return {
    off_local_recall: recall,
    local_false_route: falseRoute,
    precision_at_prevalence: precision,
    short_off_local: shortOff.length,
    short_routed_or_abstained: shortSafe,
    short_rate: rate(shortSafe, shortOff.length),
    short_meets_5_of_6: shortOff.length ? shortSafe / shortOff.length >= 5 / 6 : null,
  };
}

/** Everything the prereg asks for, from the answer rows alone. */
export function summarize(sample, rows, prevalence) {
  const byGoal = new Map();
  for (const r of rows) {
    if (!byGoal.has(r.i)) byGoal.set(r.i, []);
    byGoal.get(r.i).push(r);
  }
  const incoherent = rows.filter((r) => !r.ok && r.reason === 'no-answers').length;
  const transport = rows.filter((r) => !r.ok && r.reason !== 'no-answers').length;
  const answered = sample.filter((g) => (byGoal.get(g.i) ?? []).some((r) => r.ok));
  let drift = 0;
  const actionByGoal = new Map();
  for (const g of answered) {
    const ok = byGoal.get(g.i).filter((r) => r.ok);
    if (new Set(ok.map((r) => r.choice)).size > 1) drift++;
    actionByGoal.set(g.i, majority(ok.map((r) => r.action)));
  }
  const distribution = {};
  for (const g of answered) {
    const a = actionByGoal.get(g.i);
    distribution[g.label] ??= {};
    distribution[g.label][a] = (distribution[g.label][a] ?? 0) + 1;
  }
  const jev = routeStats(answered, (g) => actionByGoal.get(g.i), prevalence);
  const pane1 = routeStats(answered.filter((g) => g.from_pane1), (g) => actionByGoal.get(g.i), prevalence);
  const others = routeStats(answered.filter((g) => !g.from_pane1), (g) => actionByGoal.get(g.i), prevalence);
  return {
    requests: rows.length,
    incoherent,
    transport_failures: transport,
    goals_answered: answered.length,
    drift_goals: drift,
    distribution,
    jev,
    jev_pane1_dispatches: pane1,
    jev_other_goals: others,
    always_local: routeStats(answered, () => 'local', prevalence),
    lexical: routeStats(answered, (g) => lexicalRoute(g.goal), prevalence),
  };
}

function loadGoals(file) {
  const bytes = readFileSync(file);
  const sha = createHash('sha256').update(bytes).digest('hex');
  const goals = bytes.toString('utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l));
  return { goals, sha };
}

function keyStatusOk() {
  const r = spawnSync('python3', [path.join(ROOT, 'scripts', 'key-status.py')], { encoding: 'utf8' });
  process.stdout.write(r.stdout ?? '');
  process.stderr.write(r.stderr ?? '');
  return r.status === 0;
}

async function pool(items, width, fn) {
  let next = 0;
  await Promise.all(
    Array.from({ length: width }, async () => {
      while (next < items.length) await fn(items[next++]);
    }),
  );
}

export async function runTrial({ sample, askChoice = askJevChoice, write = () => {}, codeSha, now = () => new Date(), concurrency = 8, timeoutMs = 15000 }) {
  const rows = [];
  let hardStops = 0;
  let stopped = false;
  const jobs = sample.flatMap((g) => Array.from({ length: REPEATS }, (_, repeat) => ({ g, repeat })));
  await pool(jobs, concurrency, async ({ g, repeat }) => {
    if (stopped) return;
    const r = await askChoice({ state: routeState({ goal: g.goal }), instructions: INSTRUCTIONS, classes: CRITERIA, model: MODEL, timeoutMs });
    const status = /\b(401|402)\b/.test(String(r.error ?? '')) ? 'auth-or-billing' : null;
    hardStops = status ? hardStops + 1 : 0;
    if (hardStops >= 3) stopped = true;
    const row = {
      i: g.i,
      repeat,
      label: g.label,
      short: g.short,
      from_pane1: g.from_pane1,
      ok: r.ok,
      reason: r.ok ? null : r.reason,
      error: r.ok ? null : String(r.error ?? '').slice(0, 200),
      choice: r.ok ? r.choice : null,
      confidence: r.ok ? r.confidence : null,
      probabilities: r.ok ? r.probabilities : null,
      action: policyAction(r),
      latencyMs: r.latencyMs,
      model: r.model,
      code_sha256: codeSha,
      recorded_at_utc: now().toISOString(),
    };
    rows.push(row);
    write(row);
  });
  return { rows, stopped };
}

function fmt(x) {
  if (x === null || x === undefined) return '-';
  if (typeof x === 'number') return x.toFixed(3);
  return String(x);
}

async function main() {
  const args = process.argv.slice(2);
  const opt = (name) => {
    const k = args.indexOf(name);
    return k >= 0 ? args[k + 1] : undefined;
  };
  const limit = opt('--limit') ? Number(opt('--limit')) : undefined;
  const out = opt('--out') ?? path.join(HERE, 'trial-rows-2026-09-25.jsonl');

  if (!process.env.TYPESAFE_API_KEY) {
    console.log('NOT_RUN: TYPESAFE_API_KEY unset; run under infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --');
    return 2;
  }
  const { goals, sha } = loadGoals(GOALS);
  if (sha.length !== GOALS_SHA256.length || !timingSafeEqual(Buffer.from(sha), Buffer.from(GOALS_SHA256))) {
    console.log(`REFUSED: ${path.relative(ROOT, GOALS)} sha256 ${sha} != preregistered ${GOALS_SHA256}`);
    return 3;
  }
  if (!keyStatusOk()) {
    console.log('REFUSED: scripts/key-status.py did not print OK; no request sent');
    return 3;
  }
  let sample = sampleGoals(goals);
  if (limit) sample = sample.slice(0, limit);
  const codeSha = createHash('sha256').update(readFileSync(fileURLToPath(import.meta.url))).digest('hex');
  const prevalence = goals.filter((g) => g.label !== 'local').length / goals.length;
  const { rows, stopped } = await runTrial({ sample, codeSha, write: (row) => appendFileSync(out, JSON.stringify(row) + '\n') });

  for (const g of sample) {
    const mine = rows.filter((r) => r.i === g.i).sort((a, b) => a.repeat - b.repeat);
    const cells = mine.map((r) => (r.ok ? `${r.choice}@${fmt(r.confidence)}` : `ERR:${r.reason}`)).join(' ');
    const p = mine.find((r) => r.ok)?.probabilities;
    console.log(`goal ${g.i} label=${g.label}${g.short ? ' short' : ''} :: ${cells} :: p=${p ? JSON.stringify(p) : '-'}`);
  }
  const s = summarize(sample, rows, prevalence);
  console.log(JSON.stringify({ corpus_sha256: sha, sample: sample.length, prevalence, stopped, rows_file: path.relative(ROOT, out), ...s }, null, 1));
  if (stopped) {
    console.log('STOPPED: three consecutive 401/402 answers');
    return 3;
  }
  return 0;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().then(
    (code) => process.exit(code),
    (err) => {
      console.error(err);
      process.exit(1);
    },
  );
}
