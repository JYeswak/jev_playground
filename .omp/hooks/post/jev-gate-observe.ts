/**
 * Observe-only tool-call gate (bead jev-deep-kit-8q7.7 follow-up: dogfood).
 *
 * On every completed `bash` tool call, records a local observation in
 * On every completed bash tool call, records a local risk observation in
 * ~/.local/state/jev/gate-observe.jsonl and asks Jev through the shared kit client.
 * The live asker uses work/jev-client's Infisical user-session provider, with its
 * separately approved machine-identity fallback. Observe only: fail open; never
 * block or rewrite the command or result.
 *
 * Secrets: commands matching the PRIVATE/SECRET filters in
 * `work/bicameral-gate/real-sample.py` are never sent to the API — logged
 * `skipped:secret` with a redacted prefix. The patterns are compiled from that
 * file's source at load (`loadFilters`), so there is one owner and no copy to
 * drift; importing the .py is refused because it rewrites its output file at
 * module scope. If the source cannot be read or parsed, every command is
 * skipped `filter-error`: a filter failure fails safe toward skip.
 *
 * Full-command sidecar (bead jev-izhc, R92 retry): the log above keeps a
 * 200-char redacted prefix. Every command that passes the filters is also
 * appended verbatim to the local-only sidecar for offline review, with
 * `{ts, session, cmdSha, cmd}` joined to the log by `cmdSha`.
 * Commands dropped by filters (secret or filter-error) write nothing there. The file is
 * created and re-asserted mode 600 on every append, lives outside every repo,
 * and must never be copied into a committed extract.
 *
 * Missing OMP session: one NOT_RUN session-unavailable row and no provider lookup.
 * Each handler is capped at 100 attempts per UTC date; HTTP 401/402/403 pause the client.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { appendFile, mkdir, open } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { askJevBundle, BILLING_HOLD_MS, billingHoldActive, noteBillingRefusal, resetBillingHold } from "../../../kit/src/client.ts";
import { useInfisicalKey } from "../../../work/jev-client/src/use-infisical-key.ts";
export { BILLING_HOLD_MS, resetBillingHold };
import { CUT, RISK, STATE_CONTEXT } from "../../../work/bicameral-gate/questions.mjs";

export const MODEL = "jev-1.13.0";
export const MAX_PREFIX = 200;
export const MAX_DAILY_CALLS = 100;
export const LOG_REL = "state/jev/gate-observe.jsonl";
export const SIDECAR_REL = "state/jev/gate-observe-full.jsonl";
export const SIDECAR_MODE = 0o600;
export const SIDECAR_KEYS = ["ts", "session", "cmdSha", "cmd"] as const;
/** Local-only; `cmd` is the full scored command. Never commit one. */
export type SidecarRow = Pick<ObserveRow, "ts" | "session" | "cmdSha" | "cmd">;
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
  "ts", "session", "cmdSha", "cmd", "status", "model", "probs", "flag",
  "latencyMs", "tokens", "skipped", "error",
] as const;
export type RowStatus = "scored" | "skipped" | "not-run" | "error";
export interface ObserveRow {
  ts: string;
  session: string;
  cmdSha: string;
  cmd: string;
  status: RowStatus;
  model: string | null;
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
}): Pick<ObserveRow, "ts" | "session" | "cmdSha" | "cmd" | "model"> {
  return {
    ts: (init.now ?? (() => new Date().toISOString()))(),
    session: init.session,
    cmdSha: createHash("sha256").update(init.command).digest("hex"),
    cmd: redact(init.command),
    model: null,
  };
}

export interface ObserveDeps {
  asker?: (args: {
    state: Record<string, unknown>;
    questions: typeof RISK;
    model: string;
    timeoutMs: number;
  }) => Promise<{
    ok: boolean;
    reason?: string;
    error?: string;
    scores?: Record<string, number>;
    model?: string;
    latencyMs?: number;
    usage?: { input_tokens: number; output_tokens: number };
  }>;
  append?: (path: string, line: string) => Promise<void>;
  logPath?: string;
  filter?: (command: string) => { drop: boolean; reason?: string };
  appendSidecar?: (path: string, line: string) => Promise<void>;
  sidecarPath?: string;
  now?: () => string;
  session?: string;
  nowMs?: () => number;
  dailyCap?: number;
  dailyBudget?: { day: string; calls: number };
}

const processDailyBudget = { day: "", calls: 0 };

const liveAsker: NonNullable<ObserveDeps["asker"]> = async (args) => {
  useInfisicalKey();
  const result = await askJevBundle(args);
  if (!result.ok) return result;

  const scores: Record<string, number> = {};
  for (const key in RISK) {
    const answer = result.answers[key];
    if (answer === null || typeof answer !== "object" || !("noul" in answer)) {
      return { ok: false, reason: "no-answers", error: "bundle answer is missing a Noul score", latencyMs: result.latencyMs };
    }
    const score = answer.noul;
    if (typeof score !== "number" || !Number.isFinite(score) || score < 0 || score > 1) {
      return { ok: false, reason: "no-answers", error: "bundle answer has an invalid Noul score", latencyMs: result.latencyMs };
    }
    scores[key] = score;
  }
  return {
    ok: true,
    scores,
    model: result.resolvedModel,
    latencyMs: result.latencyMs,
    usage: result.usage ? { input_tokens: result.usage.input_tokens, output_tokens: result.usage.output_tokens } : undefined,
  };
};

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

