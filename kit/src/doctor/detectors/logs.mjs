import { promises as fs } from 'node:fs';
import path from 'node:path';

const TAIL_BYTES = 4 * 1024 * 1024;
const HOUR = 60 * 60 * 1000;

export function declaredLogSurfaces(ctx) {
  const surfaces = ctx.inventory?.surfaces;
  if (!Array.isArray(surfaces)) return [];
  return surfaces.filter((surface) =>
    surface && typeof surface.id === 'string' && typeof surface.log === 'string' &&
    surface.log.length > 0 && !path.isAbsolute(surface.log) &&
    !surface.log.split('/').includes('..') && !surface.log.split('\\').includes('..'));
}

export function logPath(ctx, surface) {
  return path.join(ctx.stateDir, surface.log);
}

export async function readLogTail(file) {
  let handle;
  try {
    handle = await fs.open(file, 'r');
    const stat = await handle.stat();
    const size = Math.min(stat.size, TAIL_BYTES);
    if (size === 0) return { exists: true, rows: [], mode: stat.mode & 0o777 };
    const buffer = Buffer.allocUnsafe(size);
    await handle.read(buffer, 0, size, stat.size - size);
    let text = buffer.toString('utf8');
    if (stat.size > size) {
      const firstNewline = text.indexOf('\n');
      text = firstNewline < 0 ? '' : text.slice(firstNewline + 1);
    }
    const lines = text.split('\n');
    if (lines.at(-1) === '') lines.pop();
    const rows = lines.map((line) => {
      const normalized = line.endsWith('\r') ? line.slice(0, -1) : line;
      try { return { row: JSON.parse(normalized) }; }
      catch { return { row: null }; }
    });
    return { exists: true, rows, mode: stat.mode & 0o777 };
  } catch (error) {
    if (error?.code === 'ENOENT' || error?.code === 'ENOTDIR') return { exists: false, rows: [], mode: null };
    return { exists: null, rows: [], mode: null };
  } finally {
    await handle?.close().catch(() => {});
  }
}

export function rowTime(row) {
  if (!row || typeof row.ts !== 'string') return null;
  const ms = Date.parse(row.ts);
  return Number.isFinite(ms) ? ms : null;
}

export function inWindow(row, now, duration) {
  const ts = rowTime(row);
  return ts !== null && ts >= now - duration && ts <= now;
}

export function safeFinding(severity, kind, title, evidence, remedy) {
  return { severity, kind, title, evidence, remediation: remedy };
}

const manual = { action: 'manual', reason: 'Review the declared surface and its log writer.' };

