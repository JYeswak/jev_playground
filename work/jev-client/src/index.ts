/**
 * jev-client — the ONLY sanctioned way to call Jev systemOne in this lane.
 *
 * WHY THIS EXISTS. Every hand-rolled call in this repo has gotten the shape wrong at least once:
 *   - `{questions: [...], context}`            -> HTTP 400 (invented, 2026-09-19)
 *   - `.probability` / `.distribution`         -> undefined reads (SDK-SURFACE.md)
 *   - unset key logged as a decision row        -> 27 rows of `not configured` nobody noticed
 * Auth was never the problem. The BODY was. So the body now lives in exactly one place.
 *
 * Do not construct a systemOne request anywhere else. If you need a shape this does not
 * support, extend this file and its tests — do not fork the fetch.
 *
 * TRANSPORT: the network goes through the vendored first-party SDK
 * (upstream/typesafe-ai/typesafe-sdk-js @ 66880cc, loaded from
 * work/sdk/node_modules/@typesafe-ai/sdk) and nothing else. Imported by
 * relative path so no install step can drift it; never edit upstream/.
 * Our code owns the failure taxonomy, the field guards, and the fail-safe
 * direction — the SDK owns the wire. Single-attempt semantics are preserved
 * (SDK retry disabled per call); our 4 s default timeout is passed through.
 *
 * CONTRACT, verified against a working live call:
 *   POST https://api.typesafe.ai/v1/systemone
 *   { model, state, questions: { <key>: { type: "noul", instructions } } }
 *   -> { answers: { <key>: { noul: number } } }
 * Field names per docs/demos/SDK-SURFACE.md (`NoulResponse.noul`, `ChoiceResponse.probabilities`;
 * there is no `.probability` and no `.distribution`).
 */
import { TypeSafeClient, APIError, APIConnectionError, APITimeoutError, APIUserAbortError } from "../../sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs";

/** The endpoint the SDK targets by default. No fetch() is constructed beside it. */
export const SYSTEMONE_ENDPOINT = "https://api.typesafe.ai/v1/systemone";
export const DEFAULT_MODEL = "jev-1.13.0";

/** Discriminated result. There is no "empty success": a caller cannot mistake failure for a clean score. */
export type JevResult =
  | { ok: true; scores: Record<string, number>; latencyMs: number; model: string }
  | { ok: false; reason: JevFailure; error: string; latencyMs: number; model: string };

/**
 * A MULTICLASS answer: exactly one label out of a fixed set, with the full distribution.
 * Field names per docs/demos/SDK-SURFACE.md (`ChoiceResponse.choice/.confidence/.probabilities`);
 * there is no `.distribution`. Confirmed against a live 200 on 2026-09-19:
 *   {"answers":{"choice":{"type":"choice","choice":"argument","confidence":0.97,
 *                         "probabilities":{"transient":0.0,"argument":0.98,"bug":0.02}}}}
 */
export type JevChoiceResult =
  | {
      ok: true;
      choice: string;
      confidence: number;
      probabilities: Record<string, number>;
      latencyMs: number;
      model: string;
    }
  | { ok: false; reason: JevFailure; error: string; latencyMs: number; model: string };

/** Named failure classes, so a caller can branch without string-matching a message. */
export type JevFailure = "unconfigured" | "http" | "non-json" | "no-answers" | "transport";

export type AskOptions = {
  /** The object the questions are asked about. Serialised as-is into `state`. */
  state: Record<string, unknown>;
  /** key -> instructions. Keys come back as the score keys. */
  questions: Record<string, string>;
  timeoutMs?: number;
  model?: string;
  apiKey?: string;
  /** Transport override for offline tests. Defaults to globalThis.fetch, read at call time. */
  fetchImpl?: typeof fetch;
};

export type AskChoiceOptions = {
  /** The object the question is asked about. Serialised as-is into `state`. */
  state: Record<string, unknown>;
  /** The question itself, as text. */
  instructions: string;
  /** label -> description of that label. At least two; exactly one label comes back. */
  classes: Record<string, string>;
  timeoutMs?: number;
  model?: string;
  apiKey?: string;
  /** Transport override for offline tests. Defaults to globalThis.fetch, read at call time. */
  fetchImpl?: typeof fetch;
};

