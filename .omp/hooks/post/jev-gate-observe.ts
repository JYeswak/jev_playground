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
 * Secrets: commands matching the PRIVATE/SECRET filters in
 * `work/bicameral-gate/real-sample.py` are never sent to the API — logged
 * `skipped:secret` with a redacted prefix. The patterns are compiled from that
 * file's source at load (`loadFilters`), so there is one owner and no copy to
 * drift; importing the .py is refused because it rewrites its output file at
 * module scope. If the source cannot be read or parsed, every command is
 * skipped `filter-error`: a filter failure fails safe toward skip.
 *
 * No key: one row `NOT_RUN reason=unconfigured`, no throw. Any throw anywhere
 * in this module is caught: the tool path never sees us.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { appendFile, mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { askJev } from "../../../work/jev-client/src/index.ts";
import { CUT, RISK, STATE_CONTEXT } from "../../../work/bicameral-gate/questions.mjs";

export const MODEL = "jev-1.13.0";
export const MAX_PREFIX = 200;
export const LOG_REL = "state/jev/gate-observe.jsonl";
export const REAL_SAMPLE = fileURLToPath(new URL("../../../work/bicameral-gate/real-sample.py", import.meta.url));

export interface Filters {
  privateRe: RegExp;
  secretRe: RegExp;
  scrubRe: RegExp;
}

/**
 * Compile real-sample.py's `PRIVATE` and `SECRET` from its source text: the
 * concatenated r"..." fragments of each `re.compile(...)`, case-insensitive
 * when the call passes `re.I`. Throws when either is missing.
 */
export function loadFilters(src: string): Filters {
  const grab = (name: string): { source: string; ignoreCase: boolean } => {
    const call = src.match(new RegExp(`^${name} = re\\.compile\\(([\\s\\S]*?)\\n\\)`, "m"));
    if (!call) throw new Error(`${name} = re.compile(...) not found`);
    const parts = [...call[1].matchAll(/r"((?:[^"\\]|\\.)*)"/g)].map((p) => p[1]);
    if (parts.length === 0) throw new Error(`${name} has no raw-string fragments`);
    return { source: parts.join(""), ignoreCase: /\bre\.(I|IGNORECASE)\b/.test(call[1]) };
  };
  const priv = grab("PRIVATE");
  const secret = grab("SECRET");
  return {
    privateRe: new RegExp(priv.source, priv.ignoreCase ? "i" : ""),
    secretRe: new RegExp(secret.source, secret.ignoreCase ? "i" : ""),
    scrubRe: new RegExp(secret.source, secret.ignoreCase ? "gi" : "g"),
  };
}

function loadOwnedFilters(): Filters | null {
  try {
    return loadFilters(readFileSync(REAL_SAMPLE, "utf8"));
  } catch {
    return null;
  }
}
export const FILTERS: Filters | null = loadOwnedFilters();

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


/**
 * Redacted prefix for the log: HOME → ~, secret shapes scrubbed, then the
 * first 200 chars. Scrubbing before the cut matters: a key straddling char 200
 * would otherwise be cut below the pattern's minimum length and logged raw.
 */
export function redact(command: string, home: string = homedir(), filters: Filters | null = FILTERS): string {
  if (!filters) return "[filter-unavailable]";
  return command.replaceAll(home, "~").trim().replace(filters.scrubRe, "[REDACTED]").slice(0, MAX_PREFIX);
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
    questions: typeof RISK;
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
  /** omp session id, read from the hook ctx by `makeHandler`. */
  session?: string;
}

export function makeFilter(filters: Filters | null): (command: string) => { drop: boolean; reason?: string } {
  return (command) => {
    if (!filters) return { drop: true, reason: "filter-error" };
    try {
      if (filters.privateRe.test(command) || filters.secretRe.test(command)) return { drop: true, reason: "secret" };
      return { drop: false };
    } catch {
      return { drop: true, reason: "filter-error" };
    }
  };
}
export const defaultFilter = makeFilter(FILTERS);

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
    const base = buildRow({ session: deps.session ?? "unknown", command, now: deps.now });
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
    let answer;
    try {
      answer = await (deps.asker ?? askJev)({
        state: { command, context: STATE_CONTEXT },
        questions: RISK,
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
    // Strictly above the cut, as every measured runner scores it (real-traffic.mjs, real-score.py).
    await write({
      ...base, status: "scored", probs, flag: Math.max(...Object.values(probs).map(Number)) > CUT,
      latencyMs: answer.latencyMs ?? null, tokens: answer.usage ?? null,
      skipped: null, error: null,
    });
    return undefined;
  } catch {
    return undefined;
  }
}

/**
 * The `tool_result` handler. Synchronous by contract: it reads the command and
 * session id, schedules the observation on a timer, and returns undefined, so
 * hashing, filtering, the Jev call and the disk write all run after omp's
 * awaited handler chain has moved on. `deps` is the test seam.
 */
export function makeHandler(deps: ObserveDeps = {}) {
  return (event: unknown, ctx?: { sessionManager?: { getSessionId?: () => string } }): undefined => {
    try {
      const e = event as Parameters<typeof observe>[0];
      if (e?.toolName !== "bash") return undefined;
      let session = deps.session ?? "unknown";
      try {
        session = ctx?.sessionManager?.getSessionId?.() ?? session;
      } catch {
        /* a missing session id is logged as unknown */
      }
      const seen = { toolName: e.toolName, input: { command: e.input?.command } };
      setTimeout(() => void observe(seen, { ...deps, session }).catch(() => {}), 0);
    } catch {
      /* observe only: the tool path never sees us */
    }
    return undefined;
  };
}

export default function hook(pi: {
  on: (event: string, handler: (event: unknown, ctx?: unknown) => unknown) => void;
}): void {
  pi.on("tool_result", makeHandler() as (event: unknown, ctx?: unknown) => unknown);
}
