import { promises as fs } from 'node:fs';
import path from 'node:path';

const CANARY = 'ai.zeststream.jev-latest-canary';
const GATEWAY = 'com.localbench.ollama-gateway';
const CANARY_PLIST = 'Library/LaunchAgents/ai.zeststream.jev-latest-canary.plist';
const manual = (reason) => ({ action: 'manual', reason });

async function launchctlRows(ctx) {
  try {
    const result = await ctx.exec('launchctl', ['list'], { timeout: 500 });
    if (result?.code !== 0 || typeof result.stdout !== 'string') return null;
    return result.stdout.split('\n').map((line) => line.trim().replaceAll('\t', ' ').split(' ').filter(Boolean)).filter((parts) => parts.length >= 3);
  } catch { return null; }
}

function rowFor(rows, label) {
  return rows?.find((parts) => parts.at(-1) === label) ?? null;
}

export const detectors = [
  {
    id: 'fm-daemons-canary-agent', subsystem: 'daemons', tier: 'Q', repo_required: false,
    data_sources: ['$home/Library/LaunchAgents/ai.zeststream.jev-latest-canary.plist', 'launchctl list'],
    async run(ctx) {
      const plist = path.join(ctx.home, CANARY_PLIST);
      let plistPresent;
      try { await fs.access(plist); plistPresent = true; } catch (error) {
        if (error.code === 'ENOENT') plistPresent = false;
        else return [];
      }
      const rows = await launchctlRows(ctx);
      if (rows === null) return [];
      const row = rowFor(rows, CANARY);
      const listed = row !== null;
      const lastExit = listed && Number.isInteger(Number(row[1])) ? Number(row[1]) : null;
      if (plistPresent && listed && lastExit === 0) return [];
      return [{
        severity: 'P2', kind: 'E', title: 'Jev latest canary LaunchAgent is not healthy',
        evidence: { plist, plist_present: plistPresent, listed, last_exit: lastExit },
        remediation: manual(`Bootstrap the canary LaunchAgent from ${plist} after reviewing its state.`),
      }];
    },
  },
  {
    id: 'fm-daemons-gateway-down', subsystem: 'daemons', tier: 'Q', repo_required: false,
    data_sources: ['launchctl list com.localbench.ollama-gateway', 'TCP 127.0.0.1:11300'],
    async run(ctx) {
      const rows = await launchctlRows(ctx);
      if (rows === null) return [];
      const row = rowFor(rows, GATEWAY);
      const hasPid = row !== null && row[0] !== '-' && Number.isInteger(Number(row[0])) && Number(row[0]) >= 0;
      if (!hasPid) {
        return [{
          severity: 'P1', kind: 'E', title: 'Localbench gateway daemon is not running',
          evidence: { label: GATEWAY, listed: row !== null, has_pid: false, endpoint: '127.0.0.1:11300' },
          remediation: manual('Restore the localbench ollama-gateway daemon.'),
        }];
      }
      if (typeof ctx.exec !== 'function') return [];
      let probe;
      try { probe = await ctx.exec('nc', ['-z', '-w', '1', '127.0.0.1', '11300'], { timeout: 500 }); } catch { probe = null; }
      if (probe === null) return [];
      if (probe.code === 0) return [];
      return [{
        severity: 'P1', kind: 'E', title: 'Localbench gateway daemon is not reachable',
        evidence: { label: GATEWAY, listed: true, has_pid: true, endpoint: '127.0.0.1:11300', reachable: false },
        remediation: manual('Restore localbench gateway reachability on 127.0.0.1:11300.'),
      }];
    },
  },
  {
    id: 'fm-daemons-needs-human-watch', subsystem: 'daemons', tier: 'Q', repo_required: false,
    data_sources: ['process list fleet-idle-watch.py'],
    async run(ctx) {
      if (typeof ctx.exec !== 'function') return [];
      let result;
      try { result = await ctx.exec('pgrep', ['-fl', 'fleet-idle-watch.py'], { timeout: 500 }); } catch { return []; }
      if (result?.code === 0 && typeof result.stdout === 'string' && result.stdout.trim().length > 0) return [];
      if (result?.code !== 1) return [];
      return [{
        severity: 'P2', kind: 'E', title: 'Fleet human-watch process is not running',
        evidence: { process: 'fleet-idle-watch.py', present: false },
        remediation: manual('Start or otherwise supervise fleet-idle-watch.py.'),
      }];
    },
  },
];
