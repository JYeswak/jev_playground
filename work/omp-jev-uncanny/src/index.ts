/**
 * omp-jev-uncanny — observe-only scorer for product-as-observer copy.
 *
 * WHY THIS ONE CALLS JEV. "I noticed you haven't finished setup" is a regex.
 * "Still here? I can help" is not. Jev earns the remainder. The prefilter is a
 * GATE, not a verdict: a miss never records `uncanny_regex`. v1 only fires when
 * the prefilter hits, to keep call volume down; paraphrase that the regex misses
 * is therefore not scored yet.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `uncanny_error`, never a pass.
 */
import { askJev } from "../../jev-client/src/index.ts";
import {
  isUserFacingWrite,
  filePathFromEvent,
  contentFromEvent,
  toolCallId,
  clip,
} from "../../taste-loop/src/detect.mjs";

import { recording } from "../../jev-score-register/register.mjs";

/**
 * Export what this extension already computes. Every Jev score it produces is
 * appended to the register instead of being discarded when the run ends.
 * The register stores a sha256 of the input and NEVER the input itself, and it is
 * not a cache: it records that a question was answered, it never answers one.
 */
const REGISTER = process.env.JEV_SCORE_REGISTER ?? "work/jev-score-register/scores.jsonl";
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-uncanny", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-uncanny.decision.v1";

export const QUESTIONS = {
  watching: "Does this copy address the user as if the product is a person who is observing them?",
};

/**
 * Volume gate, not a verdict. Hits cheap first-person-observer phrases so
 * ordinary copy ("Save changes") is 0 rows. Paraphrase the regex misses still
 * needs Jev; v1 does not send those, on purpose.
 */
const WATCHING_GATE =
  /\b(i noticed|i see you|you haven't|looks like you|i've been watching|while you were)\b/i;
const CHECKING_IN = /\b(hey there|just checking in)\b/i;

function prefilterHits(text: string): boolean {
  return WATCHING_GATE.test(text) || CHECKING_IN.test(text);
}

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

export default function ompJevUncanny(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      if (!prefilterHits(content)) return undefined;

      const path = filePathFromEvent(event);
      const id = toolCallId(event);
      const result = await ask({
        state: { path, copy: clip(content, 4000) },
        questions: QUESTIONS,
        timeoutMs: 2500,
      });
      const probabilities = result.ok ? result.scores : undefined;
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;
      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "uncanny_scored" : "uncanny_error",
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
