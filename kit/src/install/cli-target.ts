// CLI target (T5): versions dir, `current` symlink, bin link, foreign-bin
// conflict, --take-over-bin with restore, --rollback across versions.
// All paths derive from an explicit home; nothing reads process.env.
// Writes are byte-compared before touching the filesystem so re-runs and
// refusals leave bytes and mtimes alone.

import { createHash } from "node:crypto";
import { chmod, lstat, mkdir, readFile, readdir, readlink, realpath, rm, symlink, unlink, writeFile } from "node:fs/promises";
import { execFile } from "node:child_process";
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { INSTALL_MANIFEST_MARKER, INSTALL_MANIFEST_VERSION, readInstallManifest, writeInstallManifest, type InstallManifest } from "./manifest.js";
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
  try {
    for (const version of versions) checkSegment(version, "state version");
    if (current !== null) checkSegment(current, "current state version");
  } catch {
    throw targetError(`install state contains an unsafe version path: ${stateFile}`, "IO");
  }
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
  packageDir: string;
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

const CLI_PAYLOAD_MANIFEST = ".classifier-install.json";

type PayloadFile = { path: string; bytes: Buffer; mode: number };
type CliPayload = { entry: string; files: PayloadFile[]; manifest: InstallManifest };

function packagePath(path: string): string {
  const clean = path.startsWith("./") ? path.slice(2) : path;
  if (!clean || isAbsolute(clean) || clean.includes("\\") || clean.includes("\0")
    || clean.split("/").some((part) => part === ".." || part === "" || part === ".")
    || clean.includes("*") || clean.includes("?")) {
    throw targetError(`unsafe prepared-package path: ${path}`, "USAGE");
  }
  return clean;
}

async function packageJson(path: string): Promise<Record<string, unknown>> {
  let value: unknown;
  try {
    if (await pathKind(path) !== "file") {
      throw targetError(`prepared package metadata is not a regular file: ${path}`, "USAGE");
    }
    value = JSON.parse(await readFile(path, "utf8"));
  } catch (cause) {
    throw targetError(`cannot read prepared package metadata ${path}: ${errorMessage(cause)}`, "USAGE");
  }
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw targetError(`invalid prepared package metadata: ${path}`, "USAGE");
  }
  return value as Record<string, unknown>;
}

