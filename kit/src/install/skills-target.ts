// Skill-store target (T12): copy a packaged skill tree into one store dir,
// tracked by a marker file. An existing store with unmarked files is a
// conflict (exit 4) and stays byte-identical. Uninstall removes only marked
// files. Symlinks in the source tree are refused, never followed. All paths
// are explicit; nothing reads process.env.

import { lstat, mkdir, readdir, readFile, rmdir, unlink, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, join, relative, resolve, sep } from "node:path";
import { EXIT_CODES } from "../families/registry.js";

export const SKILLS_MARKER = ".classifier-skills.json";

export type SkillsTargetError = Error & { code: "USAGE" | "IO" };

function skillsError(message: string, code: SkillsTargetError["code"]): SkillsTargetError {
  return Object.assign(new Error(message), { code });
}

function describeCause(cause: unknown): string {
  return cause instanceof Error ? cause.message : String(cause);
}


export type SkillsMarker = {
  version: 1;
  files: string[];
};

async function listFilesRecursive(root: string): Promise<string[]> {
  const found: string[] = [];
  async function walk(dir: string): Promise<void> {
    let names: string[];
    try {
      names = await readdir(dir);
    } catch (error) {
      if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") return;
      throw skillsError(`cannot list ${dir}: ${describeCause(error)}`, "IO");
    }
    for (const name of names.sort()) {
      const full = join(dir, name);
      const st = await lstat(full);
      if (st.isSymbolicLink()) {
        throw skillsError(`refusing to follow symlink: ${full}`, "USAGE");
      }
      if (st.isDirectory()) {
        await walk(full);
      } else if (st.isFile()) {
        found.push(relative(root, full).split(sep).join("/"));
      }
    }
  }
  await walk(root);
  return found;
}

async function readMarker(storeDir: string): Promise<{ marker: SkillsMarker | undefined; raw: Buffer | undefined }> {
  const path = join(storeDir, SKILLS_MARKER);
  let raw: Buffer;
  try {
    raw = await readFile(path);
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return { marker: undefined, raw: undefined };
    }
    throw skillsError(`cannot read ${path}: ${describeCause(error)}`, "IO");
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw.toString("utf8"));
  } catch {
    throw skillsError(`skill marker is not JSON: ${path}`, "IO");
  }
  if (!parsed || typeof parsed !== "object" || !("files" in parsed) || !Array.isArray(parsed.files)) {
    throw skillsError(`skill marker is corrupt: ${path}`, "IO");
  }
  const files: string[] = [];
  for (const entry of parsed.files) {
    if (typeof entry !== "string" || entry === "" || entry.startsWith("/") || entry.includes("..")) {
      throw skillsError(`skill marker lists an unsafe path: ${path}`, "IO");
    }
    files.push(entry);
  }
  return { marker: { version: 1, files }, raw };
}

async function writeBytesIfChanged(path: string, bytes: Uint8Array, writes: string[]): Promise<void> {
  let current: Buffer | undefined;
  try {
    current = await readFile(path);
  } catch (error) {
    if (!error || typeof error !== "object" || !("code" in error) || error.code !== "ENOENT") {
      throw skillsError(`cannot read ${path}: ${describeCause(error)}`, "IO");
    }
  }
  if (current !== undefined && createHash("sha256").update(current).digest("hex") === createHash("sha256").update(bytes).digest("hex")) return;
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, bytes);
  writes.push(path);
}

export type InstallSkillsInput = {
  storeDir: string;
  sourceDir: string;
};

export type InstallSkillsResult = {
  status: "installed" | "already" | "conflict";
  exit: number;
  writes: string[];
  files: string[];
};

