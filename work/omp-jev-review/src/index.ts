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
const DECISION = "com.zeststream.omp-jev-review.decision.v1";
const DIAG = "com.zeststream.omp-jev-review.diagnostic.v1";

const ENDPOINT = "https://api.typesafe.ai/v1/systemone";
const TIMEOUT_MS = 2500;
const MAX_DIFF = 12000;

const QUESTIONS = [
  "does this change alter behaviour a caller depends on",
  "does this change touch a security or permission boundary",
  "is this change larger than its message implies",
];

type ToolCallEvent = { toolName?: unknown; name?: unknown; toolCallId?: unknown; input?: unknown; command?: unknown };
type Host = {
  on: (event: string, handler: (event: ToolCallEvent) => Promise<undefined>) => void;
  appendEntry: (type: string, data: Record<string, unknown>) => Promise<unknown>;
};

/** Named because the systemOne request shape is a contract, not a rename. */
async function scoreDiff(diff: string, apiKey: string): Promise<Record<string, number> | undefined> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "content-type": "application/json", authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ questions: QUESTIONS, context: diff.slice(0, MAX_DIFF) }),
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`systemOne HTTP ${response.status}`);
    const body: unknown = await response.json();
    if (body && typeof body === "object" && "probabilities" in body) {
      const candidate = body.probabilities;
      if (candidate && typeof candidate === "object") return candidate as Record<string, number>;
    }
    return undefined;
  } finally {
    clearTimeout(timer);
  }
}

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

      const apiKey = process.env.TYPESAFE_API_KEY;
      const started = Date.now();
      let probabilities: Record<string, number> | undefined;
      let error: string | undefined;

      if (!apiKey) {
        // An unset key is a CONFIGURATION state, not a review result. The observer logged
        // "JEV_OBSERVER_ENDPOINT is not configured" for 27 rows and nobody noticed, because
        // the rows still looked like decisions.
        error = "TYPESAFE_API_KEY is not set";
      } else {
        try {
          probabilities = await scoreDiff(command, apiKey);
          if (!probabilities) error = "systemOne returned no probabilities";
        } catch (err) {
          error = String(err);
        }
      }

      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "review_scored" : "review_error",
          command: command.slice(0, 2000),
          toolCallId,
          // absent, never defaulted: a missing score must not read as a clean review
          ...(probabilities ? { probabilities } : {}),
          ...(error === undefined ? {} : { error }),
          latencyMs: Date.now() - started,
          model: apiKey ? "typesafe-systemone" : "none-unconfigured",
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
