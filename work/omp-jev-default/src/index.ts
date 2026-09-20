/**
 * omp-jev-default — observe-only scorer for preselected defaults.
 *
 * WHY THIS ONE CALLS JEV. `defaultChecked` / `defaultValue` / `selected: true`
 * is a regex. Whether that default serves the client (remember last account)
 * or the vendor (pre-tick partner offers) is not. Jev earns the remainder.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `default_error`, never a pass.
 */
import { askJev } from "../../jev-client/src/index.ts";
import {
  isUserFacingWrite,
  hasPreselection,
  filePathFromEvent,
  contentFromEvent,
  toolCallId,
  clip,
} from "../../taste-loop/src/detect.mjs";

const DECISION = "com.zeststream.omp-jev-default.decision.v1";

export const QUESTIONS = {
  serves_client: "Does this default serve the client, or the vendor?",
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

export default function ompJevDefault(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      if (!hasPreselection(content)) return undefined;
      const path = filePathFromEvent(event);
      const id = toolCallId(event);

      const result = await askJev({
        state: { path, copy: clip(content, 3000) },
        questions: QUESTIONS,
        timeoutMs: 2500,
      });
      const probabilities = result.ok ? result.scores : undefined;
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;
      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "default_scored" : "default_error",
          path,
          toolCallId: id,
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
