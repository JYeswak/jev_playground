import { createHash } from 'node:crypto';
import { lstat, readFile } from 'node:fs/promises';
import { relative, resolve, sep } from 'node:path';
import { mutate } from '../mutate.js';
import type { RepairContext, RepairFinding, RepairPlan } from '../repair.js';

function refuse(message: string): Error & { code: 'REFUSED' } {
  return Object.assign(new Error(message), { code: 'REFUSED' as const });
}

export async function planLogMode(finding: RepairFinding, context: RepairContext): Promise<RepairPlan | null> {
  const candidate = finding.evidence?.path;
  if (finding.id !== 'fm-logs-mode-too-open' || typeof candidate !== 'string') return null;
  const stateDir = resolve(context.stateDir);
  const target = resolve(candidate);
  const relativePath = relative(stateDir, target);
  if (!relativePath || relativePath === '..' || relativePath.startsWith(`..${sep}`) || relativePath.includes('\\')) {
    throw refuse('log-mode target is outside the configured state directory');
  }
  let metadata;
  try { metadata = await lstat(target); }
  catch (cause) { throw refuse(`log-mode target is unavailable: ${cause instanceof Error ? cause.message : String(cause)}`); }
  if (!metadata.isFile() || metadata.isSymbolicLink() || !relativePath.endsWith('.jsonl')) throw refuse('log-mode target is not a regular declared log');
  const bytes = await readFile(target);
  const mode = metadata.mode & 0o777;
  if ((mode & 0o077) === 0) return null;
  const targetHash = createHash('sha256').update(bytes).digest('hex');
  const normalized = relativePath.split(sep).join('/');
  return {
    action: { fixer: 'log-mode', finding_id: finding.id, operation: 'chmod', target: normalized, desired: '0600' },
    apply: (runId) => mutate({
      root: stateDir,
      doctorDir: context.doctorDir,
      target: normalized,
      writeScopes: [normalized],
      operation: 'chmod',
      mode: 0o600,
      runId,
      expectedBeforeSha256: targetHash,
      expectedBeforeMode: mode,
    }),
  };
}
