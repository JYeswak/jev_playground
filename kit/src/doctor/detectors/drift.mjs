import { readFile } from 'node:fs/promises';
import { join, relative, resolve } from 'node:path';

const BAD_ON_VERDICTS = new Set(['OFF', 'MISSING', 'REFUTED', 'BROKEN', 'FAIL', 'FAILED', 'RED', 'NOT-FOUND']);
const WATCH_INTERVAL_MS = 60_000;

function finding(severity, kind, title, evidence, manual) {
  return { severity, kind, title, evidence, remediation: { manual } };
}
function surfaces(inventory) {
  return Array.isArray(inventory?.surfaces) ? inventory.surfaces : [];
}
function declaredPath(surface) {
  for (const key of ['file', 'extension', 'path']) {
    if (typeof surface?.[key] === 'string' && surface[key].startsWith('.')) return surface[key];
  }
  return null;
}
async function readJsonLines(path) {
  try {
    const text = await readFile(path, 'utf8');
    const rows = [];
    for (const line of text.split('\n')) {
      if (!line.trim()) continue;
      try { rows.push(JSON.parse(line)); } catch { /* malformed tail rows are not liveness evidence */ }
    }
    return rows;
  } catch { return null; }
}

export const detectors = [
  {
    id: 'fm-hooks-global-link-broken', subsystem: 'hooks', tier: 'D', repo_required: true,
    availability: 'unavailable',
    skipped_reason: 'pin-global audit implementation is not present',
    data_sources: ['pin-global audit script (unavailable)'],
    async run() { return []; },
  },
  {
    id: 'fm-surfaces-outside-repo-audit', subsystem: 'drift', tier: 'D', repo_required: false,
    availability: 'unavailable',
    skipped_reason: 'outside-repo audit implementation is not present',
    data_sources: ['outside-repo audit script (unavailable)'],
    async run() { return []; },
  },
  {
    id: 'fm-fleet-watch-stale', subsystem: 'drift', tier: 'D', repo_required: false,
    data_sources: ['ctx.stateDir/fleet-watch-liveness.jsonl', 'expected inventory fleet needs-human declaration'],
    async run(ctx) {
      const declared = surfaces(ctx.inventory).some((surface) => surface?.expect === 'on' && (surface?.process === 'fleet-idle-watch.py' || surface?.id === 'needs-human'));
      if (!declared) return [];
      const rows = await readJsonLines(join(ctx.stateDir, 'fleet-watch-liveness.jsonl'));
      if (!rows?.length) return [finding('P2', 'E', 'Declared fleet watcher has no liveness record', { file: 'fleet-watch-liveness.jsonl', declared_on: true }, 'Start or diagnose the fleet idle watcher.')];
      let latest = null;
      for (const row of rows) {
        const ts = typeof row.ts === 'number' ? row.ts : Date.parse(row.ts);
        if (Number.isFinite(ts) && (!latest || ts > latest.ts)) latest = { row, ts };
      }
      if (!latest) return [finding('P2', 'E', 'Fleet watcher liveness timestamps are unavailable', { file: 'fleet-watch-liveness.jsonl', declared_on: true }, 'Inspect the fleet watcher liveness writer.')];
      const ageMs = Math.max(0, ctx.now - latest.ts);
      if (ageMs <= 2 * WATCH_INTERVAL_MS) return [];
      return [finding('P2', 'E', 'Declared fleet watcher liveness is stale', { file: 'fleet-watch-liveness.jsonl', age_ms: ageMs, max_age_ms: 2 * WATCH_INTERVAL_MS }, 'Start or diagnose the fleet idle watcher.')];
    },
  },
  {
    id: 'fm-inventory-enforcement-switch-missing', subsystem: 'drift', tier: 'D', repo_required: false,
    data_sources: ['ctx.inventory memory-filter enforcement declaration', 'ctx.stateDir/memory-filter-enforce'],
    async run(ctx) {
      const enforced = surfaces(ctx.inventory).some((surface) =>
        surface?.id === 'memory-filter' && surface?.expect === 'on' && surface?.verdict === 'ENFORCING');
      if (!enforced) return [];
      try {
        await readFile(join(ctx.stateDir, 'memory-filter-enforce'));
        return [];
      } catch {
        return [finding('P1', 'A', 'Memory-filter enforcement claim has no enforcement switch', {
          surface: 'memory-filter',
          file: 'memory-filter-enforce',
          claimed: 'ENFORCING',
          enforcement_switch_present: false,
        }, 'Reconcile the memory-filter enforcement claim and switch state.')];
      }
    },
  },
  {
    id: 'fm-inventory-expected-stale', subsystem: 'drift', tier: 'D', repo_required: true,
    data_sources: ['ctx.inventory surfaces declarations', 'declared repo-relative paths'],
    async run(ctx) {
      if (!ctx.repo || !ctx.inventory) return [];
      const findings = [];
      for (const surface of surfaces(ctx.inventory)) {
        if (surface?.expect !== 'on') continue;
        const path = declaredPath(surface);
        if (path) {
          const candidate = resolve(ctx.repo, path);
          const repoRelative = relative(resolve(ctx.repo), candidate);
          if (!repoRelative || repoRelative.startsWith('..')) continue;
          try { await readFile(candidate); }
          catch { findings.push(finding('P1', 'A', 'Expected ON surface path is missing', { surface: surface.id ?? null, file: path, claimed: 'on' }, 'Restore or update the declared ON surface.')); }
        }
        const verdict = typeof surface?.verdict === 'string' ? surface.verdict.toUpperCase() : '';
        if (BAD_ON_VERDICTS.has(verdict)) findings.push(finding('P1', 'A', 'Expected ON surface has a contradictory verdict', { surface: surface.id ?? null, claimed: 'on', verdict }, 'Reconcile the expected inventory verdict with the current surface claim.'));
      }
      return findings;
    },
  },
];
