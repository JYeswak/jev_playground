#!/usr/bin/env node
// Offline + live CLI for the skillranker EVAL CONTRACT process.
//
// Default is offline: frozen-loss check, expected_values, always-abstain,
// coin-flip, planted-negative RED. Live is a separate lane and prints
// NOT_RUN when TYPESAFE_API_KEY is absent — never a silent skip-as-pass.
//
// --score <picks.jsonl> applies the ≥0.90 gate as exit 2 (explicit FAIL).
// Controls are expected to miss that gate and do not use that exit.

import { readFileSync } from 'node:fs';
import { parseArgs } from 'node:util';
import {
  LOSS,
  TOP1_GATE,
  applyPromotionGate,
  assertFrozenLoss,
  exportJsonl,
  expectedCoinFlipLoss,
  judgeSkillPick,
  loadCases,
  loadPlanted,
  loadPolicy,
  rosterOf,
  runAlwaysAbstain,
  runCoinFlip,
  runPlanted,
  scoreCase,
  summarize,
  verifyExpectedValues,
} from './score.mjs';

const usage = `usage: node work/skillranker-eval/run.mjs [flags]

  --offline              contract + controls + planted RED (default)
  --control NAME         always-abstain | coin-flip
  --trials N             coin-flip trials (default 5000)
  --seed N               coin-flip seed (default 1)
  --planted-negative     wrong-pick fixture; must score 2
  --selftest             planted RED + hard gate + expected_values
  --score FILE           score a candidate picks JSONL; gate FAIL → exit 2
  --live                 Jev choice on the 12 cases; NOT_RUN without a key
  --export FILE          write eval score rows as JSONL
  --binary PATH          reserved; this harness never claims product measured
`;

function parse() {
  const { values } = parseArgs({
    options: {
      offline: { type: 'boolean', default: false },
      control: { type: 'string' },
      trials: { type: 'string', default: '5000' },
      seed: { type: 'string', default: '1' },
      'planted-negative': { type: 'boolean', default: false },
      selftest: { type: 'boolean', default: false },
      score: { type: 'string' },
      live: { type: 'boolean', default: false },
      export: { type: 'string' },
      binary: { type: 'string' },
      help: { type: 'boolean', default: false },
    },
    allowPositionals: false,
  });
  if (values.help) {
    process.stdout.write(usage);
    process.exit(0);
  }
  const named = values.control || values['planted-negative'] || values.selftest || values.score || values.live;
  if (!named) values.offline = true;
  return values;
}

function printSummary(title, summary, extra = {}) {
  console.log(title);
  console.log(`  n=${summary.n}  positives=${summary.positives}  prevalence=${(100 * summary.prevalence).toFixed(1)}%`);
  console.log(`  mean loss=${Number(summary.meanLoss).toFixed(3)}  top-1=${Number(summary.precision).toFixed(3)}  (gate ${TOP1_GATE})`);
  console.log(`  abstains=${summary.abstains}  false-abstain=${summary.falseAbstentions}  wrong-pick=${summary.wrongPicks}  holes=${summary.holes}`);
  if (extra.expected != null) console.log(`  coin-flip exact E[loss]=${extra.expected.toFixed(3)}`);
  if (summary.sampledMean != null) {
    console.log(`  coin-flip sampled mean=${summary.sampledMean.toFixed(3)} sd=${summary.sampledSd.toFixed(3)} trials=${summary.trials} seed=${summary.seed}`);
  }
}

function printNoClaim() {
  console.log('NO-CLAIM: diagnostic_synthetic n=12; not a SkillRanker product measurement (no sr binary invoked); not a promotion.');
}

function maybeExport(path, rows) {
  if (!path) return;
  const out = exportJsonl(path, rows);
  console.log(`EXPORT  ${out.n} rows → ${out.path}  schema=jev.skillranker-eval.score.v1`);
}

function readPicks(path) {
  return readFileSync(path, 'utf8')
    .split('\n')
    .filter((l) => l.trim())
    .map((l) => JSON.parse(l));
}

function scorePicks(cases, picks) {
  const byId = new Map(picks.map((p) => [p.case_id, p]));
  const missing = [];
  const rows = cases.map((c) => {
    const p = byId.get(c.case_id);
    if (!p) {
      missing.push(c.case_id);
      return scoreCase(c, NONE, { judge: 'injected', lane: 'offline', unavailable: true });
    }
    return scoreCase(c, p.pick ?? NONE, {
      judge: p.judge ?? 'injected',
      lane: p.lane ?? 'offline',
      unavailable: p.unavailable === true,
      model: p.model ?? null,
    });
  });
  if (missing.length) {
    console.log(`MISSING PICKS treated as operational unavailable (loss 2): ${missing.join(', ')}`);
  }
  return { rows, summary: summarize(rows) };
}

async function runLive(cases) {
  const key = process.env.TYPESAFE_API_KEY;
  if (!key) {
    console.log('LIVE: NOT_RUN (TYPESAFE_API_KEY unset). Offline lane is the default; this is not a pass.');
    return { notRun: true, rows: [], summary: null };
  }
  const { askJevChoice } = await import('../../kit/src/client.ts');
  const rows = [];
  for (const c of cases) {
    const judged = await judgeSkillPick({
      roster: rosterOf(c),
      task: c.prompt_summary,
      constraints: c.current_constraints ?? '',
      already_loaded: c.already_available_references ?? [],
      ask: askJevChoice,
      model: process.env.JEV_MODEL ?? 'jev-1.13.0',
    });
    const row = scoreCase(c, judged.pick, {
      judge: 'jev-choice',
      lane: 'live',
      unavailable: judged.unavailable === true,
      model: judged.model,
      topP: judged.topP,
      measured_product: false,
    });
    rows.push(row);
    process.stderr.write('.');
  }
  process.stderr.write('\n');
  return { notRun: false, rows, summary: summarize(rows) };
}

