#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, relative } from 'node:path';
import { readSessionLogs } from '../src/transcript-reader.mjs';
import {
  DEFAULT_POLICY,
  MIN_CLASSIFIABLE_TURNS,
  runCounterfactual,
  validateBacktestFloor,
} from '../src/counterfactual.mjs';

function usage(message) {
  if (message) console.error(`ERROR ${message}`);
  console.error('usage: npm run backtest -- <session.jsonl>... --out runs/backtest.json');
  console.error('');
  console.error('Answers one question: would model routing have saved money on YOUR sessions?');
  console.error('Offline, no API key, no network. Reads omp session JSONL and writes a receipt.');
  console.error('');
  console.error('  npm run backtest -- fixtures/real-excerpt-t1-t6.jsonl --out runs/try.json');
  console.error('');
  console.error('The other fixtures are INTENTIONAL NEGATIVES (unknown model, zero classifiable');
  console.error('turns) and are meant to fail; a glob over all of them returns a failure receipt.');
  // process.exitCode alone does NOT stop execution: argument validation continued with `out`
  // undefined, reached dirname(undefined), and the FIRST THING A STRANGER SAW was an
  // ERR_INVALID_ARG_TYPE stack trace instead of this text. Exit here.
  process.exit(2);
}

function displayPath(path) {
  const home = process.env.HOME;
  if (home && path.startsWith(`${home}/`)) return `~/${path.slice(home.length + 1)}`;
  const rel = relative(process.cwd(), path);
  return rel && !rel.startsWith('../') ? rel : path;
}

function parseArgs(argv) {
  const inputs = [];
  let out = null;
  let prices = null;
  let maxPromptTokens = null;
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--out') {
      out = argv[++index];
      if (!out) usage('--out needs a path');
    } else if (arg === '--max-prompt-tokens') {
      // THE POLICY WAS HARDCODED AT 20,000 AND A READER COULD NOT ASK A DIFFERENT QUESTION.
      // On a real Claude Code corpus every turn carries a large cached prefix, so with the ruled
      // context rule (input + cache_read + cache_creation) NOT ONE of 47,428 turns fit the 20k
      // budget and the demo refused with NO_CHEAP_CANDIDATES. That refusal is honest, but "no turn
      // fits 20k" is only interesting if you can also ask what budget WOULD fit — otherwise the
      // demo answers one question about someone else's assumption.
      maxPromptTokens = Number(argv[++index]);
      if (!Number.isFinite(maxPromptTokens) || maxPromptTokens <= 0) {
        usage('--max-prompt-tokens needs a positive number');
      }
    } else if (arg === '--prices') {
      // The engine has ALWAYS accepted an injected price table (runCounterfactual's options.priceTable);
      // the CLI simply had no way to pass one, so every run used the built-in table and any model
      // outside it was refused with MISSING_PRICE_MODEL. That refusal is correct and stays. This flag
      // only lets a reader supply rates for their OWN models instead of being unable to answer at all.
      prices = argv[++index];
      if (!prices) usage('--prices needs a path to a price-table JSON');
    } else if (arg.startsWith('--')) {
      usage(`unknown option: ${arg}`);
    } else {
      inputs.push(arg);
    }
  }
  if (inputs.length === 0) usage('at least one session JSONL is required');
  if (!out) usage('--out is required so the run is receipted');
  return { inputs, out, prices, maxPromptTokens };
}

const { inputs, out, prices, maxPromptTokens } = parseArgs(process.argv.slice(2));
const absoluteInputs = inputs.map((path) => (path.startsWith('/') ? path : `${process.cwd()}/${path}`));
const baseReceipt = {
  schema: 'jev.route-backtest.receipt.v1',
  generated_at: new Date().toISOString(),
  inputs: absoluteInputs.map(displayPath),
  // THE EFFECTIVE POLICY, not the default. The receipt printed DEFAULT_POLICY, so a run with
  // --max-prompt-tokens would have recorded 20000 while having actually used another number —
  // a receipt that misstates the assumption it ran under is worse than no receipt.
  policy: maxPromptTokens !== null ? { ...DEFAULT_POLICY, maxPromptTokens } : DEFAULT_POLICY,
  floor: {
    minimumClassifiableTurns: MIN_CLASSIFIABLE_TURNS,
    requiresCheapCandidate: true,
    requiresBaselineCandidate: true,
  },
  failures: [],
};

try {
  const parsed = await readSessionLogs(absoluteInputs);
  let priceTable;
  if (prices) {
    try {
      priceTable = JSON.parse(readFileSync(prices, 'utf8'));
    } catch (err) {
      console.error(`backtest: price table unreadable: ${err.message}`);
      process.exit(2);
    }
    if (!priceTable.models || typeof priceTable.models !== 'object') {
      console.error('backtest: price table has no models object');
      process.exit(2);
    }
  }
  const options = {};
  if (priceTable) options.priceTable = priceTable;
  if (maxPromptTokens !== null) options.policy = { ...DEFAULT_POLICY, maxPromptTokens };
  const result = runCounterfactual(parsed.sessions, Object.keys(options).length ? options : undefined);
  const failures = validateBacktestFloor(result);
  const receipt = {
    ...baseReceipt,
    priceTable: result.priceTable,
    denominator: parsed.totals,
    // WHY EACH TURN DID NOT QUALIFY, aggregated. The engine already computes a reason per turn and
    // the receipt threw every one away, so the demo could report that routing was blocked but never
    // BY WHAT. Measured on real logs: zero turns exceeded the 2,000-token completion budget while 291
    // of 500 carried tool calls, so the completion budget never binds and maxToolCalls does — and the
    // prompt-budget sweep alone would have told a reader none of that. A histogram, not per-turn rows:
    // one line per reason keeps the receipt small enough to read.
    blockedBy: result.turns.reduce((acc, turn) => {
      if (turn.cheapSufficient) return acc;
      // classificationReason, not reason. My first version read `turn.reason`, which does not
      // exist on these objects, and every blocked turn aggregated as 'unrecorded' — a histogram
      // that looked populated and carried no information. The 'unrecorded' bucket is KEPT rather
      // than defaulted away, so the same mistake shows up as a number next time instead of
      // hiding behind a plausible label.
      const reason = turn.classificationReason ?? 'unrecorded';
      acc[reason] = (acc[reason] ?? 0) + 1;
      return acc;
    }, {}),
    sessions: parsed.sessions.map((session) => ({
      source: displayPath(session.source),
      sessionId: session.sessionId,
      rows: session.rows,
      totals: session.totals,
    })),
    perModel: result.perModel,
    totals: result.totals,
    turns: result.turns,
    failures,
  };
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, `${JSON.stringify(receipt, null, 2)}\n`);
  console.log(JSON.stringify({ output: out, denominator: parsed.totals, failures: failures.length }));
  process.exitCode = failures.length ? 1 : 0;
} catch (error) {
  const receipt = {
    ...baseReceipt,
    failures: [{ code: error.code ?? 'BACKTEST_ERROR', message: error.message }],
  };
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, `${JSON.stringify(receipt, null, 2)}\n`);
  console.error(JSON.stringify(receipt));
  process.exitCode = 1;
}