/**
 * Opens for append with mode 600 and re-asserts 600 before writing, so a file
 * that pre-exists with wider bits is narrowed before it gets a new command.
 */
export async function defaultSidecarAppend(path: string, line: string): Promise<void> {
  await mkdir(dirname(path), { recursive: true, mode: 0o700 });
  const fh = await open(path, "a", SIDECAR_MODE);
  try {
    await fh.chmod(SIDECAR_MODE);
    await fh.appendFile(line + "\n");
  } finally {
    await fh.close();
  }
}

export function defaultLogPath(): string {
  return join(homedir(), ".local", LOG_REL);
}

export function defaultSidecarPath(): string {
  return join(homedir(), ".local", SIDECAR_REL);
}

/**
 * One observation. Always resolves undefined; never throws. Every failure
 * mode below is a row, not an exception.
 */
export async function observe(
  event: { toolName?: string; toolCallId?: unknown; input?: { command?: unknown } },
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
    const session = typeof deps.session === "string" ? deps.session : "unknown";
    const base = buildRow({ session, command, now: deps.now });
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
    if (!session.trim() || session === "unknown") {
      await write({ ...base, status: "not-run", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: "NOT_RUN reason=session-unavailable" });
      return undefined;
    }
    const now = (deps.nowMs ?? Date.now)();
    const until = billingHoldActive(now);
    if (until !== null) {
      await write({ ...base, status: "not-run", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: "NOT_RUN reason=billing-hold until=" + new Date(until).toISOString() });
      return undefined;
    }
    const budget = deps.dailyBudget ?? processDailyBudget;
    const day = base.ts.slice(0, 10);
    if (budget.day !== day) {
      budget.day = day;
      budget.calls = 0;
    }
    if (budget.calls >= (deps.dailyCap ?? MAX_DAILY_CALLS)) {
      await write({ ...base, status: "not-run", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: "NOT_RUN reason=daily-cap" });
      return undefined;
    }
    budget.calls += 1;
    try {
      const full: SidecarRow = { ts: base.ts, session: base.session, cmdSha: base.cmdSha, cmd: command };
      await (deps.appendSidecar ?? defaultSidecarAppend)(deps.sidecarPath ?? defaultSidecarPath(), JSON.stringify(full));
    } catch {
      /* best-effort like the log; the tool path never sees us */
    }
    let answer: Awaited<ReturnType<NonNullable<ObserveDeps["asker"]>>>;
    try {
      answer = await (deps.asker ?? liveAsker)({
        state: { command, context: STATE_CONTEXT },
        questions: RISK,
        model: MODEL,
        timeoutMs: 20000,
      });
    } catch (err) {
      await write({ ...base, status: "error", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: "ask-threw: " + (err instanceof Error ? err.message : String(err)) });
      return undefined;
    }
    if (!answer.ok) {
      if (answer.reason === "unconfigured") {
        await write({ ...base, status: "not-run", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: "NOT_RUN reason=unconfigured" });
      } else if (answer.reason === "billing-hold") {
        await write({ ...base, status: "not-run", probs: null, flag: null, latencyMs: null, tokens: null, skipped: null, error: "NOT_RUN reason=" + (answer.error ?? "billing-hold") });
      } else {
        noteBillingRefusal(answer, now);
        await write({ ...base, status: "error", probs: null, flag: null, latencyMs: answer.latencyMs ?? null, tokens: null, skipped: null, error: (answer.reason ?? "unknown") + ": " + (answer.error ?? "") });
      }
      return undefined;
    }
    const probs = answer.scores ?? {};
    let maxScore = -Infinity;
    for (const key in probs) {
      const score = probs[key];
      if (typeof score === "number" && Number.isFinite(score) && score > maxScore) maxScore = score;
    }
    await write({
      ...base,
      status: "scored",
      model: answer.model ?? null,
      probs,
      flag: maxScore > CUT,
      latencyMs: answer.latencyMs ?? null,
      tokens: answer.usage ?? null,
      skipped: null,
      error: null,
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
      const seen = { toolName: e.toolName, toolCallId: e.toolCallId, input: { command: e.input?.command } };
      setTimeout(() => void observe(seen, { ...deps, session }).catch(() => {}), 0);
    } catch {
      /* observe only: the tool path never sees us */
    }
    return undefined;
  };
}

export default function hook(pi: {
  on: (event: string, handler: (event: unknown, ctx?: unknown) => unknown) => void;
}, deps: ObserveDeps = {}): void {
  pi.on("tool_result", makeHandler(deps) as (event: unknown, ctx?: unknown) => unknown);
}
