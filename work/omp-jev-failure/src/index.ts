/**
 * omp-jev-failure — observe-only Jev scoring for errored tool executions.
 *
 * A failed tool is not a clean result and must never be silently swallowed. Jev failures are
 * recorded as failure_error; successful questions are failure_classified. There is no third clean
 * state and no default class.
 *
 * ONE MULTICLASS QUESTION, NOT THREE BINARY ONES — measured, not preferred.
 * The three classes are mutually exclusive by construction, but three independent binary questions
 * cannot express that: they can answer yes twice, or no three times, and they did. Measured on the
 * committed eleven cases (work/omp-jev-failure/measure-multiclass.mjs, 2026-09-19, 3 runs each,
 * one session):
 *   three binary questions  9/11, 9/11, 9/11 — and TWO structurally impossible answers every run
 *                           (`argument` and `bug` both true on the same failure)
 *   one choice question    11/11, 11/11, 11/11, zero drift, on BOTH candidate wordings
 * Rewording the binary `argument` question did not fix it (that rescue is in this file's history);
 * the shape did. See docs/demos/upstream-repro/multiclass-failure-20260919.md.
 */
import { askJevChoice, type JevChoiceResult } from "../../../kit/src/client.ts";
import { recordingChoice } from "../../jev-score-register/register.mjs";

/**
 * Export what this extension already computes. askJevChoice returns
 * {choice, confidence, probabilities} and NOT `scores`, so it needs recordingChoice —
 * passing it through recording() would file every successful call as a failure.
 * The register stores a sha256 of the input and NEVER the input, and it is not a
 * cache: it records that a question was answered, it never answers one.
 *
 * Wired at the DEFAULT of the injectable `ask` parameter, not at the call site, so a
 * test that passes its own stub stays unrecorded and stays offline.
 */
const REGISTER = process.env.JEV_SCORE_REGISTER ?? "work/jev-score-register/scores.jsonl";
const recordedAskChoice = recordingChoice(askJevChoice, {
  path: REGISTER,
  extension: "omp-jev-failure",
  model: "jev-1.13.0",
  questionKey: "failure_class",
});

const DECISION = "com.zeststream.omp-jev-failure.decision.v1";
const DIAG = "com.zeststream.omp-jev-failure.diagnostic.v1";

export type ToolExecutionEnd = {
  type?: unknown;
  toolCallId?: unknown;
  toolName?: unknown;
  args?: unknown;
  result?: unknown;
  isError?: unknown;
};

type Host = {
  on: (event: string, handler: (event: ToolExecutionEnd) => Promise<undefined>) => void;
  appendEntry: (type: string, data: Record<string, unknown>) => Promise<unknown> | unknown;
};

export const FAILURE_QUESTION = "Which failure class best fits this tool failure?";

/**
 * The classes, as descriptions rather than questions. Both wordings scored 11/11; these are the
 * declarative ones, chosen because the weakest case (`permission-denied-system-path`) kept a
 * top-1/top-2 margin of 0.55-0.63 under them against 0.23-0.41 under the question-shaped strings.
 * Same verdicts, more room before the argmax could move.
 */
export const FAILURE_CLASSES = {
  transient: "The failure is most consistent with a transient environment or dependency failure.",
  argument: "The failure is most consistent with a wrong argument, path, or invocation.",
  bug: "The failure is most consistent with a genuine bug in the code under edit.",
};

function failureText(event: ToolExecutionEnd): string {
  const value = event.result;
  if (typeof value === "string") return value.slice(0, 4000);
  try { return JSON.stringify(value ?? { isError: event.isError, toolName: event.toolName }).slice(0, 4000); }
  catch { return "[unserializable tool failure]"; }
}

async function appendSafe(host: Host, type: string, data: Record<string, unknown>): Promise<void> {
  try { await host.appendEntry(type, data); } catch { /* fail-open */ }
}

export async function handleToolExecutionEnd(
  host: Host,
  event: ToolExecutionEnd,
  ask: typeof askJevChoice = recordedAskChoice,
): Promise<undefined> {
  try {
    const toolCallId = typeof event.toolCallId === "string" ? event.toolCallId : undefined;
    const toolName = typeof event.toolName === "string" ? event.toolName : undefined;
    if (event?.isError !== true) {
      await appendSafe(host, DIAG, { kind: "tool_execution_end_observed", toolCallId, toolName, isError: false, timestamp: new Date().toISOString() });
      return undefined;
    }
    const started = Date.now();
    const failure = failureText(event);
    await appendSafe(host, DIAG, { kind: "tool_execution_error_observed", toolCallId, toolName, failure, timestamp: new Date().toISOString() });

    let result: JevChoiceResult;
    try {
      result = await ask({
        state: { toolName, toolCallId, args: event.args ?? null, failure },
        instructions: FAILURE_QUESTION,
        classes: FAILURE_CLASSES,
        timeoutMs: 4000,
      });
    } catch (error) {
      result = { ok: false, reason: "transport", error: String(error), latencyMs: Date.now() - started, model: "unknown" };
    }

    const row: Record<string, unknown> = {
      schemaVersion: 2,
      kind: result.ok ? "failure_classified" : "failure_error",
      toolCallId,
      toolName,
      failure,
      latencyMs: result.latencyMs,
      model: result.model,
      timestamp: new Date().toISOString(),
    };
    if (result.ok) {
      // The full distribution goes on the row, not just the winner: a 0.98 argmax and a 0.34
      // argmax are different facts, and a reader that only sees the label cannot tell them apart.
      row.failureClass = result.choice;
      row.confidence = result.confidence;
      row.probabilities = result.probabilities;
    } else { row.failureReason = result.reason; row.error = result.error; }
    await appendSafe(host, DECISION, row);
    return undefined;
  } catch {
    return undefined;
  }
}

export default function ompJevFailure(pi: Host): void {
  pi.on("tool_execution_end", async (event) => handleToolExecutionEnd(pi, event));
}
