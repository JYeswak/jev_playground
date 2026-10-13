import { validateChoiceAnswer, validateNoulAnswer } from "./validate.ts";
import { questionSha, plattMap, type ClefCalibration, type ModelFingerprint } from "./calibration.ts";
import { readSystemOneUsage, type SystemOneUsage } from "./usage.ts";
import { sizePreflight } from "./preflight.ts";

export type ClefPrimitive = "choice" | "noul";
export type ClefFailureReason = "uncalibrated" | "truncated" | "backend-hold" | "online-required" | "refused-unsafe" | "http" | "non-json" | "no-answers" | "transport";

type ClefFailure = {
  ok: false;
  reason: ClefFailureReason;
  error: string;
  latencyMs: number;
  model: string;
  backend: "clef";
};

export type ClefChoiceResult = {
  ok: true;
  choice: string;
  confidence: number;
  probabilities: Record<string, number>;
  probabilitiesRaw: true;
  latencyMs: number;
  model: string;
  usage?: SystemOneUsage;
  backend: "clef";
};

export type ClefNoulResult = {
  ok: true;
  scores: Record<string, number>;
  latencyMs: number;
  model: string;
  usage?: SystemOneUsage;
  backend: "clef";
};

export type AskClefOptions = {
  primitive: ClefPrimitive;
  state: string | Record<string, unknown>;
  question: Record<string, unknown>;
  callerKey: string;
  calibration?: ClefCalibration;
  fingerprint?: ModelFingerprint;
  fetchImpl?: typeof fetch;
  url?: string;
  timeoutMs?: number;
};

const TRUNCATION_LIMIT = 16_384;

function failure(reason: ClefFailureReason, error: string, latencyMs: number, taskModel = "clef-flash"): ClefFailure {
  return { ok: false, reason, error, latencyMs, model: taskModel, backend: "clef" };
}

function eligibleCalibration(options: AskClefOptions): ClefCalibration | undefined {
  const calibration = options.calibration;
  if (!calibration || calibration.primitive !== options.primitive) return undefined;
  if (options.question.type !== options.primitive || !options.callerKey) return undefined;
  if (!options.fingerprint) return undefined;
  if (options.fingerprint.joint_head_sha256 !== calibration.model.joint_head_sha256 ||
      options.fingerprint.index_sha256 !== calibration.model.index_sha256) return undefined;
  const stateKeys = typeof options.state === "string" ? [] : Object.keys(options.state);
  if (stateKeys.length === 0) return undefined;
  try {
    if (questionSha(options.question, stateKeys) !== calibration.question_sha256) return undefined;
  } catch {
    return undefined;
  }
  return calibration;
}

function localEndpoint(value: string): URL | undefined {
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    return undefined;
  }
  const loopback = url.hostname === "127.0.0.1" || url.hostname === "localhost" || url.hostname === "[::1]";
  if (!loopback || url.protocol !== "http:" || url.port === "8010" || url.username || url.password) return undefined;
  return url;
}

let clefRequestActive = false;
const clefRequestWaiters: Array<() => void> = [];

async function withClefRequestSlot<T>(operation: () => Promise<T>): Promise<T> {
  if (clefRequestActive) await new Promise<void>((resolve) => clefRequestWaiters.push(resolve));
  clefRequestActive = true;
  try {
    return await operation();
  } finally {
    const next = clefRequestWaiters.shift();
    if (next) next();
    else clefRequestActive = false;
  }
}