export async function installSkills(input: InstallSkillsInput): Promise<InstallSkillsResult> {
  const sourceFiles = await listFilesRecursive(input.sourceDir);
  if (sourceFiles.length === 0) {
    throw skillsError(`skill source tree is empty: ${input.sourceDir}`, "USAGE");
  }
  const { marker } = await readMarker(input.storeDir);
  const present = await listFilesRecursive(input.storeDir);
  const marked = new Set(marker === undefined ? [] : marker.files);
  const unmarked = present.filter(
    (rel) => rel !== SKILLS_MARKER && !marked.has(rel),
  );
  if (unmarked.length > 0) {
    return { status: "conflict", exit: EXIT_CODES.REFUSED_UNSAFE, writes: [], files: sourceFiles };
  }
  const writes: string[] = [];
  for (const rel of sourceFiles) {
    const bytes = await readFile(join(input.sourceDir, ...rel.split("/")));
    await writeBytesIfChanged(join(input.storeDir, ...rel.split("/")), bytes, writes);
  }
  const markerBytes = Buffer.from(JSON.stringify({ version: 1, files: sourceFiles }, null, 2) + "\n", "utf8");
  const markerPath = join(input.storeDir, SKILLS_MARKER);
  let markerCurrent: Buffer | undefined;
  try {
    markerCurrent = await readFile(markerPath);
  } catch (error) {
    if (!error || typeof error !== "object" || !("code" in error) || error.code !== "ENOENT") {
      throw skillsError(`cannot read ${markerPath}: ${describeCause(error)}`, "IO");
    }
  }
  if (markerCurrent === undefined || createHash("sha256").update(markerCurrent).digest("hex") !== createHash("sha256").update(markerBytes).digest("hex")) {
    await mkdir(input.storeDir, { recursive: true });
    await writeFile(markerPath, markerBytes);
    writes.push(markerPath);
  }
  if (writes.length === 0) {
    return { status: "already", exit: EXIT_CODES.OK, writes, files: sourceFiles };
  }
  return { status: "installed", exit: EXIT_CODES.OK, writes, files: sourceFiles };
}

export type UninstallSkillsInput = {
  storeDir: string;
  apply?: boolean;
};

export type UninstallSkillsResult = {
  status: "dry-run" | "removed" | "unknown-store";
  exit: number;
  writes: string[];
  wouldRemove: string[];
};

async function removeEmptyParents(storeDir: string, fileRel: string): Promise<void> {
  let dir = dirname(resolve(storeDir, fileRel));
  const root = resolve(storeDir);
  while (dir !== root && dir.startsWith(root)) {
    try {
      await rmdir(dir);
    } catch {
      break;
    }
    dir = dirname(dir);
  }
}

export async function uninstallSkills(input: UninstallSkillsInput): Promise<UninstallSkillsResult> {
  const { marker } = await readMarker(input.storeDir);
  if (marker === undefined) {
    return { status: "unknown-store", exit: EXIT_CODES.REFUSED_UNSAFE, writes: [], wouldRemove: [] };
  }
  if (input.apply !== true) {
    return { status: "dry-run", exit: EXIT_CODES.OK, writes: [], wouldRemove: [...marker.files, SKILLS_MARKER] };
  }
  const writes: string[] = [];
  for (const rel of marker.files) {
    const full = join(input.storeDir, ...rel.split("/"));
    try {
      await unlink(full);
      writes.push(full);
    } catch (error) {
      if (!error || typeof error !== "object" || !("code" in error) || error.code !== "ENOENT") {
        throw skillsError(`cannot remove ${full}: ${describeCause(error)}`, "IO");
      }
    }
    await removeEmptyParents(input.storeDir, rel);
  }
  try {
    await unlink(join(input.storeDir, SKILLS_MARKER));
    writes.push(join(input.storeDir, SKILLS_MARKER));
  } catch (error) {
    if (!error || typeof error !== "object" || !("code" in error) || error.code !== "ENOENT") {
      throw skillsError(`cannot remove marker: ${describeCause(error)}`, "IO");
    }
  }
  return { status: "removed", exit: EXIT_CODES.OK, writes, wouldRemove: [...marker.files, SKILLS_MARKER] };
}