/** The key the single choice question is filed under. Internal; callers never see it. */
const CHOICE_KEY = "choice";

type Posted =
  | { ok: true; answers: object; latencyMs: number; resolvedModel: string }
  | { ok: false; reason: JevFailure; error: string; latencyMs: number };

/**
 * The ONE place a systemOne request is built and its envelope validated.
 * Both askJev and askJevChoice go through here, so a body shape can only be wrong once.
 */
async function postSystemOne(
  apiKey: string,
  model: string,
  state: Record<string, unknown>,
  questions: Record<string, unknown>,
  timeoutMs: number,
  fetchImpl: typeof fetch,
): Promise<Posted> {
  const started = Date.now();
  // One client per call: no shared mutable transport, and the injected fetch
  // is read at call time so offline tests can swap it per case. Construction
  // is inside the try so a config rejection degrades to transport, never throws.
  let result: { answers: unknown; usage?: unknown; model?: unknown };
  try {
    const client = new TypeSafeClient({
      apiKey,
      fetch: fetchImpl,
      timeout: timeoutMs,
      retry: { maxRetries: 0 },
    });
    result = await client.systemOne({ state, questions, model });
  } catch (err) {
    const latencyMs = Date.now() - started;
    if (err instanceof APIError) {
      return { ok: false, reason: "http", error: `systemOne HTTP ${err.status}: ${err.message}`, latencyMs };
    }
    if (err instanceof APIConnectionError || err instanceof APITimeoutError || err instanceof APIUserAbortError) {
      return { ok: false, reason: "transport", error: String(err.message), latencyMs };
    }
    return { ok: false, reason: "transport", error: String(err instanceof Error ? err.message : err), latencyMs };
  }
  const latencyMs = Date.now() - started;
  // The SDK resolves non-JSON bodies as raw text (parseBody is lenient by
  // design). Text where answers belong means the server did not answer JSON.
  if (typeof result === "string") {
    return { ok: false, reason: "non-json", error: "response carried text, not an `answers` object", latencyMs };
  }
  if (!result || typeof result !== "object" || !("answers" in result)) {
    return { ok: false, reason: "no-answers", error: "response carried no `answers`", latencyMs };
  }
  const answers: unknown = result.answers;
  if (!answers || typeof answers !== "object") {
    return { ok: false, reason: "no-answers", error: "`answers` was not an object", latencyMs };
  }
  const resolvedModel =
    "model" in result && typeof result.model === "string" ? result.model : model;
  return { ok: true, answers, latencyMs, resolvedModel };
}

export async function askJev(options: AskOptions): Promise<JevResult> {
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  const apiKey = options.apiKey ?? process.env.TYPESAFE_API_KEY;

  // An unset key is a CONFIGURATION state and must never look like an answer.
  // Source it with:
  //   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>
  // See .env.example. `infisical secrets` failing in an unlinked dir is NOT a missing secret.
  if (!apiKey) {
    return {
      ok: false,
      reason: "unconfigured",
      error: "TYPESAFE_API_KEY is not set — see .env.example, use infisical run --projectId=…",
      latencyMs: 0,
      model,
    };
  }
  if (Object.keys(options.questions).length === 0) {
    return { ok: false, reason: "no-answers", error: "no questions supplied", latencyMs: 0, model };
  }

  const questions = Object.fromEntries(
    Object.entries(options.questions).map(([key, instructions]) => [key, { type: "noul", instructions }]),
  );

  const posted = await postSystemOne(apiKey, model, options.state, questions, options.timeoutMs ?? 4000, options.fetchImpl ?? globalThis.fetch);
  if (!posted.ok) return { ok: false, reason: posted.reason, error: posted.error, latencyMs: posted.latencyMs, model };
  const { answers, latencyMs } = posted;

  const scores: Record<string, number> = {};
  const missing: string[] = [];
  for (const key of Object.keys(options.questions)) {
    if (!(key in answers)) {
      missing.push(key);
      continue;
    }
    const answer: unknown = Reflect.get(answers, key);
    if (!answer || typeof answer !== "object" || !("noul" in answer)) {
      missing.push(key);
      continue;
    }
    const value: unknown = answer.noul;
    if (typeof value === "number") scores[key] = value;
    else missing.push(key);
  }
  if (Object.keys(scores).length === 0) {
    return {
      ok: false,
      reason: "no-answers",
      error: `no numeric noul for any question (missing: ${missing.join(", ")})`,
      latencyMs,
      model,
    };
  }
  return { ok: true, scores, latencyMs, model };
}

