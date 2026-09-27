import { appendFileSync, mkdirSync } from "node:fs";
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { homedir } from "node:os";

export const MODEL = "jev-1.13.0";
export const MAX_DAILY_CALLS = 100;
export const LOG_SCHEMA = "jev-injection-shadow.v1";

type Event = { toolName?: unknown; toolCallId?: unknown; content?: unknown; result?: unknown; isError?: unknown };
type Host = { on: (event: string, handler: (event: Event) => Promise<unknown>) => void };

type Deps = { append?: (path: string, line: string) => Promise<void>; path?: string; cap?: number; now?: () => string };

function defaultPath(): string { return process.env.JEV_INJECTION_SHADOW_PATH ?? join(homedir(), ".local", "state", "jev", "injection-shadow.jsonl"); }
function hash(value: string): string { return createHash("sha256").update(value).digest("hex"); }
function text(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map((part) => part && typeof part === "object" && typeof part.text === "string" ? part.text : typeof part === "string" ? part : "").join("\n");
  return value && typeof value === "object" ? JSON.stringify(value) : "";
}
function outputText(event: Event): string {
  const result = event.result && typeof event.result === "object" ? event.result as Record<string, unknown> : {};
  return text(event.content ?? result.content);
}
function syncObserved(path: string, row: Record<string, unknown>): void {
  try { mkdirSync(dirname(path), { recursive: true, mode: 0o700 }); appendFileSync(path, JSON.stringify(row) + "\n", { mode: 0o600 }); } catch { /* observe-only */ }
}
function launch(path: string, row: Record<string, unknown>, raw: string): void {
  try {
    const child = spawn(process.execPath, ["--experimental-strip-types", join(process.cwd(), ".omp", "hooks", "jev-shadow-worker.ts")], { detached: true, stdio: ["pipe", "ignore", "ignore"] });
    child.stdin.write(JSON.stringify({ kind: "injection", path, row, text: raw })); child.stdin.end(); child.unref();
  } catch { /* observe-only */ }
}

export function makeInjectionShadowHandler(deps: Deps = {}) {
  const path = deps.path ?? defaultPath();
  const cap = deps.cap ?? Number(process.env.JEV_INJECTION_SHADOW_DAILY_CAP ?? String(MAX_DAILY_CALLS));
  const now = deps.now ?? (() => new Date().toISOString());
  let calls = 0;
  let day = now().slice(0, 10);
  const write = async (row: Record<string, unknown>): Promise<void> => {
    if (deps.append) { await deps.append(path, JSON.stringify(row)); return; }
    syncObserved(path, row);
  };
  return async (event: Event): Promise<undefined> => {
    const current = now().slice(0, 10); if (current !== day) { day = current; calls = 0; }
    if (event.isError === true) return undefined;
    const raw = outputText(event); if (!raw) return undefined;
    if (calls >= cap) { await write({ schema: LOG_SCHEMA, ts: now(), toolName: event.toolName ?? null, outputSha256: hash(raw), status: "cap" }); return undefined; }
    calls += 1;
    const row = { schema: LOG_SCHEMA, ts: now(), toolName: event.toolName ?? null, outputSha256: hash(raw), status: "observed" };
    await write(row); launch(path, row, raw); return undefined;
  };
}

export default function jevInjectionShadowHook(host: Host): void {
  const seen = new Set<string>(); const handler = makeInjectionShadowHandler();
  const observe = (event: Event): Promise<undefined> => { const id = typeof event.toolCallId === "string" ? event.toolCallId : undefined; if (id && seen.has(id)) return Promise.resolve(undefined); if (id) { seen.add(id); setTimeout(() => seen.delete(id), 60_000); } return handler(event); };
  host.on("tool_result", observe); host.on("tool_execution_end", observe);
}
