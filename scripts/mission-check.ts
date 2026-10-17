#!/usr/bin/env bun
/** Mission Protocol adapter. Runs existing acceptance; never promotes fixture evidence to live. */
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const PILLARS = ['live', 'measured', 'honest', 'local-first', 'portable', 'current'] as const;
type Pillar = typeof PILLARS[number];
type Verdict = { verdict: 'PASS' | 'FAIL' | 'UNKNOWN'; reason: string };
const classes: Record<Pillar, string> = {
  live: 'live-witness', measured: 'live-witness', honest: 'invariant',
  'local-first': 'invariant', portable: 'live-witness', current: 'invariant',
};
const isObject = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === 'object' && !Array.isArray(value);
const unknown = (reason: string): Verdict => ({ verdict: 'UNKNOWN', reason });
const fail = (reason: string): Verdict => ({ verdict: 'FAIL', reason });
const pass = (): Verdict => ({ verdict: 'PASS', reason: 'required acceptance evidence passed' });

export function scheduledRuns(value: unknown, now = Date.now()): Verdict {
  if (!Array.isArray(value) || value.length !== 7) return fail('seven scheduled runs required');
  const ids = new Set();
  const days: number[] = [];
  for (const row of value) {
    if (!isObject(row) || typeof row.databaseId !== 'number' || !Number.isSafeInteger(row.databaseId) || ids.has(row.databaseId)) return fail('invalid or duplicate scheduled run');
    ids.add(row.databaseId);
    if (row.event !== 'schedule' || row.status !== 'completed' || row.conclusion !== 'success') return fail('scheduled run incomplete or failed; manual success cannot substitute');
    const time = typeof row.createdAt === 'string' ? Date.parse(row.createdAt) : NaN;
    if (!Number.isFinite(time) || time > now || typeof row.headSha !== 'string' || !row.headSha || typeof row.url !== 'string' || !row.url) return fail('scheduled run provenance missing or future-dated');
    days.push(Math.floor(time / 86_400_000));
  }
  days.sort((a, b) => b - a);
  const today = Math.floor(now / 86_400_000);
  // Existing stranger-run schedule is 03:17 UTC. A pending scheduled day is not green.
  const expected = now % 86_400_000 >= (3 * 60 + 17) * 60_000 ? today : today - 1;
  if (days.some((day, index) => day !== expected - index)) return fail('seven consecutive current scheduled days required');
  return pass();
}

export function doctorReport(value: unknown, subsystem: 'live' | 'drift'): Verdict {
  if (!isObject(value) || value.schema_version !== '1.0' || value.doctor_contract_version !== '1.0' || !Array.isArray(value.checks) || !Array.isArray(value.findings)) return unknown('doctor report schema unavailable');
  const subsystems = subsystem === 'drift' ? ['drift', 'hooks', 'observability_logs'] : ['live'];
  const selected = value.checks.filter((check: unknown) => isObject(check) && typeof check.subsystem === 'string' && subsystems.includes(check.subsystem));
  if (subsystems.some((name) => !selected.some((check: unknown) => isObject(check) && check.subsystem === name))) return unknown(`${subsystem} behavioral detector coverage is not implemented`);
  if (selected.some((check: unknown) => !isObject(check) || check.ran !== true || check.provenance === 'unavailable' || check.skipped_reason)) return unknown(`${subsystem} detector coverage incomplete`);
  if (value.exit_code !== 0 || value.ok !== true || value.findings.some((finding: unknown) => isObject(finding) && typeof finding.subsystem === 'string' && subsystems.includes(finding.subsystem))) return fail(`${subsystem} acceptance reported findings`);
  if (subsystem === 'live') return unknown('both-ways L3 receipt consumer contract is not implemented and independently bound (jev-b35c.30)');
  const required = ['fm-hooks-global-link-broken', 'fm-surfaces-outside-repo-audit', 'fm-fleet-watch-stale', 'fm-inventory-enforcement-switch-missing', 'fm-inventory-expected-stale', 'fm-logs-off-surface-writing'];
  if (required.some((id) => !selected.some((check: unknown) => isObject(check) && check.id === id))) return unknown('complete installed-surface drift coverage unavailable');
  return pass();
}

