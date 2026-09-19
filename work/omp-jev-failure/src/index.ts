/**
 * omp-jev-failure — observe-only Jev scoring for errored tool executions.
 *
 * A failed tool is not a clean result and must never be silently swallowed. Jev failures are
 * recorded as failure_error; successful questions are failure_scored. There is no third clean
 * state and no default score.
 */
import { askJev, type JevResult } from "../../jev-client/src/index.ts";

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

export const QUESTIONS = {
  transient: "Is this failure most consistent with a transient environment or dependency failure?",
  argument: "Is this failure most consistent with a wrong argument, path, or invocation?",
  bug: "Is this failure most consistent with a genuine bug in the code under edit?",
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
  ask: typeof askJev = askJev,
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

    let result: JevResult;
    try {
      result = await ask({
        state: { toolName, toolCallId, args: event.args ?? null, failure },
        questions: QUESTIONS,
        timeoutMs: 4000,
      });
    } catch (error) {
      result = { ok: false, reason: "transport", error: String(error), latencyMs: Date.now() - started, model: "unknown" };
    }

    const row: Record<string, unknown> = {
      schemaVersion: 1,
      kind: result.ok ? "failure_scored" : "failure_error",
      toolCallId,
      toolName,
      failure,
      latencyMs: result.latencyMs,
      model: result.model,
      timestamp: new Date().toISOString(),
    };
    if (result.ok) row.scores = result.scores;
    else { row.failureReason = result.reason; row.error = result.error; }
    await appendSafe(host, DECISION, row);
    return undefined;
  } catch {
    return undefined;
  }
}

export default function ompJevFailure(pi: Host): void {
  pi.on("tool_execution_end", async (event) => handleToolExecutionEnd(pi, event));
}
