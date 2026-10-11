// CLI target (T5): versions dir, `current` symlink, bin link, foreign-bin
// conflict, --take-over-bin with restore, --rollback across versions.
// All paths derive from an explicit home; nothing reads process.env.
// Writes are byte-compared before touching the filesystem so re-runs and
// refusals leave bytes and mtimes alone.

import { createHash } from "node:crypto";
import { chmod, lstat, mkdir, readFile, readlink, rm, symlink, unlink, writeFile } from "node:fs/promises";
import { dirname, join, resolve, sep } from "node:path";
import { EXIT_CODES } from "../families/registry.js";

export type CliTargetError = Error & { code: "USAGE" | "IO" };

function errorMessage(cause: unknown): string {
  if (cause instanceof Error) return cause.message;
  return String(cause);
}

function targetError(message: string, code: CliTargetError["code"]): CliTargetError {
  return Object.assign(new Error(message), { code });
}

function sha256Hex(bytes: Uint8Array): string {
  return createHash("sha256").update(bytes).digest("hex");
}

async function pathKind(path: string): Promise<"missing" | "file" | "symlink" | "dir" | "other"> {
  try {
    const st = await lstat(path);
    if (st.isSymbolicLink()) return "symlink";
    if (st.isFile()) return "file";
    if (st.isDirectory()) return "dir";
    return "other";
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return "missing";
    }
    throw targetError(`cannot stat ${path}: ${errorMessage(error)}`, "IO");
  }
}

async function writeBytesIfChanged(path: string, bytes: Uint8Array, writes: string[]): Promise<void> {
  let current: Buffer | undefined;
  try {
    current = await readFile(path);
  } catch (error) {
    if (!error || typeof error !== "object" || !("code" in error) || error.code !== "ENOENT") {
      throw targetError(`cannot read ${path}: ${errorMessage(error)}`, "IO");
    }
  }
  if (current !== undefined && sha256Hex(current) === sha256Hex(bytes)) return;
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, bytes);
  writes.push(path);
}

async function writeTextIfChanged(path: string, text: string, writes: string[]): Promise<void> {
  await writeBytesIfChanged(path, Buffer.from(text, "utf8"), writes);
}

function checkSegment(value: string, what: string): void {
  if (value === "" || value === "." || value === ".." || value.includes("/") || value.includes("\\") || value.includes("\0")) {
    throw targetError(`refusing unsafe ${what}: ${value}`, "USAGE");
  }
}

export type CliLayout = {
  base: string;
  versionsBase: string;
  versionDir: string;
  versionBin: string;
  currentLink: string;
  binLink: string;
  stateFile: string;
  displacedBackup: string;
};

export function cliLayout(home: string, version: string, binName: string): CliLayout {
  checkSegment(version, "version");
  checkSegment(binName, "bin name");
  const base = join(home, ".local", "share", "classifier");
  const versionDir = join(base, "versions", version);
  return {
    base,
    versionsBase: join(base, "versions"),
    versionDir,
    versionBin: join(versionDir, "bin", binName),
    currentLink: join(base, "current"),
    binLink: join(home, ".local", "bin", binName),
    stateFile: join(base, "install-state.json"),
    displacedBackup: join(base, `displaced-${binName}.bak`),
  };
}

export type CliState = {
  versions: string[];
  current: string | null;
  displaced: { bin: string; backup: string } | null;
};