/** Send one unauthenticated Clef request; raw values never leave without an exact calibration. */
async function askClefOnce(options: AskClefOptions): Promise<ClefChoiceResult | ClefNoulResult | ClefFailure> {
  const started = Date.now();
  const calibration = eligibleCalibration(options);
  if (!calibration) return failure("uncalibrated", "no exact calibration and model fingerprint match", 0);

  const configuredUrl = options.url ?? process.env.JEV_CLEF_URL;
  if (!configuredUrl) return failure("online-required", "Clef gateway URL is not configured", 0);
  const endpoint = localEndpoint(configuredUrl);
  if (!endpoint) return failure("refused-unsafe", "Clef URL must be an explicit loopback gateway URL and may not use port 8010", 0);
  const timeoutMs = options.timeoutMs ?? Number(process.env.JEV_CLEF_TIMEOUT_MS ?? 10_000);
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1) return failure("online-required", "JEV_CLEF_TIMEOUT_MS must be a positive integer", 0);

  try {
    sizePreflight(options.state, { [calibration.question_key]: options.question }, { limitTokens: TRUNCATION_LIMIT });
  } catch (error) {
    return failure("truncated", error instanceof Error ? error.message : "Clef request exceeds the size preflight", 0);
  }

  let response: Response;
  try {
    response = await (options.fetchImpl ?? globalThis.fetch)(endpoint.toString(), {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        model: "clef-flash",
        state: options.state,
        questions: { [calibration.question_key]: options.question },
      }),
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch (error) {
    return failure("transport", error instanceof Error ? error.message : String(error), Date.now() - started, calibration.model.id);
  }
  const latencyMs = Date.now() - started;
  if (!response.ok) return failure("http", `Clef HTTP ${response.status}`, latencyMs, calibration.model.id);

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    return failure("non-json", "Clef response was not JSON", latencyMs, calibration.model.id);
  }
  if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
    return failure("no-answers", "Clef response was not an object", latencyMs, calibration.model.id);
  }
  const envelope = payload as Record<string, unknown>;
  const usage = readSystemOneUsage(envelope.usage);
  if (usage && usage.input_tokens >= TRUNCATION_LIMIT) {
    return failure("truncated", `Clef input_tokens=${usage.input_tokens} reaches the truncation limit`, latencyMs, calibration.model.id);
  }
  const answers = envelope.answers;
  if (answers === null || typeof answers !== "object" || Array.isArray(answers)) {
    return failure("no-answers", "Clef response carried no answers object", latencyMs, calibration.model.id);
  }
  const answer = Reflect.get(answers, calibration.question_key);
  if (answer === undefined) return failure("no-answers", `Clef response omitted ${calibration.question_key}`, latencyMs, calibration.model.id);
  const model = `clef-flash+platt:${calibration.task_id}.v${calibration.version}`;

  if (options.primitive === "choice") {
    const criteria = options.question.criteria;
    if (criteria === null || typeof criteria !== "object" || Array.isArray(criteria)) {
      return failure("uncalibrated", "choice calibration requires a criteria map", latencyMs, model);
    }
    const labels = Object.keys(criteria);
    try {
      const validated = validateChoiceAnswer(answer, labels);
      const confidence = plattMap(validated.probabilities[validated.choice], calibration.map);
      return {
        ok: true,
        choice: validated.choice,
        confidence,
        probabilities: validated.probabilities,
        probabilitiesRaw: true,
        latencyMs,
        model,
        ...(usage ? { usage } : {}),
        backend: "clef",
      };
    } catch (error) {
      return failure("no-answers", error instanceof Error ? error.message : "invalid Clef choice", latencyMs, model);
    }
  }

  try {
    const raw = validateNoulAnswer(answer);
    return {
      ok: true,
      scores: { [options.callerKey]: plattMap(raw, calibration.map) },
      latencyMs,
      model,
      ...(usage ? { usage } : {}),
      backend: "clef",
    };
  } catch (error) {
    return failure("no-answers", error instanceof Error ? error.message : "invalid Clef Noul", latencyMs, model);
  }
}

/** Keep the whole request/response exchange to one in-flight local Clef call per process. */
export async function askClef(options: AskClefOptions): Promise<ClefChoiceResult | ClefNoulResult | ClefFailure> {
  return withClefRequestSlot(() => askClefOnce(options));
}
