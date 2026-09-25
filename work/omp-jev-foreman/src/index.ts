/**
 * omp-jev-foreman — observe-only progress supervision.
 *
 * Local trigger first: Jev is asked only when the recent execution window repeats a command or
 * accumulates calls without a write/edit. There is no default score and no blocking path.
 */
import { askJev, readRow, type JevResult } from "../../../kit/src/client.ts";
import { recording } from "../../jev-score-register/register.mjs";

/**
 * Export what this extension already computes. Every Jev score it produces is
 * appended to the register instead of being discarded when the run ends.
 * The register stores a sha256 of the input and NEVER the input itself, and it is
 * not a cache: it records that a question was answered, it never answers one.
 *
 * Wired at the DEFAULT of the injectable `ask` parameter, not at the call site, so
 * a test that passes its own stub is still unrecorded and stays offline.
 */
const REGISTER = process.env.JEV_SCORE_REGISTER ?? "work/jev-score-register/scores.jsonl";
const recordedAskJev = recording(askJev, { path: REGISTER, extension: "omp-jev-foreman", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-foreman.decision.v1";
const WINDOW_SIZE = 20;
const REPEAT_TRIGGER = 3;
const NO_WRITE_TRIGGER = 8;

type ToolExecutionEvent = { type?: unknown; toolCallId?: unknown; toolName?: unknown; args?: unknown; result?: unknown; isError?: unknown };
type ForemanHost = { on: (event: string, handler: (event: ToolExecutionEvent) => Promise<undefined>) => void; appendEntry: Function };

function rowData(event: ToolExecutionEvent): Record<string, unknown> {
  const row = readRow(event);
  return row?.data ?? (event as Record<string, unknown>);
}
function commandText(event: ToolExecutionEvent): string {
  const args = rowData(event).args;
  if (typeof args === "string") return args.slice(0, 500);
  try { return JSON.stringify(args ?? {}).slice(0, 500); } catch { return "{}"; }
}
function isWriteTool(toolName: string): boolean { return /^(write|edit|apply_patch|write_file|file_write|save|create_file)$/i.test(toolName); }

export function createForeman({ ask = recordedAskJev, append = async () => {}, now = () => new Date().toISOString() } = {}) {
  const window: Array<{ toolCallId?: string; toolName: string; command: string; isError: boolean }> = [];
  const starts = new Map<string, ToolExecutionEvent>();
  let activeTrigger;
  return async function observe(event: ToolExecutionEvent): Promise<undefined> {
    try {
      const data = rowData(event);
      const eventType = data.type;
      const id = typeof data.toolCallId === "string" ? data.toolCallId : undefined;
      if (eventType === "tool_execution_start") {
        if (id) starts.set(id, event);
        return undefined;
      }
      if (eventType !== undefined && eventType !== "tool_execution_end") return undefined;
      const start = id ? starts.get(id) : undefined;
      if (id) starts.delete(id);
      const merged = start && data.args === undefined ? { ...start, ...data, args: start.args } : event;
      const mergedData = rowData(merged);
      const toolName = typeof mergedData.toolName === "string" ? mergedData.toolName : "unknown";
      const command = commandText(merged);
      window.push({ toolCallId: id, toolName, command, isError: mergedData.isError === true });
      while (window.length > WINDOW_SIZE) window.shift();
      const recent = window.slice(-REPEAT_TRIGGER);
      const repeats = recent.length === REPEAT_TRIGGER && new Set(recent.map((x) => `${x.toolName}:${x.command}`)).size === 1;
      const recentNoWrite = window.length >= NO_WRITE_TRIGGER && window.slice(-NO_WRITE_TRIGGER).every((x) => !isWriteTool(x.toolName));
      const trigger = repeats ? "repeated_command" : recentNoWrite ? "no_write_window" : undefined;
      if (!trigger) { activeTrigger = undefined; return undefined; }
      if (trigger === activeTrigger) return undefined;
      activeTrigger = trigger;
      const started = Date.now();
      const summary = window.map((x) => ({ toolCallId: x.toolCallId, toolName: x.toolName, command: x.command, isError: x.isError }));
      let result: JevResult;
      try { result = await ask({ state: { trigger, window: summary }, questions: { repeating: "Is the agent repeating itself or retrying the same obstacle?", progress: "Is the agent making meaningful progress toward its task?", stuck: "Is the agent stuck on one obstacle rather than progressing?" }, timeoutMs: 4000 }); }
      catch (error) { result = { ok: false, reason: "transport", error: String(error), latencyMs: Date.now() - started, model: "unknown" }; }
      const row: Record<string, unknown> = { schemaVersion: 1, kind: result.ok ? "foreman_scored" : "foreman_error", trigger, toolCallId: id, window: summary, latencyMs: result.latencyMs, model: result.model, timestamp: now() };
      if (result.ok) row.scores = result.scores;
      else { row.failureReason = result.reason; row.error = result.error; }
      try { await append(DECISION, row); } catch {}
      return undefined;
    } catch { return undefined; }
  };
}

export default function ompJevForeman(pi: ForemanHost): void {
  const observe = createForeman({ append: (type, data) => pi.appendEntry(type, data) });
  pi.on("tool_execution_start", observe);
  pi.on("tool_execution_end", observe);
}
