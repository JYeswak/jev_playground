/** Memory-relevance filter, Phase 1 shadow (bead jev-s47b; design work/jev-7vn9-design.md).
 *
 * On `before_agent_start` the handler parses `<memories>` and EE task-context
 * blocks out of the system prompt (event.systemPrompt, via ctx.getSystemPrompt
 * when present), scores each item against the user prompt with the
 * held-out-winning Noul (base wording, DROP iff noul < 0.5, invalid -> KEEP;
 * loss depth PASS 0.978, commit 9ff9f951), and logs keep/drop + tokens that
 * would be saved. It NEVER modifies anything: the handler always yields
 * undefined. Bounded per AGENTS.md: max 20 items/turn, daily call cap in
 * code, stop on 401/402/403, fail safe (KEEP) on invalid/timeout/throw.
 */
import { appendFile, mkdir, readFile } from "node:fs/promises";
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

/** Memory bullets live in the system prompt (omp memory backend injects
 * there), never in conversation messages: live `context`-event payloads
 * carry only user/assistant/toolResult/developer roles (jev-s47b:
 * 4,275 messages, zero system-role). Parse the prompt text, not messages. */
export function systemPromptText(sys: unknown): string {
  if (typeof sys === "string") return sys;
  if (Array.isArray(sys)) {
    const parts: string[] = [];
    for (const block of sys) {
      if (typeof block === "string") parts.push(block);
      else if (block && typeof block === "object") {
        const text = (block as Record<string, unknown>)["text"];
        if (typeof text === "string") parts.push(text);
      }
    }
    return parts.join("\n");
  }
  return JSON.stringify(sys ?? "");
}

/** Split one text into memory items. Exported for tests. */
export function splitMemoryBlocks(text: string): MemoryItem[] {
  const blocks: string[] = [];
  const memRe = /<memories>([\s\S]*?)<\/memories>/g;
  let m: RegExpExecArray | null;
  while ((m = memRe.exec(text)) !== null) blocks.push(m[1]);
  const eeIndex = text.indexOf("Task-relevant local EE memories");
  if (eeIndex >= 0) blocks.push(text.slice(eeIndex));
  const items: MemoryItem[] = [];
  for (const block of blocks) {
    for (const line of block.split("\n")) {
      const clean = line.replace(/^[\s>*•\-–\d.)]+/, "").trim();
      if (clean.length > 1) items.push({ text: clean.slice(0, 2000) });
    }
  }
  const seen: Record<string, true> = {};
  return items.filter((item) => {
    if (seen[item.text]) return false;
    seen[item.text] = true;
    return true;
  });
}

/** Genuine memory bullets from a system prompt. Each prompt element is parsed
 * separately: recall arrives as its own appended element, and joining first
 * would merge the instruction mention (no closing tag) with the recall close,
 * flooding the cap with static prompt text between them (live 2026-10-01:
 * merged span swallowed the whole tool-routes section). */
export function parseSystemMemories(sys: unknown): MemoryItem[] {
  const texts = Array.isArray(sys) ? (sys as unknown[]).map((b) => (typeof b === "string" ? b : systemPromptText(b))) : [systemPromptText(sys)];
  const seen: Record<string, true> = {};
  const items: MemoryItem[] = [];
  for (const text of texts) {
    for (const item of splitMemoryBlocks(text)) {
      if (seen[item.text]) continue;
      seen[item.text] = true;
      items.push(item);
    }
  }
  return items;
}

/** Removal path (default OFF): file presence enables, read per fire so no
 * restart is needed to flip. Return contract proven live 2026-10-01: a raw
 * string return is ignored, `{ systemPrompt }` replaces the prompt. */
export async function enforceEnabled(switchPath: string): Promise<boolean> {
  try {
    await readFile(switchPath, "utf8");
    return true;
  } catch {
    return false;
  }
}

/** Clean one raw line exactly as the splitter does. */
function cleanLine(line: string): string {
  return line.replace(/^[\s>*•\-–\d.)]+/, "").trim();
}

/** Drop exactly the decided-drop lines, byte-preserving everything else.
 * Keeps are never touched; unknown shapes pass through unchanged. */
export function pruneSystemPrompt(sys: unknown, dropped: Set<string>): unknown {
  const pruneText = (text: string): string => {
    if (dropped.size === 0) return text;
    const kept = text.split("\n").filter((line) => !dropped.has(cleanLine(line)) || cleanLine(line).length <= 1);
    return kept.join("\n");
  };
  if (typeof sys === "string") return pruneText(sys);
  if (Array.isArray(sys)) {
    return (sys as unknown[]).map((b) => {
      if (typeof b === "string") return pruneText(b);
      if (b && typeof b === "object" && typeof (b as Record<string, unknown>)["text"] === "string") {
        return { ...(b as Record<string, unknown>), text: pruneText((b as Record<string, unknown>)["text"] as string) };
      }
      return b;
    });
  }
  return sys;
}

const INSTRUCTIONS = "Memory: `memory`. Current request: `prompt`. Is this memory relevant to the current request?";