async function readState(stateFile: string): Promise<CliState> {
  let raw: Buffer;
  try {
    raw = await readFile(stateFile);
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return { versions: [], current: null, displaced: null };
    }
    throw targetError(`cannot read ${stateFile}: ${errorMessage(error)}`, "IO");
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw.toString("utf8"));
  } catch {
    throw targetError(`install state is not JSON: ${stateFile}`, "IO");
  }
  if (!parsed || typeof parsed !== "object" || !("versions" in parsed) || !Array.isArray(parsed.versions)) {
    throw targetError(`install state is corrupt: ${stateFile}`, "IO");
  }
  const versions = parsed.versions.filter((v): v is string => typeof v === "string");
  const current = "current" in parsed && typeof parsed.current === "string" ? parsed.current : null;
  const displacedRaw: unknown = "displaced" in parsed ? parsed.displaced : null;
  const displaced =
    displacedRaw !== null &&
    typeof displacedRaw === "object" &&
    "bin" in displacedRaw &&
    typeof displacedRaw.bin === "string" &&
    "backup" in displacedRaw &&
    typeof displacedRaw.backup === "string"
      ? { bin: displacedRaw.bin, backup: displacedRaw.backup }
      : null;
  return { versions, current, displaced };
}

export type CliInstallInput = {
  home: string;
  version: string;
  binBytes: Uint8Array;
  binName?: string;
  takeOverBin?: boolean;
};

export type CliResult = {
  status: "installed" | "already" | "conflict";
  exit: number;
  writes: string[];
  current: string | null;
};

async function pointLink(link: string, target: string, writes: string[]): Promise<void> {
  const kind = await pathKind(link);
  if (kind === "symlink") {
    const existing = await readlink(link);
    if (resolve(dirname(link), existing) === target) return;
    await unlink(link);
  } else if (kind !== "missing") {
    throw targetError(`cannot link over non-symlink: ${link}`, "IO");
  }
  await mkdir(dirname(link), { recursive: true });
  await symlink(target, link);
  writes.push(link);
}

export async function installCli(input: CliInstallInput): Promise<CliResult> {
  const binName = input.binName ?? "classifier";
  const layout = cliLayout(input.home, input.version, binName);
  const state = await readState(layout.stateFile);
  const writes: string[] = [];

  const binKind = await pathKind(layout.binLink);
  if (binKind !== "missing") {
    let owned = false;
    if (binKind === "symlink") {
      const resolved = resolve(dirname(layout.binLink), await readlink(layout.binLink));
      owned =
        resolved === layout.versionBin ||
        (resolved.startsWith(layout.versionsBase + sep) && state.versions.some((version) => resolved.startsWith(join(layout.versionsBase, version) + sep)));
    }
    if (!owned) {
      if (binKind === "dir") {
        return { status: "conflict", exit: EXIT_CODES.REFUSED_UNSAFE, writes, current: state.current };
      }
      if (!input.takeOverBin) {
        return { status: "conflict", exit: EXIT_CODES.REFUSED_UNSAFE, writes, current: state.current };
      }
      if (state.displaced === null) {
        const foreign = await readFile(layout.binLink);
        await writeBytesIfChanged(layout.displacedBackup, foreign, writes);
        state.displaced = { bin: layout.binLink, backup: layout.displacedBackup };
      }
      if (binKind !== "symlink") {
        await unlink(layout.binLink);
        writes.push(layout.binLink);
      }
    }
  }

  if (
    state.current === input.version &&
    state.versions.includes(input.version) &&
    (await pathKind(layout.versionBin)) === "file"
  ) {
    const onDisk = await readFile(layout.versionBin);
    if (sha256Hex(onDisk) === sha256Hex(input.binBytes)) {
      const currentTarget =
        (await pathKind(layout.currentLink)) === "symlink"
          ? resolve(dirname(layout.currentLink), await readlink(layout.currentLink))
          : undefined;
      const binTarget =
        (await pathKind(layout.binLink)) === "symlink"
          ? resolve(dirname(layout.binLink), await readlink(layout.binLink))
          : undefined;
      if (currentTarget === layout.versionDir && binTarget === layout.versionBin) {
        return { status: "already", exit: EXIT_CODES.OK, writes, current: state.current };
      }
    }
  }

  await writeBytesIfChanged(layout.versionBin, input.binBytes, writes);
  try {
    await chmod(layout.versionBin, 0o755);
  } catch (error) {
    throw targetError(`cannot chmod ${layout.versionBin}: ${errorMessage(error)}`, "IO");
  }
  await pointLink(layout.currentLink, layout.versionDir, writes);
  await pointLink(layout.binLink, layout.versionBin, writes);
  if (!state.versions.includes(input.version)) state.versions.push(input.version);
  state.current = input.version;
  await writeTextIfChanged(
    layout.stateFile,
    JSON.stringify({ versions: state.versions, current: state.current, displaced: state.displaced }, null, 2) + "\n",
    writes,
  );
  return { status: "installed", exit: EXIT_CODES.OK, writes, current: state.current };
}

