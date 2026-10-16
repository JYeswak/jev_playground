import type * as SdkModule from "@typesafe-ai/sdk";
import { validateBundleAnswers, validateChoiceAnswer, validateNoulAnswer, validateScoreAnswer } from "./validate.ts";
import { sizePreflight } from "./preflight.ts";
import { askClef, type ClefFailureReason } from "./clef.ts";
import { loadCalibrations, questionSha, type ClefCalibration, type ModelFingerprint } from "./calibration.ts";
import { readSystemOneUsage, type SystemOneUsage } from "./usage.ts";
declare const process: { env: Record<string, string | undefined> };
type Sdk = typeof SdkModule;
const SDK_PATH = "../../work/sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs";
let sdkLoad: Promise<Sdk | undefined> | undefined;
/** Cached; resolves undefined when the SDK is not installed (fresh clone). */
function loadSdk(): Promise<Sdk | undefined> {
  sdkLoad ??= import(SDK_PATH).catch(() => import(new URL("../node_modules/@typesafe-ai/sdk/dist/index.mjs", import.meta.url).href)).then((m) => m as Sdk, () => undefined);
  return sdkLoad;
}
/**
 * One TypeSafeClient per (transport, timeout, retry, key) shape, kept for the
 * process so repeated calls reuse the warm transport underneath. The key is a
 * nested map, never serialized or logged; entries hold no caller data beyond
 * the wrapped fetch closure. Tests inject a fresh fetchImpl per case, so each
 * lands in its own entry and stays isolated.
 */
type CachedClient = { systemOne: Sdk["TypeSafeClient"]["prototype"]["systemOne"] };
type FetchFn = typeof fetch;
const clientCache = new Map<FetchFn, Map<number, Map<number, Map<string, CachedClient>>>>();

function cachedClient(
  sdk: Sdk,
  apiKey: string,
  wrappedFetch: typeof fetch,
  fetchImpl: typeof fetch,
  timeoutMs: number,
  maxRetries: number,
): CachedClient {
  const byTimeout = getOrCreate(clientCache, fetchImpl, () => new Map());
  const byRetry = getOrCreate(byTimeout, timeoutMs, () => new Map());
  const byKey = getOrCreate(byRetry, maxRetries, () => new Map());
  return getOrCreate(byKey, apiKey, () => new sdk.TypeSafeClient({
    apiKey,
    fetch: wrappedFetch,
    timeout: timeoutMs,
    retry: { maxRetries },
  }) as CachedClient);
}

function getOrCreate<K, V>(map: Map<K, V>, key: K, make: () => V): V {
  const hit = map.get(key);
  if (hit !== undefined) return hit;
  const value = make();
  map.set(key, value);
  return value;
}

/** Test seam: drop every cached client. The live process never calls this. */
export function resetClientCache(): void {
  clientCache.clear();
}

/** Test seam: how many client shapes are cached. The live process never calls this. */
export function clientCacheSize(): number {
  let size = 0;
  for (const byTimeout of clientCache.values())
    for (const byRetry of byTimeout.values())
      for (const byKey of byRetry.values()) size += byKey.size;
  return size;
}