export type FilterDeps = { ask?: Ask; cap?: number; path?: string; sidecarPath?: string; now?: () => string; switchPath?: string };

export function makeBeforeAgentStartHandler(deps: FilterDeps = {}) {
  const switchPath = deps.switchPath ?? process.env.JEV_MEMORY_FILTER_ENFORCE_PATH ?? join(homedir(), ".local", "state", "jev", "memory-filter-enforce");
  const ask = deps.ask ?? askJev;
  const cap = deps.cap ?? MAX_DAILY_CALLS;
  const path = deps.path ?? process.env.JEV_MEMORY_FILTER_LOG_PATH ?? join(homedir(), ".local", "state", "jev", "memory-filter.jsonl");
  const sidecar = deps.sidecarPath ?? process.env.JEV_MEMORY_FILTER_SIDECAR_PATH ?? join(homedir(), ".local", "state", "jev", "memory-filter-full.jsonl");
  const now = deps.now ?? (() => new Date().toISOString());
  let day = "";
  let calls = 0;
  let paused = false;
  // Per-instance memo: re-entry retries and repeated turns resubmit identical
  // (prompt, memory) pairs. Reuse the verdict instead of re-spending a call.
  const memo = new Map<string, { noul: number; decision: string; inputTokens: number | null }>();
  let fireRepo: string | null = null;
  const write = async (row: Record<string, unknown>): Promise<void> => {
    try {
      await mkdir(join(homedir(), ".local", "state", "jev"), { recursive: true });
      await appendFile(path, JSON.stringify({ ...row, repo: fireRepo }) + "\n", { mode: 0o600 });
    } catch {
      // Logging never blocks the turn.
    }
  };
  const writeSidecar = async (row: Record<string, unknown>): Promise<void> => {
    try {
      await mkdir(join(homedir(), ".local", "state", "jev"), { recursive: true });
      await appendFile(sidecar, JSON.stringify({ ...row, repo: fireRepo }) + "\n", { mode: 0o600 });
    } catch {
      // Logging never blocks the turn.
    }
  };
  return async (event: unknown, ctx?: unknown): Promise<undefined | { systemPrompt: unknown }> => {
    const dropped = new Set<string>();
    try {
      const ev = (event ?? {}) as Record<string, unknown>;
      const rawPrompt = ev["prompt"];
      const prompt = (typeof rawPrompt === "string" ? rawPrompt : JSON.stringify(rawPrompt ?? "")).slice(0, PROMPT_CHARS);
      if (!prompt) return undefined;
      let sys: unknown;
      try {
        sys = (ctx as { getSystemPrompt?: () => unknown } | undefined)?.getSystemPrompt?.() ?? ev["systemPrompt"];
      } catch {
        return undefined;
      }
      const currentDay = now().slice(0, 10);
      fireRepo = (ctx as { cwd?: string } | undefined)?.cwd ?? null;
      if (currentDay !== day) {
        day = currentDay;
        calls = 0;
        paused = false;
      }
      const items = parseSystemMemories(sys).slice(0, MAX_ITEMS_PER_TURN);
      const promptHash = createHash("sha256").update(prompt).digest("hex");
      const started = Date.now();
      for (const item of items) {
        if (Date.now() - started > TURN_BUDGET_MS) break;
        const memoryHash = createHash("sha256").update(item.text).digest("hex");
        const memoKey = promptHash + ":" + memoryHash;
        const cached = memo.get(memoKey);
        if (cached !== undefined) {
          if (cached.decision === "drop") dropped.add(item.text);
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
        if (drop) dropped.add(item.text);
        await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "scored", promptHash, memoryHash, noul, decision, tokensSaved: drop ? Math.floor(item.text.length / 4) : 0, latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null });
        await writeSidecar({ schema: SIDECAR_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "scored", promptHash, memoryHash, prompt, memory: item.text, noul, decision });
      }
      if (dropped.size > 0 && (await enforceEnabled(switchPath))) {
        const kept = items.length - dropped.size;
        await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "enforced", promptHash, memoryHash: null, noul: null, decision: "prune", removed: dropped.size, kept, tokensSaved: 0, latencyMs: null, inputTokens: null });
        return { systemPrompt: pruneSystemPrompt(sys, dropped) };
      }
    } catch {
      // Shadow failures never affect the turn.
    }
    return undefined;
  };
}
/** Double-registration guard: in repos where the project file and a global
 * entry resolve to different spellings, the loader binds both in one session.
 * The marker lives on the per-session binding, so fresh sessions (and
 * subagents, which rebind) still register exactly once each. */
const REGISTERED_MARK = "__jevMemoryFilterRegistered";
export default function jevMemoryFilterExtension(
  pi: { on: (event: string, handler: (event: unknown, ctx?: unknown) => Promise<unknown>) => void },
  deps: FilterDeps = {},
): void {
  if (!deps.ask) useInfisicalKey();
  const binding = pi as unknown as Record<string, unknown>;
  if (binding[REGISTERED_MARK] === true) return;
  binding[REGISTERED_MARK] = true;
  pi.on("before_agent_start", makeBeforeAgentStartHandler(deps));
}
