/**
 * One Score question per passage through askJevScore. Rubric text and the
 * expected-level reduction are rank.ts verbatim (JevScoreBatch, nevir 0.7115).
 * Previously one batched askJevBundle call; now one validated call per passage
 * so every answer passes the SDK-typed guards. Costs N requests instead of 1.
 */
import { askJevScore } from "../../jev-client/src/index.ts";
import { expectedLevel, passageId, scoreQuestion, type RankAnswer } from "./rank.ts";

export const LIVE_MODEL = "jev-1.13.0";
export const LIVE_TIMEOUT_MS = 20_000;

export async function liveAsker(
  state: { query: string; passages: Record<string, string> },
  fetchImpl?: typeof fetch,
): Promise<RankAnswer> {
  const ids = Object.keys(state.passages);
  const scores: Record<string, number> = {};
  for (let index = 0; index < ids.length; index++) {
    const id = passageId(index);
    const q = scoreQuestion(id);
    const r = await askJevScore({
      state,
      instructions: q.instructions,
      criteria: [...q.criteria],
      model: LIVE_MODEL,
      timeoutMs: LIVE_TIMEOUT_MS,
      ...(fetchImpl ? { fetchImpl } : {}),
    });
    if (!r.ok) return { ok: false, reason: r.reason };
    const level = expectedLevel({ legend: r.legend, probabilities: r.probabilities, score: r.score });
    if (level === undefined) return { ok: false, reason: "incomplete-scores" };
    scores[id] = level;
  }
  return { ok: true, scores };
}
