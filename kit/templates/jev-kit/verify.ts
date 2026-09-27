import { askJev, type AskOptions, type JevResult, type JevUsage } from "./client.ts";
import { sizePreflight } from "./preflight.ts";

export const SCIFACT_INSTRUCTIONS = "Does the evidence support the claim?";
export const SCIFACT_CRITERIA = {
  true: "The evidence states the claim or directly implies that it is true",
  false: "The evidence contradicts the claim, or does not address what the claim asserts",
} as const;
export const SUPPORT_THRESHOLD = 0.5;

export type VerifyOptions = {
  claim: string;
  evidence: string;
  ask?: (options: AskOptions) => Promise<JevResult>;
  apiKey?: string;
  fetchImpl?: typeof fetch;
  model?: string;
};

export type VerifyResult = {
  ok: true;
  value: number;
  label: "supported" | "unsupported";
  threshold: number;
  latencyMs: number;
  model: string;
  usage?: JevUsage;
};

export async function verifyClaim(options: VerifyOptions): Promise<VerifyResult> {
  if (typeof options.claim !== "string" || options.claim.trim().length === 0) {
    throw new Error("verify claim must be a non-empty string");
  }
  if (typeof options.evidence !== "string" || options.evidence.trim().length === 0) {
    throw new Error("verify evidence must be a non-empty string");
  }

  const state = { claim: options.claim, evidence: options.evidence };
  const question = { type: "noul", instructions: SCIFACT_INSTRUCTIONS, criteria: SCIFACT_CRITERIA };
  sizePreflight(state, { value: question });

  const ask = options.ask ?? askJev;
  const result = await ask({
    state,
    questions: { value: { instructions: SCIFACT_INSTRUCTIONS, criteria: SCIFACT_CRITERIA } },
    apiKey: options.apiKey,
    fetchImpl: options.fetchImpl,
    model: options.model,
  });
  if (!result.ok) throw new Error(`verify failed (${result.reason}): ${result.error}`);
  const value = result.scores.value;
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1) {
    throw new Error("verify returned an invalid Noul value");
  }
  return {
    ok: true,
    value,
    label: value > SUPPORT_THRESHOLD ? "supported" : "unsupported",
    threshold: SUPPORT_THRESHOLD,
    latencyMs: result.latencyMs,
    model: result.model,
    ...(result.usage ? { usage: result.usage } : {}),
  };
}

export { SUPPORT_THRESHOLD as SCIFACT_SUPPORT_THRESHOLD };
