import { createHash } from "node:crypto";
import { mkdir, open } from "node:fs/promises";
import { dirname, join } from "node:path";
import { homedir } from "node:os";
import { askJevChoice } from "../../../kit/src/client.ts";
import { useInfisicalKey } from "../../../work/jev-client/src/use-infisical-key.ts";
import { rerankTop1, type RerankOptions } from "../../../kit/src/rerank.ts";
export const MODEL = "jev-1.13.0";
export const MAX_RESULTS = 20;
export const MAX_NEXT_TOOL_CALLS = 10;
export const LOG_SCHEMA = "jev-web-search-rerank.v1";


export type SearchEvent = {
  toolName?: unknown;
  toolCallId?: unknown;
  input?: unknown;
  args?: unknown;
  details?: unknown;
  result?: unknown;
  content?: unknown;
  isError?: unknown;
};
type HookContext = { sessionManager?: { getSessionId?: () => string | undefined } };
type Ask = NonNullable<RerankOptions["ask"]>;
type Append = (path: string, line: string) => Promise<void>;

type ResultItem = {
  id: string;
  title: string;
  text: string;
  url?: string;
};

type Pending = {
  sessionHash: string;
  queryHash: string;
  query: string;
  items: ResultItem[];
  pickIndex: number | null;
  latencyMs: number | null;
  inputTokens: number | null;
  outputTokens: number | null;
  nextCalls: number;
  openedPick: boolean;
  openedRank1: boolean;
  status: string;
  error: string | null;
  openedHashes: Set<string>;
};

type ShadowDeps = {
  ask?: Ask;
  append?: Append;
  path?: string;
  now?: () => string;
  session?: string;
  cap?: number;
  enabled?: boolean;
};

function defaultPath(): string {
  return process.env.JEV_WEB_SEARCH_RERANK_PATH ?? join(homedir(), ".local", "state", "jev", "websearch-rerank.jsonl");
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

export function hashValue(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}

function dayKey(now: () => string): string {
  return now().slice(0, 10);
}

function stringValue(value: unknown): string | undefined {
  return typeof value === "string" && value ? value : undefined;
}

function rawText(content: unknown): string | undefined {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content.map((part) => {
      if (typeof part === "string") return part;
      if (part && typeof part === "object") {
        const text = (part as Record<string, unknown>).text;
        if (typeof text === "string") return text;
      }
      return "";
    }).join("\n");
  }
  if (content && typeof content === "object") return JSON.stringify(content);
  return undefined;
}

function parseJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

export function parseSearchResult(event: SearchEvent): { query: string; items: ResultItem[] } | undefined {
function markdownItems(text: string): ResultItem[] {
  const pattern = /(?:^|\n)\[(\d+)\]\s+([^\n]+)\n\s+(https?:\/\/\S+)([\s\S]*?)(?=\n\[\d+\]\s+|$)/g;
  return [...text.matchAll(pattern)].slice(0, MAX_RESULTS).map((match, index) => ({
    id: `result-${index}`, title: match[2].trim(), url: match[3].trim(), text: match[4].trim(),
  }));
}
  const source = event.input ?? event.args;
  const input = source && typeof source === "object" ? source as Record<string, unknown> : {};
  const query = stringValue(input.query) ?? stringValue(input.q);
  const execution = event.result && typeof event.result === "object" ? event.result as Record<string, unknown> : {};
  const details = event.details ?? execution.details;
  const content = event.content ?? execution.content;
  const parsedDetails = details && typeof details === "object" && !Array.isArray(details)
    && (Array.isArray((details as Record<string, unknown>).results) || Array.isArray((details as Record<string, unknown>).items))
    ? details : undefined;
  const raw = rawText(content) ?? rawText(details) ?? "";
  const parsed = parsedDetails ?? parseJson(raw);
  const root = parsed && typeof parsed === "object" ? parsed as Record<string, unknown> : {};
  const jsonItems = Array.isArray(root.results) ? root.results : Array.isArray(root.items) ? root.items : [];
  const rawItems = jsonItems.length >= 2 ? jsonItems : markdownItems(raw);
  if (!query || rawItems.length < 2) return undefined;
  const items = rawItems.slice(0, MAX_RESULTS).flatMap((item, index) => {
    if (!item || typeof item !== "object") return [];
    const row = item as Record<string, unknown>;
    const url = stringValue(row.url) ?? stringValue(row.link);
    const title = stringValue(row.title) ?? "";
    const text = stringValue(row.snippet) ?? stringValue(row.text) ?? stringValue(row.description) ?? "";
    if (!url && !text) return [];
    return [{ id: `result-${index}`, title, text, ...(url ? { url } : {}) }];
  });
  return items.length >= 2 ? { query, items } : undefined;
}

function eventTool(event: SearchEvent): string {
  return stringValue(event.toolName) ?? "";
}

function openHashes(event: SearchEvent): Set<string> {
  const input = event.input && typeof event.input === "object" ? event.input as Record<string, unknown> : {};
  const values = [input.url, input.path, input.query, input.input].flatMap((value) => typeof value === "string" ? [value] : []);
  return new Set(values.map(hashValue));
}

function isOpenEvent(event: SearchEvent): boolean {
  return ["read", "fetch", "web_extract", "open_url"].includes(eventTool(event));
}

function stopReason(result: { reason?: string; error?: string }): string | undefined {
  const error = result.error ?? "";
  if (/\b(?:401|402|403)\b/.test(error) || ["billing-hold", "http-401", "http-402", "http-403"].includes(result.reason ?? "")) return "auth-or-billing";
  return undefined;
}

