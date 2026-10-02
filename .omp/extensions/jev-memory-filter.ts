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
import { askJev, type AskOptions, type JevResult } from "/Users/josh/Developer/jev/kit/src/client.ts";
import { useInfisicalKey } from "/Users/josh/Developer/jev/work/jev-client/src/use-infisical-key.ts";

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

export const CONCURRENCY = 4;
export const FILTER_DEADLINE_MS = 1500;


export type MemoryItem = {
  /** Cleaned judgment key. Identical cleaning/slicing to the serial
   * incumbent, so recorded-transport replay decides exactly the same. */
  text: string;
  /** Index into the parsed element-text array (0 when sys is one string). */
  element: number;
  /** Char offsets of the RAW line within that element text (end excludes \n). */
  start: number;
  end: number;
  /** sha256 of the raw line bytes; prune re-validates before removing. */
  hash: string;
};

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

/** All memory occurrences in one element text, with exact spans. Each
 * occurrence must lie inside a validated recall block (`<memories>` pair or
 * the EE tail); identically-worded lines anywhere else are not occurrences
 * and can never be pruned (COD hazard: instruction echo of a recall line). */
export function occurrencesIn(text: string, element: number): MemoryItem[] {
  const blocks: Array<{ body: string; base: number }> = [];
  const memRe = /<memories>([\s\S]*?)<\/memories>/g;
  let m: RegExpExecArray | null;
  while ((m = memRe.exec(text)) !== null) {
    blocks.push({ body: m[1], base: m.index + "<memories>".length });
  }
  const eeIndex = text.indexOf("Task-relevant local EE memories");
  if (eeIndex >= 0) blocks.push({ body: text.slice(eeIndex), base: eeIndex });
  const out: MemoryItem[] = [];
  for (const block of blocks) {
    let off = 0;
    for (const line of block.body.split("\n")) {
      const start = block.base + off;
      const end = start + line.length;
      off = end - block.base + 1;
      const clean = line.replace(/^[\s>*•\-–\d.)]+/, "").trim();
      if (clean.length > 1) {
        out.push({
          text: clean.slice(0, 2000),
          element,
          start,
          end,
          hash: createHash("sha256").update(line).digest("hex"),
        });
      }
    }
  }
  return out;
}

/** Every occurrence across all elements, judgment order (first-seen wins). */
export function parseOccurrences(sys: unknown): MemoryItem[] {
  const texts = Array.isArray(sys) ? (sys as unknown[]).map((b) => (typeof b === "string" ? b : systemPromptText(b))) : [systemPromptText(sys)];
  const out: MemoryItem[] = [];
  texts.forEach((text, element) => {
    out.push(...occurrencesIn(text, element));
  });
  return out;
}

/** Genuine memory bullets from a system prompt. Each prompt element is parsed
 * separately: recall arrives as its own appended element, and joining first
 * would merge the instruction mention (no closing tag) with the recall close,
 * flooding the cap with static prompt text between them (live 2026-10-01:
 * merged span swallowed the whole tool-routes section). Judgments dedupe by
 * text (first occurrence wins); every occurrence address is retained by
 * parseOccurrences for span-scoped pruning. */
export function parseSystemMemories(sys: unknown): MemoryItem[] {
  const seen: Record<string, true> = {};
  const items: MemoryItem[] = [];
  for (const item of parseOccurrences(sys)) {
    if (seen[item.text]) continue;
    seen[item.text] = true;
    items.push(item);
  }
  return items;
}

/** Removal scope (jev-9cqw): drop precision is verified on jev-repo memories
 * only, so removal applies inside the jev tree; everywhere else decided drops
 * are logged (shadow) until the non-jev blind label passes, then widen. */
export const ENFORCE_ROOT = "/Users/josh/Developer/jev";
export function inEnforceScope(repo: string | null): boolean {
  return repo === ENFORCE_ROOT || (repo !== null && repo.startsWith(ENFORCE_ROOT + "/"));
}

export async function enforceEnabled(switchPath: string): Promise<boolean> {
  try {
    await readFile(switchPath, "utf8");
    return true;
  } catch {
    return false;
  }
}

/** Splice validated drop spans out of one element text. A span applies only
 * when the current bytes still hash to the recorded hash (changed source
 * keeps); removal covers the raw line plus its newline, so blank separators
 * and every non-memory byte survive exactly as the line filter left them. */