/** The endpoint the SDK targets by default. No fetch() is constructed beside it. */
export const SYSTEMONE_ENDPOINT = "https://api.typesafe.ai/v1/systemone";
export const DEFAULT_MODEL = "jev-1.13.0";
export type SystemOneBody = { state: string | Record<string, unknown>; questions: Record<string, unknown>; model: string };
export type SystemOneRequestPreview = { endpoint: string; method: "POST"; body: SystemOneBody };
export function buildSystemOneBody(state: string | Record<string, unknown>, questions: Record<string, unknown>, model: string): SystemOneBody {
  return { state, questions, model };
}
export function previewSystemOneRequest(state: string | Record<string, unknown>, questions: Record<string, unknown>, model = DEFAULT_MODEL): SystemOneRequestPreview {
  sizePreflight(state, questions);
  return { endpoint: SYSTEMONE_ENDPOINT, method: "POST", body: buildSystemOneBody(state, questions, model) };
}
export type BackendMode = "jev" | "clef" | "auto";
type BackendMetadata = { backend?: "jev" | "clef"; backendRequested?: BackendMode; routeReason?: string; fallbackReason?: string };
export type BackendRouteInput = {
  requested: BackendMode;
  primitive: "choice" | "noul" | "score" | "bundle";
  questionCount: number;
  calibration?: ClefCalibration;
  questionKey?: string;
  questionHash?: string;
  fingerprint?: ModelFingerprint;
  familyReceiptRegistered: boolean;
  backendHoldActive: boolean;
};
export type BackendRoute = { backend: "jev" | "clef"; backendRequested: BackendMode; routeReason?: string };
export type BackendOptions = {
  backend?: BackendMode;
  clefFetchImpl?: typeof fetch;
  clefUrl?: string;
  clefCalibration?: ClefCalibration;
  clefFingerprint?: ModelFingerprint;
};
export type BackendDryRunResult = {
  ok: true;
  dryRun: true;
  request: SystemOneRequestPreview;
  latencyMs: 0;
  model: string;
  backend: "jev";
  backendRequested: BackendMode;
  routeReason?: string;
  fallbackReason?: string;
};
export function configuredBackend(backend?: BackendMode): BackendMode | undefined {
  const value = backend ?? process.env.JEV_BACKEND ?? "jev";
  return value === "jev" || value === "clef" || value === "auto" ? value : undefined;
}
export function previewJevRequest(
  state: string | Record<string, unknown>,
  questions: Record<string, unknown>,
  model: string | undefined,
  requested: BackendMode,
  primitive: BackendRouteInput["primitive"],
): BackendDryRunResult {
  if (requested === "clef") throw new Error("uncalibrated: a Clef request preview requires a committed calibration");
  const route = requested === "auto" ? resolveBackendRoute({
    requested,
    primitive,
    questionCount: Object.keys(questions).length,
    familyReceiptRegistered: false,
    backendHoldActive: clefBackendHoldActive(Date.now()),
  }) : undefined;
  const routeReason = route?.routeReason;
  const resolvedModel = model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  return {
    ok: true,
    dryRun: true,
    request: previewSystemOneRequest(state, questions, resolvedModel),
    latencyMs: 0,
    model: resolvedModel,
    backend: "jev",
    backendRequested: requested,
    ...(routeReason ? { routeReason, fallbackReason: routeReason } : {}),
  };
}

/**
 * Usage exactly as the server reported it; never invented, never zero-filled.
 * `input_tokens`/`output_tokens` are the fields both SDKs declare (typesafe-sdk-js
 * src/types.ts:127-132; typesafe-sdk-python _schemas/models.py:151-160, where input tokens
 * are "billable" and output tokens "currently free of charge"). `billing_units` is declared by
 * NEITHER SDK: the Python SDK drops it (tests/test_responses.py:143,152), while the JS SDK
 * returns the parsed body untouched (dist/index.mjs:571-574), so it survives to here.
 * `billing_units: null` means the usage object carried no finite number under that name —
 * absent, and reported as absent. `extra` holds every other finite numeric usage field verbatim
 * (for example `reasoning_tokens`), `{}` when there are none.
 */
export type JevUsage = SystemOneUsage;
export type JevResult =
  | ({ ok: true; scores: Record<string, number>; latencyMs: number; model: string; usage?: JevUsage } & BackendMetadata)
  | ({ ok: false; reason: JevFailure; error: string; latencyMs: number; model: string } & BackendMetadata);

/**
 * A MULTICLASS answer: exactly one label out of a fixed set, with the full distribution.
 * Field names per docs/demos/SDK-SURFACE.md (`ChoiceResponse.choice/.confidence/.probabilities`);
 * there is no `.distribution`. Confirmed against a live 200 on 2026-09-19:
 *   {"answers":{"choice":{"type":"choice","choice":"argument","confidence":0.97,
 *                         "probabilities":{"transient":0.0,"argument":0.98,"bug":0.02}}}}
 */
export type JevChoiceResult =
  | ({
      ok: true;
      choice: string;
      confidence: number;
      probabilities: Record<string, number>;
      probabilitiesRaw?: true;
      latencyMs: number;
      model: string;
      usage?: JevUsage;
    } & BackendMetadata)
  | ({ ok: false; reason: JevFailure; error: string; latencyMs: number; model: string } & BackendMetadata);

/**
 * Named failure classes, so a caller can branch without string-matching a message.
 * `unconfigured` = no key; `sdk-missing` = key present but work/sdk/node_modules absent (fresh
 * clone before `npm ci --prefix work/sdk`). Distinct so a demo never reports a missing SDK as a
 * missing key.
 */
export type JevFailure = "usage" | "unconfigured" | "sdk-missing" | "http" | "non-json" | "no-answers" | "transport" | "billing-hold" | "uncalibrated" | "truncated" | "backend-hold" | "online-required" | "refused-unsafe";
/**
 * Wrap the transport and report when a request reaches it. Callers use this
 * to distinguish a failure before dispatch (no key, billing hold, missing
 * SDK) from a response or transport failure after a request was sent.
 */
export function observedFetch(onRequest: () => void, fetchImpl: typeof fetch = globalThis.fetch): typeof fetch {
  return ((input: Parameters<typeof fetch>[0], init?: Parameters<typeof fetch>[1]) => {
    onRequest();
    return fetchImpl(input, init);
  }) as typeof fetch;
}



