import { promises as fs } from 'node:fs';
import path from 'node:path';
import { readLogTail } from './logs.mjs';

const DAY = 24 * 60 * 60 * 1000;
const MACHINE_CONFIG = '.config/infisical/zeststream.env';
const manual = (reason) => ({ action: 'manual', reason });

async function exists(file) {
  try { await fs.access(file); return true; } catch { return false; }
}

async function hasPathBinary(ctx) {
  const directories = typeof ctx.env?.PATH === 'string' ? ctx.env.PATH.split(path.delimiter) : [];
  for (const directory of directories) {
    if (!directory || directory === '.') continue;
    if (await exists(path.join(directory, 'infisical'))) return true;
  }
  return false;
}

export async function resolveKeySource(ctx) {
  const envPresent = typeof ctx.env?.TYPESAFE_API_KEY === 'string' && ctx.env.TYPESAFE_API_KEY.length > 0;
  const localBinary = await exists(path.join(ctx.home, '.local', 'bin', 'infisical'));
  const pathBinary = !localBinary && typeof ctx.env?.PATH === 'string' ? await hasPathBinary(ctx) : false;
  const userBinary = localBinary || pathBinary;
  const machineConfig = await exists(path.join(ctx.home, MACHINE_CONFIG));
  let machineIdentity = false;
  if (machineConfig) {
    try {
      const config = await fs.readFile(path.join(ctx.home, MACHINE_CONFIG), 'utf8');
      machineIdentity = config.split('\n').some((line) => line.trimStart().startsWith('export INFISICAL_CLIENT_ID='));
    } catch { /* unreadable configuration is not a usable source */ }
  }
  const key_source = envPresent ? 'env' : userBinary ? 'infisical-user' : machineIdentity ? 'infisical-machine' : 'none';
  return { key_source, checked: { env: envPresent, infisical_user: userBinary, infisical_machine: machineIdentity } };
}

export const detectors = [
  {
    id: 'fm-secrets-no-key-source', subsystem: 'secrets', tier: 'Q', repo_required: false,
    data_sources: ['ctx.env.TYPESAFE_API_KEY presence', '$home/.local/bin/infisical', 'ctx.env.PATH infisical binary', '$home/.config/infisical/zeststream.env INFISICAL_CLIENT_ID'],
    async run(ctx) {
      const found = await resolveKeySource(ctx);
      if (found.key_source !== 'none') return [];
      return [{
        severity: 'P0', kind: 'G', title: 'No TypeSafe key source is configured',
        evidence: { checked: found.checked, key_source: found.key_source },
        remediation: manual('Run infisical login or configure TYPESAFE_API_KEY, then rerun this check.'),
      }];
    },
  },
  {
    id: 'fm-secrets-key-wrapper-missing', subsystem: 'secrets', tier: 'Q', repo_required: false,
    data_sources: ['ctx.inventory.profiles', '$home/.omp/agent/models.yml', '$home/.omp/profiles/<profile>/agent/models.yml'],
    async run(ctx) {
      const profiles = ctx.inventory?.profiles;
      if (!Array.isArray(profiles)) return [];
      const findings = [];
      const required = ['default', ...profiles.filter((profile) => typeof profile === 'string' && profile !== 'default')];
      for (const profile of new Set(required)) {
        const file = profile === 'default'
          ? path.join(ctx.home, '.omp', 'agent', 'models.yml')
          : path.join(ctx.home, '.omp', 'profiles', profile, 'agent', 'models.yml');
        let text;
        try { text = await fs.readFile(file, 'utf8'); } catch (error) {
          if (error.code !== 'ENOENT') continue;
          text = null;
        }
        if (text !== null && text.includes('typesafe-key.mjs')) continue;
        findings.push({
          severity: 'P0', kind: 'G', title: `TypeSafe key wrapper is missing for profile ${profile}`,
          evidence: { profile, file, line: null },
          remediation: manual('Restore the typesafe-key.mjs wrapper in the profile models.yml configuration.'),
        });
      }
      return findings;
    },
  },
  {
    id: 'fm-secrets-machine-config-mode', subsystem: 'secrets', tier: 'Q', repo_required: false,
    data_sources: ['$home/.config/infisical/zeststream.env file mode'],
    async run(ctx) {
      const file = path.join(ctx.home, MACHINE_CONFIG);
      let mode;
      try { mode = (await fs.stat(file)).mode & 0o777; } catch { return []; }
      if ((mode & 0o077) === 0) return [];
      return [{
        severity: 'P1', kind: 'D', title: 'Infisical machine configuration permissions are too open',
        evidence: { file, mode },
        remediation: manual('Restrict the machine configuration to mode 0600.'),
      }];
    },
  },
  {
    id: 'fm-secrets-recent-resolve-failures', subsystem: 'secrets', tier: 'D', repo_required: false,
    data_sources: ['ctx.stateDir/gate-observe.jsonl'],
    async run(ctx) {
      const file = path.join(ctx.stateDir, 'gate-observe.jsonl');
      const result = await readLogTail(file);
      if (result.exists !== true) return [];
      let count = 0;
      for (const { row } of result.rows) {
        const ts = typeof row?.ts === 'string' ? Date.parse(row.ts) : NaN;
        if (Number.isFinite(ts) && ts >= ctx.now - DAY && ts <= ctx.now && typeof row.error === 'string' && row.error.includes('key-source=infisical')) count += 1;
      }
      if (!count) return [];
      return [{
        severity: 'P1', kind: 'G', title: 'Recent Infisical key resolution failures were recorded',
        evidence: { file, failures_24h: count },
        remediation: manual('Check the Infisical machine identity and key provider configuration.'),
      }];
    },
  },
];
