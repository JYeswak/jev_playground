import { appendFile, mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { homedir } from "node:os";
import { createHash } from "node:crypto";

export const LOG_SCHEMA = "jev-read-dedup.v1";
export const MAX_ENTRIES = 5000;

type Event = { toolName?: unknown; toolCallId?: unknown; content?: unknown; result?: unknown; isError?: unknown };
type Host = { on: (event: string, handler: (event: Event) => Promise<unknown>) => void };
type Deps = { append?: (path: string, line: string) => Promise<void>; path?: string; now?: () => string; maxEntries?: number };

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
  const seen = new Map<string, { ts: string; chars: number; hits: number }>();
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
  return async (event: Event): Promise<unknown> => {
    try {
      // Observer class (rust-hook-pattern ladder): never denies, never rewrites.
      // Shadow only: log would-skip, always pass the result through unchanged.
      if (event.isError === true || event.toolName !== "read") return undefined;
      const resultContent = (event.result as { content?: unknown } | null | undefined)?.content;
      const raw = text(event.content ?? resultContent);
      if (!raw) return undefined;
      const sha = createHash("sha256").update(raw).digest("hex");
      const prev = seen.get(sha);
      if (prev) {
        prev.hits += 1;
        await write({
          schema: LOG_SCHEMA, ts: now(), toolName: "read", outputSha256: sha,
          status: "would-skip", chars: raw.length, firstTs: prev.ts, repeats: prev.hits,
        });
        return undefined;
      }
      if (seen.size >= maxEntries) {
        const oldest = seen.keys().next();
        if (!oldest.done) seen.delete(oldest.value);
      }
      seen.set(sha, { ts: now(), chars: raw.length, hits: 0 });
    } catch {
      // fail open: a broken observer must never break the session
    }
    return undefined;
  };
}

export default function jevReadDedupHook(host: Host, deps?: Deps): void {
  host.on("tool_result", makeReadDedupHandler(deps));
}
