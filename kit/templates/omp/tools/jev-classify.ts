/**
 * Model-callable Banking77-style intent classifier.
 *
 * This tool delegates to kit/src/classify.ts: one Choice over the supplied
 * labels using the measured Banking77 instruction. Confidence is returned as
 * information only; no action threshold is invented here.
 */
import { classifyText, type ClassifyResult } from "../jev-kit/classify.ts";
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
    content: [{ type: "text", text: `label=null verdict=not_run reason=${reason} NOT_RUN` }],
    details: { verdict: "not_run", reason, label: null, confidence: null, model: null },
  };
}

export default function jevClassifyTool(pi: ToolHost, asker?: ChoiceAsker) {
  if (!asker) useInfisicalKey();
  return {
    name: "jev_classify",
    label: "Jev classify",
    description:
      "Classify text with the measured Banking77 intent-routing Choice design. Supply the offered labels (the measured corpus has 77); confidence is passed through without an invented action threshold. Without Jev it returns NOT_RUN.",
    parameters: pi.zod.object({
      text: pi.zod.string().min(1),
      labels: pi.zod.array(pi.zod.string().min(1)).min(2).max(77),
    }),
    async execute(_id: string, params: { text: string; labels: string[] }) {
      try {
        const result: ClassifyResult = await classifyText({ text: params.text, labels: params.labels, ...(asker ? { ask: asker } : {}) });
        return {
          content: [{ type: "text", text: `label=${result.label} confidence=${result.confidence.toFixed(3)} model=${result.model}` }],
          details: {
            verdict: "classified",
            label: result.label,
            confidence: result.confidence,
            probabilities: result.probabilities,
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
