/**
 * Model-callable top-1 passage selection.
 *
 * This tool uses kit/src/rerank.ts: one Choice over 2-20 passages. The measured
 * design proves only the selected top-1, not a complete ranking. It is advisory
 * and returns NOT_RUN when Jev cannot be called.
 */
import { rerankTop1, type RerankResult } from "../jev-kit/rerank.ts";
import { useInfisicalKey } from "../jev-kit/use-infisical-key.ts";
import type { AskChoiceOptions, JevChoiceResult } from "../jev-kit/client.ts";

type ToolHost = {
  zod: {
    object: (shape: Record<string, unknown>) => unknown;
    string: () => { min: (n: number) => unknown };
    array: (item: unknown) => { min: (n: number) => { max: (n: number) => unknown } };
  };
};
type ChoiceAsker = (options: AskChoiceOptions) => Promise<JevChoiceResult>;

function notRun(reason: string) {
  return {
    content: [{ type: "text", text: `top1=false verdict=not_run reason=${reason} NOT_RUN` }],
    details: { top1: false, verdict: "not_run", reason, choice: null, selectedIndex: null, model: null },
  };
}

export default function jevRerankTool(pi: ToolHost, asker?: ChoiceAsker) {
  if (!asker) useInfisicalKey();
  return {
    name: "jev_rerank",
    label: "Jev rerank top-1",
    description:
      "Select the single most relevant passage with one Jev Choice over 2-20 passages. This is the measured FiQA/NFCorpus top-1 design; it does not produce a full ranking. Advisory only; without Jev it returns NOT_RUN.",
    parameters: pi.zod.object({
      query: pi.zod.string().min(1),
      passages: pi.zod.array(pi.zod.string().min(1)).min(2).max(20),
    }),
    async execute(_id: string, params: { query: string; passages: string[] }) {
      try {
        const candidates = params.passages.map((text, index) => ({ id: String(index), text }));
        const result: RerankResult = await rerankTop1({ query: params.query, candidates, ...(asker ? { ask: asker } : {}) });
        const selectedIndex = Number(result.choice);
        const selected = result.orderedCandidates[0];
        return {
          content: [{ type: "text", text: `top1=true choice=${result.choice} index=${selectedIndex} model=${result.model}\n${selected.text}` }],
          details: {
            top1: true,
            verdict: "selected",
            reason: null,
            choice: result.choice,
            selectedIndex,
            passage: selected.text,
            model: result.model,
            latencyMs: result.latencyMs,
            usage: result.usage ?? null,
          },
        };
      } catch (error) {
        return notRun(error instanceof Error ? error.message : String(error));
      }
    },
  };
}
