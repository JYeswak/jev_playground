/**
 * omp-jev-heckle — observe-only scorer for error / empty / loading copy.
 *
 * WHY THIS ONE CALLS JEV. Planted dead strings ("An error occurred") are a
 * regex. "Couldn't save payroll. Retry?" vs "Error: ECONNRESET" is not.
 * Jev earns the remainder. The regex still wins the planted class — if
 * measurement shows Jev matching the regex there, drop Jev (harm-rule replay).
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `heckle_error`, never a pass.
 */
import { askJev } from "../../jev-client/src/index.ts";
import {
  isUserFacingWrite,
  filePathFromEvent,
  contentFromEvent,
  toolCallId,
  regexCatchesHeckle,
  copyClass,
  clip,
} from "../../taste-loop/src/detect.mjs";

const DECISION = "com.zeststream.omp-jev-heckle.decision.v1";

export const QUESTIONS = {
  next_action: "Does the user know the next action from this copy?",
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

export default function ompJevHeckle(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      const klass = copyClass(content);
      const path = filePathFromEvent(event);
      const id = toolCallId(event);

      if (regexCatchesHeckle(content)) {
        try {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "heckle_regex",
            copyClass: klass,
            path,
            toolCallId: id,
            excerpt: clip(content, 240),
            timestamp: new Date().toISOString(),
          });
        } catch { /* observability must never break the session */ }
        return undefined;
      }

      // Remainder only: skip files with no recovery/empty/loading language.
      if (!/\b(error|empty|loading|retry|failed|saved|couldn't|could not)\b/i.test(content) && klass === "other") {
        return undefined;
      }

      const result = await askJev({
        state: { path, copy: clip(content, 4000) },
        questions: QUESTIONS,
        timeoutMs: 2500,
      });
      const probabilities = result.ok ? result.scores : undefined;
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;
      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "heckle_scored" : "heckle_error",
          path,
          toolCallId: id,
          copyClass: klass,
          ...(probabilities ? { probabilities } : {}),
          ...(error === undefined ? {} : { error }),
          latencyMs: result.latencyMs,
          model: result.model,
          ...(result.ok ? {} : { failure: result.reason }),
          timestamp: new Date().toISOString(),
        });
      } catch { /* observability must never break the session */ }
      return undefined;
    } catch {
      return undefined;
    }
  });
}
