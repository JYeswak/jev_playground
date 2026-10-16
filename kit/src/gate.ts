type RiskModule = { RISK: Record<string, unknown>; STATE_CONTEXT: string; CUT: number };
const riskModule = await (async (): Promise<RiskModule> => {
  try {
    // @ts-expect-error The frozen JS RISK module has no declaration file.
    return await import("../../work/bicameral-gate/questions.mjs") as RiskModule;
  } catch {
    // The package carries this build-generated copy for fresh installs.
    // @ts-expect-error The generated package artifact has no declaration file.
    return await import("./questions.mjs") as RiskModule;
  }
})();
const { RISK, STATE_CONTEXT, CUT } = riskModule;
import { askJevBundle, configuredBackend, DEFAULT_MODEL, previewJevRequest, type BackendDryRunResult, type BackendMode, type JevBundleResult, type JevUsage } from "./client.ts";
import { sizePreflight } from "./preflight.ts";
import { validateNoulAnswer } from "./validate.ts";

export { CUT, RISK, STATE_CONTEXT };

export type GateScores = Record<string, number>;

export type GateResult =
  | {
      ok: true;
      flag: boolean;
      maxScore: number;
      scores: GateScores;
      model: string;
      latencyMs: number;
      usage?: JevUsage;
      backend?: "jev" | "clef";
      backendRequested?: BackendMode;
      routeReason?: string;
      fallbackReason?: string;
    }
  | {
      ok: false;
      reason: string;
      error: string;
      model: string;
      latencyMs: number;
      backend?: "jev" | "clef";
      backendRequested?: BackendMode;
      routeReason?: string;
      fallbackReason?: string;
    }
  | BackendDryRunResult;

export type GateAsk = (options: {
  state: Record<string, unknown>;
  questions: typeof RISK;
  model: string;
  backend?: BackendMode;
}) => Promise<JevBundleResult>;

export type GateOptions = {
  command: string;
  model?: string;
  backend?: BackendMode;
  dryRun?: boolean;
  ask?: GateAsk;
};

/**
 * Apply the frozen five-Noul RISK design to one command.
 * The question object is imported from bicameral-gate; it is not copied here.
 */
export async function gateCommand(options: GateOptions): Promise<GateResult> {
  if (typeof options.command !== "string" || options.command.trim().length === 0) {
    return { ok: false, reason: "invalid-input", error: "command must be non-empty", model: options.model ?? DEFAULT_MODEL, latencyMs: 0 };
  }
  const model = options.model ?? DEFAULT_MODEL;
  const state = { command: options.command, context: STATE_CONTEXT };
  sizePreflight(state, RISK);
  if (options.dryRun) {
    const requested = configuredBackend(options.backend);
    if (!requested) return { ok: false, reason: "usage", error: "backend must be jev, clef, or auto", model, latencyMs: 0 };
    if (requested === "clef") return { ok: false, reason: "uncalibrated", error: "Clef does not support bundled questions", model, latencyMs: 0, backend: "clef", backendRequested: requested };
    return previewJevRequest(state, RISK, model, requested, "bundle");
  }
  const ask = options.ask ?? ((request) => askJevBundle(request));
  const result = await ask({state, questions: RISK, model, ...(options.backend === undefined ? {} : { backend: options.backend })});
  if (!result.ok) return result;
  const scores: GateScores = {};
  for (const [key, answer] of Object.entries(result.answers)) scores[key] = validateNoulAnswer(answer);
  const maxScore = Math.max(...Object.values(scores));
  return { ok: true, flag: maxScore > CUT, maxScore, scores, model: result.resolvedModel, latencyMs: result.latencyMs, usage: result.usage, ...(result.backend ? { backend: result.backend } : {}), ...(result.backendRequested ? { backendRequested: result.backendRequested } : {}), ...(result.routeReason ? { routeReason: result.routeReason } : {}), ...(result.fallbackReason ? { fallbackReason: result.fallbackReason } : {}) };
}