export function measuredReport(value: unknown, expectedIds: string[]): Verdict {
  if (!isObject(value) || value.schema !== 'jev-mvvh.ledger.v1' || !Array.isArray(value.rows) || !Array.isArray(value.strict_failures)) return unknown('ledger gate report schema unavailable');
  if (!isObject(value.window) || value.window.days !== 7 || typeof value.window.start !== 'string' || typeof value.window.end !== 'string' || value.generated_at !== value.window.end) return unknown('seven-day ledger window provenance unavailable');
  const start = Date.parse(value.window.start);
  const end = Date.parse(value.window.end);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end - start !== 7 * 86_400_000 || end > Date.now()) return fail('invalid seven-day ledger window');
  if (expectedIds.length === 0 || value.rows.length === 0) return fail('expected-ON population is empty; no measured coverage');
  const actual = new Set<string>();
  for (const row of value.rows) {
    if (!isObject(row) || typeof row.id !== 'string' || actual.has(row.id)) return fail('invalid or duplicate ledger surface');
    actual.add(row.id);
    if (row.verdict === 'KEEP' && row.live !== 'on') return fail('KEEP surface has unknown live state');
    if (row.verdict === 'KILL' && (row.live !== 'off' || row.switch_verified_off !== true || row.fresh_session_rows !== 0)) return fail('KILL surface still active or off-switch unverified');
    if (row.verdict !== 'KEEP' && row.verdict !== 'KILL') return fail('ledger reports unmeasured value policy');
  }
  if (actual.size !== expectedIds.length || expectedIds.some((id) => !actual.has(id))) return unknown('ledger does not exactly cover canonical expected-ON population');
  if (value.strict_failures.length) return fail('ledger strict value policy failed');
  return pass();
}


// TAP pass-count extraction (no regex): an absent or malformed summary
// reads as zero passes, which the judge treats as missing evidence.
export function parseTapPasses(stdout: string): number {
  for (const line of stdout.split('\n')) {
    const trimmed = line.trim();
    if (trimmed.startsWith('# pass ')) {
      const n = Number(trimmed.slice('# pass '.length).trim());
      if (Number.isSafeInteger(n) && n >= 0) return n;
    }
  }
  return 0;
}

// Read-only calibration discovery through the actual consumer path: the
// runtime loader (kit calibration/clef) reads top-level *.json only, so the
// check reads exactly that directory. A calibration anywhere else never
// routes and is out of scope; unparseable files are skipped like the loader
// skips them (they cannot route either).
export function scanCalibrationDir(dirAbs: string): { path: string; doc: unknown }[] {
  const out: { path: string; doc: unknown }[] = [];
  let names: string[] = [];
  try {
    names = readdirSync(dirAbs).sort();
  } catch { return out; }
  for (const name of names) {
    if (!name.endsWith('.json')) continue;
    try {
      out.push({ path: name, doc: JSON.parse(readFileSync(resolve(dirAbs, name), 'utf8')) });
    } catch { continue; }
  }
  return out;
}
export type ClefCalibration = { path: string; doc: unknown; preregResolves: boolean; resultResolves: boolean; preregCt: number; resultCt: number };


// Local-first pillar judge (jev-b35c.44). A family routes to Clef only where a
// committed receipt shows it non-inferior to Jev under the same calibration;
// otherwise Jev (or the rule incumbent). Missing evidence is red/UNKNOWN,
// never presence-only green: PASS requires the backend route acceptance to
// have run green with at least one passing test (parsed TAP, not just exit),
// AND every discovered Clef calibration to carry a verified receipt stating
// an explicit margin over a positive sample (or none to exist, stated).
export function localFirstReport(suiteExit: number | null, suitePasses: number, calibrations: ClefCalibration[], envBackend?: string): Verdict {
  if (suiteExit !== 0) return fail('backend route acceptance failed; default-Jev unproven');
  if (!Number.isSafeInteger(suitePasses) || suitePasses < 1) return unknown('backend route acceptance ran no passing tests');
  const envRoutesClef = envBackend !== undefined && envBackend !== 'jev';
  const verified = calibrations.filter((cal) => niReceiptReason(cal.doc, cal.preregResolves, cal.resultResolves, cal.preregCt, cal.resultCt) === null);
  if (envRoutesClef && verified.length === 0) return fail('JEV_BACKEND routes to Clef without a committed non-inferiority receipt');
  for (const cal of calibrations) {
    const reason = niReceiptReason(cal.doc, cal.preregResolves, cal.resultResolves, cal.preregCt, cal.resultCt);
    if (reason !== null) return fail(`family routes to Clef without a committed non-inferiority receipt: ${cal.path} (${reason})`);
  }
  return calibrations.length === 0 && !envRoutesClef
    ? { verdict: 'PASS', reason: 'backend route acceptance passed; scan found no Clef-routed families' }
    : pass();
}

