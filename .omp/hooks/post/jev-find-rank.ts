import { createHash } from "node:crypto";
import { mkdir, open } from "node:fs/promises";
import { dirname, join } from "node:path";
import { homedir } from "node:os";

export const MAX_NEXT_TOOL_CALLS = 10;
export const LOG_SCHEMA = "jev-find-rank.v1";

export type FindHit = { rel?: unknown };
export type ToolEvent = {
  toolName?: unknown;
  toolCallId?: unknown;
  input?: unknown;
  details?: unknown;
  content?: unknown;
  isError?: unknown;
};
export type HookContext = { sessionManager?: { getSessionId?: () => string } };
export type Append = (path: string, line: string) => Promise<void>;

export type LoggedWindow = {
  schema: typeof LOG_SCHEMA;
  ts: string;
  session: string;
  hits: string[];
  count: number;
  nextToolCalls: Array<{ ordinal: number; tool: string; touched: string[] }>;
  complete: boolean;
};

type PendingWindow = {
  session: string;
  createdAt: string;
  rawHits: string[];
  hashedHits: string[];
  nextToolCalls: Array<{ ordinal: number; tool: string; touched: string[] }>;
};

type FindRankDeps = {
  append?: Append;
  path?: string;
  now?: () => string;
  session?: string;
};

type FindRankHandler = ((event: unknown, ctx?: HookContext) => undefined) & {
  flush: () => Promise<void>;
  pending: () => number;
};

function defaultPath(): string {
  return process.env.JEV_FIND_RANK_PATH ?? join(homedir(), ".local", "state", "jev", "find-rank.jsonl");
}

async function defaultAppend(path: string, line: string): Promise<void> {
  await mkdir(dirname(path), { recursive: true, mode: 0o700 });
  const file = await open(path, "a", 0o600);
  try {
    await file.chmod(0o600);
    await file.appendFile(line + "\n");
  } finally {
    await file.close();
  }
}

function sessionId(ctx: HookContext | undefined, fallback: string): string {
  try {
    const current = ctx?.sessionManager?.getSessionId?.() as string | undefined;
    return (current ?? fallback) || process.env.OMP_SESSION_ID || "unknown";
  } catch {
    // Unknown session is still safe: no path or content is logged.
  }
  return fallback || process.env.OMP_SESSION_ID || "unknown";
}

export function hashPath(path: string): string {
  return createHash("sha256").update(path).digest("hex");
}

export function rankedPaths(details: unknown): string[] {
  if (!details || typeof details !== "object") return [];
  const hits = (details as Record<string, unknown>).hits;
  if (!Array.isArray(hits)) return [];
  return hits.flatMap((hit) => {
    if (!hit || typeof hit !== "object") return [];
    const rel = (hit as FindHit).rel;
    return typeof rel === "string" && rel ? [rel] : [];
  });
}

function inputValues(event: ToolEvent): string[] {
  const input = event.input;
  if (!input || typeof input !== "object") return [];
  const args = input as Record<string, unknown>;
  const tool = typeof event.toolName === "string" ? event.toolName : "";
  if (tool === "read" || tool === "write") return typeof args.path === "string" ? [args.path] : [];
  if (tool === "edit") return typeof args.input === "string" ? [args.input] : [];
  if (tool === "grep" || tool === "glob") {
    return [args.path, args.searchPath].filter((value): value is string => typeof value === "string");
  }
  if (tool === "bash") return typeof args.command === "string" ? [args.command] : [];
  return [];
}

export function touchedRanks(event: ToolEvent, rawHits: string[]): number[] {
  const tool = typeof event.toolName === "string" ? event.toolName : "";
  if (!["read", "edit", "write", "grep", "glob", "bash"].includes(tool)) return [];
  const values = inputValues(event);
  const ranks: number[] = [];
  for (const value of values) {
    rawHits.forEach((hit, index) => {
      if (value === hit || value.endsWith(`/${hit}`) || value.includes(hit)) ranks.push(index + 1);
    });
  }
  return [...new Set(ranks)].sort((a, b) => a - b);
}

function eventTool(event: unknown): string {
  const value = (event as ToolEvent | null)?.toolName;
  return typeof value === "string" ? value : "";
}

function makeRow(pending: PendingWindow): LoggedWindow {
  return {
    schema: LOG_SCHEMA,
    ts: pending.createdAt,
    session: pending.session,
    hits: pending.hashedHits,
    count: pending.hashedHits.length,
    nextToolCalls: pending.nextToolCalls,
    complete: pending.nextToolCalls.length >= MAX_NEXT_TOOL_CALLS,
  };
}

export function makeFindRankHandler(deps: FindRankDeps = {}): FindRankHandler {
  const path = deps.path ?? defaultPath();
  const append = deps.append ?? defaultAppend;
  const now = deps.now ?? (() => new Date().toISOString());
  const pending = new Map<string, PendingWindow[]>();
  const writes = new Set<Promise<void>>();

  const write = (row: LoggedWindow): void => {
    const operation = Promise.resolve(append(path, JSON.stringify(row))).catch(() => undefined);
    writes.add(operation);
    void operation.finally(() => writes.delete(operation));
  };

  const flushCompleted = (session: string): void => {
    const windows = pending.get(session) ?? [];
    const remaining: PendingWindow[] = [];
    for (const window of windows) {
      if (window.nextToolCalls.length >= MAX_NEXT_TOOL_CALLS) write(makeRow(window));
      else remaining.push(window);
    }
    if (remaining.length) pending.set(session, remaining);
    else pending.delete(session);
  };

  const flush = async (): Promise<void> => {
    for (const windows of pending.values()) {
      for (const window of windows) write(makeRow(window));
    }
    pending.clear();
    await Promise.all([...writes]);
  };

  const handler = ((event: unknown, ctx?: HookContext): undefined => {
    try {
      const typed = (event ?? {}) as ToolEvent;
      const session = sessionId(ctx, deps.session ?? "");
      const tool = eventTool(typed);
      const isResult = "details" in typed || "content" in typed || "isError" in typed;
      if (tool === "find" && isResult && typed.isError !== true) {
        const rawHits = rankedPaths(typed.details);
        const window: PendingWindow = {
          session,
          createdAt: now(),
          rawHits,
          hashedHits: rawHits.map(hashPath),
          nextToolCalls: [],
        };
        pending.set(session, [...(pending.get(session) ?? []), window]);
      } else if (!isResult) {
        const windows = pending.get(session) ?? [];
        for (const window of windows) {
          if (window.nextToolCalls.length >= MAX_NEXT_TOOL_CALLS) continue;
          const touched = touchedRanks(typed, window.rawHits).map((rank) => window.hashedHits[rank - 1]);
          window.nextToolCalls.push({ ordinal: window.nextToolCalls.length + 1, tool, touched });
        }
        flushCompleted(session);
      }
    } catch {
      // Observe-only: logger failure must never affect tool execution.
    }
    return undefined;
  }) as FindRankHandler;

  handler.flush = flush;
  handler.pending = () => [...pending.values()].reduce((sum, windows) => sum + windows.length, 0);
  return handler;
}

export default function jevFindRankHook(pi: {
  on: (event: string, handler: (event: unknown, ctx?: HookContext) => unknown) => void;
}): void {
  const handler = makeFindRankHandler();
  pi.on("tool_result", handler);
  pi.on("tool_call", handler);
  pi.on("session_shutdown", () => handler.flush());
}
