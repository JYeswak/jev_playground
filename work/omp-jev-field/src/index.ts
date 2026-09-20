/**
 * omp-jev-field — observe-only scorer for form fields.
 *
 * WHY THIS ONE CALLS JEV. `<input>` / `placeholder` / `label` presence is a
 * regex. Whether the label is the user's language, whether the placeholder
 * merely repeats it, and whether the error copy tells the user how to fix
 * the field are paraphrase. Jev earns the three.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `field_error`, never a pass.
 */
import { askJev } from "../../jev-client/src/index.ts";
import {
  isUserFacingWrite,
  filePathFromEvent,
  contentFromEvent,
  toolCallId,
  looksLikeForm,
  placeholderAsLabel,
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
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-field", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-field.decision.v1";

export const QUESTIONS = {
  user_language: "Is the field label in the user's language rather than engineering jargon?",
  placeholder_dup: "Does the placeholder merely repeat the label instead of giving an example?",
  recoverable: "Does the error copy tell the user how to fix the field?",
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

export default function ompJevField(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      if (!looksLikeForm(content)) return undefined;
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
          kind: probabilities ? "field_scored" : "field_error",
          path,
          toolCallId: id,
          placeholderAsLabel: placeholderAsLabel(content),
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
