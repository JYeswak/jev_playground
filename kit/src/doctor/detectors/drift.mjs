import { createHash } from 'node:crypto';
import { lstat, readdir, readFile, realpath, stat } from 'node:fs/promises';
import { basename, dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';

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

function safeInventoryPath(value) {
  return typeof value === 'string' && value.length > 0 && !isAbsolute(value) &&
    !value.includes('\\') && !value.split('/').includes('..') && !value.split('/').includes('.');
}
function isWithin(root, candidate) {
  const path = relative(resolve(root), resolve(candidate));
  return path !== '..' && !path.startsWith(`..${sep}`) && !isAbsolute(path);
}
async function safeDirectoryParents(root, directory) {
  if (!isWithin(root, directory)) return false;
  let current = resolve(root);
  const parts = relative(current, resolve(directory)).split(sep).filter(Boolean);
  for (const part of parts) {
    current = join(current, part);
    try {
      const entry = await lstat(current);
      if (entry.isSymbolicLink() || !entry.isDirectory()) return false;
    } catch (error) {
      if (error?.code === 'ENOENT' || error?.code === 'ENOTDIR') return true;
      throw error;
    }
  }
  return true;
}
async function globalHookFindings(ctx) {
  if (!ctx.repo || !ctx.home || !ctx.inventory) return [];
  let repoRoot;
  let homeRoot;
  try {
    [repoRoot, homeRoot] = await Promise.all([realpath(ctx.repo), realpath(ctx.home)]);
  } catch { return []; }
  const profiles = [{ name: 'agent', path: join(homeRoot, '.omp', 'agent') }];
  const profileRoot = join(homeRoot, '.omp', 'profiles');
  if (await safeDirectoryParents(homeRoot, profileRoot)) {
    try {
      for (const entry of await readdir(profileRoot, { withFileTypes: true })) {
        if (entry.isDirectory() && safeInventoryPath(entry.name)) {
          profiles.push({ name: entry.name, path: join(profileRoot, entry.name, 'agent') });
        }
      }
    } catch (error) {
      if (error?.code !== 'ENOENT' && error?.code !== 'ENOTDIR') throw error;
    }
  }
  const findings = [];
  for (const surface of surfaces(ctx.inventory)) {
    if (surface?.expect !== 'on' || surface?.group !== 'global') continue;
    if (!safeInventoryPath(surface.repo) || typeof surface.hookfile !== 'string' ||
      basename(surface.hookfile) !== surface.hookfile || surface.hookfile === '.' || surface.hookfile === '..') continue;
    const source = resolve(repoRoot, surface.repo);
    if (!isWithin(repoRoot, source)) continue;
    let sourceBytes = null;
    let committedBytes = null;
    let sourceStat = null;
    try {
      const sourceReal = await realpath(source);
      const sourceLstat = await lstat(source);
      if (isWithin(repoRoot, sourceReal) && sourceLstat.isFile() && !sourceLstat.isSymbolicLink()) {
        sourceBytes = await readFile(source);
        sourceStat = await stat(source);
      }
    } catch { /* unavailable source is reported as drift below */ }
    try {
      const committed = await ctx.exec('git', ['-C', repoRoot, 'show', `HEAD:${surface.repo}`], {
        timeout: 1000, maxBuffer: 4 * 1024 * 1024,
      });
      if (committed?.code === 0) committedBytes = Buffer.from(committed.stdout, 'utf8');
    } catch { /* unavailable source is not healthy evidence */ }
    const sourceMatches = sourceBytes !== null && committedBytes !== null && sourceBytes.equals(committedBytes);
    for (const profile of profiles) {
      const target = join(profile.path, 'hooks', 'post', surface.hookfile);
      if (!isWithin(homeRoot, target)) continue;
      const parentSafe = await safeDirectoryParents(homeRoot, dirname(target));
      let targetLstat = null;
      let targetStat = null;
      let targetBytes = null;
      if (parentSafe) {
        try {
          targetLstat = await lstat(target);
          if (!targetLstat.isSymbolicLink() && targetLstat.isFile()) {
            targetStat = await stat(target);
            targetBytes = await readFile(target);
          }
        } catch (error) {
          if (error?.code !== 'ENOENT' && error?.code !== 'ENOTDIR') throw error;
        }
      }
      const linkType = !sourceMatches ? 'source_drift' :
        !parentSafe ? 'path_escape' :
          !targetLstat ? 'missing' :
            targetLstat.isSymbolicLink() ? 'symlink' :
              !targetStat?.isFile() ? 'not_file' :
                sourceStat.dev === targetStat.dev && sourceStat.ino === targetStat.ino ? 'hardlink' : 'copy';
      if (linkType === 'hardlink') continue;
      findings.push(finding('P1', 'A', 'Global hook is not linked to the committed source', {
        surface: surface.id ?? null,
        source: surface.repo,
        target: relative(homeRoot, target),
        profile: profile.name,
        link_type: linkType,
        source_sha256: sourceBytes ? createHash('sha256').update(sourceBytes).digest('hex') : null,
        target_sha256: targetBytes ? createHash('sha256').update(targetBytes).digest('hex') : null,
      }, 'Run classifier repair --apply --only fm-hooks-global-link-broken.'));
    }
  }
  return findings;
}

// This is a current-state audit, not proof that a loaded hook behaved correctly.
// Unsupported declarations stay UNKNOWN rather than inheriting a presence-only pass.
async function outsideRepoFindings(ctx) {
  const findings = [];
  const report = (surface, reason, details = {}, unknown = false) => {
    findings.push(finding('P1', 'A', unknown ? 'Outside-repo audit coverage is UNKNOWN' : 'Outside-repo declared state differs from observed state', {
      surface: surface?.id ?? null, reason, ...details,
    }, 'Reconcile the canonical inventory with the named installed evidence; do not change live switches during an audit.'));
  };
  if (!ctx.repo || !ctx.home || !ctx.stateDir || ctx.inventory?.schema !== 'jev-inventory.expected.v1' ||
    !Array.isArray(ctx.inventory.surfaces) || !ctx.inventory.surfaces.length ||
    !Array.isArray(ctx.inventory.profiles) || !ctx.inventory.profiles.length ||
    ctx.inventory.profiles.some((name) => !safeInventoryPath(name) || name.includes('/'))) {
    report(null, 'required_inventory_or_scope_unavailable', {}, true);
    return findings;
  }
  let repo;
  let home;
  try { [repo, home] = await Promise.all([realpath(ctx.repo), realpath(ctx.home)]); }
  catch (error) {
    report(null, 'scope_unreadable', { code: error?.code ?? 'UNKNOWN' }, true);
    return findings;
  }
  const profiles = ctx.inventory.profiles.map((name) => ({
    name, path: name === 'default' ? join(home, '.omp', 'agent') : join(home, '.omp', 'profiles', name, 'agent'),
  }));
  const ids = new Set();
  for (const surface of ctx.inventory.surfaces) {
    if (!surface || typeof surface.id !== 'string' || ids.has(surface.id) ||
      !['on', 'off', 'inert'].includes(surface.expect)) {
      report(surface, 'unsupported_surface_declaration', {}, true);
      continue;
    }
    ids.add(surface.id);
    if (surface.expect === 'off' && surface.log) {
      // Only rerank's canonical inventory semantics define 3h silence as OFF.
      // Extension logs alone cannot establish that their configured switch is OFF.
      if (surface.id !== 'websearch-rerank') report(surface, 'off_switch_coverage_unavailable', {}, true);
      if (!safeInventoryPath(surface.log) || surface.log.includes('/')) {
        report(surface, 'unsupported_log_path', {}, true);
        continue;
      }
      try {
        const text = await readFile(join(ctx.stateDir, surface.log), 'utf8');
        let recent = 0;
        let invalid = false;
        for (const line of text.split('\n')) {
          if (!line.trim()) continue;
          try {
            const row = JSON.parse(line);
            const ts = typeof row.ts === 'number' ? row.ts : Date.parse(row.ts);
            if (!Number.isFinite(ts)) invalid = true;
            else if (ts >= ctx.now - 3 * 60 * 60 * 1000) recent += 1;
          } catch { invalid = true; }
        }
        if (recent) report(surface, 'declared_off_writer_active', { recent_rows: recent, window_ms: 3 * 60 * 60 * 1000 });
        if (invalid) report(surface, 'writer_log_unparseable', {}, true);
      } catch (error) {
        // A missing log is not evidence that an OFF writer has stopped.
        report(surface, 'writer_log_unavailable', { code: error?.code ?? 'UNKNOWN' }, true);
      }
      continue;
    }
    if (surface.group !== 'global' || surface.expect !== 'on') {
      report(surface, 'unsupported_surface_scope', { group: surface.group ?? null }, true);
      continue;
    }
    if (!safeInventoryPath(surface.repo) || typeof surface.hookfile !== 'string' ||
      !safeInventoryPath(surface.hookfile) || surface.hookfile.includes('/')) {
      report(surface, 'unsupported_install_declaration', {}, true);
      continue;
    }
    const source = join(repo, surface.repo);
    let sourceBytes;
    let sourceStat;
    try {
      const sourceReal = await realpath(source);
      sourceStat = await lstat(source);
      if (!isWithin(repo, sourceReal) || sourceStat.isSymbolicLink() || !sourceStat.isFile()) throw new Error('unsafe source');
      sourceBytes = await readFile(source);
    } catch (error) {
      report(surface, 'required_source_unavailable', { source: surface.repo, code: error?.code ?? 'UNSAFE' }, true);
      continue;
    }
    let committed;
    try {
      committed = await ctx.exec('git', ['-C', repo, 'show', `HEAD:${surface.repo}`], {
        timeout: 1000, maxBuffer: 4 * 1024 * 1024,
      });
    } catch { /* Report absent authority without printing command output or secrets. */ }
    if (committed?.code !== 0 || typeof committed.stdout !== 'string') {
      report(surface, 'committed_source_unavailable', { source: surface.repo }, true);
      continue;
    }
    if (!sourceBytes.equals(Buffer.from(committed.stdout, 'utf8'))) {
      report(surface, 'source_differs_from_committed', { source: surface.repo });
    }
    for (const profile of profiles) {
      const target = join(profile.path, 'hooks', 'post', surface.hookfile);
      const details = { profile: profile.name, target: relative(home, target), source: surface.repo };
      try {
        if (!await safeDirectoryParents(home, dirname(target))) {
          report(surface, 'installed_path_escape', details);
          continue;
        }
        const installed = await lstat(target);
        if (!installed.isFile() || installed.isSymbolicLink()) {
          report(surface, 'installed_not_regular_file', details);
          continue;
        }
        const bytes = await readFile(target);
        if (!bytes.equals(sourceBytes)) report(surface, 'installed_bytes_differ', details);
        else if (installed.dev !== sourceStat.dev || installed.ino !== sourceStat.ino) {
          report(surface, 'installed_not_source_hardlink', details);
        }
      } catch (error) {
        report(surface, 'required_install_unavailable', { ...details, code: error?.code ?? 'UNKNOWN' }, true);
      }
    }
  }
  return findings;
}

export const detectors = [
  {
    id: 'fm-hooks-global-link-broken', subsystem: 'hooks', tier: 'D', repo_required: true,
    data_sources: ['ctx.inventory global hook declarations', 'committed source via git show HEAD:<repo>', 'ctx.home global and profile hook paths'],
    async run(ctx) { return globalHookFindings(ctx); },
  },
  {
    id: 'fm-surfaces-outside-repo-audit', subsystem: 'drift', tier: 'D', repo_required: false,
    data_sources: ['ctx.inventory declared profiles and surfaces', 'committed source via git show HEAD:<repo>', 'installed global hook bytes and identity', 'declared-OFF writer logs (3h)'],
    async run(ctx) { return outsideRepoFindings(ctx); },
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
