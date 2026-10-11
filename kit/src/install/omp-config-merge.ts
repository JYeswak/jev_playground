// OMP config merge (T7): append-only `extensions:` block-list merge with backup,
// read-back verification and rollback. A strict YAML-subset reader covers only
// what the merge needs: top-level scalar mappings, one block sequence of
// scalar items under `extensions:`, full-line comments, CRLF. Anything richer
// (tabs, flow collections, anchors, nested maps under extensions, duplicate
// keys) fails closed with no write. Inline `extensions: [...]` is refused
// (exit 4, byte-identical): flow edits are not installer-safe. No YAML
// dependency: the subset is small enough to parse by hand and every refusal
// is covered by a test. This module reads no process environment.

import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { basename, dirname, isAbsolute, normalize, resolve } from "node:path";
import { EXIT_CODES } from "../families/registry.js";

export type ConfigMergeError = Error & { code: "USAGE" | "IO" | "CONFIG_MERGE" };

function mergeError(message: string, code: ConfigMergeError["code"]): ConfigMergeError {
  return Object.assign(new Error(message), { code });
}


export type ParsedExtensionsConfig = {
  lines: string[];
  newline: string;
  extensionsIndex: number;
  items: string[];
  itemLineIndexes: number[];
  inlineExtensions: boolean;
};

function stripTrailingComment(line: string): string {
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === "'" && !inDouble) {
      inSingle = !inSingle;
    } else if (char === '"' && !inSingle) {
      inDouble = !inDouble;
    } else if (char === "#" && !inSingle && !inDouble && i > 0 && line[i - 1] === " ") {
      return line.slice(0, i - 1);
    }
  }
  return line;
}

function unquoteScalar(raw: string): string {
  const text = raw.trim();
  if (text.length >= 2 && text.startsWith('"') && text.endsWith('"')) {
    return text.slice(1, -1);
  }
  if (text.length >= 2 && text.startsWith("'") && text.endsWith("'")) {
    return text.slice(1, -1).split("''").join("'");
  }
  return text;
}

export function normalizeExtensionEntry(entry: string): string {
  const text = entry.trim();
  if (text.length >= 2 && text.startsWith('"') && text.endsWith('"')) {
    return unquoteScalar(text);
  }
  if (text.length >= 2 && text.startsWith("'") && text.endsWith("'")) {
    return unquoteScalar(text);
  }
  return entry;
}

function isBareScalar(text: string): boolean {
  if (text === "") return false;
  for (const char of text) {
    const ok =
      (char >= "a" && char <= "z") ||
      (char >= "A" && char <= "Z") ||
      (char >= "0" && char <= "9") ||
      char === "_" ||
      char === "." ||
      char === "/" ||
      char === "~" ||
      char === "+" ||
      char === "-" ||
      char === ":" ||
      char === "@";
    if (!ok) return false;
  }
  return true;
}

export function readExtensionItems(content: string): string[] {
  return parseExtensionsConfig(content).items;
}

