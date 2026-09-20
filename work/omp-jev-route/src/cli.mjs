#!/usr/bin/env node
/**
 * ACCEPTANCE runner for the skillranker process slice.
 * Offline. No key. No network.
 *
 *   node work/omp-jev-route/src/cli.mjs decide --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl
 *   node work/omp-jev-route/src/cli.mjs gate --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { decide } from './process.mjs';
import { evaluate, POLICY } from './gate.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_FIXTURE = path.join(__dirname, '..', 'fixtures', 'process-cases.v1.jsonl');

function arg(name, fallback) {
  const i = process.argv.indexOf(name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

function loadFixture(file) {
  const raw = readFileSync(file, 'utf8');
  return raw.split('\n').filter((l) => l.trim() && !l.trim().startsWith('#')).map((l) => JSON.parse(l));
}

const cmd = process.argv[2];
const fixture = arg('--fixture', DEFAULT_FIXTURE);

if (cmd !== 'decide' && cmd !== 'gate') {
  process.stderr.write('usage: node work/omp-jev-route/src/cli.mjs decide|gate [--fixture <jsonl>]\n');
  process.exit(2);
}

const cases = loadFixture(fixture);
const rows = cases.map((c) => ({
  case_id: c.case_id,
  y: c.y ?? [],
  decision: decide(c),
}));

if (cmd === 'decide') {
  const out = {
    schema: 'jev.omp-jev-route.process-log.v1',
    fixture,
    n: rows.length,
    rows: rows.map((r) => ({ case_id: r.case_id, y: r.y, ...r.decision })),
  };
  process.stdout.write(JSON.stringify(out, null, 2) + '\n');
  process.exit(0);
}

const report = evaluate(rows);
process.stdout.write(JSON.stringify({ policy: POLICY, fixture, ...report }, null, 2) + '\n');
// Contract runner: exit 0 when the GATE SHAPE holds. The default fixture plants
// every loss class, so always-abstain can beat it — that is the control working,
// not a promotion. Exit 2 only if the contract itself is broken.
const ok =
  report.promoted === false &&
  report.split === 'diagnostic_synthetic' &&
  typeof report.always_abstain_mean_loss === 'number' &&
  report.status === 'frozen_contract_not_evidence';
process.exit(ok ? 0 : 2);
