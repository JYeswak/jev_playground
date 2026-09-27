import { askJevChoice, type AskChoiceOptions, type JevChoiceResult, type JevUsage } from "./client.ts";
import { optionsPreflight, sizePreflight } from "./preflight.ts";

export const BANKING77_INSTRUCTIONS = "The primary intent of this customer banking message";

export type ClassifyOptions = {
  text: string;
  labels: readonly string[];
  ask?: (options: AskChoiceOptions) => Promise<JevChoiceResult>;
  apiKey?: string;
  fetchImpl?: typeof fetch;
  model?: string;
};

export type ClassifyResult = {
  ok: true;
  label: string;
  confidence: number;
  probabilities: Record<string, number>;
  latencyMs: number;
  model: string;
  usage?: JevUsage;
};

function validateLabels(labels: readonly string[]): string[] {
  if (!Array.isArray(labels) || labels.length < 2) {
    throw new Error(`classify needs at least 2 labels, got ${Array.isArray(labels) ? labels.length : "non-list"}`);
  }
  if (labels.some((label) => typeof label !== "string" || label.length === 0)) {
    throw new Error("classify labels must be non-empty strings");
  }
  if (new Set(labels).size !== labels.length) {
    throw new Error("classify labels must be unique");
  }
  return [...labels];
}

export async function classifyText(options: ClassifyOptions): Promise<ClassifyResult> {
  if (typeof options.text !== "string") throw new Error("classify text must be a string");
  const labels = validateLabels(options.labels);
  const classes = Object.fromEntries(labels.map((label) => [label, null]));
  const state = { customer_message: options.text };
  const question = { type: "choice", instructions: BANKING77_INSTRUCTIONS, criteria: classes };
  optionsPreflight(question);
  sizePreflight(state, question);

  const ask = options.ask ?? askJevChoice;
  const result = await ask({
    state,
    instructions: BANKING77_INSTRUCTIONS,
    classes,
    apiKey: options.apiKey,
    fetchImpl: options.fetchImpl,
    model: options.model,
  });
  if (!result.ok) throw new Error(`classify failed (${result.reason}): ${result.error}`);
  if (!labels.includes(result.choice)) throw new Error(`classify returned an unoffered label: ${result.choice}`);
  return {
    ok: true,
    label: result.choice,
    confidence: result.confidence,
    probabilities: result.probabilities,
    latencyMs: result.latencyMs,
    model: result.model,
    ...(result.usage ? { usage: result.usage } : {}),
  };
}