export type AskOptions = BackendOptions & {
  /** The object the questions are asked about. Serialised as-is into `state`. */
  state: Record<string, unknown>;
  /** key -> instructions, or a noul body with optional criteria. Keys come back as the score keys. */
  questions: Record<string, string | { instructions: string; criteria?: { true: string; false: string } }>;
  timeoutMs?: number;
  model?: string;
  apiKey?: string;
  /** Transport override for offline tests. Defaults to globalThis.fetch, read at call time. */
  fetchImpl?: typeof fetch;
  /** Wall clock in ms for the billing hold. Tests inject it. Defaults to Date.now. */
  nowMs?: () => number;
};

export type AskChoiceOptions = BackendOptions & {
  /** The object the question is asked about. Serialised as-is into `state`. */
  state: Record<string, unknown>;
  /** The question itself, as text. */
  instructions: string;
  /** label -> description of that label. At least two; exactly one label comes back. */
  classes: Record<string, string | null>;
  timeoutMs?: number;
  model?: string;
  apiKey?: string;
  /** Transport override for offline tests. Defaults to globalThis.fetch, read at call time. */
  fetchImpl?: typeof fetch;
  nowMs?: () => number;
};

/** The key the single choice question is filed under. Internal; callers never see it. */
const CHOICE_KEY = "choice";
/** The key the single score question is filed under. Internal; callers never see it. */
const SCORE_KEY = "score";

type Posted =
  | { ok: true; answers: object; latencyMs: number; resolvedModel: string; usage?: JevUsage }
  | { ok: false; reason: JevFailure; error: string; latencyMs: number };

const AUTO_FALLBACK_REASONS: Record<string, true> = { http: true, transport: true, truncated: true, uncalibrated: true };
let consecutiveClefFailures = 0;
let clefHoldUntil = 0;

export function resetClefBackendHold(): void {
  consecutiveClefFailures = 0;
  clefHoldUntil = 0;
}

export function recordClefFailure(reason: ClefFailureReason | "timeout", nowMs = Date.now()): void {
  if (clefHoldUntil !== 0 && nowMs >= clefHoldUntil) {
    consecutiveClefFailures = 0;
    clefHoldUntil = 0;
  }
  if (reason === "transport" || reason === "timeout") {
    consecutiveClefFailures += 1;
    if (consecutiveClefFailures >= 2) clefHoldUntil = nowMs + 60_000;
  } else {
    consecutiveClefFailures = 0;
  }
}

export function recordClefSuccess(): void {
  consecutiveClefFailures = 0;
}

export function clefBackendHoldActive(nowMs = Date.now()): boolean {
  return nowMs < clefHoldUntil;
}

export function resolveBackendRoute(input: BackendRouteInput): BackendRoute {
  if (input.requested === "jev") return { backend: "jev", backendRequested: input.requested };
  if (input.requested === "clef") return { backend: "clef", backendRequested: input.requested };
  if (!input.familyReceiptRegistered) return { backend: "jev", backendRequested: "auto", routeReason: "not-a-family-receipt" };
  if (!input.calibration || input.calibration.receipt.verdict !== "PASS" || !input.calibration.receipt.result_commit) {
    return { backend: "jev", backendRequested: "auto", routeReason: "no-calibration" };
  }
  if (input.questionKey !== input.calibration.question_key || input.questionHash !== input.calibration.question_sha256) {
    return { backend: "jev", backendRequested: "auto", routeReason: "question-mismatch" };
  }
  if (input.questionCount !== 1) return { backend: "jev", backendRequested: "auto", routeReason: "multi-question" };
  if (!input.fingerprint) return { backend: "jev", backendRequested: "auto", routeReason: "fingerprint-unavailable" };
  if (input.fingerprint.joint_head_sha256 !== input.calibration.model.joint_head_sha256 ||
      input.fingerprint.index_sha256 !== input.calibration.model.index_sha256) {
    return { backend: "jev", backendRequested: "auto", routeReason: "fingerprint-mismatch" };
  }
  if (input.backendHoldActive) return { backend: "jev", backendRequested: "auto", routeReason: "backend-hold" };
  return { backend: "clef", backendRequested: "auto" };
}

export async function withAutoFallback<T extends { ok: boolean; reason?: string }>(
  requested: BackendMode,
  fallbackAllowed: boolean,
  clefAttempt: () => Promise<T>,
  jevAttempt: () => Promise<T>,
): Promise<T> {
  const clef = await clefAttempt();
  if (requested !== "auto" || clef.ok || !fallbackAllowed || !AUTO_FALLBACK_REASONS[clef.reason ?? ""]) return clef;
  return jevAttempt();
}
function selectedBackend(options: BackendOptions): BackendMode | undefined {
  const value = options.backend ?? process.env.JEV_BACKEND ?? "jev";
  return value === "jev" || value === "clef" || value === "auto" ? value : undefined;
}