function loggedRow(pending: Pending, now: () => string): Record<string, unknown> {
  return {
    schema: LOG_SCHEMA,
    ts: now(),
    sessionHash: pending.sessionHash,
    queryHash: pending.queryHash,
    resultCount: pending.items.length,
    pickIndex: pending.pickIndex,
    providerRank1Index: 0,
    latencyMs: pending.latencyMs,
    inputTokens: pending.inputTokens,
    outputTokens: pending.outputTokens,
    nextToolCalls: pending.nextCalls,
    openedPick: pending.openedPick,
    openedRank1: pending.openedRank1,
    status: pending.status,
    error: pending.error,
  };
}

export function makeWebSearchRerankHandler(deps: ShadowDeps = {}) {
  const ask = deps.ask ?? askJevChoice;
  const append = deps.append ?? defaultAppend;
  const path = deps.path ?? defaultPath();
  const now = deps.now ?? (() => new Date().toISOString());
  const cap = deps.cap ?? Number(process.env.JEV_WEB_SEARCH_RERANK_DAILY_CAP ?? "100");
  let day = dayKey(now);
  let calls = 0;
  let paused = false;
  const pending = new Map<string, Pending>();
  const seenEvents = new Set<string>();
  const write = (row: Record<string, unknown>): void => {
    void Promise.resolve(append(path, JSON.stringify(row))).catch(() => undefined);
  };

  const handler = async (event: SearchEvent, ctx?: HookContext): Promise<undefined> => {
    try {
      const session = ctx?.sessionManager?.getSessionId?.() ?? deps.session;
      if (!session) return undefined;
      const key = hashValue(session);
      const eventId = typeof event.toolCallId === "string" ? event.toolCallId : undefined;
      const dedupKey = eventId ? `${key}:${eventId}` : undefined;
      if (dedupKey && seenEvents.has(dedupKey)) return undefined;
      if (dedupKey) { seenEvents.add(dedupKey); setTimeout(() => seenEvents.delete(dedupKey), 60_000); }
      const currentDay = dayKey(now);
      if (currentDay !== day) { day = currentDay; calls = 0; paused = false; }
      const active = pending.get(key);
      if (active) {
        active.nextCalls += 1;
        if (isOpenEvent(event)) {
          const opened = openHashes(event);
          const selectedUrl = active.pickIndex === null ? undefined : active.items[active.pickIndex]?.url;
          active.openedPick ||= selectedUrl !== undefined && opened.has(hashValue(selectedUrl));
          active.openedRank1 ||= active.items[0]?.url !== undefined && opened.has(hashValue(active.items[0].url));
        }
        if (active.nextCalls >= MAX_NEXT_TOOL_CALLS) { write(loggedRow(active, now)); pending.delete(key); }
      }
      if (isOpenEvent(event)) return undefined;
      const parsed = parseSearchResult(event);
      if (!parsed) return undefined;
      if (active && pending.get(key) === active) {
        write(loggedRow(active, now));
        pending.delete(key);
      }
      const base: Pending = {
        sessionHash: key,
        queryHash: hashValue(parsed.query),
        query: parsed.query,
        items: parsed.items,
        pickIndex: null,
        latencyMs: null,
        inputTokens: null,
        outputTokens: null,
        nextCalls: 0,
        openedPick: false,
        openedRank1: false,
        status: "not-admitted",
        error: null,
        openedHashes: new Set(),
      };
      base.error = null;
      if (paused || calls >= cap) { write(loggedRow(base, now)); return undefined; }
      calls += 1;
      try {
        const result = await Promise.race([
          rerankTop1({ query: parsed.query, candidates: parsed.items, ask, model: MODEL }),
          new Promise<never>((_, reject) => setTimeout(() => reject(new Error("rerank shadow timeout")), 25_000)),
        ]);
        base.pickIndex = parsed.items.findIndex((item) => item.id === result.choice);
        base.latencyMs = result.latencyMs;
        base.inputTokens = result.usage?.input_tokens ?? null;
        base.outputTokens = result.usage?.output_tokens ?? null;
        base.status = "answered";
        pending.set(key, base);
      } catch (error) {
        const reason = stopReason({ reason: "", error: String(error) });
        if (reason) paused = true;
        base.status = reason ? "auth-or-billing" : "error";
        base.error = String(error instanceof Error ? error.message : error);
        write(loggedRow(base, now));
      }
    } catch {
      // Shadow failures never affect the observed web_search result.
    }
    return undefined;
  };
  return handler;
}

/** OFF by default (jev-ib1h loss depth 2026-10-01: 0 opens in 15 answered, 4
 * discriminating cases below the 6-case bar; spend stopped here). There is no
 * config hook switch, so the factory itself is the switch: pass
 * enabled:true (or JEV_WEB_SEARCH_RERANK_ENABLED=1) to re-enable for study.
 * Sessions keep working; only Jev scoring + logging stop. */
export default function jevWebSearchRerankHook(
  host: { on: (event: string, handler: (event: SearchEvent, ctx?: HookContext) => Promise<undefined>) => void },
  deps: ShadowDeps = {},
): void {
  const enabled = deps.enabled ?? process.env.JEV_WEB_SEARCH_RERANK_ENABLED === "1";
  if (!enabled) return;
  if (!deps.ask) useInfisicalKey();
  const handler = makeWebSearchRerankHandler(deps);
  host.on("tool_result", handler);
  host.on("tool_execution_end", handler);
}
