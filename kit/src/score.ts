import { askJevScore, type AskScoreOptions, type JevScoreResult, type JevUsage } from "./client.ts";
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
};

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

  const ask = options.ask ?? askJevScore;
  const result = await ask({
    state: { text: options.text },
    instructions: SST5_INSTRUCTIONS,
    criteria: levels,
    apiKey: options.apiKey,
    fetchImpl: options.fetchImpl,
    model: options.model,
  });
  if (!result.ok) throw new Error(`score failed (${result.reason}): ${result.error}`);
  if (!Number.isInteger(result.score) || result.score < 0 || result.score >= levels.length) {
    throw new Error(`score returned an invalid level index: ${result.score}`);
  }
  const level = levels[result.score];
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
  };
}

export { SST5_LEVELS as DEFAULT_SST5_LEVELS };
