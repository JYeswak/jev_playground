import { appendFile, lstat, mkdir, readFile, rename, truncate } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';

type LockError = Error & { code: 'RETRYABLE' | 'REFUSED' | 'IO' };
type LockOwner = { pid: number; started_at: string };

function lockError(message: string, code: LockError['code'], cause?: unknown): LockError {
  return Object.assign(new Error(message, cause === undefined ? undefined : { cause }), { code });
}

function isErrno(cause: unknown, code: string): boolean {
  return Boolean(cause && typeof cause === 'object' && 'code' in cause && cause.code === code);
}

function pidIsAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (cause) {
    return !isErrno(cause, 'ESRCH');
  }
}

async function readOwner(path: string): Promise<LockOwner | null> {
  let directoryMetadata;
  try { directoryMetadata = await lstat(path); }
  catch (cause) {
    if (isErrno(cause, 'ENOENT')) return null;
    throw lockError(`cannot inspect doctor lock owner directory: ${path}`, 'IO', cause);
  }
  if (!directoryMetadata.isDirectory() || directoryMetadata.isSymbolicLink() || (directoryMetadata.mode & 0o077) !== 0) {
    throw lockError(`doctor lock owner directory is unsafe: ${path}`, 'REFUSED');
  }
  const ownerPath = join(path, 'owner');
  let ownerMetadata;
  let contents: string;
  try {
    ownerMetadata = await lstat(ownerPath);
    if (!ownerMetadata.isFile() || ownerMetadata.isSymbolicLink() || (ownerMetadata.mode & 0o077) !== 0) {
      throw lockError(`doctor lock owner file is unsafe: ${ownerPath}`, 'REFUSED');
    }
    contents = await readFile(ownerPath, 'utf8');
  } catch (cause) {
    if (isErrno(cause, 'ENOENT')) return null;
    if (cause && typeof cause === 'object' && 'code' in cause && cause.code === 'REFUSED') throw cause;
    throw lockError(`cannot read doctor lock owner: ${path}`, 'IO', cause);
  }
  if (!contents.trim()) return null;
  let parsed: unknown;
  try { parsed = JSON.parse(contents); } catch (cause) {
    throw lockError(`doctor lock owner is malformed: ${path}`, 'REFUSED', cause);
  }
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw lockError(`doctor lock owner is invalid: ${path}`, 'REFUSED');
  }
  const owner = parsed as LockOwner;
  if (!Number.isSafeInteger(owner.pid) || owner.pid <= 0 || typeof owner.started_at !== 'string' || Number.isNaN(Date.parse(owner.started_at))) {
    throw lockError(`doctor lock owner is invalid: ${path}`, 'REFUSED');
  }
  return owner;
}

async function exists(path: string): Promise<boolean> {
  try { await lstat(path); return true; }
  catch (cause) {
    if (isErrno(cause, 'ENOENT')) return false;
    throw cause;
  }
}

export type DoctorLock = {
  owner: LockOwner;
  stale_owner?: LockOwner;
  release: () => Promise<void>;
};

export async function acquireDoctorLock(directory: string): Promise<DoctorLock> {
  const root = resolve(directory);
  try {
    await mkdir(root, { recursive: true, mode: 0o700 });
    const metadata = await lstat(root);
    if (!metadata.isDirectory() || metadata.isSymbolicLink() || (metadata.mode & 0o077) !== 0) throw lockError(`doctor lock directory is unsafe: ${root}`, 'REFUSED');
  } catch (cause) {
    if (cause && typeof cause === 'object' && 'code' in cause && cause.code === 'REFUSED') throw cause;
    throw lockError(`cannot prepare doctor lock directory: ${root}`, 'IO', cause);
  }

  const free = join(root, 'lock.free');
  const held = join(root, 'lock.held');
  let staleOwner: LockOwner | undefined;
  for (let attempt = 0; attempt < 4; attempt += 1) {
    if (await exists(held)) {
      const current = await readOwner(held);
      if (!current) throw lockError('doctor repair lock is being acquired (owner not recorded yet)', 'RETRYABLE');
      if (pidIsAlive(current.pid)) throw lockError(`doctor repair is already running (pid ${current.pid})`, 'RETRYABLE');
      try {
        await rename(held, join(root, `lock.stale.${current.pid}.${randomUUID()}`));
        staleOwner = current;
      } catch (cause) {
        if (!isErrno(cause, 'ENOENT')) throw lockError(`cannot quarantine stale doctor lock: ${held}`, 'IO', cause);
      }
      continue;
    }

    if (!(await exists(free))) {
      try {
        await mkdir(free, { mode: 0o700 });
        await appendFile(join(free, 'owner'), '', { mode: 0o600 });
      } catch (cause) {
        if (!isErrno(cause, 'EEXIST')) throw lockError(`cannot initialize doctor lock: ${free}`, 'IO', cause);
      }
    }

    try {
      await rename(free, held);
    } catch (cause) {
      if (isErrno(cause, 'ENOENT') || isErrno(cause, 'EEXIST') || isErrno(cause, 'ENOTEMPTY')) continue;
      throw lockError(`cannot acquire doctor lock: ${held}`, 'IO', cause);
    }

    const owner: LockOwner = { pid: process.pid, started_at: new Date().toISOString() };
    const ownerText = `${JSON.stringify(owner)}\n`;
    try { await appendFile(join(held, 'owner'), ownerText, { mode: 0o600 }); }
    catch (cause) {
      try { await rename(held, free); } catch { /* preserve the lock path for recovery */ }
      throw lockError(`cannot record doctor lock owner: ${held}`, 'IO', cause);
    }

    let released = false;
    return {
      owner,
      ...(staleOwner ? { stale_owner: staleOwner } : {}),
      async release() {
        if (released) return;
        const ownerPath = join(held, 'owner');
        let currentText: string;
        try { currentText = await readFile(ownerPath, 'utf8'); }
        catch (cause) { throw lockError(`doctor lock ownership changed: ${held}`, 'REFUSED', cause); }
        if (currentText !== ownerText) throw lockError(`doctor lock ownership changed: ${held}`, 'REFUSED');
        if (await exists(free)) {
          const candidate = await readOwner(free);
          if (candidate) throw lockError(`unexpected doctor free lock owner: ${candidate.pid}`, 'REFUSED');
          await rename(free, join(root, `lock.free.raced.${randomUUID()}`));
        }
        await truncate(ownerPath, 0);
        try { await rename(held, free); }
        catch (cause) { throw lockError(`cannot release doctor lock: ${held}`, 'IO', cause); }
        released = true;
      },
    };
  }
  throw lockError(staleOwner
    ? `doctor repair lock recovery raced; stale owner pid ${staleOwner.pid}`
    : 'doctor repair lock acquisition raced', 'RETRYABLE');
}
