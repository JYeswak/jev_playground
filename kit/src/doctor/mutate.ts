import { constants } from 'node:fs';
import { appendFile, chmod, link, lstat, mkdir, open, readFile, rename, truncate } from 'node:fs/promises';
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { acquireDoctorLock } from './lock.js';

export type MutationOperation = 'chmod' | 'hardlink' | 'write' | 'quarantine' | 'restore';
export type MutationInput = {
  root: string;
  doctorDir: string;
  target: string;
  writeScopes: string[];
  operation: MutationOperation;
  runId?: string;
  mode?: number;
  content?: Uint8Array | string;
  source?: string;
  sourceRoot?: string;
  expectedBeforeSha256?: string | null;
  expectedBeforeMode?: number | null;
  expectedSourceSha256?: string;
  expectedSourceMode?: number;
  actionKind?: 'repair' | 'uninstall' | 'undo';
  undoOf?: string;
};

type MutationError = Error & { code: 'REFUSED' | 'RETRYABLE' | 'IO' };
type Snapshot = { exists: boolean; bytes: Buffer | null; sha256: string | null; mode: number | null };

const PROTECTED_NAMES: Record<string, true> = {
  'models.yml': true,
  'config.yml': true,
  'expected.json': true,
  'cascade-off': true,
  'read-screen-off': true,
  'memory-filter-enforce': true,
  'memory-cap3': true,
  'fleet-router.off': true,
};

export function isProtectedMutationPath(relativePath: string): boolean {
  const leaf = relativePath.split('/').at(-1)!;
  return Object.hasOwn(PROTECTED_NAMES, leaf);
}

function mutationError(message: string, code: MutationError['code'], cause?: unknown): MutationError {
  return Object.assign(new Error(message, cause === undefined ? undefined : { cause }), { code });
}

function isErrno(cause: unknown, code: string): boolean {
  return Boolean(cause && typeof cause === 'object' && 'code' in cause && cause.code === code);
}

function sha256(bytes: Uint8Array): string {
  return createHash('sha256').update(bytes).digest('hex');
}

function runId(value?: string): string {
  if (value && value.length <= 80 && !value.includes('/') && !value.includes('\\') && !value.includes('..')) return value;
  if (value !== undefined) throw mutationError('invalid mutation run id', 'REFUSED');
  return `${new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-')}.${randomUUID()}`;
}

async function snapshot(path: string): Promise<Snapshot> {
  let metadata;
  try { metadata = await lstat(path); }
  catch (cause) {
    if (isErrno(cause, 'ENOENT') || isErrno(cause, 'ENOTDIR')) return { exists: false, bytes: null, sha256: null, mode: null };
    throw mutationError(`cannot inspect mutation target: ${path}`, 'IO', cause);
  }
  if (!metadata.isFile() || metadata.isSymbolicLink()) throw mutationError(`mutation target is not a regular file: ${path}`, 'REFUSED');
  let bytes: Buffer;
  try { bytes = await readFile(path); }
  catch (cause) { throw mutationError(`cannot read mutation target: ${path}`, 'IO', cause); }
  return { exists: true, bytes, sha256: sha256(bytes), mode: metadata.mode & 0o777 };
}

async function safeParents(root: string, target: string): Promise<void> {
  const rootMetadata = await lstat(root).catch((cause) => {
    throw mutationError(`mutation root is unavailable: ${root}`, 'IO', cause);
  });
  if (!rootMetadata.isDirectory() || rootMetadata.isSymbolicLink()) throw mutationError(`mutation root is unsafe: ${root}`, 'REFUSED');
  let current = root;
  for (const part of relative(root, dirname(target)).split(sep).filter(Boolean)) {
    current = join(current, part);
    try {
      const metadata = await lstat(current);
      if (metadata.isSymbolicLink() || !metadata.isDirectory()) throw mutationError(`mutation parent is unsafe: ${current}`, 'REFUSED');
    } catch (cause) {
      if (isErrno(cause, 'ENOENT') || isErrno(cause, 'ENOTDIR')) return;
      throw cause;
    }
  }
}

