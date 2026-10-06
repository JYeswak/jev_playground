import { declaredLogSurfaces, inWindow, logPath, readLogTail, rowTime, safeFinding } from './logs.mjs';

const DAY = 24 * 60 * 60 * 1000;
const WEEK = 7 * DAY;

const CAPS = Object.freeze({
  'gate-observe': 100,
  'injection-shadow': 3500,
  'webscreen': 25,
  'memory-filter': 600,
  'vendor-shadow': 100,
  'skill-veto': null,
});

export function capHit(surface, row) {
  if (!row || typeof row !== 'object') return false;
  switch (surface.id) {
    case 'gate-observe':
      return row.status === 'not-run' && typeof row.error === 'string' && row.error.includes('reason=daily-cap');
    case 'injection-shadow':
      return row.status === 'cap' && row.reason === 'daily-call-cap';
    case 'webscreen':
      return row.status === 'local-only' && row.reason === 'daily-cap';
    case 'memory-filter':
      return row.status === 'daily-cap';
    case 'vendor-shadow':
      return row.status === 'fail_open' && row.reason === 'cap';
    case 'skill-veto':
      return row.status === 'fail_open:cap';
    default:
      return false;
  }
}

function tokenCount(row) {
  if (Number.isFinite(row.tokens) && row.tokens >= 0) return row.tokens;
  if (!row.usage || typeof row.usage !== 'object') return 0;
  return ['input_tokens', 'output_tokens', 'prompt_tokens', 'completion_tokens']
    .reduce((total, key) => total + (Number.isFinite(row.usage[key]) && row.usage[key] > 0 ? row.usage[key] : 0), 0);
}

export const detectors = [{
  id: 'fm-caps-hit', subsystem: 'caps', tier: 'D', repo_required: false,
  data_sources: ['ctx.inventory.surfaces[].log', 'ctx.stateDir log tail'],
  async run(ctx) {
    const findings = [];
    for (const surface of declaredLogSurfaces(ctx)) {
      if (!Object.hasOwn(CAPS, surface.id)) continue;
      const file = logPath(ctx, surface);
      const result = await readLogTail(file);
      if (!result.exists) continue;
      const parsed = result.rows.map(({ row }) => row).filter((row) => row && inWindow(row, ctx.now, WEEK));
      const recent = parsed.filter((row) => inWindow(row, ctx.now, DAY));
      const hits = recent.filter((row) => capHit(surface, row));
      if (!hits.length) continue;
      const times = hits.map(rowTime).filter((value) => value !== null).sort((a, b) => a - b);
      const tokenTotal7d = parsed.reduce((sum, row) => sum + tokenCount(row), 0);
      const severe = surface.verdict === 'ENFORCING' ? 'P1' : 'P2';
      findings.push(safeFinding(severe, 'G', `Daily cap hit: ${surface.id}`, {
        surface: surface.id, path: file, cap: CAPS[surface.id], hits_24h: hits.length,
        first_hit_ts: times.length ? new Date(times[0]).toISOString() : null,
        share_of_rows: recent.length ? hits.length / recent.length : 0,
      }, {
        action: 'manual', reason: 'Raising a cap is a spend decision; review the recent measured usage first.',
        measured_7d_tokens: tokenTotal7d,
      }));
    }
    return findings;
  },
}];
