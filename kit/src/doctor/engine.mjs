import path from 'node:path';
import { detectors as logDetectors } from './detectors/logs.mjs';
import { detectors as capDetectors } from './detectors/caps.mjs';
import { detectors as anomalyDetectors } from './detectors/anomalies.mjs';
import { detectors as secretDetectors, resolveKeySource } from './detectors/secrets.mjs';
import { detectors as backendDetectors } from './detectors/backends.mjs';
import { detectors as daemonDetectors } from './detectors/daemons.mjs';
import { detectors as surfaceDetectors } from './detectors/surfaces.mjs';
import { detectors as driftDetectors } from './detectors/drift.mjs';

const DETECTORS = Object.freeze([
  ...secretDetectors,
  ...logDetectors,
  ...capDetectors,
  ...anomalyDetectors,
  ...backendDetectors,
  ...daemonDetectors,
  ...surfaceDetectors,
  ...driftDetectors,
]);

const TIERS = Object.freeze({
  quick: new Set(['Q']),
  default: new Set(['Q', 'D']),
  deep: new Set(['Q', 'D', 'X']),
});
const SEVERITIES = ['P0', 'P1', 'P2', 'P3'];

function selectors(value) {
  if (Array.isArray(value)) return new Set(value.filter((item) => typeof item === 'string'));
  if (typeof value !== 'string') return new Set();
  return new Set(value.split(',').map((item) => item.trim()).filter(Boolean));
}

function sourcesFor(detector, repo) {
  return (Array.isArray(detector.data_sources) ? detector.data_sources : []).map((source) => {
    if (repo && typeof source === 'string' && source.startsWith('.omp/')) return path.join(repo, source);
    return source;
  });
}

function unavailableCheck(detector, reason, dataSources) {
  return {
    id: detector.id,
    subsystem: detector.subsystem,
    tier: detector.tier,
    ran: false,
    provenance: 'unavailable',
    skipped_reason: reason,
    duration_ms: 0,
    data_sources: dataSources,
  };
}

function skippedCheck(detector, reason, dataSources) {
  return {
    id: detector.id,
    subsystem: detector.subsystem,
    tier: detector.tier,
    ran: false,
    provenance: 'offline',
    skipped_reason: reason,
    duration_ms: 0,
    data_sources: dataSources,
  };
}

function timestamp(ms) {
  return new Date(ms).toISOString();
}

function runId(instant, repo, tier) {
  const stamp = timestamp(instant).replaceAll(':', '-').replaceAll('.', '-');
  const identity = `${repo ?? 'no-repo'}\n${tier}`;
  let hash = 2166136261;
  for (const char of identity) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
  return `${stamp}__${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

export async function runDoctor(input) {
  const ctx = input ?? {};
  const fixedTime = Number.isFinite(ctx.now);
  const now = fixedTime ? ctx.now : Date.now();
  const runStarted = performance.now();
  const tier = Object.hasOwn(TIERS, ctx.tier) ? ctx.tier : 'default';
  const selected = selectors(ctx.only);
  const skipped = selectors(ctx.skip);
  const permittedTiers = new Set(TIERS[tier]);
  if (ctx.online === true) permittedTiers.add('O');
  const checks = [];
  const findings = [];
  let onlineSkipped = 0;

  for (const detector of DETECTORS) {
    const dataSources = sourcesFor(detector, ctx.repo ?? null);
    if (selected.size && !selected.has(detector.id) && !selected.has(detector.subsystem)) {
      checks.push(skippedCheck(detector, 'not selected', dataSources));
      continue;
    }
    if (skipped.has(detector.id) || skipped.has(detector.subsystem)) {
      checks.push(skippedCheck(detector, 'skipped by request', dataSources));
      continue;
    }
    if (detector.availability === 'unavailable') {
      checks.push(unavailableCheck(detector, detector.skipped_reason ?? 'detector unavailable', dataSources));
      continue;
    }
    if (detector.repo_required && !ctx.repo) {
      checks.push(unavailableCheck(detector, 'repository not available', dataSources));
      continue;
    }
    if (!permittedTiers.has(detector.tier)) {
      if (detector.tier === 'O' && ctx.online !== true) onlineSkipped += 1;
      checks.push(skippedCheck(detector, detector.tier === 'O' ? 'online checks disabled' : `requires ${detector.tier} tier`, dataSources));
      continue;
    }

    const checkStarted = performance.now();
    const results = await detector.run({ ...ctx, now, tier, online: ctx.online === true });
    if (!Array.isArray(results)) throw new TypeError(`Doctor detector ${detector.id} did not return a finding array`);
    checks.push({
      id: detector.id,
      subsystem: detector.subsystem,
      tier: detector.tier,
      ran: true,
      provenance: ctx.provenance ?? (ctx.calls ? 'offline' : 'live'),
      skipped_reason: null,
      duration_ms: Math.max(0, Math.round(performance.now() - checkStarted)),
      data_sources: dataSources,
    });
    for (const finding of results) findings.push({ id: detector.id, subsystem: detector.subsystem, ...finding });
  }

  const key = await resolveKeySource({ ...ctx, now });
  const clefCheck = checks.find((check) => check.id === 'fm-clef-unreachable');
  const clefDown = findings.some((finding) => finding.id === 'fm-clef-unreachable');
  const bySeverity = Object.fromEntries(SEVERITIES.map((severity) => [severity, findings.filter((finding) => finding.severity === severity).length]));
  const unavailable = checks.filter((check) => check.provenance === 'unavailable').length;
  const skippedCount = checks.filter((check) => !check.ran && check.provenance !== 'unavailable').length;
  const ok = findings.length === 0 && unavailable === 0;
  const finished = fixedTime ? now : Date.now();

  return {
    schema_version: '1.0',
    tool: 'jev',
    tool_version: '0.0.0',
    doctor_version: '1.0.0',
    doctor_contract_version: '1.0',
    run_id: runId(now, ctx.repo ?? null, tier),
    run_dir: null,
    started_at: timestamp(now),
    finished_at: timestamp(finished),
    duration_ms: Math.max(0, Math.round(performance.now() - runStarted)),
    target_sha: ctx.target_sha ?? null,
    repo: ctx.repo ?? null,
    tier,
    online: ctx.online === true,
    state: findings.length ? 'DONE_FINDINGS' : skippedCount || unavailable ? 'DONE_PARTIAL' : 'DONE_OK',
    ok,
    jev_on_path: ctx.omp?.jev_path ?? null,
    backends: {
      jev: {
        status: 'NOT_RUN',
        key_source: key.key_source,
        model: 'jev-1.13.0',
        provenance: 'unavailable',
      },
      clef: {
        status: !clefCheck?.ran ? 'UNKNOWN' : clefDown ? 'DOWN' : 'UP',
        endpoint: 'http://127.0.0.1:11300/healthz',
        model: null,
        provenance: clefCheck?.provenance ?? 'unavailable',
      },
    },
    checks,
    summary: {
      checks_run: checks.filter((check) => check.ran).length,
      checks_unavailable: unavailable,
      total_findings: findings.length,
      by_severity: bySeverity,
      auto_fixable: 0,
      online_skipped: onlineSkipped,
    },
    findings,
    next_steps: findings.map((finding) => finding.remediation?.reason).filter((reason) => typeof reason === 'string'),
    notes: [],
    exit_code: ok ? 0 : 1,
  };
}
