/**
 * omp-jev-fork — observe-only scorer for successive copy variants.
 *
 * WHY THIS ONE CALLS JEV. A second write to the same user-facing path is a
 * Map. Which variant a first-time client would actually read is not.
 * A | B | none is a choice; `none` is first-class so "both fine" is sayable.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `fork_error`, never a pass.
 */
import { askJevChoice } from "../../jev-client/src/index.ts";
import {
  isUserFacingWrite,
  filePathFromEvent,
  contentFromEvent,
  toolCallId,
  clip,
} from "../../taste-loop/src/detect.mjs";

const DECISION = "com.zeststream.omp-jev-fork.decision.v1";

export const CHOICE = {
  instructions: "Which variant is clearer for a first-time client?",
  classes: {
    A: "The earlier copy",
    B: "The later copy",
    none: "Neither is clearly better",
  },
};

type ToolCallEvent = {
  toolName?: unknown;
  name?: unknown;
  toolCallId?: unknown;
  input?: unknown;
};
type Host = {
  on: (event: string, handler: (event: ToolCallEvent) => Promise<undefined>) => void;
  appendEntry: (type: string, data: Record<string, unknown>) => Promise<unknown>;
};

export default function ompJevFork(pi: Host) {
  const lastByPath = new Map<string, string>();

  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const path = filePathFromEvent(event);
      const content = contentFromEvent(event);
      if (path === undefined || content === undefined) return undefined;

      const previous = lastByPath.get(path);
      lastByPath.set(path, content);
      if (previous === undefined) return undefined;
      if (previous === content) return undefined;

      const result = await askJevChoice({
        state: { path, A: clip(previous), B: clip(content) },
        instructions: CHOICE.instructions,
        classes: CHOICE.classes,
        timeoutMs: 2500,
      });
      const id = toolCallId(event);

      try {
        if (result.ok) {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "fork_scored",
            path,
            toolCallId: id,
            choice: result.choice,
            confidence: result.confidence,
            probabilities: result.probabilities,
            latencyMs: result.latencyMs,
            model: result.model,
            timestamp: new Date().toISOString(),
          });
        } else {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "fork_error",
            path,
            toolCallId: id,
            error: `${result.reason}: ${result.error}`,
            failure: result.reason,
            latencyMs: result.latencyMs,
            model: result.model,
            timestamp: new Date().toISOString(),
          });
        }
      } catch { /* observability must never break the session */ }
      return undefined;
    } catch {
      return undefined;
    }
  });
}
