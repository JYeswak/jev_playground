/**
 * omp-jev-rerank — observe-only relevance scoring for noisy search output.
 *
 * REPO MINED: jev-rerank-bench (RUN; headline reproduces from its committed cache, Jev rubric
 * 0.692; receipt docs/demos/upstream-repro/jev-rerank-bench-20260918.json). Its question is
 * "can Jev rerank thirty search results usefully".
 *
 * THE OMP SURFACE. A `grep`/`rg` across a large repo returns dozens of hits, and the agent reads
 * them top-to-bottom in whatever order the tool emitted. Ordering by relevance to the stated
 * intent is a judgement — there is no regex for "this hit is the definition, those twelve are
 * call sites" — so a judge earns its seat here, exactly as it did not on the harm gate where
 * four regexes beat it 12/12 to 11/12.
 *
 * OBSERVE-ONLY, AND THAT IS NOT TEMPORARY CAUTION. Nothing here reorders what the agent sees.
 * We have no evidence these scores improve anything on OUR corpus — upstream's number came from
 * their cache, and this lane has already watched a model's headline invert on real data twice
 * (R28, router savings). Scoring first, acting later, only if a measurement earns it.
 *
 * Never blocks. Never throws into the host. Returns undefined on every path.
 * A failed call records `rerank_error` — never a silent pass (R40).
 */
import { askJev } from "../../jev-client/src/index.ts";

const DECISION = "com.zeststream.omp-jev-rerank.decision.v1";
const DIAG = "com.zeststream.omp-jev-rerank.diagnostic.v1";

const MIN_HITS = 8;       // below this, ordering is not a problem worth an API call
const MAX_HITS = 30;      // upstream's benchmark size
const MAX_LINE = 240;

type ToolResultEvent = {
  toolName?: unknown;
  name?: unknown;
  toolCallId?: unknown;
  input?: unknown;
  isError?: unknown;
  content?: unknown;
};
type Host = {
  on: (event: string, handler: (event: ToolResultEvent) => Promise<undefined>) => void;
  appendEntry: (type: string, data: Record<string, unknown>) => Promise<unknown>;
};

function readString(source: unknown, key: string): string | undefined {
  if (!source || typeof source !== "object" || !(key in source)) return undefined;
  const value: unknown = Reflect.get(source, key);
  return typeof value === "string" ? value : undefined;
}

/**
 * `tool_result` carries `content` as an ARRAY of parts, not a string — verified against
 * ~/.omp/omp-extensions/observational-tool-result.ts:142, which guards on
 * `!Array.isArray(event.content)`. I first wrote this against an invented `event.result`
 * string and a `tool_call_result` event that does not exist; the real event names are
 * tool_call, tool_result, user_bash, session_start.
 */
function resultText(content: unknown): string | undefined {
  if (!Array.isArray(content)) return undefined;
  const parts: string[] = [];
  for (const part of content) {
    const text = readString(part, "text") ?? (typeof part === "string" ? part : undefined);
    if (text !== undefined) parts.push(text);
  }
  return parts.length > 0 ? parts.join("\n") : undefined;
}

export default function ompJevRerank(pi: Host) {
  pi.on("tool_result", async (event) => {
    try {
      const tool = String(event?.toolName ?? event?.name ?? "");
      if (tool !== "grep" && tool !== "glob") return undefined;
      if (event?.isError === true) return undefined;

      const text = resultText(event?.content);
      if (text === undefined) return undefined;
      const hits = text.split("\n").filter((line) => line.trim().length > 0);
      if (hits.length < MIN_HITS) return undefined;

      const pattern = readString(event?.input, "pattern") ?? readString(event?.input, "path") ?? "";
      const intent = readString(event?.input, "i") ?? "";
      const toolCallId = typeof event?.toolCallId === "string" ? event.toolCallId : null;

      try {
        await pi.appendEntry(DIAG, {
          kind: "search_result_observed",
          tool,
          hitCount: hits.length,
          toolCallId,
          timestamp: new Date().toISOString(),
        });
      } catch {}

      const candidates = hits.slice(0, MAX_HITS).map((line, index) => `${index}: ${line.slice(0, MAX_LINE)}`);
      const result = await askJev({
        state: { intent, pattern, candidates },
        // Question-shape holdout c6b77b8 rescued noise and definitional; ordered remains shipped.
        questions: {
          ordered: "Are these candidates already ordered with the most relevant to the stated intent first?",
          noise: "Does any entry fail to show a code line with the term?",
          definitional: "Do any of the first three show a definition signature?",
        },
        timeoutMs: 3000,
      });

      try {
        await pi.appendEntry(DECISION, {
          schemaVersion: 1,
          kind: result.ok ? "rerank_scored" : "rerank_error",
          tool,
          intent: intent.slice(0, 300),
          pattern: pattern.slice(0, 300),
          hitCount: hits.length,
          scoredCount: candidates.length,
          toolCallId,
          // absent, never defaulted: a missing score must not read as a clean list
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
