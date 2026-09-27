/**
 * Model-callable SciFact claim verifier.
 *
 * This tool delegates to kit/src/verify.ts: one Noul over {claim, evidence}
 * with the measured 0.5 support cut. It is advisory and never blocks a tool.
 */
import { verifyClaim, type VerifyResult } from "../jev-kit/verify.ts";
import { useInfisicalKey } from "../jev-kit/use-infisical-key.ts";
import type { AskOptions, JevResult } from "../jev-kit/client.ts";

type ToolHost = {
  zod: { object: (shape: Record<string, unknown>) => unknown; string: () => { min: (n: number) => unknown } };
};
type NoulAsker = (options: AskOptions) => Promise<JevResult>;

function notRun(reason: string) {
  return {
    content: [{ type: "text", text: `verdict=not_run reason=${reason} NOT_RUN` }],
    details: { verdict: "not_run", reason, label: null, value: null, threshold: 0.5, model: null },
  };
}

export default function jevClaimCheckTool(pi: ToolHost, asker?: NoulAsker) {
  if (!asker) useInfisicalKey();
  return {
    name: "jev_claim_check",
    label: "Jev claim check",
    description:
      "Check whether evidence supports a qualitative claim with the measured SciFact Noul design. Uses a fixed 0.5 cut: supported above 0.5, unsupported at or below 0.5. Advisory only; numeric claims are not a measured scope. Without Jev it returns NOT_RUN.",
    parameters: pi.zod.object({
      claim: pi.zod.string().min(1),
      evidence: pi.zod.string().min(1),
    }),
    async execute(_id: string, params: { claim: string; evidence: string }) {
      try {
        const result: VerifyResult = await verifyClaim({ claim: params.claim, evidence: params.evidence, ...(asker ? { ask: asker } : {}) });
        return {
          content: [{ type: "text", text: `verdict=${result.label} value=${result.value.toFixed(3)} threshold=${result.threshold} model=${result.model}` }],
          details: {
            verdict: result.label,
            label: result.label,
            value: result.value,
            threshold: result.threshold,
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
