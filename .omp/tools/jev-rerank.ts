/**
 * Model-callable rerank. Returns an order the caller uses.
 *
 * The observe-only hook at work/omp-jev-rerank scores grep hits and changes
 * nothing. This tool is the other half: given a query and passages, it returns
 * them ordered by the score-batch rubric that won NevIR (0.711 vs BM25 0.022,
 * n=1383, jev-rerank-bench/results/nevir.json).
 *
 * No key: input order, ordered=false, reason=unconfigured. Never throws.
 * Never prints a key.
 */
import { rerank } from "../../work/nev-rerank/src/rank.ts";
import { liveAsker } from "../../work/nev-rerank/src/live.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

type ToolHost = {
  zod: {
    object: (shape: Record<string, unknown>) => unknown;
    string: () => { min: (n: number) => unknown };
    array: (item: unknown) => { min: (n: number) => { max: (n: number) => unknown } };
  };
};

export default function jevRerankTool(pi: ToolHost) {
  useInfisicalKey();
  return {
    name: "jev_rerank",
    label: "Jev rerank",
    description:
      "Reorder passages by how well each supplies the query. Uses the Jev 4-level score rubric. Returns the ordered list. If the API key is absent, returns the input order and says NOT_RUN.",
    parameters: pi.zod.object({
      query: pi.zod.string().min(1),
      passages: pi.zod.array(pi.zod.string().min(1)).min(2).max(30),
    }),
    async execute(_id: string, params: { query: string; passages: string[] }) {
      try {
        const result = await rerank(params.query, params.passages, liveAsker);
        const lines = result.ranking.map((row, place) => `${place + 1}. [${row.id} ${Number.isFinite(row.score) ? row.score.toFixed(3) : "-"}] ${row.text}`);
        const head = result.ordered
          ? "ordered=true calledModel=true"
          : `ordered=false reason=${result.reason ?? "unknown"} NOT_RUN`;
        return {
          content: [{ type: "text", text: `${head}\n${lines.join("\n")}` }],
          details: {
            ordered: result.ordered,
            reason: result.reason ?? null,
            calledModel: result.calledModel,
            truncated: result.truncated,
            ranking: result.ranking.map((row) => ({ id: row.id, index: row.index, score: row.score })),
          },
        };
      } catch (err) {
        const reason = err instanceof Error ? err.message : "throw";
        return {
          content: [{ type: "text", text: `ordered=false reason=throw NOT_RUN\n${reason}` }],
          details: { ordered: false, reason: "throw", calledModel: false, truncated: false, ranking: [] },
        };
      }
    },
  };
}
