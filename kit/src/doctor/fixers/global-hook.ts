import { createHash } from 'node:crypto';
import { lstat, readFile, realpath } from 'node:fs/promises';
import { isAbsolute, relative, resolve, sep } from 'node:path';
import { mutate } from '../mutate.js';
import type { RepairContext, RepairFinding, RepairPlan } from '../repair.js';

function refuse(message: string): Error & { code: 'REFUSED' } {
  return Object.assign(new Error(message), { code: 'REFUSED' as const });
}

function safeHookTarget(value: string): boolean {
  const parts = value.split('/');
  if (parts.some((part) => !part || part === '.' || part === '..' || part.includes('\\'))) return false;
  if (parts[0] !== '.omp' || parts.at(-1) === undefined) return false;
  return (parts[1] === 'agent' && parts[2] === 'hooks' && parts[3] === 'post' && parts.length === 5)
    || (parts[1] === 'profiles' && parts.length === 7 && parts[3] === 'agent' && parts[4] === 'hooks' && parts[5] === 'post');
}

export async function planGlobalHook(finding: RepairFinding, context: RepairContext): Promise<RepairPlan | null> {
  const evidence = finding.evidence ?? {};
  if (finding.id !== 'fm-hooks-global-link-broken' || typeof context.repo !== 'string' || typeof evidence.source !== 'string' || typeof evidence.target !== 'string') return null;
  const repo = resolve(context.repo);
  const home = resolve(context.home);
  const sourceValue = evidence.source;
  if (isAbsolute(sourceValue) || sourceValue.includes('\\') || sourceValue.split('/').some((part) => part === '..' || part === '.')) {
    throw refuse('global-hook source path is unsafe');
  }
  const source = resolve(repo, sourceValue);
  const sourceRelative = relative(repo, source);
  if (!sourceRelative || sourceRelative === '..' || sourceRelative.startsWith(`..${sep}`)) throw refuse('global-hook source escapes the repository');
  const targetRelative = evidence.target;
  if (!safeHookTarget(targetRelative)) throw refuse('global-hook target is outside declared hook paths');
  const target = resolve(home, targetRelative);
  const targetCheck = relative(home, target);
  if (!targetCheck || targetCheck === '..' || targetCheck.startsWith(`..${sep}`)) throw refuse('global-hook target escapes HOME');

  let sourceReal: string;
  let repoReal: string;
  let sourceMetadata;
  let targetMetadata;
  try {
    [repoReal, sourceReal, sourceMetadata, targetMetadata] = await Promise.all([
      realpath(repo), realpath(source), lstat(source), lstat(target),
    ]);
  } catch (cause) {
    throw refuse(`global-hook source or target is unavailable: ${cause instanceof Error ? cause.message : String(cause)}`);
  }
  const sourceWithinRepo = relative(repoReal, sourceReal);
  if (!sourceMetadata.isFile() || sourceMetadata.isSymbolicLink() || sourceWithinRepo === '..' || sourceWithinRepo.startsWith(`..${sep}`)) {
    throw refuse('global-hook source is not a regular file within the repository');
  }
  if (!targetMetadata.isFile() || targetMetadata.isSymbolicLink()) throw refuse('global-hook target is not a regular file');
  const [sourceBytes, targetBytes] = await Promise.all([readFile(source), readFile(target)]);
  if (!sourceBytes.equals(targetBytes)) throw refuse('global-hook target bytes differ from committed source; manual review required');
  const sourceHash = createHash('sha256').update(sourceBytes).digest('hex');
  const targetHash = createHash('sha256').update(targetBytes).digest('hex');
  const normalizedTarget = targetCheck.split(sep).join('/');
  return {
    action: { fixer: 'global-hook', finding_id: finding.id, operation: 'hardlink', target: normalizedTarget, desired: sourceValue },
    apply: (runId) => mutate({
      root: home,
      doctorDir: context.doctorDir,
      target: normalizedTarget,
      writeScopes: [normalizedTarget],
      operation: 'hardlink',
      source,
      sourceRoot: repo,
      runId,
      expectedBeforeSha256: targetHash,
      expectedBeforeMode: targetMetadata.mode & 0o777,
      expectedSourceSha256: sourceHash,
      expectedSourceMode: sourceMetadata.mode & 0o777,
    }),
  };
}
