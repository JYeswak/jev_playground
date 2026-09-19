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
 * CONTRACT, verified against a working live call:
 *   POST https://api.typesafe.ai/v1/systemone
 *   { model, state, questions: { <key>: { type: "noul", instructions } } }
 *   -> { answers: { <key>: { noul: number } } }
 * Field names per docs/demos/SDK-SURFACE.md (`NoulResponse.noul`, `ChoiceResponse.probabilities`;
 * there is no `.probability` and no `.distribution`).
 */
export const SYSTEMONE_ENDPOINT = "https://api.typesafe.ai/v1/systemone";
export const DEFAULT_MODEL = "jev-1.13.0";

/** Discriminated result. There is no "empty success": a caller cannot mistake failure for a clean score. */
export type JevResult =
  | { ok: true; scores: Record<string, number>; latencyMs: number; model: string }
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
};

export async function askJev(options: AskOptions): Promise<JevResult> {
  const model = options.model ?? process.env.JEV_MODEL ?? DEFAULT_MODEL;
  const apiKey = options.apiKey ?? process.env.TYPESAFE_API_KEY;
  const started = Date.now();

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

  let response: Response;
  let text: string;
  try {
    response = await fetch(SYSTEMONE_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ model, state: options.state, questions }),
      signal: AbortSignal.timeout(options.timeoutMs ?? 4000),
    });
    text = await response.text();
  } catch (err) {
    return { ok: false, reason: "transport", error: String(err), latencyMs: Date.now() - started, model };
  }

  const latencyMs = Date.now() - started;
  let body: unknown;
  try {
    body = JSON.parse(text);
  } catch {
    return { ok: false, reason: "non-json", error: `non-JSON body (status ${response.status})`, latencyMs, model };
  }
  if (!response.ok) {
    return { ok: false, reason: "http", error: `systemOne HTTP ${response.status}: ${text.slice(0, 300)}`, latencyMs, model };
  }
  if (!body || typeof body !== "object" || !("answers" in body)) {
    return { ok: false, reason: "no-answers", error: "response carried no `answers`", latencyMs, model };
  }
  const answers = body.answers;
  if (!answers || typeof answers !== "object") {
    return { ok: false, reason: "no-answers", error: "`answers` was not an object", latencyMs, model };
  }

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
