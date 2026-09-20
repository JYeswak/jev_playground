/**
 * omp-jev-skip — observe-only scorer for onboarding exits.
 *
 * WHY THIS ONE CALLS JEV. `skip` / `not now` / `later` is a regex. Whether a
 * returning user can leave a wizard that has no obvious skip (a back control,
 * an X, copy that lets them defer) is not. Jev earns the remainder. The regex
 * still wins the planted class — if measurement shows skip-presence equalling
 * noul, drop Jev.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `skip_error`, never a pass.
 */
import { askJev } from "../../jev-client/src/index.ts";
import {
  isUserFacingWrite,
  isOnboardingPath,
  hasSkipExit,
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
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-skip", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-skip.decision.v1";

export const QUESTIONS = {
  can_leave: "Can a returning user leave this onboarding without completing it?",
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

export default function ompJevSkip(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const path = filePathFromEvent(event);
      if (!isOnboardingPath(path)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      const id = toolCallId(event);

      if (hasSkipExit(content)) {
        try {
          await pi.appendEntry(DECISION, {
            schemaVersion: 1,
            kind: "skip_regex",
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
        state: { path, copy: clip(content, 3000) },
        questions: QUESTIONS,
        timeoutMs: 2500,
      });
      const probabilities = result.ok ? result.scores : undefined;
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;
      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "skip_scored" : "skip_error",
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