function pruneText(text: string, spans: MemoryItem[]): string {
  const good = spans
    .filter((s) => text.slice(s.start, s.end).length === s.end - s.start
      && createHash("sha256").update(text.slice(s.start, s.end)).digest("hex") === s.hash)
    .sort((a, b) => b.start - a.start);
  let out = text;
  for (const s of good) {
    const nl = out[s.end] === "\n" ? 1 : 0;
    const lead = nl === 0 && s.start > 0 && out[s.start - 1] === "\n" ? 1 : 0;
    out = out.slice(0, s.start - lead) + out.slice(s.end + nl);
  }
  return out;
}

/** Drop exactly the validated recall occurrences, byte-preserving everything
 * else. Only spans recorded by parseOccurrences are eligible: identically
 * worded lines outside a recall block, changed spans (hash mismatch), and
 * unknown element shapes all pass through unchanged. Keeps never touched. */
export function pruneSystemPrompt(sys: unknown, dropped: MemoryItem[]): unknown {
  if (dropped.length === 0) return sys;
  const byElement = new Map<number, MemoryItem[]>();
  for (const s of dropped) {
    const list = byElement.get(s.element) ?? [];
    list.push(s);
    byElement.set(s.element, list);
  }
  const texts = Array.isArray(sys)
    ? (sys as unknown[]).map((b) => (typeof b === "string" ? b : systemPromptText(b)))
    : null;
  if (typeof sys === "string") return pruneText(sys, byElement.get(0) ?? []);
  if (Array.isArray(sys)) {
    return (sys as unknown[]).map((b, i) => {
      const text = texts?.[i] ?? "";
      if (typeof b === "string") return pruneText(text, byElement.get(i) ?? []);
      if (b && typeof b === "object" && typeof (b as Record<string, unknown>)["text"] === "string") {
        return { ...(b as Record<string, unknown>), text: pruneText(text, byElement.get(i) ?? []) };
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
    const droppedTexts = new Set<string>();
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
      const occurrences = parseOccurrences(sys);
      const seen: Record<string, true> = {};
      const items = occurrences
        .filter((item) => {
          if (seen[item.text]) return false;
          seen[item.text] = true;
          return true;
        })
        .slice(0, MAX_ITEMS_PER_TURN);
      const promptHash = createHash("sha256").update(prompt).digest("hex");
      // Phase 1 (synchronous, item order): memo hits and cap reservation.
      // Cap counting is identical to the serial incumbent: first-come wins.
      const slots: Array<{ item: MemoryItem; memoryHash: string; memoKey: string }> = [];
      for (const item of items) {
        const memoryHash = createHash("sha256").update(item.text).digest("hex");
        const memoKey = promptHash + ":" + memoryHash;
        const cached = memo.get(memoKey);
        if (cached !== undefined) {
          if (cached.decision === "drop") droppedTexts.add(item.text);
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "memo", promptHash, memoryHash, noul: cached.noul, decision: cached.decision, tokensSaved: cached.decision === "drop" ? Math.floor(item.text.length / 4) : 0, latencyMs: null, inputTokens: cached.inputTokens });
          await writeSidecar({ schema: SIDECAR_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "memo", promptHash, memoryHash, prompt, memory: item.text, noul: cached.noul, decision: cached.decision });
          continue;
        }
        if (paused || calls >= cap) {
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: paused ? "paused" : "daily-cap", promptHash, memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: null, inputTokens: null });
          continue;
        }
        calls += 1;
        slots.push({ item, memoryHash, memoKey });
      }
      // Phase 2: at most CONCURRENCY asks in flight, FILTER_DEADLINE_MS total.
      // Unresolved at the deadline keeps (logged); late answers are ignored
      // for decisions and logged late-ignored for spend visibility.
      const settled = new Array<boolean>(slots.length).fill(false);
      // Claim-before-write: the deadline loop awaits between rows, so a late
      // settle can complete mid-loop. Every terminal row must win this claim
      // first, or one slot emits two rows (live-found 2026-10-02: 22 rows for
      // 20 slots, deadline-keep + late-ignored on the same slot).
      const claim = (idx: number): boolean => {
        if (settled[idx]) return false;
        settled[idx] = true;
        return true;
      };
      let timedOut = false;
      const settle = async (idx: number): Promise<void> => {
        const slot = slots[idx];
        const t0 = Date.now();
        let result: JevResult;
        try {
          result = await ask({
            state: { prompt, memory: slot.item.text },
            questions: { rel: { instructions: INSTRUCTIONS } },
            model: MODEL,
            timeoutMs: CALL_TIMEOUT_MS,
          });
        } catch (error) {
          // Post-deadline failures leave the row to the deadline loop.
          if (!timedOut && claim(idx)) {
            await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "fail_open", promptHash, memoryHash: slot.memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: Date.now() - t0, inputTokens: null, error: error instanceof Error ? error.message : String(error) });
          }
          return;
        }
        if (timedOut) {
          if (claim(idx)) {
            await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "late-ignored", promptHash, memoryHash: slot.memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null });
          }
          return;
        }
        if (!result.ok) {
          if (/\bHTTP (?:401|402|403)\b/.test(result.error)) paused = true;
          // Post-deadline failures leave the row to the deadline loop.
          if (!timedOut && claim(idx)) {
            await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "fail_open", promptHash, memoryHash: slot.memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: result.latencyMs, inputTokens: null, error: result.error });
          }
          return;
        }
        const noul = result.scores["rel"];
        // Contract mirror of kit finiteProbability: finite and in [0,1].
        if (typeof noul !== "number" || !Number.isFinite(noul) || noul < 0 || noul > 1) {
          // Post-deadline invalid answers keep spend visible as late-ignored.
          if (!timedOut && claim(idx)) {
            await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "invalid-keep", promptHash, memoryHash: slot.memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null });
          } else if (timedOut && claim(idx)) {
            await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "late-ignored", promptHash, memoryHash: slot.memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null, error: "invalid-score" });
          }
          return;
        }
        const drop = noul < CUT;
        const decision = drop ? "drop" : "keep";
        if (!timedOut && claim(idx)) {
          if (memo.size >= MAX_MEMO) {
            const oldest = memo.keys().next();
            if (!oldest.done) memo.delete(oldest.value);
          }
          memo.set(slot.memoKey, { noul, decision, inputTokens: result.usage?.input_tokens ?? null });
          if (drop) droppedTexts.add(slot.item.text);
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "scored", promptHash, memoryHash: slot.memoryHash, noul, decision, tokensSaved: drop ? Math.floor(slot.item.text.length / 4) : 0, latencyMs: result.latencyMs, inputTokens: result.usage?.input_tokens ?? null });
          await writeSidecar({ schema: SIDECAR_SCHEMA, ts: now(), instance: INSTANCE, model: result.model, status: "scored", promptHash, memoryHash: slot.memoryHash, prompt, memory: slot.item.text, noul, decision });
        }
      };
      const deadlineAt = Date.now() + FILTER_DEADLINE_MS;
      let cursor = 0;
      const worker = async (): Promise<void> => {
        for (;;) {
          if (timedOut || Date.now() >= deadlineAt) return;
          const idx = cursor;
          cursor += 1;
          if (idx >= slots.length) return;
          await settle(idx);
        }
      };
      const workers: Array<Promise<void>> = [];
      for (let w = 0; w < CONCURRENCY && w < slots.length; w += 1) workers.push(worker());
      await Promise.race([
        Promise.all(workers),
        new Promise<void>((resolve) => setTimeout(resolve, Math.max(0, deadlineAt - Date.now()))),
      ]);
      timedOut = true;
      for (let idx = 0; idx < slots.length; idx += 1) {
        if (claim(idx)) {
          const slot = slots[idx];
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "deadline-keep", promptHash, memoryHash: slot.memoryHash, noul: null, decision: "keep", tokensSaved: 0, latencyMs: null, inputTokens: null });
        }
      }
      const dropSpans = occurrences.filter((o) => droppedTexts.has(o.text));
      if (dropSpans.length > 0 && (await enforceEnabled(switchPath))) {
        const kept = items.length - droppedTexts.size;
        if (inEnforceScope(fireRepo)) {
          await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "enforced", promptHash, memoryHash: null, noul: null, decision: "prune", removed: dropSpans.length, kept, tokensSaved: 0, latencyMs: null, inputTokens: null });
          return { systemPrompt: pruneSystemPrompt(sys, dropSpans) };
        }
        await write({ schema: LOG_SCHEMA, ts: now(), instance: INSTANCE, model: MODEL, status: "shadowed", promptHash, memoryHash: null, noul: null, decision: "would-drop", removed: dropSpans.length, kept, tokensSaved: 0, latencyMs: null, inputTokens: null });
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
