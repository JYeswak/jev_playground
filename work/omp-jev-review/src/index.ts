/**
 * omp-jev-review — observe-only review scorer for omp.
 *
 * WHY THIS ONE CALLS JEV, WHEN omp-jev-harm AND omp-jev-preaction DO NOT.
 * Those gates were measured against a live model and WON: four regexes beat Jev 12/12 to 11/12
 * at FP 0/38, so paying an API call per bash was a cost-benefit loss. That was a ruling about
 * ONE SURFACE, not a ban on the model.
 *
 * This surface is the opposite case. "Does this diff deserve review attention?" has no cheap
 * expression — there is no regex for `this refactor silently changed a default`. A judge earns
 * its seat exactly where a rule cannot be written, which is the premise of the lane.
 *
 * Upstream `jev-review` is RUN at 13/13 offline
 * (docs/demos/upstream-repro/jev-review-real-diffs-20260919.md).
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `review_error`, never a pass — NEGATIVE_EVIDENCE R40: a crashed
 * classifier recording a pass is indistinguishable from a clean result.
 */
import { askJev } from "../../jev-client/src/index.ts";

import { recording } from "../../jev-score-register/register.mjs";

/**
 * Export what this extension already computes. Every Jev score it produces is
 * appended to the register instead of being discarded when the run ends.
 * The register stores a sha256 of the input and NEVER the input itself, and it is
 * not a cache: it records that a question was answered, it never answers one.
 */
const REGISTER = process.env.JEV_SCORE_REGISTER ?? "work/jev-score-register/scores.jsonl";
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-review", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-review.decision.v1";
const DIAG = "com.zeststream.omp-jev-review.diagnostic.v1";

const MAX_DIFF = 12000;

/**
 * Questions only. The WIRE SHAPE lives in work/jev-client and nowhere else — this extension
 * hand-rolled its own fetch once and got HTTP 400 for inventing `{questions: [...], context}`.
 * If you need a shape the client does not support, extend the client and its tests.
 *
 * TWO questions, because measurement killed the third. `measure.mjs` scored all three against
 * seven diffs whose answers we know by construction. `scope` said **no** on every one of them,
 * including the 400-line rename sold as "tidy up" that it exists to catch (0.39, twice), and
 * scored that case BELOW a three-line auth deletion (0.43) — so it is not a threshold problem,
 * the ordering is wrong too. Its 6/7 was the base rate of a mostly-false label, not judgement.
 * A question whose verdict does not change with its input is noise with a confidence attached.
 */
const QUESTIONS = {
  behaviour: "Does this diff alter behaviour that an existing caller depends on?",
  boundary: "Does this diff touch a security, permission, or authentication boundary?",
};

type ToolCallEvent = { toolName?: unknown; name?: unknown; toolCallId?: unknown; input?: unknown; command?: unknown };
type Host = {
  on: (event: string, handler: (event: ToolCallEvent) => Promise<undefined>) => void;
  appendEntry: (type: string, data: Record<string, unknown>) => Promise<unknown>;
};

export default function ompJevReview(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      const tool = String(event?.toolName ?? event?.name ?? "");
      const input = event?.input;
      const raw =
        (input && typeof input === "object" && "command" in input ? input.command : undefined) ??
        event?.command;
      const command = typeof raw === "string" ? raw : undefined;
      if (tool !== "bash" || command === undefined || !/\bgit\s+(diff|show)\b/.test(command)) {
        return undefined;
      }

      const toolCallId = typeof event?.toolCallId === "string" ? event.toolCallId : null;
      try {
        await pi.appendEntry(DIAG, {
          kind: "diff_command_observed",
          toolCallId,
          timestamp: new Date().toISOString(),
        });
      } catch {}

      const result = await ask({
        state: { diff: command.slice(0, MAX_DIFF) },
        questions: QUESTIONS,
        timeoutMs: 2500,
      });
      const probabilities = result.ok ? result.scores : undefined;
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;

      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "review_scored" : "review_error",
          command: command.slice(0, 2000),
          toolCallId,
          // absent, never defaulted: a missing score must not read as a clean review
          ...(probabilities ? { probabilities } : {}),
          ...(error === undefined ? {} : { error }),
          latencyMs: result.latencyMs,
          model: result.model,
          ...(result.ok ? {} : { failure: result.reason }),
          timestamp: new Date().toISOString(),
        });
      } catch {
        /* observability must never break the session */
      }
      return undefined;
    } catch {
      return undefined;
    }
  });
}
