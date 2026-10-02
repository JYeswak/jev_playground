/**
 * Long-result keep/summarize/drop shadow (WindyLantern longres lever).
 *
 * Advisory observer at the tool_result seam: for results at or above the
 * size floor it asks the frozen Choice and logs a would-summarize /
 * would-drop row (result hash, size, decision, confidence; never raw text).
 * It NEVER alters context: the handler returns undefined on every path.
 * Default OFF: with no switch file present it does nothing (no rows, no
 * model calls). Switch path overridable for sandboxed proofs.
 */
import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { askJevChoice } from "../../kit/src/client.ts";

export const SIZE_FLOOR = 10000;
export const QUESTION =
  "This tool result just arrived. How should it be kept for the rest of the session?";
export const CLASSES: Record<string, string> = {
  keep: "the task will need its details",
  summarize: "its gist suffices",
  drop: "it will not be needed",
};
export const SWITCH_REL = "state/jev/longres-shadow";
export const LOG_REL = "state/jev/longres-shadow.jsonl";
export const MODEL = "jev-1.13.0";

export type Deps = {
  ask?: typeof askJevChoice;
  append?: (path: string, line: string) => Promise<void>;
  path?: string;
  switchPath?: string;
  sizeFloor?: number;
  now?: () => string;
};

function textOf(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    const parts: string[] = [];
    for (const b of content) {
      if (b && typeof b === "object" && "text" in b && typeof b.text === "string") parts.push(b.text);
    }
    return parts.join("\n");
  }
  return "";
}

export function makeLongresShadowHandler(deps: Deps = {}) {
  const ask = deps.ask ?? askJevChoice;
  const now = deps.now ?? (() => new Date().toISOString());
  const floor = deps.sizeFloor ?? SIZE_FLOOR;
  const switchPath = deps.switchPath ?? join(homedir(), ".local", SWITCH_REL);
  const logPath = deps.path ?? join(homedir(), ".local", LOG_REL);
  return async (event: { toolName?: unknown; content?: unknown }): Promise<undefined> => {
    let on = false;
    try {
      on = existsSync(switchPath);
    } catch {
      on = false;
    }
    if (!on) return undefined;
    const text = textOf(event.content);
    if (text.length < floor) return undefined;
    const sha = createHash("sha256").update(text).digest("hex").slice(0, 16);
    let decision = "keep";
    let conf: number | null = null;
    try {
      const r = await ask({
        state: {},
        instructions: QUESTION + "\n\nResult head:\n" + text.slice(0, 350) + "\n\nResult tail:\n" + text.slice(-350),
        classes: CLASSES,
        model: MODEL,
        timeoutMs: 20000,
      });
      if (r.ok && (r.choice === "keep" || r.choice === "summarize" || r.choice === "drop")) {
        decision = r.choice;
        conf = typeof r.confidence === "number" ? r.confidence : null;
      }
    } catch {
      decision = "keep";
    }
    if (deps.append) {
      await deps.append(
        logPath,
        JSON.stringify({ ts: now(), resultHash: sha, size: text.length, decision, conf, screen: "would-" + decision }),
      );
    }
    return undefined;
  };
}

/**
 * Loader entry: registers the tool_result observer. The switch check lives
 * inside the handler, so merely loading this file changes nothing until an
 * operator creates the switch file. Never alters context on any path.
 */
export default function jevLongresShadowExtension(
  pi: { on: (event: string, handler: (event: unknown, ctx?: unknown) => unknown) => void },
  deps: Deps = {},
): void {
  pi.on("tool_result", makeLongresShadowHandler(deps) as (event: unknown, ctx?: unknown) => unknown);
}
