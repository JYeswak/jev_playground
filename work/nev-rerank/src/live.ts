/**
 * One systemOne call, one Score question per passage. Wire shape is jev.py
 * JevScoreBatch, sent through work/jev-client so we do not invent a second body.
 */
import { askJevBundle } from "../../jev-client/src/index.ts";
import { expectedLevel, passageId, scoreQuestion, type RankAnswer } from "./rank.ts";

export const LIVE_MODEL = "jev-1.13.0";
export const LIVE_TIMEOUT_MS = 20_000;

export async function liveAsker(state: { query: string; passages: Record<string, string> }): Promise<RankAnswer> {
  const ids = Object.keys(state.passages);
  const questions: Record<string, unknown> = {};
  for (const id of ids) questions[id] = scoreQuestion(id);
  const posted = await askJevBundle({
    state,
    questions,
    model: LIVE_MODEL,
    timeoutMs: LIVE_TIMEOUT_MS,
  });
  if (!posted.ok) return { ok: false, reason: posted.reason };
  const scores: Record<string, number> = {};
  for (let index = 0; index < ids.length; index++) {
    const id = passageId(index);
    const level = expectedLevel(Reflect.get(posted.answers, id));
    if (level === undefined) return { ok: false, reason: "incomplete-scores" };
    scores[id] = level;
  }
  return { ok: true, scores };
}