async function preparePayload(input: CliInstallInput): Promise<CliPayload> {
  if (typeof input.packageDir !== "string" || !input.packageDir) {
    throw targetError("CLI installation requires a complete prepared package directory", "USAGE");
  }
  let root: string;
  try {
    root = await realpath(resolve(input.packageDir));
  } catch (cause) {
    throw targetError(`prepared package directory is unavailable: ${errorMessage(cause)}`, "USAGE");
  }
  const pkg = await packageJson(join(root, "package.json"));
  if (pkg.version !== input.version || !Array.isArray(pkg.files) || pkg.files.length === 0
    || pkg.bin === null || typeof pkg.bin !== "object" || Array.isArray(pkg.bin)
    || !("classifier" in pkg.bin) || typeof pkg.bin.classifier !== "string") {
    throw targetError("prepared classifier package has no matching version, file inventory, or classifier entry", "USAGE");
  }
  const entry = packagePath(pkg.bin.classifier);
  const alias = `bin/${input.binName ?? "classifier"}`;
  const files = new Map<string, PayloadFile>();
  const collect = async (path: string): Promise<void> => {
    const rel = packagePath(relative(root, path).split(sep).join("/"));
    if (rel === CLI_PAYLOAD_MANIFEST || rel.startsWith(CLI_PAYLOAD_MANIFEST + "/")) {
      throw targetError(`prepared package asset uses the reserved installer manifest path: ${rel}`, "USAGE");
    }
    if (files.has(rel)) return;
    let metadata;
    try {
      metadata = await lstat(path);
      if (!(await realpath(path)).startsWith(root + sep)) {
        throw targetError(`prepared package asset escapes its source root: ${rel}`, "USAGE");
      }
    } catch (cause) {
      throw targetError(`prepared package asset is unavailable: ${rel}: ${errorMessage(cause)}`, "USAGE");
    }
    if (metadata.isSymbolicLink()) {
      // A previously installed package has this derived, wholly internal alias.
      if (rel === alias && resolve(dirname(path), await readlink(path)) === join(root, entry)) return;
      throw targetError(`prepared package asset is a symlink: ${rel}`, "USAGE");
    }
    if (metadata.isDirectory()) {
      for (const name of (await readdir(path)).sort()) await collect(join(path, name));
      return;
    }
    if (!metadata.isFile()) throw targetError(`prepared package asset is not a file: ${rel}`, "USAGE");
    files.set(rel, { path: rel, bytes: await readFile(path), mode: metadata.mode & 0o777 });
  };
  await collect(join(root, "package.json"));
  for (const path of pkg.files) {
    if (typeof path !== "string") throw targetError("prepared package file inventory must contain paths", "USAGE");
    await collect(join(root, packagePath(path)));
  }
  if (!files.has(entry) || (alias !== entry && files.has(alias))) {
    throw targetError("prepared package is missing its classifier entry or conflicts with the installed alias", "USAGE");
  }
  const visited = new Set<string>();
  const dependencies = async (metadata: Record<string, unknown>, from: string): Promise<void> => {
    const declared = metadata.dependencies;
    if (declared === undefined) return;
    if (declared === null || typeof declared !== "object" || Array.isArray(declared)) {
      throw targetError("invalid prepared runtime dependency inventory", "USAGE");
    }
    for (const name of Object.keys(declared).sort()) {
      packagePath(name);
      let parent = from;
      let found: string | undefined;
      while (parent === root || parent.startsWith(root + sep)) {
        const candidate = join(parent, "node_modules", name);
        if (await pathKind(candidate) === "dir") { found = candidate; break; }
        if (parent === root) break;
        parent = dirname(parent);
      }
      if (found === undefined) throw targetError(`prepared runtime dependency is missing: ${name}`, "USAGE");
      if (!(await realpath(found)).startsWith(root + sep)) {
        throw targetError(`prepared runtime dependency escapes its source root: ${name}`, "USAGE");
      }
      if (visited.has(found)) continue;
      visited.add(found);
      const dependency = await packageJson(join(found, "package.json"));
      if (dependency.name !== name) throw targetError(`prepared runtime dependency identity differs: ${name}`, "USAGE");
      await collect(found);
      await dependencies(dependency, found);
      // Dependency names come from the prepared package; load their actual runtime-selected ESM entries.
      await new Promise<void>((accept, reject) => {
        execFile(process.execPath, ["--input-type=module", "--eval", "await import(process.argv[1])", name], {
          cwd: from, env: { HOME: input.home }, encoding: "utf8", timeout: 10000, maxBuffer: 1024 * 1024,
        }, (cause, _stdout, stderr) => {
          if (cause) {
            reject(targetError(`prepared runtime dependency cannot load: ${name}: ${stderr.trim() || errorMessage(cause)}`, "USAGE"));
          } else accept();
        });
      });
    }
  };
  await dependencies(pkg, root);
  try {
    await new Promise<void>((accept, reject) => {
      execFile(process.execPath, [join(root, entry), "--version"], {
        cwd: root, env: { HOME: input.home }, encoding: "utf8", timeout: 10000, maxBuffer: 1024 * 1024,
      }, (cause, stdout, stderr) => {
        if (cause || stdout !== `classifier ${input.version}\n`) {
          reject(targetError(`prepared classifier cannot run its declared version: ${stderr.trim() || errorMessage(cause)}`, "USAGE"));
        } else accept();
      });
    });
  } catch (cause) {
    if (cause instanceof Error && "code" in cause && cause.code === "USAGE") throw cause;
    throw targetError(`cannot verify prepared classifier: ${errorMessage(cause)}`, "USAGE");
  }
  for (const file of files.values()) {
    if (!(await readFile(join(root, file.path))).equals(file.bytes)) {
      throw targetError(`prepared package changed during verification: ${file.path}`, "USAGE");
    }
  }
  const ordered = [...files.values()].sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  return {
    entry, files: ordered,
    manifest: {
      version: INSTALL_MANIFEST_VERSION,
      entries: ordered.map((file) => ({
        target: "cli", path: file.path, sha256: sha256Hex(file.bytes),
        marker: INSTALL_MANIFEST_MARKER, version: input.version,
      })),
    },
  };
}

async function payloadMatches(directory: string, manifest: InstallManifest, entry: string, alias: string): Promise<boolean> {
  try {
    const stored = await readInstallManifest(join(directory, CLI_PAYLOAD_MANIFEST));
    if (!stored || JSON.stringify(stored) !== JSON.stringify(manifest)) return false;
    const expected = new Set([CLI_PAYLOAD_MANIFEST, ...manifest.entries.map((file) => file.path)]);
    if (alias !== entry) expected.add(alias);
    const observed = new Set<string>();
    const walk = async (path: string): Promise<void> => {
      for (const name of await readdir(path)) {
        const full = join(path, name);
        const metadata = await lstat(full);
        if (metadata.isDirectory()) await walk(full);
        else observed.add(relative(directory, full).split(sep).join("/"));
      }
    };
    await walk(directory);
    if (observed.size !== expected.size || [...observed].some((path) => !expected.has(path))) return false;
    for (const file of manifest.entries) {
      const path = join(directory, packagePath(file.path));
      if (await pathKind(path) !== "file" || sha256Hex(await readFile(path)) !== file.sha256) return false;
    }
    const executable = join(directory, entry);
    if (((await lstat(executable)).mode & 0o111) === 0) return false;
    return alias === entry || (await pathKind(join(directory, alias)) === "symlink"
      && resolve(dirname(join(directory, alias)), await readlink(join(directory, alias))) === executable);
  } catch {
    return false;
  }
}

