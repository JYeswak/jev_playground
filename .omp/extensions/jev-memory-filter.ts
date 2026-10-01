/** Memory-relevance filter, Phase 1 shadow (bead jev-7vn9, design work/jev-7vn9-design.md).
 *
 * On the `context` event the handler parses `<memories>` and EE task-context
 * blocks out of the LLM-bound message copy, scores each item with the
 * held-out-winning Noul (base wording, DROP iff noul < 0.5, invalid -> KEEP;
 * loss depth PASS 0.978, commit 9ff9f951), and logs keep/drop + tokens that
 * would be saved. It NEVER modifies anything: the handler always yields
 * undefined. Bounded per AGENTS.md: max 20 items/turn, daily call cap in
 * code, stop on 401/402/403, fail safe (KEEP) on invalid/timeout/throw.
 */
import { appendFile, mkdir } from "node:fs/promises";
import { createHash } from "node:crypto";
import { homedir } from "node:os";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { askJev, type AskOptions, type JevResult } from "../../kit/src/client.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

export const MODEL = "jev-1.13.0";
export const CUT = 0.5;
export const MAX_ITEMS_PER_TURN = 20;
export const MAX_DAILY_CALLS = 200;
export const CALL_TIMEOUT_MS = 15000;
export const TURN_BUDGET_MS = 45000;
export const PROMPT_CHARS = 2000;
const LOG_SCHEMA = "jev-memory-filter.v1";
const SIDECAR_SCHEMA = "jev-memory-filter-full.v1";
export const MAX_MEMO = 2000;

// One extension load serves one session process: rows stay attributable.
const INSTANCE = randomUUID().slice(0, 8);

type Ask = (options: AskOptions) => Promise<JevResult>;

export type MemoryItem = { text: string };

/** Split injected memory blocks into items. Exported for tests. */
export function parseMemories(messages: unknown): MemoryItem[] {
  const texts: string[] = [];
  const walk = (node: unknown): void => {
    if (typeof node === "string") {
      if (node.includes("<memories>") || node.includes("Task-relevant local EE memories")) texts.push(node);
      return;
    }
    if (Array.isArray(node)) {
      for (const child of node) walk(child);
      return;
    }
    if (node && typeof node === "object") {
      for (const value of Object.values(node as Record<string, unknown>)) walk(value);
    }
  };
  walk(messages);
  const items: MemoryItem[] = [];
  for (const text of texts) {
    const blocks: string[] = [];
    const memRe = /<memories>([\s\S]*?)<\/memories>/g;
    let m: RegExpExecArray | null;
    while ((m = memRe.exec(text)) !== null) blocks.push(m[1]);
    const eeIndex = text.indexOf("Task-relevant local EE memories");
    if (eeIndex >= 0) blocks.push(text.slice(eeIndex));
    for (const block of blocks) {
      for (const line of block.split("\n")) {
        const clean = line.replace(/^[\s>*•\-–\d.)]+/, "").trim();
        if (clean.length > 1) items.push({ text: clean.slice(0, 2000) });
      }
    }
  }
  const seen: Record<string, true> = {};
  return items.filter((item) => {
    if (seen[item.text]) return false;
    seen[item.text] = true;
    return true;
  });
}

/** Last user-role message text, the Noul's prompt side. Exported for tests. */
export function currentPrompt(messages: unknown): string {
  let last = "";
  const walk = (node: unknown): void => {
    if (Array.isArray(node)) {
      for (const child of node) walk(child);
      return;
    }
    if (node && typeof node === "object") {
      const record = node as Record<string, unknown>;
      if (record["role"] === "user") {
        const content = record["content"];
        if (typeof content === "string") last = content;
        else if (Array.isArray(content)) {
          for (const part of content) {
            if (part && typeof part === "object" && (part as Record<string, unknown>)["type"] === "text") {
              const text = (part as Record<string, unknown>)["text"];
              if (typeof text === "string") last += text + "\n";
            }
          }
        }
      } else {
        for (const value of Object.values(record)) walk(value);
      }
    }
  };
  walk(messages);
  return last.slice(0, PROMPT_CHARS);
}

const INSTRUCTIONS = "Memory: `memory`. Current request: `prompt`. Is this memory relevant to the current request?";

export type FilterDeps = { ask?: Ask; cap?: number; path?: string; sidecarPath?: string; now?: () => string };