function relativeTarget(root: string, value: string): { absolute: string; relative: string } {
  const absolute = isAbsolute(value) ? resolve(value) : resolve(root, value);
  const rel = relative(root, absolute);
  if (!rel || rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) throw mutationError('mutation target escapes its root', 'REFUSED');
  const normalized = rel.split(sep).join('/');
  return { absolute, relative: normalized };
}

function validateOperation(operation: MutationOperation, relativePath: string, writeScopes: string[]): void {
  if (operation !== 'chmod' && operation !== 'hardlink' && operation !== 'write' && operation !== 'quarantine' && operation !== 'restore') {
    throw mutationError('unknown mutation operation', 'REFUSED');
  }
  if (!Array.isArray(writeScopes) || writeScopes.some((scope) => typeof scope !== 'string')) {
    throw mutationError('mutation requires declared string write scopes', 'REFUSED');
  }
  if (isProtectedMutationPath(relativePath)) throw mutationError(`mutation target is protected: ${relativePath.split('/').at(-1)}`, 'REFUSED');
  if (!writeScopes.includes(relativePath)) throw mutationError(`mutation target is outside declared write scopes: ${relativePath}`, 'REFUSED');
  if (operation === 'chmod' && !relativePath.endsWith('.jsonl')) throw mutationError('chmod is allowed only for declared log files', 'REFUSED');
  if (operation === 'restore' && relativePath.endsWith('.jsonl')) return;
  if (operation !== 'chmod' && operation !== 'restore' && !relativePath.startsWith('.omp/')) throw mutationError(`${operation} is restricted to installer-managed .omp files`, 'REFUSED');
  const managedPath = ['.omp/tools/', '.omp/hooks/', '.omp/extensions/', '.omp/jev-kit/', '.omp/agent/hooks/post/', '.omp/profiles/'].some((prefix) => relativePath.startsWith(prefix));
  const uninstallManifest = ['quarantine', 'restore'].includes(operation) && relativePath === '.omp/jev-kit-manifest.json';
  if (['write', 'hardlink', 'restore', 'quarantine'].includes(operation) && !managedPath && !uninstallManifest) {
    throw mutationError(`mutation operation is not allowed for this path: ${relativePath}`, 'REFUSED');
  }
}

async function atomicWrite(path: string, bytes: Uint8Array, mode: number, quarantineDir: string, token: string): Promise<void> {
  const temporary = `${path}.${token}.tmp`;
  let handle;
  try {
    handle = await open(temporary, constants.O_CREAT | constants.O_EXCL | constants.O_WRONLY, 0o600);
    await handle.writeFile(bytes);
    await handle.sync();
    await handle.close();
    handle = undefined;
    await chmod(temporary, mode);
    await rename(temporary, path);
  } catch (cause) {
    await handle?.close().catch(() => undefined);
    if (await lstat(temporary).then(() => true, () => false)) {
      await mkdir(quarantineDir, { recursive: true, mode: 0o700 });
      await rename(temporary, join(quarantineDir, `failed-write-${token}`)).catch(() => undefined);
    }
    throw mutationError(`cannot atomically mutate file: ${path}`, 'IO', cause);
  }
}

async function makeBackup(root: string, path: string, bytes: Buffer, backupPath: string): Promise<void> {
  await safeParents(root, backupPath);
  await mkdir(dirname(backupPath), { recursive: true, mode: 0o700 });
  await safeParents(root, backupPath);
  const backupDirectory = await lstat(dirname(backupPath));
  if (!backupDirectory.isDirectory() || backupDirectory.isSymbolicLink() || (backupDirectory.mode & 0o077) !== 0) {
    throw mutationError('mutation backup directory is unsafe', 'REFUSED');
  }
  let handle;
  try {
    handle = await open(backupPath, constants.O_CREAT | constants.O_EXCL | constants.O_WRONLY, 0o600);
    await handle.writeFile(bytes);
    await handle.sync();
    await handle.close();
    handle = undefined;
    const verified = await readFile(backupPath);
    if (!verified.equals(bytes)) throw mutationError(`verbatim backup verification failed: ${path}`, 'IO');
  } catch (cause) {
    await handle?.close().catch(() => undefined);
    throw cause;
  }
}