/**
 * Ask ONE multiclass question: mutually-exclusive labels, exactly one answer.
 *
 * Why this exists beside askJev. Three independent binary questions over three classes that are
 * mutually exclusive by construction let the model answer yes twice, or no three times; nothing
 * in the call shape forbids it. A choice question forbids it in the protocol. That difference is
 * what work/omp-jev-failure/measure-multiclass.mjs measures.
 *
 * WIRE SHAPE, verified against a live 200 (not inferred):
 *   { model, state, questions: { choice: { type: "choice", instructions, criteria: {label: desc} } } }
 *   -> { answers: { choice: { type, choice, confidence, probabilities } } }
 * `criteria` is a MAP; the SDK itself rejects a list
 * (@typesafe-ai/sdk dist/index.mjs:339 "Choice criteria must be a map of labels to descriptions").
 */
export async function askJevChoice(options: AskChoiceOptions): Promise<JevChoiceResult> {
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  const apiKey = options.apiKey ?? process.env.TYPESAFE_API_KEY;

  if (!apiKey) {
    return {
      ok: false,
      reason: "unconfigured",
      error: "TYPESAFE_API_KEY is not set — see .env.example, use infisical run --projectId=…",
      latencyMs: 0,
      model,
    };
  }
  // A one-label choice has no alternative to choose against, and a list is the shape the SDK
  // refuses outright. Both are caller bugs: refuse before spending a call, never after.
  if (Array.isArray(options.classes)) {
    return { ok: false, reason: "no-answers", error: "classes must be a map of label -> description, not a list", latencyMs: 0, model };
  }
  const labels = Object.keys(options.classes ?? {});
  if (labels.length < 2) {
    return { ok: false, reason: "no-answers", error: `a choice needs at least 2 labels, got ${labels.length}`, latencyMs: 0, model };
  }

  const questions = {
    [CHOICE_KEY]: { type: "choice", instructions: options.instructions, criteria: options.classes },
  };
  const posted = await postSystemOne(apiKey, model, options.state, questions, options.timeoutMs ?? 4000, options.fetchImpl ?? globalThis.fetch);
  if (!posted.ok) return { ok: false, reason: posted.reason, error: posted.error, latencyMs: posted.latencyMs, model };
  const { answers, latencyMs } = posted;

  const answer: unknown = Reflect.get(answers, CHOICE_KEY);
  if (!answer || typeof answer !== "object") {
    return { ok: false, reason: "no-answers", error: "`answers.choice` was missing or not an object", latencyMs, model };
  }
  // Read only the documented fields, and fail loudly on anything else. A scorer that silently
  // reads a missing field does not crash — it fabricates a finding (SDK-SURFACE.md, the 0.500 AUC).
  const chosen: unknown = Reflect.get(answer, "choice");
  if (typeof chosen !== "string" || !(chosen in options.classes)) {
    return { ok: false, reason: "no-answers", error: `\`choice\` was not one of the offered labels: ${JSON.stringify(chosen)}`, latencyMs, model };
  }
  const rawProbabilities: unknown = Reflect.get(answer, "probabilities");
  if (!rawProbabilities || typeof rawProbabilities !== "object" || Array.isArray(rawProbabilities)) {
    return { ok: false, reason: "no-answers", error: "`probabilities` was missing or not an object (there is no `.distribution`)", latencyMs, model };
  }
  const probabilities: Record<string, number> = {};
  for (const label of labels) {
    const value: unknown = Reflect.get(rawProbabilities, label);
    if (typeof value !== "number") {
      return { ok: false, reason: "no-answers", error: `\`probabilities.${label}\` was not a number`, latencyMs, model };
    }
    probabilities[label] = value;
  }
  const confidence: unknown = Reflect.get(answer, "confidence");
  if (typeof confidence !== "number") {
    return { ok: false, reason: "no-answers", error: "`confidence` was not a number", latencyMs, model };
  }
  return { ok: true, choice: chosen, confidence, probabilities, latencyMs, model };
}