function withBackendMetadata<T extends { ok: boolean }>(
  result: T,
  backend: "jev" | "clef",
  backendRequested: BackendMode,
  routeReason?: string,
): T & BackendMetadata {
  return {
    ...result,
    backend,
    backendRequested,
    ...(routeReason ? { routeReason, fallbackReason: routeReason } : {}),
  };
}

async function selectCalibration(
  options: BackendOptions,
  primitive: "choice" | "noul",
  question: Record<string, unknown>,
  state: Record<string, unknown>,
): Promise<ClefCalibration | undefined> {
  let candidates: ClefCalibration[];
  try {
    candidates = options.clefCalibration ? [options.clefCalibration] : await loadCalibrations();
  } catch {
    return undefined;
  }
  try {
    const hash = questionSha(question, Object.keys(state));
    const matches = candidates.filter((item) => item.primitive === primitive && item.question_sha256 === hash);
    return matches.length === 1 ? matches[0] : undefined;
  } catch {
    return undefined;
  }
}

async function askClefNoul(options: AskOptions, requested: BackendMode, callerKey: string, question: Record<string, unknown>): Promise<JevResult> {
  const calibration = await selectCalibration(options, "noul", question, options.state);
  const result = await askClef({
    primitive: "noul",
    state: options.state,
    question,
    callerKey,
    calibration,
    fingerprint: options.clefFingerprint,
    fetchImpl: options.clefFetchImpl,
    url: options.clefUrl,
    timeoutMs: options.timeoutMs,
  });
  if (result.ok) recordClefSuccess();
  else recordClefFailure(result.reason, options.nowMs?.() ?? Date.now());
  if (result.ok && "scores" in result) return withBackendMetadata(result, "clef", requested);
  if (!result.ok) return withBackendMetadata(result, "clef", requested);
  return withBackendMetadata({ ok: false, reason: "uncalibrated", error: "Clef returned the wrong answer primitive", latencyMs: result.latencyMs, model: result.model }, "clef", requested);
}

async function askClefChoice(options: AskChoiceOptions, requested: BackendMode, question: Record<string, unknown>): Promise<JevChoiceResult> {
  const calibration = await selectCalibration(options, "choice", question, options.state);
  const result = await askClef({
    primitive: "choice",
    state: options.state,
    question,
    callerKey: CHOICE_KEY,
    calibration,
    fingerprint: options.clefFingerprint,
    fetchImpl: options.clefFetchImpl,
    url: options.clefUrl,
    timeoutMs: options.timeoutMs,
  });
  if (result.ok) recordClefSuccess();
  else recordClefFailure(result.reason, options.nowMs?.() ?? Date.now());
  if (result.ok && "choice" in result) return withBackendMetadata(result, "clef", requested);
  if (!result.ok) return withBackendMetadata(result, "clef", requested);
  return withBackendMetadata({ ok: false, reason: "uncalibrated", error: "Clef returned the wrong answer primitive", latencyMs: result.latencyMs, model: result.model }, "clef", requested);
}

/**
 * When guardedFetch aborts a request that has not yet delivered headers:
 * 25 ms inside the SDK's `timeoutMs`, never below 1 ms. Exported so the
 * timeout-leak test derives its latency floor from the real deadline.
 */
export function guardDeadlineMs(timeoutMs: number): number {
  return Math.max(1, timeoutMs - 25);
}

/**
 * The ONE place a systemOne request is built and its envelope validated.
 * Both askJev and askJevChoice go through here, so a body shape can only be wrong once.
 */
/**
 * The SDK's internal timeout abort leaks an unobserved AbortError rejection
 * (dist/index.mjs `Timeout._onTimeout` → `AbortController.abort`; the
 * half-received response's abandoned stream branch rejects where neither the
 * SDK nor a fetch-level catch can observe it). On a default Node host one
 * such rejection kills the process (W7.0 T9: ~1/3 of timed-out requests
 * did; a fetch-promise catch was proven insufficient by the regression
 * test). So we own the timeout: our deadline fires strictly before the
 * SDK's, we abort OUR controller, and we throw the SDK's own
 * APITimeoutError — same class the SDK would throw, so the `reason:
 * "transport"` contract below is unchanged and the SDK's timer is cleared
 * in its `finally` before it can ever fire. Nothing here edits the
 * vendored SDK.
 */