function niReceiptReason(doc: unknown, preregResolves: boolean, resultResolves: boolean, preregCt: number, resultCt: number): string | null {
  if (!isObject(doc)) return 'calibration is not an object';
  const receipt = doc['receipt'];
  if (!isObject(receipt)) return 'missing NI receipt block';
  if (receipt['verdict'] !== 'PASS') return 'receipt verdict is not PASS';
  for (const field of ['prereg_commit', 'result_commit'] as const) {
    if (typeof receipt[field] !== 'string' || !/^[0-9a-f]{40}$/.test(receipt[field] as string)) return `receipt ${field} not pinned`;
  }
  if (!preregResolves) return 'prereg_commit not in history';
  if (!resultResolves) return 'result_commit not in history';
  if (receipt['prereg_commit'] === receipt['result_commit']) return 'preregistration identical to results';
  if (preregCt >= 0 && resultCt >= 0 && preregCt > resultCt) return 'preregistration not before results';
  // NI margins in this codebase compare rates on [0,1] (X2 PREREG: 5pp
  // paired accuracy margin); a margin above 1, however finite, is vacuous.
  if (typeof receipt['margin'] !== 'number' || !(receipt['margin'] as number >= 0)) return 'receipt margin not stated';
  if ((receipt['margin'] as number) > 1) return 'receipt margin vacuous';
  if (!Number.isSafeInteger(receipt['n']) || (receipt['n'] as number) < 1) return 'receipt sample size not stated';
  if (typeof receipt['question_key'] === 'string' && receipt['question_key'] !== (doc as Record<string, unknown>)['question_key']) return 'receipt question_key differs';
  const modelId = isObject((doc as Record<string, unknown>)['model']) ? ((doc as Record<string, unknown>)['model'] as Record<string, unknown>)['id'] : undefined;
  if (typeof receipt['model_id'] === 'string' && receipt['model_id'] !== modelId) return 'receipt model_id differs';
  // The receipt binds the evaluated bytes: payload is the artifact minus its
  // receipt block in canonical (sorted-key) JSON, mirroring the stage-exit
  // payload/source split. A changed calibration with an unchanged receipt
  // refuses instead of passing on stale provenance.
  const { receipt: _detached, ...payload } = doc as Record<string, unknown>;
  const actual = createHash('sha256').update(canonicalJson(payload), 'utf8').digest('hex');
  if (typeof receipt['calibration_sha256'] !== 'string' || receipt['calibration_sha256'] !== actual) return 'receipt not bound to calibration bytes';
  return null;
}

// Deterministic canonical JSON: sorted object keys, compact separators.
export function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (isObject(value)) {
    return `{${Object.keys(value).sort().map((k) => `${JSON.stringify(k)}:${canonicalJson(value[k])}`).join(',')}}`;
  }
  return JSON.stringify(value) ?? 'null';
}

type Child = { argv: string[]; exit: number | null; signal: string | null; stdout: string; stderr: string; error: string | null };
function run(argv: string[]): Child {
  const result = spawnSync(argv[0], argv.slice(1), { cwd: ROOT, encoding: 'utf8', timeout: 120_000, maxBuffer: 8 * 1024 * 1024, env: process.env });
  return { argv, exit: result.status, signal: result.signal, stdout: result.stdout ?? '', stderr: result.stderr ?? '', error: result.error?.message ?? null };
}
function report(child: Child): unknown {
  try { return JSON.parse(child.stdout); } catch { return null; }
}
const classifier = (args: string[]) => run(['node', resolve(ROOT, 'kit/bin/jev.mjs'), ...args]);

