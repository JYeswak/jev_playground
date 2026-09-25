/**
 * omp-jev-undo — observe-only scorer for destructive UI.
 *
 * WHY THIS ONE CALLS JEV. A destructive verb (`delete|remove|reset|…`) is a
 * regex. `Cancel keeps it` / `Undo` is also a regex and never reaches Jev.
 * "Is there a way back" on the remainder is paraphrase — a confirmation that
 * names an export, a toast whose exit is not the word undo. Jev earns that.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `undo_error`, never a pass.
 */
import { askJev } from "../../../kit/src/client.ts";
import {
  isUserFacingWrite,
  filePathFromEvent,
  contentFromEvent,
  toolCallId,
  hasDestructiveVerb,
  hasWayBack,
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
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-undo", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-undo.decision.v1";

export const QUESTIONS = {
  way_back: "Is there a way for the user to undo or leave this action without an extended dialogue?",
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

export default function ompJevUndo(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      if (!hasDestructiveVerb(content)) return undefined;
      const path = filePathFromEvent(event);
      const id = toolCallId(event);

      if (hasWayBack(content)) {
        try {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "undo_regex",
            hasExit: true,
            path,
            toolCallId: id,
            excerpt: clip(content, 240),
            timestamp: new Date().toISOString(),
          });
        } catch { /* observability must never break the session */ }
        return undefined;
      }

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
          kind: probabilities ? "undo_scored" : "undo_error",
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