export function makeMemoryFilterHandler(deps: FilterDeps = {}) {
  const ask = deps.ask ?? askJev;
  const cap = deps.cap ?? MAX_DAILY_CALLS;
  const path = deps.path ?? process.env.JEV_MEMORY_FILTER_LOG_PATH ?? join(homedir(), ".local", "state", "jev", "memory-filter.jsonl");
  const sidecar = deps.sidecarPath ?? process.env.JEV_MEMORY_FILTER_SIDECAR_PATH ?? join(homedir(), ".local", "state", "jev", "memory-filter-full.jsonl");
  const now = deps.now ?? (() => new Date().toISOString());
  let day = "";
  let calls = 0;
  let paused = false;
  // Per-instance memo: identical (prompt, memory) pairs reappear every context
  // event of a long turn. Reuse the verdict instead of re-spending a call.
  const memo = new Map<string, { noul: number; decision: string; inputTokens: number | null }>();
  const write = async (row: Record<string, unknown>): Promise<void> => {
    try {
      await mkdir(join(homedir(), ".local", "state", "jev"), { recursive: true });
      await appendFile(path, JSON.stringify(row) + "\n", { mode: 0o600 });
    } catch {
      // Logging never blocks the turn.
    }
  };
  const writeSidecar = async (row: Record<string, unknown>): Promise<void> => {
    try {
      await mkdir(join(homedir(), ".local", "state", "jev"), { recursive: true });
      await appendFile(sidecar, JSON.stringify(row) + "\n", { mode: 0o600 });
    } catch {
      // Logging never blocks the turn.
    }
  };
  return async (event: { messages?: unknown }): Promise<undefined> => {
    try {
      const messages = event?.messages;
      if (!messages) return undefined;
      const currentDay = now().slice(0, 10);
      if (currentDay !== day) {
        day = currentDay;
        calls = 0;
        paused = false;
      }
      const items = parseMemories(messages).slice(0, MAX_ITEMS_PER_TURN);
      const prompt = currentPrompt(messages);
      const promptHash = createHash("sha256").update(prompt).digest("hex");
      const started = Date.now();
      for (const item of items) {
        if (Date.now() - started > TURN_BUDGET_MS) break;
        const memoryHash = createHash("sha256").update(item.text).digest("hex");
        const memoKey = promptHash + ":" + memoryHash;
        const cached = memo.get(memoKey);
        if (cached !== undefined) {
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "memo", promptHash, memoryHash, noul: cached.noul, decision: cached.decision, tokensSaved: cached.decision === "drop" ? Math.floor(item.text.length / 4) : 0, latencyMs: null, inputTokens: cached.inputTokens });
          await writeSidecar({ schema: SIDECAR_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "memo", promptHash, memoryHash, prompt, memory: item.text, noul: cached.noul, decision: cached.decision });
          continue;
        }
        if (paused || calls >= cap) {
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: paused ? "paused" : "daily-cap", promptHash, memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: null, inputTokens: null });
          continue;
        }
        calls += 1;
        const t0 = Date.now();
        let result: JevResult;
        try {
          result = await ask({
            state: { prompt, memory: item.text },
            questions: { rel: { instructions: INSTRUCTIONS } },
            model: MODEL,
            timeoutMs: CALL_TIMEOUT_MS,
          });
        } catch (error) {
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "fail_open", promptHash, memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: Date.now() - t0, inputTokens: null, error: error instanceof Error ? error.message : String(error) });
          continue;
        }
        if (!result.ok) {
          if (/\bHTTP (?:401|402|403)\b/.test(result.error)) paused = true;
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "fail_open", promptHash, memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: result.latencyMs, inputTokens: null, error: result.error });
          continue;
        }
        const noul = result.scores["rel"];
        if (typeof noul !== "number" || !Number.isFinite(noul)) {
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "invalid-keep", promptHash, memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null });
          continue;
        }
        const drop = noul < CUT;
        const decision = drop ? "drop" : "keep";
        if (memo.size >= MAX_MEMO) {
          const oldest = memo.keys().next();
          if (!oldest.done) memo.delete(oldest.value);
        }
        memo.set(memoKey, { noul, decision, inputTokens: result.usage?.input_tokens ?? null });
        await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "scored", promptHash, memoryHash, noul, decision, tokensSaved: drop ? Math.floor(item.text.length / 4) : 0, latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null });
        await writeSidecar({ schema: SIDECAR_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "scored", promptHash, memoryHash, prompt, memory: item.text, noul, decision });
      }
    } catch {
      // Shadow failures never affect the turn.
    }
    return undefined;
  };
}

export default function jevMemoryFilterExtension(
  pi: { on: (event: string, handler: (event: { messages?: unknown }) => Promise<unknown>) => void },
  deps: FilterDeps = {},
): void {
  if (!deps.ask) useInfisicalKey();
  pi.on("context", makeMemoryFilterHandler(deps));
}
