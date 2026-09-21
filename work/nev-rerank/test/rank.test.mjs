import test from "node:test";
import assert from "node:assert/strict";
import { expectedLevel, lexicalOrder, orderByScores, rerank, RUBRIC } from "../src/rank.ts";

const QUERY = "Which runtime does NOT use a garbage collector?";
const TRAP = "This runtime uses a garbage collector to reclaim unused memory automatically.";
const ANSWER = "This runtime frees memory by explicit ownership. Collection is not part of the design.";

test("lexical overlap ranks the negation trap first", () => {
  const order = lexicalOrder(QUERY, [ANSWER, TRAP]);
  assert.deepEqual(order, [1, 0]);
});

test("score order puts the answering passage first when the asker says so", async () => {
  let calls = 0;
  const result = await rerank(QUERY, [TRAP, ANSWER], async () => {
    calls += 1;
    return { ok: true, scores: { p01: 0.05, p02: 0.95 } };
  });
  assert.equal(calls, 1);
  assert.equal(result.ordered, true);
  assert.equal(result.ranking[0].text, ANSWER);
  assert.equal(result.ranking[1].text, TRAP);
  assert.ok(result.ranking[0].score > result.ranking[1].score);
});

test("a failed asker returns the input order and does not claim a ranking", async () => {
  const result = await rerank(QUERY, [TRAP, ANSWER], async () => ({ ok: false, reason: "unconfigured" }));
  assert.equal(result.ordered, false);
  assert.equal(result.reason, "unconfigured");
  assert.equal(result.ranking[0].text, TRAP);
  assert.equal(result.ranking[1].text, ANSWER);
});

test("a missing score is not filled in as zero", () => {
  assert.equal(orderByScores([TRAP, ANSWER], { p01: 0.9 }), undefined);
});

test("one passage does not call the model", async () => {
  let calls = 0;
  const result = await rerank(QUERY, [ANSWER], async () => {
    calls += 1;
    return { ok: true, scores: { p01: 1 } };
  });
  assert.equal(calls, 0);
  assert.equal(result.reason, "nothing-to-rank");
  assert.equal(result.calledModel, false);
});

test("expected level matches jev.py on a four-bin distribution", () => {
  const answer = {
    legend: { "0": RUBRIC[0], "1": RUBRIC[1], "2": RUBRIC[2], "3": RUBRIC[3] },
    probabilities: { "0": 0, "1": 0, "2": 0.25, "3": 0.75 },
  };
  const level = expectedLevel(answer);
  assert.ok(level !== undefined);
  assert.ok(Math.abs(level - (0 * 0 + 1 * 0 + 2 * 0.25 + 3 * 0.75) / 3) < 1e-12);
});

test("a probability that is not a number is refused", () => {
  const answer = {
    legend: { "0": RUBRIC[0], "1": RUBRIC[1] },
    probabilities: { "0": 0.5, "1": "high" },
  };
  assert.equal(expectedLevel(answer), undefined);
});
