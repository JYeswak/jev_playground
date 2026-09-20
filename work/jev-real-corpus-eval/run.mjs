#!/usr/bin/env node
// One-command scorer for the frozen toolcall corpus. Offline. No TYPESAFE.
//
// Prints n, prevalence, always-abstain mean loss, isError baseline mean loss,
// planted-RED. Exit 0 on a completed measurement; 2 if identity lock or
// planted RED fails; 1 on unexpected error.
//
// CASS (~59.8k conv) and live agent-mail (~6510 messages) are NOT queried
// here. This cloud VM cannot reach those volumes.

import { writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { parseArgs } from 'node:util';
import {
  FROZEN,
  loadFrozen,
  loadRows,
  refuseAuthoredSubstitute,
  runAlwaysAbstain,
  runAlwaysAllow,
  runIsErrorBaseline,
  runPlantedFalseAllow,
  toolCensus,
} from './score.mjs';

const usage = `usage: node work/jev-real-corpus-eval/run.mjs [flags]

  (default)              score frozen corpus + always-abstain + isError baseline + planted RED
  --selftest             same planted RED arms the unit tests prove
  --control NAME         always-abstain | always-allow
  --help
`;

function parse() {
  const { values } = parseArgs({
    options: {
      selftest: { type: 'boolean', default: false },
      control: { type: 'string' },
      help: { type: 'boolean', default: false },
    },
    allowPositionals: false,
  });
  if (values.help) {
    process.stdout.write(usage);
    process.exit(0);
  }
  return values;
}

function fmt(n) {
  return Number(n).toFixed(6);
}

function printLine(title, summary) {
  console.log(
    `${title}  n=${summary.n}  GOOD=${summary.good}  BAD=${summary.bad}  ` +
      `prevalence=${fmt(summary.prevalence)}  mean_loss=${fmt(summary.meanLoss)}`,
  );
}

function writePlant(rows) {
  const path = join(tmpdir(), `jev-real-corpus-plant-${process.pid}.jsonl`);
  writeFileSync(path, rows.map((r) => JSON.stringify(r)).join('\n') + '\n');
  return path;
}

function plantedRed() {
  const bad = {
    ts: '2026-09-20T00:00:00.000Z',
    kind: 'dcg_allow',
    tid: 'planted-false-allow',
    sess: 'plant',
    tool: 'bash',
    isError: false,
    args: '{"command":"planted"}',
    outcome: 'BAD',
  };
  const falseAllow = runPlantedFalseAllow([bad]);
  const authored = Array.from({ length: 10 }, (_, i) => ({
    ...bad,
    tid: `authored-${i}`,
    outcome: i < 8 ? 'GOOD' : 'BAD',
  }));
  const authoredPath = writePlant(authored);
  let refused = false;
  try {
    refuseAuthoredSubstitute(authoredPath);
  } catch (err) {
    const msg = String(err.message ?? err);
    if (/authored|diagnostic_synthetic|n=10|7846/.test(msg)) refused = true;
    else throw err;
  }
  if (!refused) {
    throw new Error('PLANTED NEGATIVE DID NOT RED: 10-row authored substitute was scored');
  }
  return {
    falseAllowLoss: falseAllow.rows[0].loss,
    authoredRefused: true,
    authoredPath,
  };
}

function main() {
  const opt = parse();

  if (opt.selftest) {
    const plant = plantedRed();
    console.log(`PLANTED-RED  false-allow-on-BAD loss=${plant.falseAllowLoss}  authored-n=10 REFUSED`);
    console.log('SELFTEST PASS');
    return;
  }

  if (opt.control === 'always-abstain' || opt.control === 'always-allow') {
    const { rows, identity } = loadFrozen();
    const run = opt.control === 'always-abstain' ? runAlwaysAbstain : runAlwaysAllow;
    const { summary } = run(rows);
    console.log(`FROZEN  sha256=${identity.sha256}  path=${identity.path}`);
    printLine(`CONTROL ${opt.control}`, summary);
    return;
  }

  const { rows, identity } = loadFrozen();
  const control = runAlwaysAbstain(rows).summary;
  const baseline = runIsErrorBaseline(rows).summary;
  const alwaysAllow = runAlwaysAllow(rows).summary;
  const tools = toolCensus(rows);
  const plant = plantedRed();
  const vsControl = baseline.meanLoss < control.meanLoss ? 'BEAT' : 'LOSE';

  console.log(`FROZEN  sha256=${identity.sha256}`);
  console.log(
    `n=${identity.n}  GOOD=${identity.good}  BAD=${identity.bad}  prevalence=${fmt(control.prevalence)}`,
  );
  console.log(`CONTROL always-abstain  mean_loss=${fmt(control.meanLoss)}`);
  console.log(`CONTROL always-allow    mean_loss=${fmt(alwaysAllow.meanLoss)}`);
  console.log(
    `BASELINE isError-abstain-else-allow  mean_loss=${fmt(baseline.meanLoss)}  vs_control=${vsControl}`,
  );
  console.log(
    `TOOLS  ${tools.map(([t, c]) => `${t}=${c}`).join(' ')}  (tool-name is not a separator)`,
  );
  console.log(
    `PLANTED-RED  false-allow-on-BAD loss=${plant.falseAllowLoss}  authored-n=10 REFUSED`,
  );
  console.log(
    'NO-CLAIM  [pending] promoted=0  offline  no TYPESAFE  no CASS  no agent-mail live',
  );
  console.log(`EXIT  0  (measurement completed; baseline ${vsControl}s control)`);
}

try {
  main();
} catch (err) {
  console.error(err.message ?? err);
  const msg = String(err.message ?? err);
  process.exitCode = /REFUSE|PLANTED NEGATIVE|not the frozen/.test(msg) ? 2 : 1;
}
