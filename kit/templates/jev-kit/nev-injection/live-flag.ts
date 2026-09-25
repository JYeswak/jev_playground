/**
 * Live asker for the injection flag: one Noul per call through work/jev-client.
 * Separated from the tool factory so tests inject a fake without touching network.
 */
import { askJev, observedFetch } from "../client.ts";

export const LIVE_MODEL = "jev-1.13.0";
export const LIVE_TIMEOUT_MS = 20000;

export async function liveAsker(input, fetchImpl?: typeof fetch) {
  let sent = false;
  const transport = observedFetch(() => { sent = true; }, fetchImpl ?? globalThis.fetch);
  const posted = await askJev({
    state: { assistant: input.assistant, user_message: input.userMessage },
    questions: { inj: input.question },
    model: LIVE_MODEL,
    timeoutMs: LIVE_TIMEOUT_MS,
    fetchImpl: transport,
  });
  if (!posted.ok) return { ok: false, reason: posted.reason, calledModel: sent };
  const value = posted.scores["inj"];
  if (typeof value !== "number") return { ok: false, reason: "incomplete-scores", calledModel: sent };
  return { ok: true, probability: value, latencyMs: posted.latencyMs };
}