export function parseExtensionsConfig(content: string): ParsedExtensionsConfig {
  const newline = content.includes("\r\n") ? "\r\n" : "\n";
  const rawLines = content.split(newline);
  const lines = rawLines.map((line) => (line.endsWith("\r") ? line.slice(0, -1) : line));
  let extensionsIndex = -1;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("\t")) {
      throw mergeError(`config uses tab indentation at line ${i + 1}`, "CONFIG_MERGE");
    }
    if (line.startsWith(" ") || line.trim() === "" || line.trimStart().startsWith("#")) {
      continue;
    }
    const code = stripTrailingComment(line).trimEnd();
    if (code === "extensions:") {
      if (extensionsIndex !== -1) {
        throw mergeError("duplicate extensions key", "CONFIG_MERGE");
      }
      extensionsIndex = i;
      continue;
    }
    if (code.startsWith("extensions:")) {
      throw mergeError("inline extensions value is not installer-editable", "CONFIG_MERGE");
    }
    if (code.includes(": ") || code.endsWith(":")) {
      continue;
    }
    if (code !== "") {
      throw mergeError(`unexpected top-level line ${i + 1}`, "CONFIG_MERGE");
    }
  }
  const items: string[] = [];
  const itemLineIndexes: number[] = [];
  if (extensionsIndex !== -1) {
    for (let i = extensionsIndex + 1; i < lines.length; i++) {
      const line = lines[i];
      if (line.trim() === "" || line.trimStart().startsWith("#")) continue;
      if (!line.startsWith(" ") || line.startsWith("\t")) break;
      const stripped = line.trimStart();
      if (!stripped.startsWith("- ")) {
        throw mergeError(`non-item line inside extensions block at line ${i + 1}`, "CONFIG_MERGE");
      }
      const raw = stripTrailingComment(stripped.slice(2)).trim();
      if (raw === "" || raw.includes(": ")) {
        throw mergeError(`nested or empty extensions item at line ${i + 1}`, "CONFIG_MERGE");
      }
      const value = raw.startsWith('"') || raw.startsWith("'") ? unquoteScalar(raw) : raw;
      if (!(raw.startsWith('"') || raw.startsWith("'")) && !isBareScalar(value)) {
        throw mergeError(`unsupported extensions item at line ${i + 1}`, "CONFIG_MERGE");
      }
      items.push(value);
      itemLineIndexes.push(i);
    }
  }
  for (const line of lines) {
    if (line.trim() === "" || line.trimStart().startsWith("#")) continue;
    const code = stripTrailingComment(line);
    let inSingle = false;
    let inDouble = false;
    for (let i = 0; i < code.length; i++) {
      const char = code[i];
      if (char === "\\" && inDouble) {
        i++;
        continue;
      }
      if (char === "'" && !inDouble) {
        inSingle = !inSingle;
        continue;
      }
      if (char === '"' && !inSingle) {
        inDouble = !inDouble;
        continue;
      }
      if (!inSingle && !inDouble && (char === "&" || char === "*" || char === "!")) {
        throw mergeError("anchors, aliases and tags are outside the installer subset", "CONFIG_MERGE");
      }
    }
  }
  return { lines, newline, extensionsIndex, items, itemLineIndexes, inlineExtensions: false };
}

export function verifyConfigSubset(before: string[], after: string[]): void {
  const kept = new Set(after);
  for (const entry of before) {
    if (!kept.has(entry)) {
      throw mergeError(`read-back dropped host entry: ${entry}`, "CONFIG_MERGE");
    }
  }
}

export type MergeExtensionsInput = {
  configPath: string;
  profileDir: string;
  addExtensions: string[];
};

export type MergeExtensionsResult = {
  status: "merged" | "already" | "refused" | "failed";
  exit: number;
  writes: string[];
  backup: string;
  added: string[];
};

async function fileBytes(path: string): Promise<Buffer | undefined> {
  try {
    return await readFile(path);
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return undefined;
    }
    throw mergeError(`cannot read ${path}: ${error instanceof Error ? error.message : String(error)}`, "IO");
  }
}

