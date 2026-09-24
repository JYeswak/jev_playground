/**
 * Score-batch rerank. The question and the expected-level math are copied from
 * jev-rerank-bench/rerankers/jev.py (JevScoreBatch), the arm that scored
 * paired_accuracy 0.7115 on NevIR (n=1383, 0 failures) against BM25 at 0.0224.
 * Receipt: jev-rerank-bench/results/nevir.json. Repo @ cd9a35b.
 *
 * This module does not call the network. It orders passages by scores an asker
 * returns. A failed asker returns the input order and says so — never a fabricated
 * ranking.
 */

export const RUBRIC = [
  "The passage is off-topic for the query.",
  "The passage is on a related topic but does not supply what the query asks for.",
  "The passage partly supplies the information needed to answer or verify the query.",
  "The passage fully supplies the information needed to answer or verify the query.",
] as const;

export const MAX_PASSAGES = 30;

export function passageId(index: number): string {
  return `p${String(index + 1).padStart(2, "0")}`;
}

export function scoreQuestion(id: string): { type: "score"; instructions: string; criteria: string[] } {
  return {
    type: "score",
    instructions: `How well does passage ${id} supply the information needed to answer or verify the query?`,
    criteria: [...RUBRIC],
  };
}

/**
 * Expected level in 0..1. Same reduction as jev.py: sort legend keys by rubric
 * index, then probability-weighted index / (n-1). Falls back to `score` only
 * when the distribution is absent. A distribution that does not cover the rubric
 * is refused — a missing probability must not become a zero that looks measured.
 */
export function expectedLevel(answer: unknown): number | undefined {
  if (!answer || typeof answer !== "object") return undefined;
  const legend = Reflect.get(answer, "legend");
  const probs = Reflect.get(answer, "probabilities");
  if (legend && typeof legend === "object" && !Array.isArray(legend) && probs && typeof probs === "object" && !Array.isArray(probs)) {
    const keys = Object.keys(legend).sort((a, b) => {
      const ia = RUBRIC.indexOf(Reflect.get(legend, a) as (typeof RUBRIC)[number]);
      const ib = RUBRIC.indexOf(Reflect.get(legend, b) as (typeof RUBRIC)[number]);
      return (ia < 0 ? 0 : ia) - (ib < 0 ? 0 : ib);
    });
    if (keys.length < 2) return undefined;
    let ev = 0;
    for (let idx = 0; idx < keys.length; idx++) {
      const p = Reflect.get(probs, keys[idx]);
      if (typeof p !== "number" || !Number.isFinite(p)) return undefined;
      ev += p * idx;
    }
    return ev / (keys.length - 1);
  }
  const score = Reflect.get(answer, "score");
  if (typeof score === "number" && Number.isFinite(score)) return score;
  return undefined;
}

/**
 * A failed asker says whether it sent a request. `calledModel` is true only when
 * the asker observed one leave (e.g. an HTTP 402 or a timeout); a failure before
 * any request (no key, billing hold, SDK missing) is false. An asker that omits
 * the field did not report a request, and rerank() reports false.
 */
export type RankAnswer =
  | { ok: true; scores: Record<string, number> }
  | { ok: false; reason: string; calledModel?: boolean };

export type Asker = (state: { query: string; passages: Record<string, string> }) => Promise<RankAnswer>;

export type Ranked = {
  id: string;
  index: number;
  text: string;
  score: number;
};

export type RankResult = {
  ordered: boolean;
  reason?: string;
  calledModel: boolean;
  truncated: boolean;
  ranking: Ranked[];
};

export function orderByScores(
  passages: readonly string[],
  scores: Record<string, number>,
): Ranked[] | undefined {
  const ranking: Ranked[] = [];
  for (let index = 0; index < passages.length; index++) {
    const id = passageId(index);
    const score = scores[id];
    if (typeof score !== "number" || !Number.isFinite(score)) return undefined;
    ranking.push({ id, index, text: passages[index], score });
  }
  ranking.sort((a, b) => b.score - a.score || a.index - b.index);
  return ranking;
}

/** Lexical overlap, the class of baseline NevIR shows cannot see negation. */
export function lexicalOrder(query: string, passages: readonly string[]): number[] {
  const terms = new Set(query.toLowerCase().split(/\W+/).filter((t) => t.length > 2));
  return passages
    .map((text, index) => {
      const words = text.toLowerCase().split(/\W+/);
      const overlap = words.filter((w) => terms.has(w)).length;
      return { index, overlap };
    })
    .sort((a, b) => b.overlap - a.overlap || a.index - b.index)
    .map((row) => row.index);
}

export async function rerank(query: string, passages: readonly string[], asker: Asker): Promise<RankResult> {
  const truncated = passages.length > MAX_PASSAGES;
  const slice = passages.slice(0, MAX_PASSAGES);
  const inputOrder = slice.map((text, index) => ({ id: passageId(index), index, text, score: Number.NaN }));
  if (query.replace(/\s+/g, " ").trim() === "" || slice.length < 2) {
    return {
      ordered: false,
      reason: slice.length < 2 ? "nothing-to-rank" : "empty-query",
      calledModel: false,
      truncated,
      ranking: inputOrder,
    };
  }
  const state = {
    query,
    passages: Object.fromEntries(slice.map((text, index) => [passageId(index), text])),
  };
  const answer = await asker(state);
  if (!answer.ok) {
    return { ordered: false, reason: answer.reason, calledModel: answer.calledModel === true, truncated, ranking: inputOrder };
  }
  const ranking = orderByScores(slice, answer.scores);
  if (!ranking) {
    return { ordered: false, reason: "incomplete-scores", calledModel: true, truncated, ranking: inputOrder };
  }
  return { ordered: true, calledModel: true, truncated, ranking };
}
