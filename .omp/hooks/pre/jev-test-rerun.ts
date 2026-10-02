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
const TESTCMD = /(^|[;&|(\s])(pytest|uv\s+run.*test|bun\s+test|npm\s+test|node\s+--test|go\s+test|cargo\s+test)\b/;

export function matchTestCommand(command: string): string | null {
  const m = TESTCMD.exec(command);
  return m ? m[2].replace(/\s+/g, " ").trim() : null;
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
