import { access, readFile, stat } from 'node:fs/promises';
import { join, resolve } from 'node:path';

const TOOL_PATHS = [
  '.omp/tools/jev-rerank.ts',
  '.omp/tools/jev-claim-check.ts',
  '.omp/tools/jev-screen.ts',
  '.omp/tools/jev-flag.ts',
  '.omp/tools/jev-gate.ts',
  '.omp/tools/jev-classify.ts',
];
const HOOK_PATHS = ['.omp/hooks/post/jev-gate-observe.ts'];
const EXTENSION_PATHS = [
  '.omp/extensions/jev-rerank.ts',
  '.omp/extensions/jev-claim-check.ts',
  '.omp/extensions/jev-screen.ts',
  '.omp/extensions/jev-flag.ts',
  '.omp/extensions/jev-classify.ts',
];
const MANIFEST = '.omp/jev-kit-manifest.json';
function finding(severity, kind, title, evidence, manual) {
  return { severity, kind, title, evidence, remediation: { manual } };
}
function rowsFromDiscovery(ctx, category, fallback) {
  const rows = ctx.omp?.[category];
  return Array.isArray(rows) ? rows.map((row) => row?.path).filter((path) => typeof path === 'string') : fallback;
}
async function exists(path) {
  try { await access(path); return true; } catch { return false; }
}
async function readManifest(repo) {
  try {
    const parsed = JSON.parse(await readFile(join(repo, MANIFEST), 'utf8'));
    return parsed && typeof parsed.files === 'object' && parsed.files ? parsed.files : null;
  } catch { return null; }
}
function manifestKey(path) {
  return path.startsWith('.omp/') ? path.slice('.omp/'.length) : path;
}
function parseFailureLine(line) {
  const marker = 'HOOK_LOAD_FAIL ';
  const start = line.indexOf(marker);
  if (start < 0) return null;
  const value = line.slice(start + marker.length);
  const separator = value.indexOf(': ');
  return separator > 0 ? value.slice(0, separator) : null;
}

export const detectors = [
  {
    id: 'fm-hooks-load-failure', subsystem: 'hooks', tier: 'X', repo_required: true,
    data_sources: ['injected bun scripts/check-hook-loads.mjs output', '.omp/config.yml', 'hook and extension sources'],
    async run(ctx) {
      const result = await ctx.exec('bun', ['scripts/check-hook-loads.mjs', '--repo', ctx.repo, '--home', ctx.home], { cwd: ctx.repo, env: ctx.env });
      const output = `${result.stderr ?? ''}\n${result.stdout ?? ''}`;
      const findings = [];
      for (const line of output.split('\n')) {
        const file = parseFailureLine(line);
        if (file) findings.push(finding('P0', 'B', 'OMP hook or extension failed to load', { file }, 'Inspect and correct the reported hook or extension source.'));
      }
      return findings;
    },
  },
  {
    id: 'fm-plugins-omp-tool-missing', subsystem: 'plugins', tier: 'Q', repo_required: true,
    data_sources: [...TOOL_PATHS, ...HOOK_PATHS, ...EXTENSION_PATHS, MANIFEST],
    async run(ctx) {
      if (!ctx.repo) return [];
      const repo = resolve(ctx.repo);
      const manifest = await readManifest(repo);
      if (!manifest) return [];
      const candidates = [
        ...rowsFromDiscovery(ctx, 'tools', TOOL_PATHS),
        ...rowsFromDiscovery(ctx, 'hooks', HOOK_PATHS),
        ...rowsFromDiscovery(ctx, 'extensions', EXTENSION_PATHS),
      ];
      const findings = [];
      for (const relativePath of candidates) {
        const repoPath = relativePath.startsWith('.omp/') ? relativePath : `.omp/${relativePath}`;
        if (!manifest[manifestKey(repoPath)] && !manifest[repoPath]) continue;
        if (await exists(join(repo, repoPath))) continue;
        findings.push(finding('P2', 'C', 'Manifest-listed OMP surface file is missing', { file: repoPath }, 'Reinstall the missing OMP file after reviewing the installer manifest.'));
      }
      return findings;
    },
  },
  {
    id: 'fm-path-jev-shadowed', subsystem: 'paths', tier: 'Q', repo_required: false,
    data_sources: ['PATH resolution for jev', 'realpath of resolved jev', 'kit/bin/jev.mjs'],
    async run(ctx) {
      const found = ctx.omp?.jev_path ?? ctx.omp?.path ?? null;
      let resolvedPath = typeof found === 'string' ? found : found?.resolved;
      let actualRealpath = found?.realpath;
      if (!resolvedPath) {
        const lookup = await ctx.exec('which', ['jev'], { env: ctx.env });
        resolvedPath = lookup.code === 0 ? (lookup.stdout ?? '').trim().split('\n')[0] : '';
      }
      if (!resolvedPath) return [];
      if (!actualRealpath) {
        const real = await ctx.exec('realpath', [resolvedPath], {});
        if (real.code !== 0) return [];
        actualRealpath = (real.stdout ?? '').trim();
      }
      const packageRoot = ctx.repo ?? new URL('../../../..', import.meta.url).pathname;
      const packageEntry = join(packageRoot, 'kit/bin/jev.mjs');
      const expected = await ctx.exec('realpath', [packageEntry], {});
      if (expected.code !== 0) return [];
      const expectedRealpath = (expected.stdout ?? '').trim();
      if (!actualRealpath || actualRealpath === expectedRealpath) return [];
      return [finding('P2', 'F', 'PATH jev resolves to a different executable', { resolved: resolvedPath, realpath_matches_package: false }, 'Invoke the kit entrypoint explicitly or correct PATH ordering.')];
    },
  },
  {
    id: 'fm-plugins-sibling-bin-missing', subsystem: 'plugins', tier: 'Q', repo_required: true,
    data_sources: ['kit/bin/jev-skill-gap.mjs executable bit'],
    async run(ctx) {
      if (!ctx.repo) return [];
      const path = join(ctx.repo, 'kit/bin/jev-skill-gap.mjs');
      try {
        const info = await stat(path);
        if ((info.mode & 0o111) !== 0) return [];
      } catch { /* missing is a finding */ }
      return [finding('P3', 'C', 'Sibling jev-skill-gap binary is missing or not executable', { file: 'kit/bin/jev-skill-gap.mjs' }, 'Restore the sibling executable from the repository package.')];
    },
  },
];

export const surfacePaths = { tools: TOOL_PATHS, hooks: HOOK_PATHS, extensions: EXTENSION_PATHS };
