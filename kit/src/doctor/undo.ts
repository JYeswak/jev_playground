import { lstat, readFile, readdir } from 'node:fs/promises';
import { join, relative, resolve, sep } from 'node:path';
import { randomUUID } from 'node:crypto';
import { mutate } from './mutate.js';

type Action = {
  id: string;
  kind: string;
  run_id: string;
  operation: string;
  root: string;
  target: string;
  before_exists: boolean;
  before_sha256: string | null;
  before_mode: number | null;
  after_exists: boolean;
  after_sha256: string | null;
  after_mode: number | null;
  backup_path: string | null;
  undo_of?: string;
};

type UndoError = Error & { code: 'REFUSED' | 'RETRYABLE' | 'IO'; actions_taken?: number };

function undoError(message: string, code: UndoError['code'], actionsTaken?: number, cause?: unknown): UndoError {
  return Object.assign(new Error(message, cause === undefined ? undefined : { cause }), { code, ...(actionsTaken === undefined ? {} : { actions_taken: actionsTaken }) });
}

function isErrno(cause: unknown, code: string): boolean {
  return Boolean(cause && typeof cause === 'object' && 'code' in cause && cause.code === code);
}

function parseActions(contents: string, path: string): Action[] {
  const actions: Action[] = [];
  for (const line of contents.split('\n')) {
    if (!line.trim()) continue;
    let parsed: unknown;
    try { parsed = JSON.parse(line); }
    catch (cause) { throw undoError(`action log is malformed: ${path}`, 'REFUSED', undefined, cause); }
    if (!parsed || typeof parsed !== 'object' || typeof (parsed as Action).id !== 'string' || typeof (parsed as Action).run_id !== 'string') {
      throw undoError(`action log row is invalid: ${path}`, 'REFUSED');
    }
    actions.push(parsed as Action);
  }
  return actions;
}

function nextRunId(): string {
  return `undo-${new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-')}-${randomUUID()}`;
}

export async function undoLatest(context: { doctorDir: string }) {
  const doctorDir = resolve(context.doctorDir);
  const runsDir = join(doctorDir, 'runs');
  let entries;
  try { entries = await readdir(runsDir, { withFileTypes: true }); }
  catch (cause) {
    if (isErrno(cause, 'ENOENT')) return { ok: true, mode: 'undo', actions_taken: 0, run_id: null };
    throw undoError(`cannot read doctor runs: ${runsDir}`, 'IO', undefined, cause);
  }
  const runs = entries.filter((entry) => entry.isDirectory() && !entry.isSymbolicLink()).map((entry) => entry.name).sort();
  const rows: Action[] = [];
  for (const run of runs) {
    const path = join(runsDir, run, 'actions.jsonl');
    let metadata;
    try { metadata = await lstat(path); }
    catch (cause) {
      if (isErrno(cause, 'ENOENT')) continue;
      throw undoError(`cannot inspect action log: ${path}`, 'IO', undefined, cause);
    }
    if (!metadata.isFile() || metadata.isSymbolicLink()) throw undoError(`action log is not a regular file: ${path}`, 'REFUSED');
    rows.push(...parseActions(await readFile(path, 'utf8'), path));
  }
  const undone = new Set(rows.filter((row) => row.kind === 'undo' && typeof row.undo_of === 'string').map((row) => row.undo_of!));
  const originalRuns = [...new Set(rows.filter((row) => row.kind !== 'undo').map((row) => row.run_id))].sort().reverse();
  const targetRun = originalRuns.find((run) => rows.some((row) => row.run_id === run && row.kind !== 'undo' && !undone.has(row.id)));
  if (!targetRun) return { ok: true, mode: 'undo', actions_taken: 0, run_id: null };
  const actions = rows.filter((row) => row.run_id === targetRun && row.kind !== 'undo' && !undone.has(row.id)).reverse();
  const undoRunId = nextRunId();
  let actionsTaken = 0;
  for (const action of actions) {
    if (!action.root || !action.target || action.target.split('/').includes('..') || action.target.startsWith('/') || (action.before_exists && !action.backup_path)) {
      throw undoError(`cannot safely undo action ${action.id}: invalid scope or backup`, 'REFUSED', actionsTaken);
    }
    const backupPath = action.backup_path ? resolve(doctorDir, action.backup_path) : null;
    if (backupPath) {
      const backupRelative = relative(doctorDir, backupPath);
      if (!backupRelative || backupRelative === '..' || backupRelative.startsWith(`..${sep}`)) {
        throw undoError(`cannot safely undo action ${action.id}: backup escapes doctor state`, 'REFUSED', actionsTaken);
      }
    }
    let currentBytes: Buffer | undefined;
    if (action.before_exists) {
      if (!backupPath) throw undoError(`action ${action.id} has no restorable backup`, 'REFUSED', actionsTaken);
      try { currentBytes = await readFile(backupPath); }
      catch (cause) { throw undoError(`cannot read verbatim backup for action ${action.id}`, 'IO', actionsTaken, cause); }
    }
    try {
      if (action.before_exists) {
        if (action.before_mode === null || !currentBytes) throw undoError(`action ${action.id} has no restorable backup metadata`, 'REFUSED', actionsTaken);
        await mutate({
          root: action.root,
          doctorDir,
          target: action.target,
          writeScopes: [action.target],
          operation: 'restore',
          content: currentBytes,
          mode: action.before_mode,
          runId: undoRunId,
          expectedBeforeSha256: action.after_sha256,
          expectedBeforeMode: action.after_mode,
          actionKind: 'undo',
          undoOf: action.id,
        });
      } else {
        await mutate({
          root: action.root,
          doctorDir,
          target: action.target,
          writeScopes: [action.target],
          operation: 'quarantine',
          runId: undoRunId,
          expectedBeforeSha256: action.after_sha256,
          expectedBeforeMode: action.after_mode,
          actionKind: 'undo',
          undoOf: action.id,
        });
      }
      actionsTaken += 1;
    } catch (cause) {
      const code = cause && typeof cause === 'object' && 'code' in cause && ['REFUSED', 'RETRYABLE', 'IO'].includes(String(cause.code))
        ? cause.code as UndoError['code'] : 'IO';
      throw undoError(`undo latest stopped after ${actionsTaken} action(s): ${cause instanceof Error ? cause.message : String(cause)}`, code, actionsTaken, cause);
    }
  }
  return { ok: true, mode: 'undo', actions_taken: actionsTaken, run_id: targetRun };
}
