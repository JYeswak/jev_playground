/** Measured SciFact claim verifier: one Noul over {claim,evidence}, fixed 0.5 cut, advisory only. */
import { verifyClaim, type VerifyResult } from "../../kit/src/verify.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";
import type { AskOptions, JevResult } from "../../kit/src/client.ts";

const NUM = String.raw`\d[\d,.]*(?:[eE][-+]?\d+)?`;
const CHUNK = new RegExp(String.raw`(?<![A-Za-z0-9_.])(?<![A-Za-z]-)${NUM}(?:-${NUM})?(?:\/${NUM})*%?`, "g");
const THOUSANDS = /^\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:[eE][-+]?\d+)?%?$/;

export function numberTokens(blanked: string): Array<{ text: string; at: number }> {
  const out: Array<{ text: string; at: number }> = [];
  for (const match of blanked.matchAll(CHUNK)) {
    const text = match[0].replace(/[.,]+$/, "");
    const at = match.index ?? 0;
    const after = blanked[at + text.length] ?? "";
    if (/[A-Za-z0-9_]/.test(after)) continue;
    if (/^\d+\.\d+\.\d+/.test(text) && !text.includes("/")) continue;
    const parts = text.split(/\/|-(?=\d)/);
    if (parts.every((part) => !part.includes(",") || THOUSANDS.test(part))) {
      out.push({ text, at });
      continue;
    }
    let offset = 0;
    for (const piece of text.split(",")) {
      if (/\d/.test(piece)) out.push({ text: piece, at: at + offset });
      offset += piece.length + 1;
    }
  }
  return out.filter((token) => !/\d{8,}/.test(token.text));
}

// Legacy numeric experiment seam. The live tool delegates to kit/src/verify.ts at 0.5;
// numeric.mjs imports this pure policy for its separate preregistered comparisons.
export const SUPPORTED_AT = 0.8;
export const UNSUPPORTED_AT = 0.2;
export function classify(probability: unknown) {
  if (typeof probability !== "number" || !Number.isFinite(probability) || probability < 0 || probability > 1) return null;
  const confidence = Math.max(probability, 1 - probability);
  if (probability >= SUPPORTED_AT) return { verdict: "supported", confidence };
  if (probability <= UNSUPPORTED_AT) return { verdict: "unsupported", confidence };
  return { verdict: "unsure", confidence };
}

type ToolHost = { zod: { object: (shape: Record<string, unknown>) => unknown; string: () => { min: (n: number) => unknown } } };
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
    description: "Check whether evidence supports a qualitative claim with the measured SciFact Noul design. Uses a fixed 0.5 cut: supported above 0.5, unsupported at or below 0.5. Advisory only; numeric claims are not a measured scope. Without Jev it returns NOT_RUN.",
    parameters: pi.zod.object({ claim: pi.zod.string().min(1), evidence: pi.zod.string().min(1) }),
    async execute(_id: string, params: { claim: string; evidence: string }) {
      try {
        const result: VerifyResult = await verifyClaim({ claim: params.claim, evidence: params.evidence, ...(asker ? { ask: asker } : {}) });
        return {
          content: [{ type: "text", text: `verdict=${result.label} value=${result.value.toFixed(3)} threshold=${result.threshold} model=${result.model}` }],
          details: { verdict: result.label, label: result.label, value: result.value, threshold: result.threshold, model: result.model, latencyMs: result.latencyMs, usage: result.usage ?? null },
        };
      } catch (error) {
        return notRun(error instanceof Error ? error.message : String(error));
      }
    },
  };
}