function guardedFetch(fetchImpl: typeof fetch, timeoutMs: number, APITimeoutError: Sdk["APITimeoutError"]): typeof fetch {
  return (async (...args: Parameters<typeof fetch>) => {
    const [url, init] = args;
    const controller = new AbortController();
    const forward = () => controller.abort(init?.signal?.reason);
    if (init?.signal?.aborted) forward();
    else init?.signal?.addEventListener("abort", forward, { once: true });
    // Strictly inside the SDK's own deadline so ours always wins the race.
    const timer = setTimeout(() => controller.abort(), guardDeadlineMs(timeoutMs));
    try {
      const p = fetchImpl(url, { ...init, signal: controller.signal });
      p.catch(() => {}); // our fetch promise never escapes unobserved either
      return await p;
    } catch (err) {
      if (controller.signal.aborted && err instanceof DOMException && err.name === "AbortError") {
        throw new APITimeoutError(timeoutMs, { cause: err });
      }
      throw err;
    } finally {
      clearTimeout(timer);
      init?.signal?.removeEventListener("abort", forward);
    }
  }) as typeof fetch;
}
/**
 * After an HTTP 402 (no TypeSafe credits) this process stops calling for this
 * long and returns reason `billing-hold`. 429, 5xx and transport do not start
 * it. Pinned literal: a test asserts this exact number, so a 1 ms window fails.
 * Measured 2026-09-24: without a hold, 233 calls hit a 402 over 4.5 h (jev-nhv9).
 */
export const BILLING_HOLD_MS = 15 * 60 * 1000;
let billingHoldUntil = 0;

/** Test seam. The live process keeps its hold for the window. */
export function resetBillingHold(): void {
  billingHoldUntil = 0;
}

/** The hold end if `nowMs` is still inside it, otherwise null. */
export function billingHoldActive(nowMs: number): number | null {
  return nowMs < billingHoldUntil ? billingHoldUntil : null;
}

/** HTTP 401, 402, or 403 starts the 15-minute hold; transient and transport failures do not. */
export function noteBillingRefusal(answer: { reason?: string; error?: string }, nowMs: number): void {
  if (answer.reason === "http" && /\bHTTP (?:401|402|403)\b/.test(answer.error ?? "")) {
    billingHoldUntil = nowMs + BILLING_HOLD_MS;
  }
}

/**
 * Where the key comes from when neither the call nor the environment supplies one. Unset by
 * default, so scripts stay keyless unless they pass a key. Real omp use (the .omp/tools
 * factories without an injected asker, and the review extension) installs the Infisical lookup
 * through use-infisical-key.ts, which keeps the key in this process's memory only: a pane's
 * shell environment never holds it. Order: explicit option, then TYPESAFE_API_KEY, then this.
 */
let keyProvider: (() => Promise<string | undefined>) | undefined;

export function setKeyProvider(provider: (() => Promise<string | undefined>) | undefined): void {
  keyProvider = provider;
}

/** Whether a provider is installed; use-infisical-key.ts never replaces one a caller chose. */
export function keyProviderInstalled(): boolean {
  return keyProvider !== undefined;
}

async function resolveApiKey(explicit: string | undefined): Promise<string | undefined> {
  const fromCall = explicit ?? process.env.TYPESAFE_API_KEY;
  if (fromCall) return fromCall;
  if (!keyProvider) return undefined;
  try {
    return (await keyProvider()) || undefined;
  } catch {
    return undefined;
  }
}

