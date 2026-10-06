import { capHit } from './caps.mjs';
import { declaredLogSurfaces, inWindow, logPath, readLogTail, rowTime, safeFinding } from './logs.mjs';

const HOUR = 60 * 60 * 1000;
const DAY = 24 * HOUR;
const WEEK = 7 * DAY;
const ERROR_STATUSES = new Set(['error', 'failed', 'fail_open', 'not-run']);

function isError(surface, row) {
  return ERROR_STATUSES.has(row?.status) && !capHit(surface, row);
}

function safeCategory(value) {
  if (typeof value !== 'string' || value.length > 64 || value.length < 2) return null;
  // Keep only compact, low-entropy reason identifiers; exclude free text and likely secrets.
  for (const char of value) {
    const code = char.charCodeAt(0);
    const valid = (code >= 65 && code <= 90) || (code >= 97 && code <= 122) ||
      (code >= 48 && code <= 57) || char === '_' || char === '-';
    if (!valid) return null;
  }
  if (!value.includes('-') && !value.includes('_')) return null;
  const lowered = value.toLowerCase();
  for (const sensitive of ['secret', 'token', 'password', 'credential', 'authorization', 'bearer', 'cookie', 'api-key']) {
    if (lowered.includes(sensitive)) return null;
  }
  return value;
}

function topCategories(rows) {
  const counts = new Map();
  for (const row of rows) {
    for (const field of ['error', 'reason']) {
      const category = safeCategory(row[field]);
      if (category) counts.set(category, (counts.get(category) ?? 0) + 1);
    }
  }
  return [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 3)
    .map(([category, count]) => ({ category, count }));
}

export const detectors = [{
  id: 'fm-anomaly-error-spike', subsystem: 'anomalies', tier: 'D', repo_required: false,
  data_sources: ['ctx.inventory.surfaces[].log', 'ctx.stateDir log tail'],
  async run(ctx) {
    const findings = [];
    for (const surface of declaredLogSurfaces(ctx)) {
      const file = logPath(ctx, surface);
      const result = await readLogTail(file);
      if (!result.exists) continue;
      const rows = result.rows.map(({ row }) => row).filter((row) => row && rowTime(row) !== null && rowTime(row) <= ctx.now);
      const week = rows.filter((row) => inWindow(row, ctx.now, WEEK));
      const day = week.filter((row) => inWindow(row, ctx.now, DAY));
      const hour = day.filter((row) => inWindow(row, ctx.now, HOUR));
      const errors7d = week.filter((row) => isError(surface, row));
      const errors24h = day.filter((row) => isError(surface, row));
      const errors1h = hour.filter((row) => isError(surface, row));
      const share7d = week.length ? errors7d.length / week.length : 0;
      const share24h = day.length ? errors24h.length / day.length : 0;
      const share1h = hour.length ? errors1h.length / hour.length : 0;
      const spike = (day.length >= 50 && share24h > Math.max(2 * share7d, 0.05)) ||
        (errors1h.length >= 20 && share1h > 0.5);
      if (!spike) continue;
      findings.push(safeFinding('P1', 'E', `Error rate spike: ${surface.id}`, {
        surface: surface.id, path: file,
        rows_24h: day.length, errors_24h: errors24h.length, error_share_24h: share24h,
        rows_7d: week.length, errors_7d: errors7d.length, error_share_7d: share7d,
        errors_1h: errors1h.length, error_share_1h: share1h,
        top_errors: topCategories(errors24h),
      }, { action: 'manual', reason: 'Inspect the affected surface and its error-rate trend.' }));
    }
    return findings;
  },
}];
