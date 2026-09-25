/**
 * omp-jev-heat — observe-only ATTENTION scorer (not taste).
 *
 * WHY THIS ONE CALLS JEV. Golden-path vs yak has no cheap regex — no literal
 * distinguishes "export the payroll CSV the client asked for" from "rewrite
 * this as a general-purpose actor framework". A judge earns its seat exactly
 * where a rule cannot be written.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `heat_error`, never a pass.
 */
import { askJevChoice } from "../../../kit/src/client.ts";
import { clip } from "../../taste-loop/src/detect.mjs";

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
  extension: "omp-jev-heat",
  model: "jev-1.13.0",
  questionKey: "heat_class",
});

const DECISION = "com.zeststream.omp-jev-heat.decision.v1";
const MAX_PROMPT = 4000;

export const CHOICE = {
  instructions: "Relative to the client's job, what is this turn?",
  classes: {
    golden_path: "The client's core job-to-be-done",
    supporting: "Necessary but not the show",
    yak: "Engineer-fun, speculative infra, premature abstraction",
    hygiene: "Tests, types, lint, a11y",
    none: "Cannot tell",
  },
};

/**
 * Copied from work/omp-jev-route (do not import route). turn_start carries
 * only {type, turnIndex, timestamp} — measured live — so this subscribes to
 * context, whose messages[] holds the user text.
 */
function promptText(event) {
  if (!event || typeof event !== "object") return undefined;
  const direct = [event.prompt, event.message, event.text, event.input];
  for (const c of direct) {
    if (typeof c === "string" && c.trim().length > 0) return c.slice(0, MAX_PROMPT);
  }
  const messages = Array.isArray(event.messages) ? event.messages : [];
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (!m || typeof m !== "object" || m.role !== "user") continue;
    if (typeof m.content === "string" && m.content.trim().length > 0) {
      return m.content.slice(0, MAX_PROMPT);
    }
    if (Array.isArray(m.content)) {
      const text = m.content
        .filter((p) => p && typeof p === "object" && p.type === "text" && typeof p.text === "string")
        .map((p) => p.text)
        .join("\n");
      if (text.trim().length > 0) return text.slice(0, MAX_PROMPT);
    }
  }
  return undefined;
}

type ContextEvent = {
  prompt?: unknown;
  message?: unknown;
  text?: unknown;
  input?: unknown;
  messages?: unknown;
  toolCallId?: unknown;
};
type Host = {
  on: (event: string, handler: (event: ContextEvent) => Promise<undefined>) => void;
  appendEntry: (type: string, data: Record<string, unknown>) => Promise<unknown>;
};

export default function ompJevHeat(pi: Host) {
  pi.on("context", async (event) => {
    try {
      const prompt = promptText(event);
      if (prompt === undefined) return undefined;
      const toolCallId = typeof event?.toolCallId === "string" ? event.toolCallId : null;
      const result = await ask({
        state: {
          brief: process.env.TASTE_BRIEF || "(none provided)",
          prompt: clip(prompt, 4000),
        },
        instructions: CHOICE.instructions,
        classes: CHOICE.classes,
        timeoutMs: 2500,
      });
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;
      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: result.ok ? "heat_scored" : "heat_error",
          toolCallId,
          ...(result.ok
            ? {
                choice: result.choice,
                confidence: result.confidence,
                probabilities: result.probabilities,
              }
            : {}),
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
