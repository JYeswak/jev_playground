import { constants } from 'node:fs';
import { lstat, mkdir, open, readFile, rename, rmdir, unlink, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';

export const INSTALL_MANIFEST_VERSION = 2;
export const INSTALL_MANIFEST_MARKER = 'classifier.install.v2';

export type InstallManifestEntry = {
  target: string;
  path: string;
  sha256: string;
  marker: string;
  version: string;
  backup?: string;
  displaced?: string;
};

export type InstallManifest = {
  version: typeof INSTALL_MANIFEST_VERSION;
  entries: InstallManifestEntry[];
};

export type ManifestError = Error & { code: 'REFUSED' | 'IO' | 'RETRYABLE' };

function manifestError(message: string, code: ManifestError['code'], cause?: unknown): ManifestError {
  return Object.assign(new Error(message, cause === undefined ? undefined : { cause }), { code });
}

function isErrno(cause: unknown, code: string): boolean {
  return Boolean(cause && typeof cause === 'object' && 'code' in cause && cause.code === code);
}

function isSha256(value: string): boolean {
  if (value.length !== 64) return false;
  for (const character of value) {
    const code = character.charCodeAt(0);
    if (!((code >= 48 && code <= 57) || (code >= 97 && code <= 102))) return false;
  }
  return true;
}

function validateManifest(value: unknown): asserts value is InstallManifest {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw manifestError('invalid installer manifest object', 'REFUSED');
  const manifest = value as Partial<InstallManifest>;
  if (manifest.version !== INSTALL_MANIFEST_VERSION || !Array.isArray(manifest.entries)) {
    throw manifestError('invalid installer manifest version or entries', 'REFUSED');
  }
  const paths = new Set<string>();
  for (const entry of manifest.entries) {
    if (!entry || typeof entry !== 'object'
      || typeof entry.target !== 'string' || !entry.target
      || typeof entry.path !== 'string' || !entry.path
      || typeof entry.sha256 !== 'string' || !isSha256(entry.sha256)
      || typeof entry.marker !== 'string' || !entry.marker
      || typeof entry.version !== 'string' || !entry.version
      || (entry.backup !== undefined && typeof entry.backup !== 'string')
      || (entry.displaced !== undefined && typeof entry.displaced !== 'string')) {
      throw manifestError('invalid installer manifest entry', 'REFUSED');
    }
    if (paths.has(entry.path)) throw manifestError(`duplicate installer manifest path: ${entry.path}`, 'REFUSED');
    paths.add(entry.path);
  }
}

export async function readInstallManifest(path: string): Promise<InstallManifest | undefined> {
  let text: string;
  try {
    text = await readFile(path, 'utf8');
  } catch (cause) {
    if (isErrno(cause, 'ENOENT')) return undefined;
    throw manifestError(`cannot read installer manifest: ${path}`, 'IO', cause);
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (cause) {
    throw manifestError(`refusing to use invalid installer manifest: ${path}`, 'REFUSED', cause);
  }
  validateManifest(parsed);
  return parsed;
}

export async function writeInstallManifest(path: string, manifest: InstallManifest): Promise<boolean> {
  validateManifest(manifest);
  const target = resolve(path);
  const existing = await readInstallManifest(target);
  const contents = `${JSON.stringify(manifest, null, 2)}\n`;
  if (existing && await readFile(target, 'utf8') === contents) return false;

  try {
    const metadata = await lstat(target);
    if (!metadata.isFile()) throw manifestError(`refusing to replace non-file installer manifest: ${target}`, 'REFUSED');
  } catch (cause) {
    if (!isErrno(cause, 'ENOENT')) throw cause;
  }

  try {
    await mkdir(dirname(target), { recursive: true });
  } catch (cause) {
    throw manifestError(`cannot create installer manifest directory: ${dirname(target)}`, 'IO', cause);
  }

  const temporary = `${target}.${process.pid}.${randomUUID()}.tmp`;
  let handle;
  try {
    handle = await open(temporary, constants.O_CREAT | constants.O_EXCL | constants.O_WRONLY, 0o600);
    await handle.writeFile(contents, 'utf8');
    await handle.sync();
    await handle.close();
    handle = undefined;
    await rename(temporary, target);
  } catch (cause) {
    await handle?.close().catch(() => undefined);
    await unlink(temporary).catch(() => undefined);
    if (cause && typeof cause === 'object' && 'code' in cause && cause.code === 'REFUSED') throw cause;
    throw manifestError(`cannot atomically write installer manifest: ${target}`, 'IO', cause);
  }
  return true;
}
function pidIsAlive(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (cause) {
    return !isErrno(cause, 'ESRCH');
  }
}

async function readLockPid(path: string): Promise<number | undefined> {
  try {
    const text = await readFile(resolve(path, 'pid'), 'utf8');
    const pid = Number(text.split('\n', 1)[0].trim());
    return Number.isSafeInteger(pid) && pid > 0 ? pid : undefined;
  } catch (cause) {
    if (isErrno(cause, 'ENOENT')) return undefined;
    throw manifestError(`cannot read installer lock owner: ${path}`, 'IO', cause);
  }
}

async function releaseDirectoryLock(path: string, token: string): Promise<void> {
  const pidPath = resolve(path, 'pid');
  let contents: string;
  try {
    contents = await readFile(pidPath, 'utf8');
  } catch (cause) {
    throw manifestError(`installer lock ownership changed: ${path}`, 'REFUSED', cause);
  }
  if (contents !== `${process.pid}\n${token}\n`) throw manifestError(`installer lock ownership changed: ${path}`, 'REFUSED');
  await unlink(pidPath);
  await rmdir(path);
}

async function reclaimStaleLock(path: string, ownerPid: number): Promise<boolean> {
  const reclaimPath = `${path}.reclaim`;
  try {
    await mkdir(reclaimPath);
  } catch (cause) {
    if (isErrno(cause, 'EEXIST')) throw manifestError(`installer lock recovery already in progress: ${path}`, 'RETRYABLE');
    throw manifestError(`cannot create installer lock recovery guard: ${reclaimPath}`, 'IO', cause);
  }

  const token = randomUUID();
  try {
    await writeFile(resolve(reclaimPath, 'pid'), `${process.pid}\n${token}\n`, { flag: 'wx', mode: 0o600 });
    const currentPid = await readLockPid(path);
    if (currentPid !== ownerPid || pidIsAlive(currentPid)) return false;
    await unlink(resolve(path, 'pid'));
    await rmdir(path);
    return true;
  } catch (cause) {
    if (isErrno(cause, 'ENOENT')) return false;
    if (cause && typeof cause === 'object' && 'code' in cause && (cause.code === 'REFUSED' || cause.code === 'RETRYABLE' || cause.code === 'IO')) throw cause;
    throw manifestError(`cannot recover stale installer lock: ${path}`, 'IO', cause);
  } finally {
    await releaseDirectoryLock(reclaimPath, token).catch((cause) => {
      if (!isErrno(cause, 'ENOENT')) throw cause;
    });
  }
}

export type InstallLock = { release: () => Promise<void> };

export async function acquireInstallLock(path: string): Promise<InstallLock> {
  const lock = resolve(path);
  try {
    await mkdir(dirname(lock), { recursive: true });
  } catch (cause) {
    throw manifestError(`cannot create installer lock parent: ${dirname(lock)}`, 'IO', cause);
  }

  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      await mkdir(lock);
    } catch (cause) {
      if (!isErrno(cause, 'EEXIST')) throw manifestError(`cannot create installer lock: ${lock}`, 'IO', cause);
      const owner = await readLockPid(lock);
      if (owner === undefined) throw manifestError(`installer lock has no valid owner: ${lock}`, 'REFUSED');
      if (pidIsAlive(owner)) throw manifestError(`installer is already running (pid ${owner})`, 'RETRYABLE');
      if (await reclaimStaleLock(lock, owner)) continue;
      continue;
    }

    const token = randomUUID();
    try {
      await writeFile(resolve(lock, 'pid'), `${process.pid}\n${token}\n`, { flag: 'wx', mode: 0o600 });
    } catch (cause) {
      await rmdir(lock).catch(() => undefined);
      throw manifestError(`cannot record installer lock owner: ${lock}`, 'IO', cause);
    }
    let released = false;
    return {
      async release() {
        if (released) return;
        await releaseDirectoryLock(lock, token);
        released = true;
      },
    };
  }
  throw manifestError(`could not acquire installer lock: ${lock}`, 'RETRYABLE');
}
