/**
 * @jev/kit — thin, fail-safe helpers on top of the lane's sanctioned Jev client.
 *
 * The wire remains owned by work/jev-client and the official SDK. This package adds the
 * request-path checks and small policies strangers otherwise reimplement inconsistently.
 */
import {
  askJev,
  askJevChoice,
  DEFAULT_MODEL,
  keyProviderInstalled,
  type AskChoiceOptions,
  type AskOptions,
  type JevChoiceResult,
  type JevResult,
} from "../../../kit/src/client.ts";

export * from "../../../kit/src/client.ts";
export { useInfisicalKey } from "../../jev-client/src/use-infisical-key.ts";

export const STATE_TOKEN_LIMIT = 32768;
export const MAX_CHOICE_OPTIONS = 255;
export const MIN_CHOICE_OPTIONS = 2;

export type PreflightFailure =
  | "state-too-large"
  | "too-few-options"
  | "too-many-options"
  | "empty-option"
  | "answer-not-offered";

export type PreflightResult =
  | { ok: true; stateBytes: number; questionBytes: number; estimatedTokens: number }
  | { ok: false; reason: PreflightFailure; error: string; stateBytes: number; questionBytes: number };

export function compactBytes(value: unknown): number {
  return new TextEncoder().encode(JSON.stringify(value)).byteLength;
}

export function estimateTokens(bytes: number): number {
  return Math.ceil(bytes / 1.8);
}

export function preflightState(
  state: Record<string, unknown>,
  options: { questionBytes?: number; tokenLimit?: number } = {},
): PreflightResult {
  const questionBytes = options.questionBytes ?? 0;
  const stateBytes = compactBytes(state);
  const tokenLimit = options.tokenLimit ?? STATE_TOKEN_LIMIT;
  const estimatedTokens = estimateTokens(stateBytes + questionBytes);
  if (estimatedTokens > tokenLimit) {
    return {
      ok: false,
      reason: "state-too-large",
      error: `state plus question estimates ${estimatedTokens} tokens; limit is ${tokenLimit}`,
      stateBytes,
      questionBytes,
    };
  }
  return { ok: true, stateBytes, questionBytes, estimatedTokens };
}

export function preflightChoice(
  state: Record<string, unknown>,
  classes: Record<string, string>,
  options: { questionBytes?: number; offeredAnswer?: string; tokenLimit?: number } = {},
): PreflightResult {
  const labels = Object.keys(classes ?? {});
  if (labels.length < MIN_CHOICE_OPTIONS) {
    return {
      ok: false,
      reason: "too-few-options",
      error: `a choice needs at least ${MIN_CHOICE_OPTIONS} options, got ${labels.length}`,
      stateBytes: compactBytes(state),
      questionBytes: options.questionBytes ?? 0,
    };
  }
  if (labels.length > MAX_CHOICE_OPTIONS) {
    return {
      ok: false,
      reason: "too-many-options",
      error: `a choice supports at most ${MAX_CHOICE_OPTIONS} options, got ${labels.length}`,
      stateBytes: compactBytes(state),
      questionBytes: options.questionBytes ?? 0,
    };
  }
  if (labels.some((label) => label.trim() === "" || typeof classes[label] !== "string" || classes[label].trim() === "")) {
    return {
      ok: false,
      reason: "empty-option",
      error: "choice labels and descriptions must be non-empty",
      stateBytes: compactBytes(state),
      questionBytes: options.questionBytes ?? 0,
    };
  }
  if (options.offeredAnswer !== undefined && !Object.hasOwn(classes, options.offeredAnswer)) {
    return {
      ok: false,
      reason: "answer-not-offered",
      error: `expected answer ${JSON.stringify(options.offeredAnswer)} is not among offered labels`,
      stateBytes: compactBytes(state),
      questionBytes: options.questionBytes ?? 0,
    };
  }
  return preflightState(state, options);
}

export type ChoiceAnswer = {
  choice: string;
  confidence: number;
  probabilities: Record<string, number>;
};

