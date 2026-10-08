import { appendFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { homedir } from "node:os";
import { createHash } from "node:crypto";

export const LOG_SCHEMA = "jev-read-dedup.v2";
export const MAX_ENTRIES = 5000;
export const TURN_BOUND_CALLS = 150;

type CallEvent = { toolName?: unknown; toolCallId?: unknown; arguments?: unknown };
type Event = { toolName?: unknown; toolCallId?: unknown; content?: unknown; result?: unknown; isError?: unknown };
type Host = { on: (event: string, handler: (event: Event) => Promise<unknown>) => void };
type Deps = { append?: (path: string, line: string) => Promise<void>; path?: string; now?: () => string; maxEntries?: number; turnBoundCalls?: number };
function defaultPath(): string {
  return process.env.JEV_READ_DEDUP_PATH ?? join(homedir(), ".local", "state", "jev", "read-dedup-shadow.jsonl");
}

function text(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map((part) => part && typeof part === "object" && typeof part.text === "string" ? part.text : typeof part === "string" ? part : "").join("\n");
  return value && typeof value === "object" ? JSON.stringify(value) : "";
}

export function makeReadDedupHandler(deps: Deps = {}) {
  const path = deps.path ?? defaultPath();
  const now = deps.now ?? (() => new Date().toISOString());
  const maxEntries = deps.maxEntries ?? MAX_ENTRIES;
  const turnBound = deps.turnBoundCalls ?? TURN_BOUND_CALLS;
  const seen = new Map<string, { ts: string; chars: number; hits: number; callIndex: number; readPath: string }>();
  const pending = new Map<unknown, string>();
  const dirty = new Set<string>();
  let callsSeen = 0;
  const write = async (row: Record<string, unknown>): Promise<void> => {
    if (deps.append) {
      try { await deps.append(path, JSON.stringify(row)); } catch { /* observe-only */ }
      return;
    }
    try {
      await mkdir(dirname(path), { recursive: true, mode: 0o700 });
      await appendFile(path, JSON.stringify(row) + "\n", { mode: 0o600 });
    } catch { /* observe-only */ }
  };
  // Would-skip v2 (jev-p55p): identical bytes + path never edited since the
  // first read + within the call-gap bound. Compaction is invisible here;
  // the map lives per session process, so a host restart (the compaction
  // path) resets it — best-effort alignment, measured offline at 94% of
  // identical re-reads post-compaction. Observer class: never denies,
  // never rewrites; shadow rows only, result always passes through.
  const onCall = async (event: CallEvent): Promise<unknown> => {
    try {
      if (typeof event.toolName !== "string") return undefined;
      callsSeen += 1;
      const args = (event.arguments ?? {}) as Record<string, unknown>;
      if ((event.toolName === "edit" || event.toolName === "write") && typeof args.path === "string") {
        dirty.add(args.path);
      } else if (event.toolName === "read" && typeof args.path === "string") {
        pending.set(event.toolCallId, args.path);
      }
    } catch { /* fail open */ }
    return undefined;
  };
  const onResult = async (event: Event): Promise<unknown> => {
    try {
      if (event.isError === true || event.toolName !== "read") return undefined;
      const resultContent = (event.result as { content?: unknown } | null | undefined)?.content;
      const raw = text(event.content ?? resultContent);
      if (!raw) return undefined;
      const sha = createHash("sha256").update(raw).digest("hex");
      const readPath = pending.get(event.toolCallId) ?? "";
      const prev = seen.get(sha);
      if (prev) {
        prev.hits += 1;
        const gap = callsSeen - prev.callIndex;
        const edited = dirty.has(prev.readPath) || (readPath !== "" && dirty.has(readPath));
        if (!edited && gap <= turnBound) {
          await write({
            schema: LOG_SCHEMA, ts: now(), toolName: "read", outputSha256: sha,
            status: "would-skip", chars: raw.length, firstTs: prev.ts,
            repeats: prev.hits, gapCalls: gap, path: readPath === "" ? null : readPath,
          });
        } else {
          await write({
            schema: LOG_SCHEMA, ts: now(), toolName: "read", outputSha256: sha,
            status: "repeat-kept", chars: raw.length,
            reason: edited ? "edited-since-first-read" : "beyond-turn-bound",
            gapCalls: gap,
          });
        }
        return undefined;
      }
      if (seen.size >= maxEntries) {
        const oldest = seen.keys().next();
        if (!oldest.done) seen.delete(oldest.value);
      }
      seen.set(sha, { ts: now(), chars: raw.length, hits: 0, callIndex: callsSeen, readPath });
    } catch {
      // fail open: a broken observer must never break the session
    }
    return undefined;
  };
  return { onCall, onResult };
}

export default function jevReadDedupHook(host: Host, deps?: Deps): void {
  const handler = makeReadDedupHandler(deps);
  host.on("tool_call", handler.onCall);
  host.on("tool_result", handler.onResult);
}
