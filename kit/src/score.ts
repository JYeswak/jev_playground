import { askJevScore, configuredBackend, previewJevRequest, type AskScoreOptions, type BackendDryRunResult, type BackendMode, type JevScoreResult, type JevUsage } from "./client.ts";
import { optionsPreflight, sizePreflight } from "./preflight.ts";

export const SST5_INSTRUCTIONS = "How positive is this movie review sentence?";
export const SST5_LEVELS = [
  "Very negative: strongly critical, scathing, or contemptuous",
  "Negative: somewhat critical or unfavorable",
  "Neutral: neither positive nor negative, or evenly mixed",
  "Positive: somewhat favorable or approving",
  "Very positive: strongly enthusiastic, glowing, or full of praise",
] as const;

export type ScoreOptions = {
  text: string;
  levels: readonly string[];
  backend?: BackendMode;
  dryRun?: boolean;
  ask?: (options: AskScoreOptions) => Promise<JevScoreResult>;
  apiKey?: string;
  fetchImpl?: typeof fetch;
  model?: string;
};

export type ScoreResult = {
  ok: true;
  score: number;
  level: string;
  confidence: number;
  probabilities: Record<string, number>;
  latencyMs: number;
  model: string;
  usage?: JevUsage;
  backend?: "jev" | "clef";
  backendRequested?: BackendMode;
  routeReason?: string;
  fallbackReason?: string;
} | BackendDryRunResult;

function validateLevels(levels: readonly string[]): string[] {
  if (!Array.isArray(levels) || levels.length < 2) {
    throw new Error(`score needs at least 2 levels, got ${Array.isArray(levels) ? levels.length : "non-list"}`);
  }
  if (levels.some((level) => typeof level !== "string" || level.trim().length === 0)) {
    throw new Error("score levels must be non-empty strings");
  }
  return [...levels];
}

export async function scoreText(options: ScoreOptions): Promise<ScoreResult> {
  if (typeof options.text !== "string" || options.text.trim().length === 0) {
    throw new Error("score text must be a non-empty string");
  }
  const levels = validateLevels(options.levels);
  const question = { type: "score", instructions: SST5_INSTRUCTIONS, criteria: levels };
  optionsPreflight(question);
  sizePreflight({ text: options.text }, question);

  if (options.dryRun) {
    const requested = configuredBackend(options.backend);
    if (!requested) throw new Error("score failed (usage): backend must be jev, clef, or auto");
    if (requested === "clef") throw new Error("score failed (uncalibrated): Clef has no score calibration");
    return previewJevRequest({ text: options.text }, { score: question }, options.model, requested, "score");
  }
  const ask = options.ask ?? askJevScore;
  const result = await ask({
    state: { text: options.text },
    instructions: SST5_INSTRUCTIONS,
    criteria: levels,
    apiKey: options.apiKey,
    fetchImpl: options.fetchImpl,
    model: options.model,
    ...(options.backend === undefined ? {} : { backend: options.backend }),
  });
  if (!result.ok) throw new Error(`score failed (${result.reason}): ${result.error}`);
  if (typeof result.score !== "number" || !Number.isFinite(result.score) || result.score < 0 || result.score > levels.length - 1) {
    throw new Error(`score returned an invalid value: ${result.score}`);
  }
  const normalized = Math.min(levels.length - 1, Math.max(0, Math.floor(result.score + 0.5)));
  const level = levels[normalized];
  if (typeof level !== "string") throw new Error("score level disappeared after validation");
  return {
    ok: true,
    score: result.score,
    level,
    confidence: result.confidence,
    probabilities: result.probabilities,
    latencyMs: result.latencyMs,
    model: result.model,
    ...(result.usage ? { usage: result.usage } : {}),
    ...(result.backend ? { backend: result.backend } : {}),
    ...(result.backendRequested ? { backendRequested: result.backendRequested } : {}),
    ...(result.routeReason ? { routeReason: result.routeReason } : {}),
    ...(result.fallbackReason ? { fallbackReason: result.fallbackReason } : {}),
  };
}

export { SST5_LEVELS as DEFAULT_SST5_LEVELS };