export async function mutate(input: MutationInput) {
  const root = resolve(input.root);
  const doctorDir = resolve(input.doctorDir);
  const target = relativeTarget(root, input.target);
  const lock = await acquireDoctorLock(doctorDir);
  try {
    await safeParents(root, target.absolute);
    const before = await snapshot(target.absolute);
    if (Object.hasOwn(input, 'expectedBeforeSha256') && input.expectedBeforeSha256 !== before.sha256) {
      throw mutationError(`mutation target changed since planning: ${target.relative}`, 'REFUSED');
    }
    if (Object.hasOwn(input, 'expectedBeforeMode') && input.expectedBeforeMode !== before.mode) {
      throw mutationError(`mutation target mode changed since planning: ${target.relative}`, 'REFUSED');
    }
    validateOperation(input.operation, target.relative, input.writeScopes);
    if (input.operation !== 'write' && input.operation !== 'restore' && !before.exists) {
      throw mutationError(`mutation target is missing: ${target.relative}`, 'REFUSED');
    }
    if (input.operation === 'write' && before.exists) throw mutationError(`refusing to overwrite existing file: ${target.relative}`, 'REFUSED');
    if ((input.operation === 'write' || input.operation === 'restore') && input.content === undefined) {
      throw mutationError(`${input.operation} requires file content`, 'REFUSED');
    }
    if (input.operation === 'chmod' && (!Number.isInteger(input.mode) || input.mode! < 0 || input.mode! > 0o777)) {
      throw mutationError('chmod requires a valid file mode', 'REFUSED');
    }

    let sourcePath: string | undefined;
    let sourceBytes: Buffer | undefined;
    let sourceMode: number | undefined;
    if (input.operation === 'hardlink') {
      if (!input.source || !input.sourceRoot) throw mutationError('hardlink requires a source path and source root', 'REFUSED');
      const sourceRoot = resolve(input.sourceRoot);
      sourcePath = relativeTarget(sourceRoot, input.source).absolute;
      await safeParents(sourceRoot, sourcePath);
      let sourceMetadata;
      try { sourceMetadata = await lstat(sourcePath); }
      catch (cause) { throw mutationError(`hardlink source is unavailable: ${sourcePath}`, 'IO', cause); }
      if (!sourceMetadata.isFile() || sourceMetadata.isSymbolicLink()) throw mutationError('hardlink source is not a regular file', 'REFUSED');
      sourceBytes = await readFile(sourcePath);
      sourceMode = sourceMetadata.mode & 0o777;
      if (input.expectedSourceSha256 && sha256(sourceBytes) !== input.expectedSourceSha256) throw mutationError('hardlink source changed since planning', 'REFUSED');
      if (input.expectedSourceMode !== undefined && sourceMode !== input.expectedSourceMode) throw mutationError('hardlink source mode changed since planning', 'REFUSED');
      if (!before.bytes?.equals(sourceBytes)) throw mutationError('refusing to replace a hook copy whose bytes differ from source', 'REFUSED');
    }

    const id = randomUUID();
    const currentRun = runId(input.runId);
    const runDir = join(doctorDir, 'runs', currentRun);
    const quarantineDir = join(runDir, 'quarantine');
    const logPath = join(runDir, 'actions.jsonl');
    await safeParents(doctorDir, runDir);
    await mkdir(runDir, { recursive: true, mode: 0o700 });
    const runsMetadata = await lstat(join(doctorDir, 'runs'));
    if (!runsMetadata.isDirectory() || runsMetadata.isSymbolicLink() || (runsMetadata.mode & 0o077) !== 0) {
      throw mutationError('mutation runs directory is unsafe', 'REFUSED');
    }
    const runMetadata = await lstat(runDir);
    if (!runMetadata.isDirectory() || runMetadata.isSymbolicLink() || (runMetadata.mode & 0o077) !== 0) {
      throw mutationError('mutation run directory is unsafe', 'REFUSED');
    }
    await safeParents(doctorDir, logPath);
    let priorLogSize = 0;
    try {
      const logMetadata = await lstat(logPath);
      if (!logMetadata.isFile() || logMetadata.isSymbolicLink() || (logMetadata.mode & 0o077) !== 0) {
        throw mutationError('mutation action log is unsafe', 'REFUSED');
      }
      priorLogSize = logMetadata.size;
    } catch (cause) {
      if (!isErrno(cause, 'ENOENT')) throw cause;
    }
    const backupPath = before.exists && input.operation !== 'quarantine'
      ? join(runDir, 'backups', `${id}.bin`)
      : null;
    if (backupPath) {
      if (!before.bytes) throw mutationError('existing mutation target has no backup bytes', 'IO');
      await makeBackup(doctorDir, target.absolute, before.bytes, backupPath);
    }
    let quarantinePath: string | null = null;
    try {
      if (input.operation === 'chmod') {
        await chmod(target.absolute, input.mode!);
      } else if (input.operation === 'hardlink') {
        const temporary = `${target.absolute}.${id}.link`;
        try {
          await link(sourcePath!, temporary);
          await rename(temporary, target.absolute);
        } catch (cause) {
          await mkdir(quarantineDir, { recursive: true, mode: 0o700 });
          await rename(temporary, join(quarantineDir, `failed-link-${id}`)).catch(() => undefined);
          throw cause;
        }
      } else if (input.operation === 'write' || input.operation === 'restore') {
        const bytes = typeof input.content === 'string' ? Buffer.from(input.content, 'utf8') : Buffer.from(input.content!);
        const mode = input.mode ?? before.mode ?? 0o600;
        await atomicWrite(target.absolute, bytes, mode, quarantineDir, id);
      } else {
        quarantinePath = join(quarantineDir, target.relative);
        await safeParents(doctorDir, quarantinePath);
        await mkdir(dirname(quarantinePath), { recursive: true, mode: 0o700 });
        await safeParents(doctorDir, quarantinePath);
        await rename(target.absolute, quarantinePath);
      }

      const after = await snapshot(target.absolute);
      const action = {
        id,
        kind: input.actionKind ?? 'repair',
        run_id: currentRun,
        operation: input.operation,
        root,
        target: target.relative,
        before_exists: before.exists,
        before_sha256: before.sha256,
        before_mode: before.mode,
        after_exists: after.exists,
        after_sha256: after.sha256,
        after_mode: after.mode,
        backup_path: quarantinePath ? relative(doctorDir, quarantinePath).split(sep).join('/') : backupPath ? relative(doctorDir, backupPath).split(sep).join('/') : null,
        ...(input.undoOf ? { undo_of: input.undoOf } : {}),
        ...(input.operation === 'hardlink' ? { source_sha256: sourceBytes ? sha256(sourceBytes) : null, source_mode: sourceMode } : {}),
        ...(lock.stale_owner ? { stale_lock_owner: lock.stale_owner } : {}),
      };
      await appendFile(logPath, `${JSON.stringify(action)}\n`, { mode: 0o600 });
      return { action, stale_lock_owner: lock.stale_owner ?? null };
    } catch (cause) {
      try {
        if (input.operation === 'chmod' && before.mode !== null) await chmod(target.absolute, before.mode);
        else if (input.operation === 'hardlink' && before.bytes) await atomicWrite(target.absolute, before.bytes, before.mode ?? 0o600, quarantineDir, `${id}.rollback`);
        else if (input.operation === 'write' || input.operation === 'restore') {
          const current = await snapshot(target.absolute);
          if (current.exists) {
            await mkdir(quarantineDir, { recursive: true, mode: 0o700 });
            await rename(target.absolute, join(quarantineDir, `unlogged-${id}`));
          }
        } else if (input.operation === 'quarantine' && quarantinePath) {
          await rename(quarantinePath, target.absolute);
        }
        await truncate(logPath, priorLogSize).catch(() => undefined);
      } catch { /* preserve the original failure; recovery files remain in quarantine */ }
      throw cause;
    }
  } finally {
    await lock.release();
  }
}
