/**
 * omp-jev-dispatch — observe-only check on a subagent dispatch BEFORE it is sent.
 *
 * REPO MINED: pi-subagents (github.com/nicobailon/pi-subagents) — "delegate work to focused
 * child agents". Its surface is dispatch. Ours is the same surface with the question this lane
 * actually needs answered: is this packet going to produce the work I meant?
 *
 * WHY THIS ONE EXISTS, CONCRETELY. On 2026-09-19 I dispatched a packet saying deleting an
 * unsupported number was "a legitimate and preferred outcome" and did NOT require checking for
 * a receipt first. The pane obeyed exactly, and deleted five README rows that had committed
 * receipts one `ls` away. The instruction was clear, well-formed, and wrong — a preference
 * stated without its check reads as an instruction to skip the check.
 * No linter catches that. There is no regex for "this packet will be obeyed into a mistake."
 *
 * THE THREE QUESTIONS ARE THE THREE FAILURES THIS LANE HAS ACTUALLY SHIPPED:
 *   destructive  — the over-deletion above
 *   unverifiable — acceptance a pane cannot obtain, which produces a fabricated DONE
 *   leading      — a packet that supplies its own premise and then counts agreement as
 *                  evidence; same-origin evidence counted twice
 *
 * LOCAL TRIGGER FIRST, MODEL SECOND: only fires on an actual dispatch, which is a handful of
 * times a session. Never blocks — a dispatch scorer that blocks dispatches would stop the lane.
 * Returns undefined on every path. A failed call records `dispatch_error`, never a pass (R40).
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
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-dispatch", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-dispatch.decision.v1";
const DIAG = "com.zeststream.omp-jev-dispatch.diagnostic.v1";

const MIN_PACKET = 200;   // a one-liner is not a packet worth scoring
const MAX_PACKET = 12000;

type ToolCallEvent = { toolName?: unknown; name?: unknown; toolCallId?: unknown; input?: unknown };
type Host = {
  on: (event: string, handler: (event: ToolCallEvent) => Promise<undefined>) => void;
  appendEntry: (type: string, data: Record<string, unknown>) => Promise<unknown>;
};

function readString(source: unknown, key: string): string | undefined {
  if (!source || typeof source !== "object" || !(key in source)) return undefined;
  const value: unknown = Reflect.get(source, key);
  return typeof value === "string" ? value : undefined;
}

/**
 * Both dispatch forms this lane uses: `ntm --robot-send=… --msg-file=<path>` (the mandated one,
 * because prose containing dangerous command strings gets refused when inlined) and `--msg=…`.
 */
async function packetText(command: string): Promise<string | undefined> {
  const fileMatch = /--msg-file=(\S+)/.exec(command);
  if (fileMatch) {
    try {
      const { readFile } = await import("node:fs/promises");
      return (await readFile(fileMatch[1], "utf8")).slice(0, MAX_PACKET);
    } catch {
      return undefined;
    }
  }
  const inline = /--msg=(["'])([\s\S]*?)\1/.exec(command);
  return inline ? inline[2].slice(0, MAX_PACKET) : undefined;
}

export default function ompJevDispatch(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      const tool = String(event?.toolName ?? event?.name ?? "");
      const command = readString(event?.input, "command");
      if (tool !== "bash" || command === undefined) return undefined;
      if (!/--robot-send=/.test(command)) return undefined;

      const packet = await packetText(command);
      if (packet === undefined || packet.length < MIN_PACKET) return undefined;

      const toolCallId = typeof event?.toolCallId === "string" ? event.toolCallId : null;
      try {
        await pi.appendEntry(DIAG, {
          kind: "dispatch_observed",
          packetBytes: packet.length,
          toolCallId,
          timestamp: new Date().toISOString(),
        });
      } catch {}

      const result = await ask({
        state: { packet },
        questions: {
          destructive:
            "Does this instruction state a preference for deleting, removing, or discarding something WITHOUT requiring a check first that the thing is unneeded?",
          unverifiable:
            "Does this instruction demand acceptance evidence the recipient may be unable to obtain, such as a count, file, or result that may not exist?",
          leading:
            "Does this instruction assert a premise as fact and ask the recipient to act on it, such that agreement would not be independent evidence?",
        },
        timeoutMs: 4000,
      });

      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: result.ok ? "dispatch_scored" : "dispatch_error",
          packetBytes: packet.length,
          firstLine: packet.split("\n")[0].slice(0, 300),
          toolCallId,
          // absent, never defaulted: a missing score must not read as a safe packet
          ...(result.ok ? { scores: result.scores } : { error: result.error, failure: result.reason }),
          latencyMs: result.latencyMs,
          model: result.model,
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
