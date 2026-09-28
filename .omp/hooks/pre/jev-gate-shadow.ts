import { createHash } from "node:crypto";
import { mkdir, open } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import type { AskBundleOptions, JevBundleResult } from "../../../kit/src/client.ts";
declare const process: { env: Record<string, string | undefined> };
import { CUT, RISK, STATE_CONTEXT } from "../../../work/bicameral-gate/questions.mjs";

export const MODEL = "jev-1.13.0";
export const MAX_DAILY_CALLS = 100;
export const LOG_SCHEMA = "jev-gate-shadow.v1";

type Event = { toolName?: unknown; name?: unknown; toolCallId?: unknown; input?: unknown; args?: unknown; arguments?: unknown; command?: unknown; details?: unknown };
type Append = (path: string, line: string) => Promise<void>;
type Ask = (options: AskBundleOptions) => Promise<JevBundleResult>;
type ShadowDeps = {
  ask?: Ask; append?: Append; path?: string; session?: string; cap?: number; now?: () => string;
  /** Keyless synthetic admission only; production has no approved recipient/data-class policy. */
  authorizeSynthetic?: (event: Event) => string | undefined;
};

function defaultPath(): string {
  return process.env.JEV_GATE_SHADOW_PATH ?? join(homedir(), ".local", "state", "jev", "gate-shadow.jsonl");
}

async function defaultAppend(path: string, line: string): Promise<void> {
  await mkdir(dirname(path), { recursive: true, mode: 0o700 });
  const file = await open(path, "a", 0o600);
  try { await file.chmod(0o600); await file.appendFile(line + "\n"); } finally { await file.close(); }
}

export function hashCommand(command: string): string {
  return createHash("sha256").update(command).digest("hex");
}
function dayKey(now: () => string): string { return now().slice(0, 10); }

function stringCommand(event: Event): string | undefined {
  const toolName = typeof event.toolName === "string" ? event.toolName : typeof event.name === "string" ? event.name : "";
  if (toolName !== "bash") return undefined;
  const source = event.input ?? event.args ?? event.arguments;
  const input = source && typeof source === "object" ? source as Record<string, unknown> : {};
  const command = input.command ?? input.cmd ?? event.command;
  return typeof command === "string" && command.length > 0 ? command : undefined;
}
function existingFlag(event: Event): boolean | null {
  const details = event.details && typeof event.details === "object" ? event.details as Record<string, unknown> : {};
  return typeof details.existingFlag === "boolean" ? details.existingFlag : null;
}
function baseRow(command: string, session: string, now: () => string): Record<string, unknown> {
  return { schema: LOG_SCHEMA, ts: now(), sessionHash: hashCommand(session || "unknown"), cmdSha: hashCommand(command), existingFlag: null };
}


export function makeGateShadowHandler(deps: ShadowDeps = {}) {
  const ask = deps.ask;
  const append = deps.append ?? defaultAppend;
  const path = deps.path ?? defaultPath();
  const now = deps.now ?? (() => new Date().toISOString());
  const cap = deps.cap ?? Number(process.env.JEV_GATE_SHADOW_DAILY_CAP ?? String(MAX_DAILY_CALLS));
  let day = dayKey(now);
  let calls = 0;
  let paused = false;

  const write = async (row: Record<string, unknown>): Promise<void> => {
    try { await append(path, JSON.stringify(row)); } catch { /* shadow-only: never affect bash execution */ }
  };

  return async (event: Event, session = deps.session ?? process.env.OMP_SESSION_ID ?? "unknown"): Promise<undefined> => {
    const command = stringCommand(event);
    if (!command) return undefined;
    try {
      const observedFlag = existingFlag(event);
      const row = { ...baseRow(command, typeof session === "string" ? session : "unknown", now), existingFlag: observedFlag, existingFlagSource: observedFlag === null ? "gate-observe.jsonl:cmdSha" : "event.details.existingFlag" };
      const approvedCommand = deps.authorizeSynthetic?.(event);
      if (!ask || !approvedCommand || typeof event.toolCallId !== "string" || !event.toolCallId || typeof session !== "string" || !session || session === "unknown") {
        await write({ ...row, status: "not-run", reason: "permission-denied", jevFlag: null, maxScore: null, scores: null, model: null, latencyMs: null, tokens: null });
        return undefined;
      }
      if (dayKey(now) !== day) { day = dayKey(now); calls = 0; paused = false; }
      if (paused) { await write({ ...row, status: "paused", jevFlag: null, maxScore: null, scores: null, model: null, latencyMs: null, tokens: null }); return undefined; }
      if (calls >= cap) { await write({ ...row, status: "cap", jevFlag: null, maxScore: null, scores: null, model: null, latencyMs: null, tokens: null }); return undefined; }
      calls += 1;
      let result: JevBundleResult;
      try {
        result = await ask({ state: { command: approvedCommand, context: STATE_CONTEXT }, questions: RISK, model: MODEL, timeoutMs: 20_000 });
      } catch (error) {
        await write({ ...row, status: "error", jevFlag: null, maxScore: null, scores: null, model: null, latencyMs: null, tokens: null, error: error instanceof Error ? error.message : String(error) });
        return undefined;
      }
      if (!result.ok) {
        if (result.reason === "http" && /\b(?:401|402|403)\b/.test(result.error)) paused = true;
        await write({ ...row, status: paused ? "paused" : "not-run", jevFlag: null, maxScore: null, scores: null, model: null, latencyMs: result.latencyMs, tokens: null, error: result.error });
        return undefined;
      }
      const scores = Object.fromEntries(Object.entries(result.answers).flatMap(([key, answer]) => {
        if (!answer || typeof answer !== "object" || !("noul" in answer) || typeof answer.noul !== "number") return [];
        return [[key, answer.noul]];
      }));
      const maxScore = Math.max(...Object.values(scores));
      await write({ ...row, status: "scored", jevFlag: maxScore > CUT, maxScore, scores, model: result.resolvedModel, latencyMs: result.latencyMs, tokens: result.usage ?? null });
    } catch { /* shadow-only: never affect bash execution */ }
    return undefined;
  };
}

export default function jevGateShadowHook(pi: { on: (event: string, handler: (event: unknown, ctx?: unknown) => unknown) => void }): void {
  const handler = makeGateShadowHandler();
  const seen = new Set<string>();
  const dispatch = (event: unknown, ctx?: unknown): unknown => {
    const e = event as Event;
    const id = typeof e?.toolCallId === "string" ? e.toolCallId : undefined;
    if (id && seen.has(id)) return undefined;
    if (id) { seen.add(id); setTimeout(() => seen.delete(id), 60_000); }
    let session = process.env.OMP_SESSION_ID ?? "unknown";
    try { session = (ctx as { sessionManager?: { getSessionId?: () => string } } | undefined)?.sessionManager?.getSessionId?.() ?? session; } catch { /* unknown: no egress */ }
    return handler(e, session);
  };
  pi.on("tool_call", dispatch);
  pi.on("tool_execution_start", dispatch);
}
