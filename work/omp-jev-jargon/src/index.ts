/**
 * omp-jev-jargon — observe-only scorer for engineering words in user-facing copy.
 *
 * WHY THIS ONE CALLS JEV. A stoplist can GATE "is there an engineering word
 * here". It cannot verdict "would the client say this word for this thing".
 * There is no regex kind: the list decides whether to ask, not what the copy is.
 *
 * NEVER blocks. NEVER throws into the host. Returns undefined on every path.
 * A failed call records `jargon_error`, never a pass.
 */
import { askJev } from "../../jev-client/src/index.ts";
import {
  isUserFacingWrite,
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
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-jargon", model: "jev-1.13.0" });

const DECISION = "com.zeststream.omp-jev-jargon.decision.v1";

export const QUESTIONS = {
  client_word: "Would the client say this word for this thing, in their own language?",
};

/** Local engineering stoptokens. Case-insensitive word-boundary GATE, not a verdict. */
export const STOPTOKENS = [
  "payload",
  "hydrate",
  "idempotent",
  "shard",
  "mutex",
  "regex",
  "protobuf",
  "sidecar",
  "ingest",
  "upsert",
  "cardinality",
  "idempotency",
  "backfill",
];

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

export function matchedTokens(content: string): string[] {
  const found: string[] = [];
  for (const token of STOPTOKENS) {
    if (new RegExp(`\\b${token}\\b`, "i").test(content)) found.push(token);
  }
  return found;
}

export default function ompJevJargon(pi: Host) {
  pi.on("tool_call", async (event) => {
    try {
      if (!isUserFacingWrite(event)) return undefined;
      const content = contentFromEvent(event);
      if (content === undefined) return undefined;
      const suspects = matchedTokens(content);
      if (suspects.length === 0) return undefined;
      const path = filePathFromEvent(event);
      const id = toolCallId(event);

      const result = await ask({
        state: { path, copy: clip(content, 3000), suspects },
        questions: QUESTIONS,
        timeoutMs: 2500,
      });
      const probabilities = result.ok ? result.scores : undefined;
      const error = result.ok ? undefined : `${result.reason}: ${result.error}`;
      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: probabilities ? "jargon_scored" : "jargon_error",
          path,
          toolCallId: id,
          suspects,
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
