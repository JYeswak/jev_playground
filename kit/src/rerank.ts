import { askJevChoice, configuredBackend, previewJevRequest, type AskChoiceOptions, type BackendDryRunResult, type BackendMode, type JevChoiceResult, type JevUsage } from "./client.ts";
import { sizePreflight } from "./preflight.ts";

export type RerankCandidate = {
  id: string;
  title?: string;
  text: string;
  [key: string]: unknown;
};

export type RerankOptions = {
  query: string;
  candidates: RerankCandidate[];
  backend?: BackendMode;
  dryRun?: boolean;
  ask?: (options: AskChoiceOptions) => Promise<JevChoiceResult>;
  apiKey?: string;
  fetchImpl?: typeof fetch;
  model?: string;
};

export type RerankResult = {
  ok: true;
  choice: string;
  orderedCandidates: RerankCandidate[];
  latencyMs: number;
  model: string;
  usage?: JevUsage;
  backend?: "jev" | "clef";
  backendRequested?: BackendMode;
  routeReason?: string;
  fallbackReason?: string;
} | BackendDryRunResult;

const MAX_CANDIDATES = 20;
const INSTRUCTIONS =
  "Select the candidate passage most relevant to the query. Choose the passage that best answers or provides evidence for the query.";

export async function rerankTop1(options: RerankOptions): Promise<RerankResult> {
  const { query, candidates } = options;
  if (!Array.isArray(candidates) || candidates.length < 2) {
    throw new Error(`rerank needs at least 2 candidates, got ${candidates?.length ?? "non-list"}`);
  }
  if (candidates.length > MAX_CANDIDATES) {
    throw new Error(`rerank accepts at most ${MAX_CANDIDATES} candidates, got ${candidates.length}; chunking is not supported`);
  }
  const ids = candidates.map((candidate) => candidate.id);
  if (ids.some((id) => typeof id !== "string" || id.length === 0) || new Set(ids).size !== ids.length) {
    throw new Error("rerank candidate ids must be non-empty and unique");
  }
  const state = { query, candidates };
  const question = {
    type: "choice",
    instructions: INSTRUCTIONS,
    criteria: Object.fromEntries(candidates.map((candidate) => [candidate.id, `Candidate passage ${candidate.id}`])),
  };
  sizePreflight(state, question);
  if (options.dryRun) {
    const requested = configuredBackend(options.backend);
    if (!requested) throw new Error("rerank failed (usage): backend must be jev, clef, or auto");
    if (requested === "clef") throw new Error("rerank failed (uncalibrated): no committed Clef calibration was supplied");
    return previewJevRequest(state, { choice: question }, options.model, requested, "choice");
  }
  const ask = options.ask ?? askJevChoice;
  const result = await ask({
    state,
    instructions: INSTRUCTIONS,
    classes: question.criteria,
    apiKey: options.apiKey,
    fetchImpl: options.fetchImpl,
    model: options.model,
    ...(options.backend === undefined ? {} : { backend: options.backend }),
  });
  if (!result.ok) throw new Error(`rerank failed (${result.reason}): ${result.error}`);
  if (!ids.includes(result.choice)) throw new Error(`rerank returned an unoffered candidate: ${result.choice}`);
  const selected = candidates.find((candidate) => candidate.id === result.choice);
  if (!selected) throw new Error("rerank selection disappeared after validation");
  return {
    ok: true,
    choice: result.choice,
    orderedCandidates: [selected, ...candidates.filter((candidate) => candidate.id !== result.choice)],
    latencyMs: result.latencyMs,
    model: result.model,
    ...(result.usage ? { usage: result.usage } : {}),
    ...(result.backend ? { backend: result.backend } : {}),
    ...(result.backendRequested ? { backendRequested: result.backendRequested } : {}),
    ...(result.routeReason ? { routeReason: result.routeReason } : {}),
    ...(result.fallbackReason ? { fallbackReason: result.fallbackReason } : {}),
  };
}

export { MAX_CANDIDATES, INSTRUCTIONS };
