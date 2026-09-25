/**
 * omp-jev-firstlook — observe-only scorer for first-screen job-to-be-done.
 *
 * WHY THIS ONE CALLS JEV. A landing path is a regex. Whether a first-time
 * user can tell what the product *does* from the copy on that path is not.
 * lost | hunting | got_it is a choice, not three independent noul scores.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `firstlook_error`, never a pass.
 */
import { askJevChoice } from "../../../kit/src/client.ts";
import {
  isUserFacingWrite,
  isFirstLookPath,
  filePathFromEvent,
  contentFromEvent,
  clip,
} from "../../taste-loop/src/detect.mjs";

import { recordingChoice } from "../../jev-score-register/register.mjs";

/**
 * Export what this extension already computes. Every Jev probability it produces is
 * appended to the register instead of being discarded when the run ends.
 * askJevChoice returns {choice, confidence, probabilities} and NOT `scores`, so it
 * needs recordingChoice — passing it through recording() would file every successful
 * call as a failure. The register stores a sha256 of the input and NEVER the input,
 * and it is not a cache: it records that a question was answered, never answers one.
 */
const REGISTER = process.env.JEV_SCORE_REGISTER ?? "work/jev-score-register/scores.jsonl";
const ask = recordingChoice(askJevChoice, {
  path: REGISTER,
  extension: "omp-jev-firstlook",
  model: "jev-1.13.0",
  questionKey: "firstlook_class",
});

const DECISION = "com.zeststream.omp-jev-firstlook.decision.v1";

export const CHOICE = {
  instructions: "How fast is the job-to-be-done obvious from this first screen copy?",
  classes: {
    lost: "A first-time user would not know what this product does",
    hunting: "They can guess but must hunt",
    got_it: "The job is obvious",
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

let buffer: string[] = [];

export default function ompJevFirstlook(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const path = filePathFromEvent(event);
      if (!isFirstLookPath(path)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      buffer.push(content);
      return undefined;
    } catch {
      return undefined;
    }
  });

  pi.on("session_stop", async () => {
    try {
      const copy = buffer.join("\n");
      buffer = [];
      if (copy.length === 0) return undefined;

      const result = await ask({
        state: { copy: clip(copy, 4000) },
        instructions: CHOICE.instructions,
        classes: CHOICE.classes,
        timeoutMs: 2500,
      });

      try {
        if (result.ok) {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "firstlook_scored",
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
            kind: "firstlook_error",
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
