/**
 * omp-jev-commit — observe-only check that a commit MESSAGE describes its DIFF.
 *
 * REPO MINED: commit-miner (github.com/devanshbatham/commit-miner) — "classify Git commit diffs
 * and messages with Jev". Upstream is a batch CLI over history. This is the same judgement
 * moved to the moment it can still matter: the commit being written, in the session writing it.
 * Our own adoption test RULED_OUT the upstream tool on cost
 * (docs/demos/upstream-repro/commit-miner-adoption-test-20260919.md: 128% of budget, draw
 * 0.0128 vs a 0.01 bar). That ruling was about MINING HISTORY. It says nothing about scoring
 * one commit at the moment it is authored, which is a different surface with a different cost.
 *
 * WHY A JUDGE EARNS ITS SEAT. "Does this subject line describe this diff?" has no regex. A
 * conventional-commit linter checks `feat(scope):` and passes a subject that says the opposite
 * of what the diff does. This lane shipped several such subjects today.
 *
 * LOCAL TRIGGER FIRST, MODEL SECOND — the harm gate already ruled against paying per call when
 * a cheap test decides. We only ask Jev when a bash command is an actual commit that carries a
 * message, which is a handful of times a session, not per tool call.
 *
 * Never blocks. Never throws into the host. Returns undefined on every path.
 * A failed call records `commit_error` — never a silent pass (NEGATIVE_EVIDENCE R40).
 */
import { askJev } from "../../jev-client/src/index.ts";
import { recording } from "../../jev-score-register/register.mjs";

/**
 * Every score this extension computes is persisted, so a later measurement can read it
 * without re-calling the API. Closes the hole named in
 * docs/demos/upstream-repro/commit-learnings-20260920.md (bf12406): 21 packages, 0
 * exporting a Jev-derived score. The register stores a sha256 of the input, never the
 * input — the diff and the message never reach disk through this path.
 */
const REGISTER = process.env.JEV_SCORE_REGISTER ?? "work/jev-score-register/scores.jsonl";
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-commit", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-commit.decision.v1";
const DIAG = "com.zeststream.omp-jev-commit.diagnostic.v1";

const MAX_DIFF = 12000;
const MAX_MESSAGE = 2000;

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
 * Both message forms this lane actually uses: `-F <file>` (the mandated one, because backticks
 * in an inline `-m` were once executed as command substitution) and `-m "..."`.
 * Returns the message text, reading the file when the command used -F.
 */
async function commitMessage(command: string): Promise<string | undefined> {
  const fileMatch = /-F\s+(\S+)/.exec(command);
  if (fileMatch) {
    try {
      const { readFile } = await import("node:fs/promises");
      return (await readFile(fileMatch[1], "utf8")).slice(0, MAX_MESSAGE);
    } catch {
      return undefined;
    }
  }
  const inline = /-m\s+(["'])([\s\S]*?)\1/.exec(command);
  return inline ? inline[2].slice(0, MAX_MESSAGE) : undefined;
}

export default function ompJevCommit(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      const tool = String(event?.toolName ?? event?.name ?? "");
      const command = readString(event?.input, "command");
      if (tool !== "bash" || command === undefined) return undefined;
      if (!/\bgit\s+commit\b/.test(command)) return undefined;

      const message = await commitMessage(command);
      if (message === undefined) return undefined;

      const toolCallId = typeof event?.toolCallId === "string" ? event.toolCallId : null;
      try {
        await pi.appendEntry(DIAG, {
          kind: "commit_observed",
          toolCallId,
          timestamp: new Date().toISOString(),
        });
      } catch {}

      // The staged diff is the ground truth the message is claiming to describe.
      let diff = "";
      try {
        const { execFile } = await import("node:child_process");
        const { promisify } = await import("node:util");
        const run = promisify(execFile);
        const { stdout } = await run("git", ["diff", "--cached"], { maxBuffer: 1024 * 1024 * 8 });
        diff = stdout.slice(0, MAX_DIFF);
      } catch {
        diff = "";
      }
      if (diff.length === 0) return undefined;

      const result = await ask({
        state: { message, diff },
        questions: {
          describes: "Does the commit message accurately describe what this diff actually changes?",
          overstates: "Does the message claim work, results, or verification that the diff does not contain?",
          omits: "Does the diff contain a significant change the message never mentions?",
        },
        timeoutMs: 4000,
      });

      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: result.ok ? "commit_scored" : "commit_error",
          subject: message.split("\n")[0].slice(0, 300),
          diffBytes: diff.length,
          toolCallId,
          // absent, never defaulted: a missing score must not read as an accurate message
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
