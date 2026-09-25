/**
 * omp-jev-promise — observe-only scorer for headline vs CTA.
 *
 * WHY THIS ONE CALLS JEV. An exact verb from the headline that also appears
 * in a control is a regex. "Take control of payroll" vs "Get started" is not.
 * Jev earns the remainder. The regex still wins the exact-verb class — if
 * measurement shows Jev matching the regex there, drop Jev (harm-rule replay).
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `promise_error`, never a pass.
 */
import { askJev } from "../../../kit/src/client.ts";
import {
  isUserFacingWrite,
  filePathFromEvent,
  contentFromEvent,
  toolCallId,
  extractHeadlinesAndCtas,
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
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-promise", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-promise.decision.v1";

export const QUESTIONS = {
  keeps_promise: "Does a control in this file do what the headline promises?",
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

/** True when any headline word of length >= 4 (lowercase) is a substring of the joined CTAs. */
export function headlineWordInCtas(headlines: string[], ctas: string[]): boolean {
  const joined = ctas.join(" ").toLowerCase();
  for (const headline of headlines) {
    for (const word of String(headline).toLowerCase().split(/\s+/)) {
      if (word.length >= 4 && joined.includes(word)) return true;
    }
  }
  return false;
}

export default function ompJevPromise(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      const { headlines, ctas } = extractHeadlinesAndCtas(content);
      if (headlines.length === 0 || ctas.length === 0) return undefined;
      const path = filePathFromEvent(event);
      const id = toolCallId(event);

      if (headlineWordInCtas(headlines, ctas)) {
        try {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "promise_regex",
            matched: true,
            path,
            toolCallId: id,
            headlines,
            ctas,
            timestamp: new Date().toISOString(),
          });
        } catch { /* observability must never break the session */ }
        return undefined;
      }

      const result = await ask({
        state: { path, headlines, ctas, copy: clip(content, 3000) },
        questions: QUESTIONS,
        timeoutMs: 2500,
      });
      const probabilities = result.ok ? result.scores : undefined;
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;
      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "promise_scored" : "promise_error",
          path,
          toolCallId: id,
          headlines,
          ctas,
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