async function postSystemOne(
  apiKey: string,
  model: string,
  state: string | Record<string, unknown>,
  questions: Record<string, unknown>,
  timeoutMs: number,
  fetchImpl: typeof fetch,
  retry?: { maxRetries?: number },
  nowMs: () => number = Date.now,
): Promise<Posted> {
  const until = billingHoldActive(nowMs());
  if (until !== null) {
    return {
      ok: false,
      reason: "billing-hold",
      error: `billing-hold until=${new Date(until).toISOString()}`,
      latencyMs: 0,
    };
  }
  const sdk = await loadSdk();
  if (!sdk) {
    return {
      ok: false,
      reason: "sdk-missing",
      error: "@typesafe-ai/sdk is not installed: run `npm ci --prefix work/sdk` once",
      latencyMs: 0,
    };
  }
  const { TypeSafeClient, APIError, APIConnectionError, APITimeoutError, APIUserAbortError } = sdk;
  // Clock starts after the load so latencyMs measures the call, as before the import went lazy.
  const started = Date.now();
  // One client per (apiKey, transport, timeout, retry) shape, kept for the
  // process: the SDK holds no per-call mutable state, and the wrapped fetch
  // is stateless across calls (a fresh AbortController per invocation), so a
  // second identical call skips reconstruction AND reuses the warm transport
  // underneath. Offline tests stay isolated because every case injects its own
  // fetchImpl closure, which keys a different cache entry. Construction stays
  // inside the try so a config rejection degrades to transport, never throws.
  // Retry is SDK-owned: callers pass maxRetries explicitly; absent means 0
  // (single attempt), preserving the fail-fast row semantics runners rely on.
  let result: { answers: unknown; usage?: unknown; model?: unknown };
  try {
    const client = cachedClient(
      sdk,
      apiKey,
      guardedFetch(fetchImpl, timeoutMs, APITimeoutError),
      fetchImpl,
      timeoutMs,
      retry?.maxRetries ?? 0,
    );
    result = await client.systemOne(buildSystemOneBody(state, questions, model) as never);
  } catch (err) {
    const latencyMs = Date.now() - started;
    if (err instanceof APIError) {
      if ([401, 402, 403].includes(err.status)) billingHoldUntil = nowMs() + BILLING_HOLD_MS;
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
  const usage = readSystemOneUsage("usage" in result ? result.usage : undefined);
  return { ok: true, answers, latencyMs, resolvedModel, ...(usage ? { usage } : {}) };
}


async function askJevUsingJev(options: AskOptions): Promise<JevResult> {
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  const apiKey = await resolveApiKey(options.apiKey);

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
    Object.entries(options.questions).map(([key, value]) => {
      if (typeof value === "string") return [key, { type: "noul", instructions: value }];
      const body: { type: "noul"; instructions: string; criteria?: { true: string; false: string } } = {
        type: "noul",
        instructions: value.instructions,
      };
      if (value.criteria) body.criteria = value.criteria;
      return [key, body];
    }),
  );

  const posted = await postSystemOne(apiKey, model, options.state, questions, options.timeoutMs ?? 4000, options.fetchImpl ?? globalThis.fetch, undefined, options.nowMs);
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
    try {
      scores[key] = validateNoulAnswer(answer);
    } catch {
      missing.push(key);
    }
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
  return { ok: true, scores, latencyMs, model, ...(posted.usage ? { usage: posted.usage } : {}) };
}

export async function askJev(options: AskOptions): Promise<JevResult> {
  const requested = selectedBackend(options);
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  if (!requested) return { ok: false, reason: "usage", error: "backend must be jev, clef, or auto", latencyMs: 0, model };
  if (requested === "jev") return withBackendMetadata(await askJevUsingJev(options), "jev", requested);

  const keys = Object.keys(options.questions ?? {});
  let routeReason: string | undefined;
  if (requested === "auto") {
    const route = resolveBackendRoute({
      requested,
      primitive: keys.length === 1 ? "noul" : "bundle",
      questionCount: keys.length,
      familyReceiptRegistered: false,
      backendHoldActive: clefBackendHoldActive(options.nowMs?.() ?? Date.now()),
    });
    routeReason = route.routeReason;
    if (route.backend === "jev") return withBackendMetadata(await askJevUsingJev(options), "jev", requested, routeReason);
  }
  if (keys.length !== 1) {
    return withBackendMetadata({ ok: false, reason: "uncalibrated", error: "Clef requires exactly one calibrated question", latencyMs: 0, model }, "clef", requested);
  }
  const callerKey = keys[0];
  const rawQuestion = options.questions[callerKey];
  const question = typeof rawQuestion === "string"
    ? { type: "noul", instructions: rawQuestion }
    : { type: "noul", instructions: rawQuestion.instructions, ...(rawQuestion.criteria ? { criteria: rawQuestion.criteria } : {}) };
  const clefAttempt = () => askClefNoul(options, requested, callerKey, question);
  if (requested === "auto") {
    let clefFailureReason: string | undefined;
    const jevHeld = billingHoldActive(options.nowMs?.() ?? Date.now()) !== null;
    const result = await withAutoFallback("auto", !jevHeld, async () => {
      const clef = await clefAttempt();
      if (!clef.ok) clefFailureReason = clef.reason;
      return clef;
    }, () => askJevUsingJev(options));
    const backend = result.backend === "clef" ? "clef" : "jev";
    return withBackendMetadata(result, backend, requested, backend === "jev" ? (clefFailureReason ?? routeReason) : undefined);
  }
  return clefAttempt();
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
async function askJevChoiceUsingJev(options: AskChoiceOptions): Promise<JevChoiceResult> {
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  const apiKey = await resolveApiKey(options.apiKey);

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
  const posted = await postSystemOne(apiKey, model, options.state, questions, options.timeoutMs ?? 4000, options.fetchImpl ?? globalThis.fetch, undefined, options.nowMs);
  if (!posted.ok) return { ok: false, reason: posted.reason, error: posted.error, latencyMs: posted.latencyMs, model };
  const { answers, latencyMs } = posted;

  const answer: unknown = Reflect.get(answers, CHOICE_KEY);
  if (!answer || typeof answer !== "object") {
    return { ok: false, reason: "no-answers", error: "`answers.choice` was missing or not an object", latencyMs, model };
  }
  try {
    const validated = validateChoiceAnswer(answer, labels);
    return { ok: true, choice: validated.choice, confidence: validated.confidence, probabilities: validated.probabilities, latencyMs, model, ...(posted.usage ? { usage: posted.usage } : {}) };
  } catch (error) {
    return { ok: false, reason: "no-answers", error: error instanceof Error ? error.message : String(error), latencyMs, model };
  }
}

export async function askJevChoice(options: AskChoiceOptions): Promise<JevChoiceResult> {
  const requested = selectedBackend(options);
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  if (!requested) return { ok: false, reason: "usage", error: "backend must be jev, clef, or auto", latencyMs: 0, model };
  if (requested === "jev") return withBackendMetadata(await askJevChoiceUsingJev(options), "jev", requested);

  const question = { type: "choice", instructions: options.instructions, criteria: options.classes };
  if (requested === "auto") {
    // R4 keeps public benchmark rows out of automatic family routing.
    const route = resolveBackendRoute({
      requested,
      primitive: "choice",
      questionCount: 1,
      calibration: options.clefCalibration,
      questionKey: options.clefCalibration?.question_key,
      questionHash: options.clefCalibration?.question_sha256,
      fingerprint: options.clefFingerprint,
      familyReceiptRegistered: false,
      backendHoldActive: clefBackendHoldActive(options.nowMs?.() ?? Date.now()),
    });
    if (route.backend === "jev") return withBackendMetadata(await askJevChoiceUsingJev(options), "jev", requested, route.routeReason);
  }
  if (Array.isArray(options.classes) || Object.keys(options.classes ?? {}).length < 2) {
    return withBackendMetadata({ ok: false, reason: "no-answers", error: "Clef choice requires at least two labels", latencyMs: 0, model }, "clef", requested);
  }
  const clefAttempt = () => askClefChoice(options, requested, question);
  if (requested === "auto") {
    let clefFailureReason: string | undefined;
    const jevHeld = billingHoldActive(options.nowMs?.() ?? Date.now()) !== null;
    const result = await withAutoFallback("auto", !jevHeld, async () => {
      const clef = await clefAttempt();
      if (!clef.ok) clefFailureReason = clef.reason;
      return clef;
    }, () => askJevChoiceUsingJev(options));
    const backend = "backend" in result && result.backend === "clef" ? "clef" : "jev";
    return withBackendMetadata(result, backend, requested, backend === "jev" ? clefFailureReason : undefined);
  }
  return clefAttempt();
}

export type AskScoreOptions = BackendOptions & {
  /** The object the question is asked about. Serialised as-is into state. */
  state: Record<string, unknown>;
  /** The question itself, as text. */
  instructions: string;
  /** Ordered rubric, one description per score from zero. At least two. */
  criteria: string[];
  timeoutMs?: number;
  model?: string;
  apiKey?: string;
  /** Transport override for offline tests. Defaults to globalThis.fetch, read at call time. */
  fetchImpl?: typeof fetch;
  nowMs?: () => number;
};
export type JevScoreResult =
  | ({
      ok: true;
      score: number;
      confidence: number;
      legend: Record<string, string>;
      probabilities: Record<string, number>;
      latencyMs: number;
      model: string;
      usage?: JevUsage;
    } & BackendMetadata)
  | ({ ok: false; reason: JevFailure; error: string; latencyMs: number; model: string } & BackendMetadata);

/**
 * Ask ONE score question: an ordered rubric, exactly one level comes back.
 * The SDK refuses a criteria list shorter than two; we refuse before spending
 * a call, with the same no-answers verdict a malformed answer earns.
 */
async function askJevScoreUsingJev(options: AskScoreOptions): Promise<JevScoreResult> {
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  const apiKey = await resolveApiKey(options.apiKey);

  if (!apiKey) {
    return {
      ok: false,
      reason: "unconfigured",
      error: "TYPESAFE_API_KEY is not set — see .env.example, use infisical run --projectId=…",
      latencyMs: 0,
      model,
    };
  }
  if (!Array.isArray(options.criteria) || options.criteria.length < 2) {
    return { ok: false, reason: "no-answers", error: `score needs a criteria list of at least 2, got ${Array.isArray(options.criteria) ? options.criteria.length : "non-list"}`, latencyMs: 0, model };
  }
  const questions = {
    [SCORE_KEY]: { type: "score", instructions: options.instructions, criteria: options.criteria },
  };
  const posted = await postSystemOne(apiKey, model, options.state, questions, options.timeoutMs ?? 4000, options.fetchImpl ?? globalThis.fetch, undefined, options.nowMs);
  if (!posted.ok) return { ok: false, reason: posted.reason, error: posted.error, latencyMs: posted.latencyMs, model };
  const { answers, latencyMs } = posted;

  const answer: unknown = Reflect.get(answers, SCORE_KEY);
  if (!answer || typeof answer !== "object") {
    return { ok: false, reason: "no-answers", error: "`answers.score` was missing or not an object", latencyMs, model };
  }
  try {
    const validated = validateScoreAnswer(answer, options.criteria);
    return { ok: true, score: validated.score, confidence: validated.confidence, legend: validated.legend, probabilities: validated.probabilities, latencyMs, model, ...(posted.usage ? { usage: posted.usage } : {}) };
  } catch (error) {
    return { ok: false, reason: "no-answers", error: error instanceof Error ? error.message : String(error), latencyMs, model };
  }
}

export async function askJevScore(options: AskScoreOptions): Promise<JevScoreResult> {
  const requested = selectedBackend(options);
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  if (!requested) return { ok: false, reason: "usage", error: "backend must be jev, clef, or auto", latencyMs: 0, model };
  if (requested === "clef") {
    return withBackendMetadata({ ok: false, reason: "uncalibrated", error: "Clef has no score calibration", latencyMs: 0, model }, "clef", requested);
  }
  if (requested === "auto") {
    const route = resolveBackendRoute({
      requested,
      primitive: "score",
      questionCount: 1,
      familyReceiptRegistered: false,
      backendHoldActive: clefBackendHoldActive(options.nowMs?.() ?? Date.now()),
    });
    return withBackendMetadata(await askJevScoreUsingJev(options), "jev", requested, route.routeReason);
  }
  return withBackendMetadata(await askJevScoreUsingJev(options), "jev", requested);
}

export type AskBundleOptions = BackendOptions & {
  /** What the questions are asked about: text (sent as a string) or an object. Serialised as-is into state. */
  state: string | Record<string, unknown>;
  /** Already-typed question objects (type: noul|choice|score). */
  questions: Record<string, unknown>;
  timeoutMs?: number;
  model?: string;
  apiKey?: string;
  /** Transport override for offline tests. Defaults to globalThis.fetch, read at call time. */
  fetchImpl?: typeof fetch;
  nowMs?: () => number;
  /** Retry owned by the SDK. Absent means maxRetries 0: one attempt per call. */
  retry?: { maxRetries?: number };
};

export type JevBundleResult =
  | ({
      ok: true;
      answers: Record<string, unknown>;
      latencyMs: number;
      model: string;
      resolvedModel: string;
      usage?: JevUsage;
    } & BackendMetadata)
  | ({ ok: false; reason: JevFailure; error: string; latencyMs: number; model: string } & BackendMetadata);

/**
 * Mixed questions against one state. Choice + Noul in one request run in parallel.
 * The only sanctioned way to ask both without forking fetch.
 */
async function askJevBundleUsingJev(options: AskBundleOptions): Promise<JevBundleResult> {
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  const apiKey = await resolveApiKey(options.apiKey);
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
  const posted = await postSystemOne(apiKey, model, options.state, options.questions, options.timeoutMs ?? 4000, options.fetchImpl ?? globalThis.fetch, options.retry, options.nowMs);
  if (!posted.ok) return { ok: false, reason: posted.reason, error: posted.error, latencyMs: posted.latencyMs, model };
  try {
    validateBundleAnswers(options.questions, posted.answers);
  } catch (error) {
    return { ok: false, reason: "no-answers", error: error instanceof Error ? error.message : String(error), latencyMs: posted.latencyMs, model };
  }
  return {
    ok: true,
    answers: posted.answers as Record<string, unknown>,
    latencyMs: posted.latencyMs,
    model,
    resolvedModel: posted.resolvedModel,
    ...(posted.usage ? { usage: posted.usage } : {}),
  };
}

export async function askJevBundle(options: AskBundleOptions): Promise<JevBundleResult> {
  const requested = selectedBackend(options);
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  if (!requested) return { ok: false, reason: "usage", error: "backend must be jev, clef, or auto", latencyMs: 0, model };
  if (requested === "clef") {
    return withBackendMetadata({ ok: false, reason: "uncalibrated", error: "Clef does not support bundled questions", latencyMs: 0, model }, "clef", requested);
  }
  if (requested === "auto") {
    const route = resolveBackendRoute({
      requested,
      primitive: "bundle",
      questionCount: Object.keys(options.questions ?? {}).length,
      familyReceiptRegistered: false,
      backendHoldActive: clefBackendHoldActive(options.nowMs?.() ?? Date.now()),
    });
    return withBackendMetadata(await askJevBundleUsingJev(options), "jev", requested, route.routeReason);
  }
  return withBackendMetadata(await askJevBundleUsingJev(options), "jev", requested);
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