export type AskBundleOptions = {
  state: Record<string, unknown>;
  /** Already-typed question objects (`type: noul|choice|score`). */
  questions: Record<string, unknown>;
  timeoutMs?: number;
  model?: string;
  apiKey?: string;
  /** Transport override for offline tests. Defaults to globalThis.fetch, read at call time. */
  fetchImpl?: typeof fetch;
};

export type JevBundleResult =
  | {
      ok: true;
      answers: Record<string, unknown>;
      latencyMs: number;
      model: string;
      resolvedModel: string;
    }
  | { ok: false; reason: JevFailure; error: string; latencyMs: number; model: string };

/**
 * Mixed questions against one state. Choice + Noul in one request run in parallel.
 * The only sanctioned way to ask both without forking fetch.
 */
export async function askJevBundle(options: AskBundleOptions): Promise<JevBundleResult> {
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  const apiKey = options.apiKey ?? process.env.TYPESAFE_API_KEY;
  if (!apiKey) {
    return {
      ok: false,
      reason: "unconfigured",
      error: "TYPESAFE_API_KEY is not set — see .env.example, use infisical run --projectId=…",
      latencyMs: 0,
      model,
    };
  }
  const keys = Object.keys(options.questions ?? {});
  if (keys.length === 0) {
    return { ok: false, reason: "no-answers", error: "no questions supplied", latencyMs: 0, model };
  }
  const posted = await postSystemOne(apiKey, model, options.state, options.questions, options.timeoutMs ?? 4000, options.fetchImpl ?? globalThis.fetch);
  if (!posted.ok) return { ok: false, reason: posted.reason, error: posted.error, latencyMs: posted.latencyMs, model };
  return {
    ok: true,
    answers: posted.answers as Record<string, unknown>,
    latencyMs: posted.latencyMs,
    model,
    resolvedModel: posted.resolvedModel,
  };
}

/**
 * omp session rows come in TWO shapes and this has now cost the lane four wrong scans:
 *   A) { customType: { type: "…decision.v1", data: {…} } }   — observer rows
 *   B) { customType: "…decision.v1", data: {…} }             — harm-rule / failure rows
 * A scanner written against one returns silently empty on the other, which reads as "no rows"
 * and has twice led me to contradict a peer who was right (NEGATIVE_EVIDENCE R33, R41).
 *
 * Use this instead of reaching into a row by hand.
 */
export function readRow(line: unknown): { type: string; data: Record<string, unknown> } | undefined {
  let parsed: unknown = line;
  if (typeof line === "string") {
    try {
      parsed = JSON.parse(line);
    } catch {
      return undefined;
    }
  }
  if (!parsed || typeof parsed !== "object" || !("customType" in parsed)) return undefined;
  const custom: unknown = parsed.customType;

  if (typeof custom === "string") {
    const data = "data" in parsed ? parsed.data : undefined;
    if (!data || typeof data !== "object") return undefined;
    return { type: custom, data: { ...data } };
  }
  if (custom && typeof custom === "object" && "type" in custom) {
    const type: unknown = custom.type;
    const data: unknown = "data" in custom ? custom.data : undefined;
    if (typeof type !== "string" || !data || typeof data !== "object") return undefined;
    return { type, data: { ...data } };
  }
  return undefined;
}