export async function installCli(input: CliInstallInput): Promise<CliResult> {
  const binName = input.binName ?? "classifier";
  const layout = cliLayout(input.home, input.version, binName);
  // Read and execute the prepared artifact before touching any consumer state.
  const payload = await preparePayload(input);
  const state = await readState(layout.stateFile);
  const writes: string[] = [];
  const versionKind = await pathKind(layout.versionDir);
  if (versionKind !== "missing" && (!state.versions.includes(input.version)
    || !await payloadMatches(layout.versionDir, payload.manifest, payload.entry, `bin/${binName}`))) {
    return { status: "conflict", exit: EXIT_CODES.REFUSED_UNSAFE, writes, current: state.current };
  }

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

  if (versionKind === "missing") {
    for (const file of payload.files) {
      const destination = join(layout.versionDir, file.path);
      await writeBytesIfChanged(destination, file.bytes, writes);
      await chmod(destination, file.mode);
    }
    await chmod(join(layout.versionDir, payload.entry), 0o755);
    if (layout.versionBin !== join(layout.versionDir, payload.entry)) {
      await pointLink(layout.versionBin, join(layout.versionDir, payload.entry), writes);
    }
    if (await writeInstallManifest(join(layout.versionDir, CLI_PAYLOAD_MANIFEST), payload.manifest)) {
      writes.push(join(layout.versionDir, CLI_PAYLOAD_MANIFEST));
    }
  }
  if (state.current === input.version
    && await pathKind(layout.currentLink) === "symlink"
    && resolve(dirname(layout.currentLink), await readlink(layout.currentLink)) === layout.versionDir
    && await pathKind(layout.binLink) === "symlink"
    && resolve(dirname(layout.binLink), await readlink(layout.binLink)) === layout.versionBin
    && writes.length === 0) {
    return { status: "already", exit: EXIT_CODES.OK, writes, current: state.current };
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
  status: "rolled-back" | "no-previous-version" | "conflict";
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
  let intact = false;
  try {
    const manifest = await readInstallManifest(join(layout.versionDir, CLI_PAYLOAD_MANIFEST));
    const pkg = await packageJson(join(layout.versionDir, "package.json"));
    if (manifest && manifest.entries.every((file) => file.target === "cli"
      && file.marker === INSTALL_MANIFEST_MARKER && file.version === previous)
      && pkg.version === previous && pkg.bin !== null && typeof pkg.bin === "object"
      && "classifier" in pkg.bin && typeof pkg.bin.classifier === "string") {
      intact = await payloadMatches(layout.versionDir, manifest, packagePath(pkg.bin.classifier), `bin/${binName}`);
    }
  } catch {
    intact = false;
  }
  if (!intact) {
    return { status: "conflict", exit: EXIT_CODES.REFUSED_UNSAFE, writes, current: state.current };
  }
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
  status: "dry-run" | "removed" | "conflict";
  exit: number;
  writes: string[];
  wouldRemove: string[];
  restored: string | null;
};

type CliRemovalPlan =
  | { status: "conflict" }
  | { status: "ready"; layout: CliLayout; owned: string[]; backup: Buffer | undefined };

async function planCliRemoval(input: CliUninstallInput): Promise<CliRemovalPlan> {
  const binName = input.binName ?? "classifier";
  const base = join(input.home, ".local", "share", "classifier");
  const stateFile = join(base, "install-state.json");
  const state = await readState(stateFile);
  const layout = cliLayout(input.home, state.current ?? "none", binName);
  if (state.displaced && (resolve(state.displaced.bin) !== resolve(layout.binLink)
    || resolve(state.displaced.backup) !== resolve(layout.displacedBackup))) {
    return { status: "conflict" };
  }
  const owned: string[] = [];
  const binKind = await pathKind(layout.binLink);
  if (binKind === "symlink") {
    const target = resolve(dirname(layout.binLink), await readlink(layout.binLink));
    if (target === layout.versionBin || target.startsWith(base + "/")) owned.push(layout.binLink);
  }
  if (await pathKind(layout.currentLink) === "symlink") owned.push(layout.currentLink);
  for (const version of state.versions) {
    const directory = join(base, "versions", version);
    if (await pathKind(directory) === "dir") owned.push(directory);
  }
  if (await pathKind(stateFile) !== "missing") owned.push(stateFile);
  if (input.apply !== true || state.displaced === null) {
    return { status: "ready", layout, owned, backup: undefined };
  }
  if (binKind !== "missing" && !owned.includes(layout.binLink)) return { status: "conflict" };
  return { status: "ready", layout, owned, backup: await readFile(layout.displacedBackup) };
}

export async function uninstallCli(input: CliUninstallInput): Promise<CliUninstallResult> {
  const plan = await planCliRemoval(input);
  if (plan.status === "conflict") {
    return { status: "conflict", exit: EXIT_CODES.REFUSED_UNSAFE, writes: [], wouldRemove: [], restored: null };
  }
  const { layout, owned, backup } = plan;
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
  if (backup !== undefined) {
    await writeBytesIfChanged(layout.binLink, backup, writes);
    restored = layout.binLink;
  }
  return { status: "removed", exit: EXIT_CODES.OK, writes, wouldRemove: owned, restored };
}