export type CliRollbackInput = {
  home: string;
  binName?: string;
};

export type CliRollbackResult = {
  status: "rolled-back" | "no-previous-version";
  exit: number;
  writes: string[];
  current: string | null;
};

export async function rollbackCli(input: CliRollbackInput): Promise<CliRollbackResult> {
  const binName = input.binName ?? "classifier";
  const state = await readState(join(input.home, ".local", "share", "classifier", "install-state.json"));
  const writes: string[] = [];
  const previous = [...state.versions].reverse().find((version) => version !== state.current);
  if (state.current === null || previous === undefined) {
    return { status: "no-previous-version", exit: EXIT_CODES.REFUSED_UNSAFE, writes, current: state.current };
  }
  const layout = cliLayout(input.home, previous, binName);
  await pointLink(layout.currentLink, layout.versionDir, writes);
  await pointLink(layout.binLink, layout.versionBin, writes);
  state.current = previous;
  await writeTextIfChanged(
    layout.stateFile,
    JSON.stringify({ versions: state.versions, current: state.current, displaced: state.displaced }, null, 2) + "\n",
    writes,
  );
  return { status: "rolled-back", exit: EXIT_CODES.OK, writes, current: state.current };
}

export type CliUninstallInput = {
  home: string;
  binName?: string;
  apply?: boolean;
};

export type CliUninstallResult = {
  status: "dry-run" | "removed";
  exit: number;
  writes: string[];
  wouldRemove: string[];
  restored: string | null;
};

export async function uninstallCli(input: CliUninstallInput): Promise<CliUninstallResult> {
  const binName = input.binName ?? "classifier";
  const base = join(input.home, ".local", "share", "classifier");
  const stateFile = join(base, "install-state.json");
  const state = await readState(stateFile);
  const layout = cliLayout(input.home, state.current ?? "none", binName);
  const owned: string[] = [];
  const binKind = await pathKind(layout.binLink);
  if (binKind === "symlink") {
    const resolved = resolve(dirname(layout.binLink), await readlink(layout.binLink));
    const underBase = resolved === layout.versionBin || resolved.startsWith(base + "/");
    if (underBase) owned.push(layout.binLink);
  }
  if ((await pathKind(layout.currentLink)) === "symlink") owned.push(layout.currentLink);
  for (const version of state.versions) {
    const dir = join(base, "versions", version);
    if ((await pathKind(dir)) === "dir") owned.push(dir);
  }
  if ((await pathKind(stateFile)) !== "missing") owned.push(stateFile);
  if (input.apply !== true) {
    return { status: "dry-run", exit: EXIT_CODES.OK, writes: [], wouldRemove: owned, restored: null };
  }
  const writes: string[] = [];
  for (const path of [layout.binLink, layout.currentLink]) {
    if (owned.includes(path)) {
      await unlink(path);
      writes.push(path);
    }
  }
  for (const path of owned) {
    if (path === layout.binLink || path === layout.currentLink) continue;
    await rm(path, { recursive: true, force: true });
    writes.push(path);
  }
  let restored: string | null = null;
  if (state.displaced !== null) {
    const backup = await readFile(state.displaced.backup);
    await writeBytesIfChanged(state.displaced.bin, backup, writes);
    restored = state.displaced.bin;
  }
  return { status: "removed", exit: EXIT_CODES.OK, writes, wouldRemove: owned, restored };
}