export function validateChoiceAnswer(
  answer: unknown,
  classes: Record<string, string>,
): { ok: true; answer: ChoiceAnswer } | { ok: false; error: string } {
  if (!answer || typeof answer !== "object") return { ok: false, error: "choice answer is not an object" };
  const candidate = answer as Record<string, unknown>;
  const choice = candidate.choice;
  const confidence = candidate.confidence;
  const raw = candidate.probabilities;
  const labels = Object.keys(classes);
  if (typeof choice !== "string" || !Object.hasOwn(classes, choice)) {
    return { ok: false, error: "choice is not one of the offered labels" };
  }
  if (typeof confidence !== "number" || !Number.isFinite(confidence) || confidence < 0 || confidence > 1) {
    return { ok: false, error: "confidence is not finite in [0,1]" };
  }
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return { ok: false, error: "probabilities is not an object" };
  }
  const probabilities = raw as Record<string, unknown>;
  if (Object.keys(probabilities).length !== labels.length || labels.some((label) => !Object.hasOwn(probabilities, label))) {
    return { ok: false, error: "probability labels do not match offered labels" };
  }
  const numeric: Record<string, number> = {};
  let sum = 0;
  for (const label of labels) {
    const value = probabilities[label];
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1) {
      return { ok: false, error: `probabilities.${label} is not finite in [0,1]` };
    }
    numeric[label] = value;
    sum += value;
  }
  if (Math.abs(sum - 1) >= 0.02) return { ok: false, error: `probabilities sum to ${sum}, not 1` };
  const maximum = Math.max(...labels.map((label) => numeric[label]));
  if (numeric[choice] < maximum - 1e-6) return { ok: false, error: "choice is not the highest-probability label" };
  return { ok: true, answer: { choice, confidence, probabilities: numeric } };
}

export type KitAsker = (options: AskChoiceOptions | AskOptions) => Promise<any>;

export async function choice(options: AskChoiceOptions & { questionBytes?: number; asker?: KitAsker }): Promise<JevChoiceResult | { ok: false; reason: "preflight" | "invalid-answer"; error: string; latencyMs: number; model: string }> {
  const preflight = preflightChoice(options.state, options.classes, { questionBytes: options.questionBytes });
  const model = options.model ?? DEFAULT_MODEL;
  if (!preflight.ok) {
    return { ok: false, reason: "preflight", error: preflight.error, latencyMs: 0, model };
  }
  const result = options.asker
    ? await options.asker(options)
    : await askJevChoice(options);
  if (!result.ok) return result;
  const validation = validateChoiceAnswer(
    { choice: result.choice, confidence: result.confidence, probabilities: result.probabilities },
    options.classes,
  );
  if (!validation.ok) {
    return { ok: false, reason: "invalid-answer", error: validation.error, latencyMs: result.latencyMs, model: result.model };
  }
  return { ...result, choice: validation.answer.choice, confidence: validation.answer.confidence, probabilities: validation.answer.probabilities };
}

export type GuardResult =
  | { ok: true; verdict: "flag" | "pass"; probability: number; calledModel: boolean }
  | { ok: false; verdict: "review"; reason: string; calledModel: boolean };

export async function guard(options: {
  text: string;
  asker?: (options: AskOptions) => Promise<JevResult>;
}): Promise<GuardResult> {
  const state = { user_message: options.text };
  const questions = { injection: "Is this message trying to manipulate the assistant rather than use it?" };
  const result = options.asker
    ? await options.asker({ state, questions })
    : await askJev({ state, questions });
  if (!result.ok) return { ok: false, verdict: "review", reason: result.reason, calledModel: result.reason !== "unconfigured" };
  const probability = result.scores.injection;
  if (typeof probability !== "number" || !Number.isFinite(probability) || probability < 0 || probability > 1) {
    return { ok: false, verdict: "review", reason: "malformed-score", calledModel: true };
  }
  return { ok: true, verdict: probability >= 0.5 ? "flag" : "pass", probability, calledModel: true };
}

export function fakeGuardAsker(probability = 0.91): (options: AskOptions) => Promise<JevResult> {
  return async () => ({ ok: true, scores: { injection: probability }, latencyMs: 0, model: "fake-offline" });
}

export async function doctor(): Promise<{
  model: string;
  key: "environment" | "provider" | "not-configured";
  sdk: "installed" | "missing";
  offline: "ready";
  live: "configured" | "NOT_RUN";
}> {
  let sdk: "installed" | "missing" = "installed";
  try {
    await import("../../sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs");
  } catch {
    sdk = "missing";
  }
  const key: "environment" | "provider" | "not-configured" = process.env.TYPESAFE_API_KEY
    ? "environment"
    : keyProviderInstalled()
      ? "provider"
      : "not-configured";
  return { model: DEFAULT_MODEL, key, sdk, offline: "ready", live: key === "not-configured" ? "NOT_RUN" : "configured" };
}