async function main() {
  const opt = parse();
  if (opt.binary) {
    console.log(`BINARY: ${opt.binary} was passed but this harness does not invoke sr.`);
    console.log('measured_product remains false. Do not cite this run as a SkillRanker product result.');
  }

  const policy = loadPolicy();
  assertFrozenLoss(policy);
  const cases = loadCases();

  if (opt.selftest) {
    verifyExpectedValues();
    const planted = runPlanted(loadPlanted());
    printSummary('PLANTED NEGATIVE (must RED / loss=2)', planted.summary);
    const aa = runAlwaysAbstain(cases);
    const gateOnAbstain = applyPromotionGate(aa.summary, { split: 'diagnostic_synthetic' });
    if (!gateOnAbstain.fail) {
      throw new Error('SELFTEST FAIL: always-abstain cleared the 0.90 gate (gate is not hard)');
    }
    const priorLive = applyPromotionGate({ ...aa.summary, precision: 0.8, positives: 10 }, { split: 'diagnostic_synthetic' });
    if (!priorLive.fail) {
      throw new Error('SELFTEST FAIL: precision 0.800 did not FAIL the gate');
    }
    const atGate = applyPromotionGate({ ...aa.summary, precision: 0.9, positives: 10 }, { split: 'diagnostic_synthetic' });
    if (atGate.fail) throw new Error('SELFTEST FAIL: precision 0.900 should rate-pass');
    if (atGate.promotable) throw new Error('SELFTEST FAIL: n=12 diagnostic_synthetic must not be promotable');
    console.log('SELFTEST PASS  planted RED, gate hard at 0.90, expected_values match, split blocks promotion');
    printNoClaim();
    maybeExport(opt.export, planted.rows);
    return;
  }

  if (opt['planted-negative']) {
    const planted = runPlanted(loadPlanted());
    printSummary('PLANTED NEGATIVE', planted.summary);
    console.log('VERDICT: RED as required (wrong pick scored 2)');
    printNoClaim();
    maybeExport(opt.export, planted.rows);
    return;
  }

  if (opt.control === 'always-abstain') {
    const { rows, summary } = runAlwaysAbstain(cases);
    printSummary('CONTROL always-abstain', summary);
    printNoClaim();
    maybeExport(opt.export, rows);
    return;
  }

  if (opt.control === 'coin-flip') {
    const trials = Number(opt.trials);
    const seed = Number(opt.seed);
    const out = runCoinFlip(cases, { trials, seed });
    printSummary('CONTROL coin-flip', out.summary, { expected: out.expected });
    printNoClaim();
    maybeExport(opt.export, out.rows);
    return;
  }

  if (opt.score) {
    const picks = readPicks(opt.score);
    const { rows, summary } = scorePicks(cases, picks);
    printSummary(`CANDIDATE ${opt.score}`, summary);
    const gate = applyPromotionGate(summary, { split: 'diagnostic_synthetic' });
    console.log(`GATE  ratePass=${gate.ratePass}  promotable=${gate.promotable}  fail=${gate.fail}`);
    for (const f of gate.failures) console.log(`  - ${f.code}: ${f.message}`);
    printNoClaim();
    maybeExport(opt.export, rows);
    if (gate.fail) {
      console.error(`GATE FAIL: top-1 precision ${summary.precision} < ${TOP1_GATE}`);
      process.exitCode = 2;
    }
    return;
  }

  if (opt.live) {
    const live = await runLive(cases);
    if (live.notRun) {
      printNoClaim();
      return;
    }
    printSummary('LIVE jev-choice on skillranker corpus (NOT skillranker the product)', live.summary);
    const gate = applyPromotionGate(live.summary, { split: 'diagnostic_synthetic' });
    console.log(`GATE  ratePass=${gate.ratePass}  promotable=${gate.promotable}  fail=${gate.fail}`);
    for (const f of gate.failures) console.log(`  - ${f.code}: ${f.message}`);
    printNoClaim();
    maybeExport(opt.export, live.rows);
    if (gate.fail) {
      console.error(`GATE FAIL: top-1 precision ${live.summary.precision} < ${TOP1_GATE}`);
      process.exitCode = 2;
    }
    return;
  }

  // default --offline
  console.log('OFFLINE  skillranker eval-contract mirror');
  console.log(`  policy=${policy.policy_id}  status=${policy.status}  loss.wrong_pick=${LOSS.incorrect_recommendation_on_positive}`);
  const expected = verifyExpectedValues();
  console.log(`  expected_values  ${expected.examples} loss examples recomputed`);
  const aa = runAlwaysAbstain(cases);
  printSummary('CONTROL always-abstain', aa.summary);
  const cf = runCoinFlip(cases, { trials: Number(opt.trials), seed: Number(opt.seed) });
  printSummary('CONTROL coin-flip', cf.summary, { expected: expectedCoinFlipLoss(cases) });
  const planted = runPlanted(loadPlanted());
  printSummary('PLANTED NEGATIVE (wrong pick → 2)', planted.summary);
  const holes = aa.rows.filter((r) => r.installableNotOffered).map((r) => r.case_id);
  console.log(`HOLE  installable≠offered (Y not in exported roster): ${holes.join(', ') || '(none)'}`);
  printNoClaim();
  maybeExport(opt.export, [...aa.rows, ...cf.rows, ...planted.rows]);
}

main().catch((err) => {
  console.error(err.message ?? err);
  process.exitCode = 1;
});