export async function mergeExtensions(input: MergeExtensionsInput): Promise<MergeExtensionsResult> {
  const writes: string[] = [];
  const existing = await fileBytes(input.configPath);
  const content = existing === undefined ? "" : existing.toString("utf8");
  let parsed: ParsedExtensionsConfig;
  try {
    parsed = parseExtensionsConfig(content);
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "CONFIG_MERGE") {
      const message = error instanceof Error ? error.message : String(error);
      if (message.includes("inline extensions value")) {
        return { status: "refused", exit: EXIT_CODES.REFUSED_UNSAFE, writes, backup: "", added: [] };
      }
      return { status: "failed", exit: EXIT_CODES.FINDINGS, writes, backup: "", added: [] };
    }
    throw error;
  }
  const absoluteOf = (entry: string): string =>
    isAbsolute(entry) ? normalize(entry) : normalize(resolve(input.profileDir, entry));
  const knownPaths = new Set(parsed.items.map((entry) => absoluteOf(entry)));
  const knownBases = new Set(parsed.items.map((entry) => basename(entry)));
  const missing = input.addExtensions.filter((entry) => {
    const value = normalizeExtensionEntry(entry);
    return !knownPaths.has(absoluteOf(value)) && !knownBases.has(basename(value));
  });
  if (missing.length === 0) {
    return { status: "already", exit: EXIT_CODES.OK, writes, backup: "", added: [] };
  }
  let next: string;
  if (parsed.extensionsIndex === -1) {
    const prefix = content === "" || content.endsWith(parsed.newline) ? content : content + parsed.newline;
    next = `${prefix}extensions:${parsed.newline}${missing.map((entry) => `  - ${entry}`).join(parsed.newline)}${parsed.newline}`;
  } else {
    const out = [...parsed.lines];
    const anchor = parsed.itemLineIndexes.length > 0 ? parsed.itemLineIndexes[parsed.itemLineIndexes.length - 1] + 1 : parsed.extensionsIndex + 1;
    out.splice(anchor, 0, ...missing.map((entry) => `  - ${entry}`));
    next = out.join(parsed.newline);
    if (content.endsWith(parsed.newline) && !next.endsWith(parsed.newline)) next += parsed.newline;
  }
  try {
    const reread = parseExtensionsConfig(next);
    verifyConfigSubset(parsed.items, reread.items);
    for (const entry of missing) {
      if (!reread.items.includes(normalizeExtensionEntry(entry))) {
        throw mergeError(`merged extensions missing added entry: ${entry}`, "CONFIG_MERGE");
      }
    }
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "CONFIG_MERGE") {
      return { status: "failed", exit: EXIT_CODES.FINDINGS, writes, backup: "", added: [] };
    }
    throw error;
  }
  let backup = `${input.configPath}.bak`;
  if (existing !== undefined) {
    let serial = 1;
    while ((await fileBytes(backup)) !== undefined) {
      serial += 1;
      backup = `${input.configPath}.bak.${serial}`;
    }
  }
  await mkdir(dirname(input.configPath), { recursive: true });
  if (existing !== undefined) {
    await writeFile(backup, existing);
    writes.push(backup);
  }
  await writeFile(input.configPath, next);
  writes.push(input.configPath);
  return { status: "merged", exit: EXIT_CODES.OK, writes, backup: existing === undefined ? "" : backup, added: missing };
}

export type RollbackExtensionsInput = {
  configPath: string;
};

export type RollbackExtensionsResult = {
  status: "rolled-back" | "no-backup";
  exit: number;
  writes: string[];
};

export async function rollbackExtensions(input: RollbackExtensionsInput): Promise<RollbackExtensionsResult> {
  let backup = `${input.configPath}.bak`;
  if ((await fileBytes(backup)) === undefined) {
    let serial = 2;
    let found: string | undefined;
    while (true) {
      const candidate = `${input.configPath}.bak.${serial}`;
      if ((await fileBytes(candidate)) === undefined) break;
      found = candidate;
      serial += 1;
      if (serial > 100) break;
    }
    if (found === undefined) {
      return { status: "no-backup", exit: EXIT_CODES.REFUSED_UNSAFE, writes: [] };
    }
    backup = found;
  }
  const bytes = await fileBytes(backup);
  if (bytes === undefined) {
    return { status: "no-backup", exit: EXIT_CODES.REFUSED_UNSAFE, writes: [] };
  }
  const current = await fileBytes(input.configPath);
  if (current !== undefined && Buffer.compare(current, bytes) === 0) {
    return { status: "rolled-back", exit: EXIT_CODES.OK, writes: [] };
  }
  await rename(backup, input.configPath);
  return { status: "rolled-back", exit: EXIT_CODES.OK, writes: [input.configPath] };
}
