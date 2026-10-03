/**
 * Test-rerun skip shadow (jev-2nk3): advisory observer, never blocks.
 *
 * On a bash tool call that invokes a test runner, hashes the tree state
 * (HEAD + status --porcelain, read-only with GIT_OPTIONAL_LOCKS=0) and
 * compares with the last recorded run of the same command. When command,
 * tree, and a previous PASS all match, it logs a would-skip row: this run
 * would almost surely repeat the previous pass. Anything else logs
 * pass-through. Outcomes arrive via observeResult (post hook or reconciler).
 * No Jev calls, no subprocess in production beyond git itself, sync return.
 */
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export const STORE_REL = "state/jev/test-rerun.json";
const DIRECT_TESTCMD = /(^|[;&|(\s])(pytest|bun\s+test|npm\s+test|node\s+--test|go\s+test|cargo\s+test)\b/;
const UV_RUN = /(^|[;&|(\s])uv\s+run/g;
const LINE_BREAKS = ["\r", "\n", "\u2028", "\u2029"];
function nextLineEnd(text: string, start: number): number {
  let end = text.length;
  for (const lineBreak of LINE_BREAKS) {
    const index = text.indexOf(lineBreak, start);
    if (index !== -1 && index < end) end = index;
  }
  return end;
}
function afterLineEnd(text: string, end: number): number {
  return text[end] === "\r" && text[end + 1] === "\n" ? end + 2 : end + 1;
}
function isWordCharacter(value: string | undefined): boolean {
  return value !== undefined && /[A-Za-z0-9_]/.test(value);
}
function testEndsByLine(command: string): Map<number, number> {
  const ends = new Map<number, number>();
  let start = 0;
  while (start <= command.length) {
    const end = nextLineEnd(command, start);
    let lastTestEnd = -1;
    for (let index = command.indexOf("test", start); index !== -1 && index < end; index = command.indexOf("test", index + 1)) {
      if (!isWordCharacter(command[index + 4])) lastTestEnd = index + 4;
    }
    if (lastTestEnd !== -1) ends.set(start, lastTestEnd);
    if (end === command.length) break;
    start = afterLineEnd(command, end);
  }
  return ends;
}
function uvRunTest(command: string): { start: number; end: number } | null {
  let cursor = 0;
  let lineStart = 0;
  let lineEnd = -1;
  let testEnds: Map<number, number> | undefined;
  while (cursor <= command.length) {
    UV_RUN.lastIndex = cursor;
    const match = UV_RUN.exec(command);
    if (!match) return null;
    if (lineEnd < 0) lineEnd = nextLineEnd(command, lineStart);
    testEnds ??= testEndsByLine(command);
    const start = match.index + match[1].length;
    const runEnd = match.index + match[0].length;
    while (runEnd > lineEnd && lineEnd < command.length) {
      lineStart = afterLineEnd(command, lineEnd);
      lineEnd = nextLineEnd(command, lineStart);
    }
    const end = testEnds.get(lineStart);
    if (end !== undefined && end > runEnd) return { start, end };
    cursor = start + 2;
  }
  return null;
}
export function matchTestCommand(command: string): string | null {
  const direct = DIRECT_TESTCMD.exec(command);
  const uv = uvRunTest(command);
  const directStart = direct ? direct.index + direct[1].length : Infinity;
  if (direct && (!uv || directStart <= uv.start)) return direct[2].replace(/\s+/g, " ").trim();
  return uv ? command.slice(uv.start, uv.end).replace(/\s+/g, " ").trim() : null;
}

export type Run = { cmd: string; cwd: string };
export type Deps = {
  run?: (cmd: string, cwd: string) => string;
  readStore?: () => Record<string, { tree: string; passed: boolean }>;
  writeStore?: (s: Record<string, { tree: string; passed: boolean }>) => void;
  append?: (path: string, line: string) => Promise<void>;
  path?: string;
  now?: () => string;
  cwd?: string;
};

function defaultRun(cmd: string, cwd: string): string {
  return execFileSync("bash", ["-c", cmd], { cwd, timeout: 15000 }).toString();
}

export function treeHash(run: (cmd: string, cwd: string) => string, cwd: string): string | null {
  try {
    const head = run("GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD", cwd).trim();
    const status = run("GIT_OPTIONAL_LOCKS=0 git status --porcelain", cwd).trim();
    return createHash("sha256").update(head + "\n" + status).digest("hex").slice(0, 16);
  } catch {
    return null;
  }
}

function loadStore(deps: Deps): Record<string, { tree: string; passed: boolean }> {
  if (deps.readStore) return deps.readStore();
  try {
    return JSON.parse(readFileSync(deps.path ?? join(homedir(), ".local", STORE_REL), "utf8"));
  } catch {
    return {};
  }
}

function saveStore(deps: Deps, s: Record<string, { tree: string; passed: boolean }>): void {
  if (deps.writeStore) {
    deps.writeStore(s);
    return;
  }
  const p = deps.path ?? join(homedir(), ".local", STORE_REL);
  mkdirSync(join(homedir(), ".local", "state", "jev"), { recursive: true });
  writeFileSync(p, JSON.stringify(s));
}

/** Pre-call: log would-skip or pass-through. Always returns undefined. */
export function makeRerunObserver(deps: Deps = {}) {
  const run = deps.run ?? defaultRun;
  const cwd = deps.cwd ?? process.cwd();
  const now = deps.now ?? (() => new Date().toISOString());
  return async (event: { toolName?: unknown; input?: { command?: unknown } }): Promise<undefined> => {
    if (event.toolName !== "bash" || typeof event.input?.command !== "string") return undefined;
    const cmd = event.input.command;
    if (!matchTestCommand(cmd)) return undefined;
    const tree = treeHash(run, cwd);
    let status = "pass-through";
    let detail: Record<string, unknown> = {};
    if (tree) {
      const store = loadStore(deps);
      const prev = store[cmd];
      if (prev && prev.tree === tree && prev.passed) {
        status = "would-skip";
        detail = { prevTree: tree };
      }
    } else {
      detail = { tree: "unknown" };
    }
    if (deps.append) {
      await deps.append(
        deps.path ?? join(homedir(), ".local", "state", "jev", "test-rerun-shadow.jsonl"),
        JSON.stringify({ ts: now(), status, cmd: cmd.slice(0, 200), ...detail }),
      );
    }
    return undefined;
  };
}

/** Post-result: record outcome for the next call. Always returns undefined. */
export function makeRerunRecorder(deps: Deps = {}) {
  const run = deps.run ?? defaultRun;
  const cwd = deps.cwd ?? process.cwd();
  return async (event: { input?: { command?: unknown }; exitCode?: unknown; isError?: unknown }): Promise<undefined> => {
    const cmd = event.input?.command;
    if (typeof cmd !== "string" || !matchTestCommand(cmd)) return undefined;
    const tree = treeHash(run, cwd);
    if (!tree) return undefined;
    const store = loadStore(deps);
    store[cmd] = { tree, passed: event.isError !== true && event.exitCode !== 1 };
    saveStore(deps, store);
    return undefined;
  };
}

/**
 * Loader entry. Intentionally registers nothing: the observer/recorder are
 * wired explicitly per session with injected deps (never fleet-wide), so a
 * bare load must stay inert. Satisfies the extension loader's factory check.
 */
export default function jevTestRerunExtension(): void {}