export function check(pillar: Pillar): { result: Verdict; children: Child[] } {
  const children: Child[] = [];
  const record = (child: Child) => { children.push(child); return child; };
  let result: Verdict;
  if (pillar === 'live' || pillar === 'current') {
    const subsystem = pillar === 'live' ? 'live' : 'drift';
    const child = record(classifier(['doctor', '--deep', '--only', pillar === 'current' ? 'drift,hooks,observability_logs' : 'live', '--json']));
    result = doctorReport(report(child), subsystem);
  } else if (pillar === 'measured') {
    const child = record(run(['python3', 'work/jev-mvvh/ledger.py', '--gate', '--days', '7', '--json']));
    let expectedIds: string[] = [];
    try {
      const inventory = JSON.parse(readFileSync(resolve(ROOT, 'work/jev-inventory/expected.json'), 'utf8'));
      if (!isObject(inventory) || !Array.isArray(inventory.surfaces)) throw new Error('invalid inventory');
      expectedIds = inventory.surfaces.flatMap((row: unknown) => {
        if (!isObject(row) || row.expect !== 'on' || typeof row.id !== 'string') return [];
        return row.id === 'memory-filter' ? ['memory-jev', 'memory-cap3'] : [row.id];
      });
    } catch { return { result: unknown('canonical expected-ON inventory unreadable'), children }; }
    result = measuredReport(report(child), expectedIds);
  } else if (pillar === 'honest') {
    const chronology = record(run(['python3', 'scripts/bar_chronology.py', '--since', '2026-09-24', '--json', '--strict']));
    const lint = record(run(['python3', 'scripts/bead-lint.py', '--all-open', '--json']));
    const chronologyReport = report(chronology);
    const lintReport = report(lint);
    // The native chronology producer owns provenance semantics; no replacement interpretation here.
    result = !isObject(chronologyReport) ? unknown('chronology acceptance producer unavailable (jev-6gun)')
      : !isObject(lintReport) || typeof lintReport.checked !== 'number' || !Number.isInteger(lintReport.checked) || lintReport.checked === 0 ? unknown('nonempty plan lint coverage unavailable')
      : chronology.exit !== 0 || lint.exit !== 0 ? fail('chronology or plan lint reported failure')
      : unknown('chronology output contract is not independently bound; cannot certify the honest pillar (jev-6gun)');
  } else if (pillar === 'local-first') {
    // Real producer: the existing backend route acceptance (default-Jev
    // routing, refusal semantics), exit/output retained, not replaced.
    const suite = record(run(['node', '--test', 'kit/test/backend.test.mjs']));
    const tapPasses = parseTapPasses(suite.stdout);
    const calibrations: ClefCalibration[] = [];
    const calDir = resolve(ROOT, 'kit/calibration/clef');
    for (const { path: name, doc } of scanCalibrationDir(calDir)) {
      if (!isObject(doc) || doc['schema'] !== 'jev.clef-calibration.v1') continue;
      const rel = `kit/calibration/clef/${name}`;
      const receipt = isObject(doc['receipt']) ? (doc['receipt'] as Record<string, unknown>) : {};
      const prereg = typeof receipt['prereg_commit'] === 'string' ? receipt['prereg_commit'] as string : '';
      const resultRef = typeof receipt['result_commit'] === 'string' ? receipt['result_commit'] as string : '';
      const preregResolves = /^[0-9a-f]{40}$/.test(prereg) && record(run(['git', 'cat-file', '-e', `${prereg}^{commit}`])).exit === 0;
      const resultResolves = /^[0-9a-f]{40}$/.test(resultRef) && record(run(['git', 'cat-file', '-e', `${resultRef}^{commit}`])).exit === 0;
      const stamp = (sha: string, ok: boolean): number => {
        if (!ok) return -1;
        const out = record(run(['git', 'show', '-s', '--format=%ct', `${sha}^{commit}`]));
        const n = Number((out.stdout ?? '').trim());
        return Number.isSafeInteger(n) && n > 0 ? n : -1;
      };
      calibrations.push({ path: rel, doc, preregResolves, resultResolves, preregCt: stamp(prereg, preregResolves), resultCt: stamp(resultRef, resultResolves) });
    }
    result = localFirstReport(suite.exit, tapPasses, calibrations, process.env.JEV_BACKEND);
  } else {
    const child = record(run(['gh', 'run', 'list', '--repo', 'JYeswak/jev_playground', '--branch', 'main', '--workflow', 'stranger-run.yml', '--event', 'schedule', '--limit', '7', '--json', 'databaseId,event,status,conclusion,createdAt,headSha,url']));
    result = scheduledRuns(report(child));
    if (result.verdict === 'PASS') {
      record(classifier(['ready', '--json']));
      result = unknown('external-project adoption target and successful family receipt are not independently bound (jev-r1vp)');
    }
  }
  if (result.verdict === 'PASS' && children.some((child) => child.exit !== 0 || child.signal || child.error)) result = fail('acceptance subprocess failed');
  return { result, children };
}

if (import.meta.main) {
  const args = process.argv.slice(2);
  if (args.length !== 2 || args[0] !== '--pillar' || !PILLARS.includes(args[1] as Pillar)) {
    console.error('usage: bun scripts/mission-check.ts --pillar live|measured|honest|local-first|portable|current');
    process.exit(2);
  }
  const pillar = args[1] as Pillar;
  try {
    const { result, children } = check(pillar);
    console.log(JSON.stringify({ schema: 'jev.mission-check.v1', pillar, claim_class: classes[pillar], evidence_tier: 'live', ...result, children }));
    process.exit(result.verdict === 'PASS' ? 0 : 1);
  } catch (error) {
    console.log(JSON.stringify({ schema: 'jev.mission-check.v1', pillar, verdict: 'UNKNOWN', reason: error instanceof Error ? error.message : String(error) }));
    process.exit(1);
  }
}
