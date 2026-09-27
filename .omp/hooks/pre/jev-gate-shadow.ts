import { createHash } from "node:crypto";
import { mkdir, open } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { askJevBundle, type AskBundleOptions, type JevBundleResult } from "../../../kit/src/client.ts";
import { useInfisicalKey } from "../../../work/jev-client/src/use-infisical-key.ts";
declare const process: { env: Record<string, string | undefined> };
import { CUT, RISK, STATE_CONTEXT } from "../../../work/bicameral-gate/questions.mjs";

export const MODEL = "jev-1.13.0";
export const MAX_DAILY_CALLS = 100;
export const LOG_SCHEMA = "jev-gate-shadow.v1";

type Event = { toolName?: unknown; name?: unknown; input?: unknown; command?: unknown; details?: unknown };
type Append = (path: string, line: string) => Promise<void>;
type Ask = (options: AskBundleOptions) => Promise<JevBundleResult>;
type ShadowDeps = { ask?: Ask; append?: Append; path?: string; session?: string; cap?: number; now?: () => string };

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
  const input = event.input && typeof event.input === "object" ? event.input as Record<string, unknown> : {};
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
  if (!ask) useInfisicalKey();
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
      if (dayKey(now) !== day) { day = dayKey(now); calls = 0; paused = false; }
      const observedFlag = existingFlag(event);
      const row = { ...baseRow(command, session, now), existingFlag: observedFlag, existingFlagSource: observedFlag === null ? "gate-observe.jsonl:cmdSha" : "event.details.existingFlag" };
      if (paused) { await write({ ...row, status: "paused", jevFlag: null, maxScore: null, scores: null, model: null, latencyMs: null, tokens: null }); return undefined; }
      if (calls >= cap) { await write({ ...row, status: "cap", jevFlag: null, maxScore: null, scores: null, model: null, latencyMs: null, tokens: null }); return undefined; }
      calls += 1;
      let result: JevBundleResult;
      try {
        result = await (ask ?? askJevBundle)({ state: { command, context: STATE_CONTEXT }, questions: RISK, model: MODEL, timeoutMs: 20_000 });
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
  pi.on("tool_call", makeGateShadowHandler() as (event: unknown, ctx?: unknown) => unknown);
}
