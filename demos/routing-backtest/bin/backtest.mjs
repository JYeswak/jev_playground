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
  process.exitCode = 2;
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
