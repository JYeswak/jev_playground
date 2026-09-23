/**
 * Live asker. The only import of jev-client in this package.
 * Offline tests never load this file.
 */
import { askJevChoice } from "../../jev-client/src/index.ts";
import { CRITERIA, INSTRUCTIONS, type ChoiceAnswer } from "./check.ts";

export const LIVE_MODEL = "jev-1.13.0";
export const LIVE_TIMEOUT_MS = 20_000;

export async function liveAsker(state: { claim: string; section: string }): Promise<ChoiceAnswer> {
  const result = await askJevChoice({
    state,
    instructions: INSTRUCTIONS,
    classes: { ...CRITERIA },
    model: LIVE_MODEL,
    timeoutMs: LIVE_TIMEOUT_MS,
  });
  if (!result.ok) return { ok: false, reason: result.reason };
  return { ok: true, choice: result.choice, confidence: result.confidence };
}
