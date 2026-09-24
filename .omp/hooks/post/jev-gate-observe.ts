/**
 * Observe-only tool-call gate (bead jev-deep-kit-8q7.7 follow-up: dogfood).
 *
 * On every completed `bash` tool call, asks the frozen gate questions from
 * `work/bicameral-gate/questions.mjs` through `work/jev-client` `askJev`
 * (pinned `jev-1.13.0`) and appends one row to
 * `~/.local/state/jev/gate-observe.jsonl`. Observe only: never blocks, never
 * rewrites a result, prints nothing. The handler returns synchronously; all
 * API and filesystem work runs detached, so the tool path waits only for the
 * synchronous slice (measured, see receipt).
 *
 * Secrets: commands matching the private/secret filters in
 * `work/bicameral-gate/real-sample.py` are never sent to the API — logged
 * `skipped:secret` with a redacted prefix. The patterns live in that file;
 * the copies below are verified against it by the parity test (direct import
 * is refused: importing real-sample.py rewrites its output file at module
 * scope). A filter failure fails safe toward skip.
 *
 * No key: one row `NOT_RUN reason=unconfigured`, no throw. Any throw anywhere
 * in this module is caught: the tool path never sees us.
 */
import { createHash } from "node:crypto";
import { appendFile, mkdir, readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { askJev } from "../../../work/jev-client/src/index.ts";
import { CUT, RISK, STATE_CONTEXT } from "../../../work/bicameral-gate/questions.mjs";

export const MODEL = "jev-1.13.0";
export const MAX_PREFIX = 200;
export const LOG_REL = "state/jev/gate-observe.jsonl";

// Mirrors of work/bicameral-gate/real-sample.py:29-37. Owned there; the
// parity test (`secret patterns match real-sample.py`) fails if they drift.
export const PRIVATE_RE = /clutter|cfsios|cfs-|hubspot|phoenix|accountcenter|grokbot|zesttube|alps|control-plane|omp-orchestrator|franken-harvest|josh-claude-config/i;
export const SECRET_RE = /sk-[A-Za-z0-9_-]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|Bearer [A-Za-z0-9._-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY/;
export const SCRUB_RE = /sk-[A-Za-z0-9_-]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|Bearer [A-Za-z0-9._-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY/g;

export const ROW_KEYS = [
  "ts", "session", "cmdSha", "cmd", "status", "probs", "flag",
  "latencyMs", "tokens", "skipped", "error",
] as const;
export type RowStatus = "scored" | "skipped" | "not-run" | "error";
export interface ObserveRow {
  ts: string;
  session: string;
  cmdSha: string;
  cmd: string;
  status: RowStatus;
  probs: Record<string, number> | null;
  flag: boolean | null;
  latencyMs: number | null;
  tokens: { input_tokens: number; output_tokens: number } | null;
  skipped: null | "secret" | "filter-error";
  error: string | null;
}


/** Redacted prefix for the log: HOME → ~, first 200 chars, secret shapes scrubbed. */
export function redact(command: string, home: string = homedir()): string {
  const short = command.replaceAll(home, "~").trim().slice(0, MAX_PREFIX);
  return short.replace(SCRUB_RE, "[REDACTED]");
}

export function buildRow(init: {
  session: string;
  command: string;
  now?: () => string;
}): Pick<ObserveRow, "ts" | "session" | "cmdSha" | "cmd"> {
  return {
    ts: (init.now ?? (() => new Date().toISOString()))(),
    session: init.session,
    cmdSha: createHash("sha256").update(init.command).digest("hex"),
    cmd: redact(init.command),
  };
}

export interface ObserveDeps {
  asker?: (args: {
    state: unknown;
    questions: Record<string, string>;
    model: string;
    timeoutMs: number;
  }) => Promise<{
    ok: boolean;
    reason?: string;
    error?: string;
    scores?: Record<string, number>;
    latencyMs?: number;
    usage?: { input_tokens: number; output_tokens: number };
  }>;
  filter?: (command: string) => { drop: boolean; reason?: string };
  append?: (path: string, line: string) => Promise<void>;
  logPath?: string;
  now?: () => string;
}

export function defaultFilter(command: string): { drop: boolean; reason?: string } {
  try {
    if (PRIVATE_RE.test(command) || SECRET_RE.test(command)) return { drop: true, reason: "secret" };
    return { drop: false };
  } catch {
    return { drop: true, reason: "filter-error" };
  }
}

async function defaultAppend(path: string, line: string): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  await appendFile(path, line + "\n");
}

export function defaultLogPath(): string {
  return join(homedir(), ".local", LOG_REL);
}

/**
 * One observation. Always resolves undefined; never throws. Every failure
 * mode below is a row, not an exception.
 */
export async function observe(
  event: { toolName?: string; input?: { command?: unknown } },
  deps: ObserveDeps = {},
): Promise<undefined> {
  const logPath = deps.logPath ?? defaultLogPath();
  const write = async (row: ObserveRow): Promise<void> => {
    try {
      await (deps.append ?? defaultAppend)(logPath, JSON.stringify(row));
    } catch {
      /* the log is best-effort; the tool path never sees us */
    }
  };
  try {
    const command = typeof event.input?.command === "string" ? event.input.command : "";
    const base = buildRow({ session: "unknown", command, now: deps.now });
    const filter = deps.filter ?? defaultFilter;
    let verdict: { drop: boolean; reason?: string };
    try {
      verdict = filter(command);
    } catch {
      verdict = { drop: true, reason: "filter-error" };
    }
    if (verdict.drop) {
      await write({ ...base, status: "skipped", probs: null, flag: null, latencyMs: null, tokens: null, skipped: verdict.reason === "filter-error" ? "filter-error" : "secret", error: null });
      return undefined;
    }
    const questions = Object.fromEntries(Object.entries(RISK).map(([k, q]) => [k, q]));
    let answer;
    try {
      answer = await (deps.asker ?? askJev)({
        state: { command, context: STATE_CONTEXT },
        questions,
        model: MODEL,
        timeoutMs: 20000,
      });
    } catch (err) {
      await write({ ...base, status: "error", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: `ask-threw: ${err instanceof Error ? err.message : String(err)}` });
      return undefined;
    }
    if (!answer.ok) {
      if (answer.reason === "unconfigured") {
        await write({ ...base, status: "not-run", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: "NOT_RUN reason=unconfigured" });
      } else {
        await write({ ...base, status: "error", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: `${answer.reason ?? "unknown"}: ${answer.error ?? ""}` });
      }
      return undefined;
    }
    const probs = answer.scores ?? {};
    await write({
      ...base, status: "scored", probs, flag: Math.max(...Object.values(probs).map(Number)) >= CUT,
      latencyMs: answer.latencyMs ?? null, tokens: answer.usage ?? null,
      skipped: null, error: null,
    });
    return undefined;
  } catch {
    return undefined;
  }
}

export default function hook(pi: {
  on: (event: string, handler: (event: unknown) => unknown) => void;
}): void {
  pi.on("tool_result", (event) => {
    const e = event as { toolName?: string };
    if (e.toolName !== "bash") return undefined;
    void observe(event as Parameters<typeof observe>[0]).catch(() => {});
    return undefined;
  });
}