export const detectors = [
  {
    id: 'fm-logs-silent-surface', subsystem: 'observability_logs', tier: 'Q', repo_required: false,
    data_sources: ['ctx.inventory.surfaces[].log', 'ctx.stateDir log tail', 'bounded read-only git log for vendor-shadow'],
    async run(ctx) {
      const findings = [];
      const now = ctx.now;
      for (const surface of declaredLogSurfaces(ctx).filter((item) => item.expect === 'on')) {
        const file = logPath(ctx, surface);
        if (ctx.tier === 'quick') {
          let stat;
          try { stat = await fs.stat(file); }
          catch (error) {
            if (error?.code === 'ENOENT' || error?.code === 'ENOTDIR') {
              findings.push(safeFinding('P1', 'E', `Declared-on surface has no log: ${surface.id}`, { surface: surface.id, path: file, reason: 'missing-log' }, manual));
            }
            continue;
          }
          if (now - stat.mtimeMs > 3 * HOUR) {
            findings.push(safeFinding('P1', 'E', `Declared-on surface log is stale: ${surface.id}`, { surface: surface.id, path: file, age_ms: Math.max(0, now - stat.mtimeMs) }, manual));
          }
          continue;
        }
        const result = await readLogTail(file);
        if (result.exists === null) continue;
        if (!result.exists) {
          findings.push(safeFinding('P1', 'E', `Declared-on surface has no log: ${surface.id}`, { surface: surface.id, path: file, reason: 'missing-log' }, manual));
          continue;
        }
        const dated = result.rows.map(({ row }) => row).filter((row) => rowTime(row) !== null && rowTime(row) <= now);
        const last = dated.reduce((value, row) => Math.max(value, rowTime(row)), -Infinity);
        if (surface.id === 'vendor-shadow') {
          if (last === -Infinity || !ctx.repo) continue;
          let probe;
          try {
            probe = await ctx.exec('git', [
              '-C', ctx.repo, 'log', `--since=${new Date(last).toISOString()}`, '--format=%H', '-n', '1',
            ], { timeout: 500, maxBuffer: 1024 });
          } catch { continue; }
          if (probe?.code === 0 && typeof probe.stdout === 'string' && probe.stdout.trim().length > 0) {
            findings.push(safeFinding('P1', 'E', `Commit-driven surface is silent: ${surface.id}`, {
              surface: surface.id, path: file, last_ts: new Date(last).toISOString(), commits_since_last_row: true,
            }, manual));
          }
          continue;
        }
        if (last === -Infinity || now - last > 3 * HOUR) {
          findings.push(safeFinding('P1', 'E', `Declared-on surface is silent: ${surface.id}`, { surface: surface.id, path: file, last_ts: last === -Infinity ? null : new Date(last).toISOString() }, manual));
        }
      }
      return findings;
    },
  },
  {
    id: 'fm-logs-off-surface-writing', subsystem: 'observability_logs', tier: 'D', repo_required: false,
    data_sources: ['ctx.inventory.surfaces[].log', 'ctx.stateDir log tail'],
    async run(ctx) {
      const findings = [];
      for (const surface of declaredLogSurfaces(ctx).filter((item) => item.expect === 'off')) {
        const file = logPath(ctx, surface);
        const result = await readLogTail(file);
        if (!result.exists) continue;
        const recent = result.rows.map(({ row }) => row).filter((row) => inWindow(row, ctx.now, 3 * HOUR));
        if (!recent.length) continue;
        const times = recent.map(rowTime).sort((a, b) => a - b);
        findings.push(safeFinding('P1', 'A', `Declared-off surface is writing: ${surface.id}`, {
          surface: surface.id, path: file, count: recent.length,
          first_ts: new Date(times[0]).toISOString(), last_ts: new Date(times.at(-1)).toISOString(),
          instances: [...new Set(recent.map((row) => row.instance).filter((value) => typeof value === 'string'))].length,
        }, { action: 'manual', reason: 'Disable or remove the unexpected log writer.' }));
      }
      return findings;
    },
  },
  {
    id: 'fm-logs-stale-schema-writer', subsystem: 'observability_logs', tier: 'D', repo_required: true,
    data_sources: ['ctx.inventory.surfaces[].file', 'declared source LOG_SCHEMA', 'ctx.stateDir log tail'],
    async run(ctx) {
      if (!ctx.repo) return [];
      const findings = [];
      for (const surface of declaredLogSurfaces(ctx)) {
        const source = surface.file ?? surface.extension;
        if (typeof source !== 'string' || path.isAbsolute(source) || source.split('/').includes('..') || source.split('\\').includes('..')) continue;
        let sourceText;
        try { sourceText = await fs.readFile(path.resolve(ctx.repo, source.startsWith('./') ? source.slice(2) : source), 'utf8'); } catch { continue; }
        const schemaName = (text) => {
          const start = text.indexOf('LOG_SCHEMA');
          if (start < 0) return null;
          const equals = text.indexOf('=', start + 10);
          if (equals < 0) return null;
          const quote = text.indexOf('"', equals + 1);
          const single = text.indexOf("'", equals + 1);
          const delimiter = quote < 0 ? single : single < 0 ? quote : Math.min(quote, single);
          if (delimiter < 0) return null;
          const close = text.indexOf(text[delimiter], delimiter + 1);
          return close < 0 ? null : text.slice(delimiter + 1, close);
        };
        const expected = schemaName(sourceText);
        if (!expected) continue;
        const schemaVersion = (schema) => {
          const marker = schema.lastIndexOf('.v');
          if (marker < 0) return null;
          const version = schema.slice(marker + 2);
          if (!version || [...version].some((char) => char < '0' || char > '9')) return null;
          return Number(version);
        };
        const version = schemaVersion(expected);
        if (version === null) continue;
        const file = logPath(ctx, surface);
        const result = await readLogTail(file);
        if (!result.exists) continue;
        const stale = result.rows.map(({ row }) => row).filter((row) => {
          if (!inWindow(row, ctx.now, 24 * HOUR) || typeof row.schema !== 'string') return false;
          const rowVersion = schemaVersion(row.schema);
          return row.schema !== expected && rowVersion !== null && rowVersion < version;
        });
        if (!stale.length) continue;
        const times = stale.map(rowTime).filter((value) => value !== null).sort((a, b) => a - b);
        findings.push(safeFinding('P1', 'F', `Stale log schema writer: ${surface.id}`, {
          surface: surface.id, path: file, schema: stale[0].schema, count: stale.length,
          last_ts: times.length ? new Date(times.at(-1)).toISOString() : null,
        }, { action: 'manual', reason: 'Restart the process using the older log schema.' }));
      }
      return findings;
    },
  },
  {
    id: 'fm-logs-unparsable-rows', subsystem: 'observability_logs', tier: 'D', repo_required: false,
    data_sources: ['ctx.inventory.surfaces[].log', 'ctx.stateDir log tail'],
    async run(ctx) {
      const findings = [];
      for (const surface of declaredLogSurfaces(ctx)) {
        const file = logPath(ctx, surface);
        const result = await readLogTail(file);
        if (!result.exists) continue;
        const malformed = result.rows.filter(({ row }) => row === null).length;
        if (malformed) findings.push(safeFinding('P2', 'B', `Unparsable log rows: ${surface.id}`, { surface: surface.id, path: file, count: malformed }, manual));
      }
      return findings;
    },
  },
  {
    id: 'fm-logs-mode-too-open', subsystem: 'observability_logs', tier: 'Q', repo_required: false,
    data_sources: ['ctx.stateDir/*.jsonl modes', 'gate-observe declared log tail for command-data presence'],
    async run(ctx) {
      let names;
      try { names = await fs.readdir(ctx.stateDir); } catch { return []; }
      const gateObserve = declaredLogSurfaces(ctx).find((surface) => surface.id === 'gate-observe');
      const gateObservePath = gateObserve ? logPath(ctx, gateObserve) : null;
      const findings = [];
      for (const name of names.filter((entry) => entry.endsWith('.jsonl'))) {
        const file = path.join(ctx.stateDir, name);
        let stat;
        try { stat = await fs.stat(file); } catch { continue; }
        if (!stat.isFile()) continue;
        const mode = stat.mode & 0o777;
        const tooOpen = (mode & 0o077) !== 0;
        const sensitiveSidecar = name.endsWith('-full.jsonl') || name.endsWith('-requests.jsonl');
        let cmdRows = 0;
        if (file === gateObservePath) {
          const result = await readLogTail(file);
          if (result.exists) cmdRows = result.rows.filter(({ row }) =>
            row && typeof row === 'object' && Object.hasOwn(row, 'cmd')).length;
        }
        if (!tooOpen && cmdRows === 0) continue;
        const hasCommandData = cmdRows > 0;
        findings.push(safeFinding(sensitiveSidecar || hasCommandData ? 'P1' : 'P2', 'D',
          hasCommandData ? 'Command data present in log: gate-observe' : `Log permissions are too open: ${name}`,
          { path: file, mode, ...(hasCommandData ? { cmd_rows: cmdRows } : {}) },
          { action: 'manual', reason: hasCommandData ? 'Review command-data logging and retain restrictive file permissions.' : 'Restrict the log file to mode 0600.' }));
      }
      return findings;
    },
  },
];
