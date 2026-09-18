#!/usr/bin/env node
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
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--out') {
      out = argv[++index];
      if (!out) usage('--out needs a path');
    } else if (arg.startsWith('--')) {
      usage(`unknown option: ${arg}`);
    } else {
      inputs.push(arg);
    }
  }
  if (inputs.length === 0) usage('at least one session JSONL is required');
  if (!out) usage('--out is required so the run is receipted');
  return { inputs, out };
}

const { inputs, out } = parseArgs(process.argv.slice(2));
const absoluteInputs = inputs.map((path) => (path.startsWith('/') ? path : `${process.cwd()}/${path}`));
const baseReceipt = {
  schema: 'jev.route-backtest.receipt.v1',
  generated_at: new Date().toISOString(),
  inputs: absoluteInputs.map(displayPath),
  policy: DEFAULT_POLICY,
  floor: {
    minimumClassifiableTurns: MIN_CLASSIFIABLE_TURNS,
    requiresCheapCandidate: true,
    requiresBaselineCandidate: true,
  },
  failures: [],
};

try {
  const parsed = await readSessionLogs(absoluteInputs);
  const result = runCounterfactual(parsed.sessions);
  const failures = validateBacktestFloor(result);
  const receipt = {
    ...baseReceipt,
    priceTable: result.priceTable,
    denominator: parsed.totals,
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
