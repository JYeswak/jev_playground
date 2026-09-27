import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { scoreText, SST5_INSTRUCTIONS, SST5_LEVELS } from "../src/score.ts";
import { createFakeFetch } from "../src/fake.ts";
import { PreflightError } from "../src/preflight.ts";

const capturedText = "These are AWFUL. They are see through, the fabric feels like tablecloth, and they fit like children’s clothing. Customer service did seem to be nice though, but I regret missing my return date for these. I wouldn’t even donate them because the quality is so poor.";
const levels = JSON.parse(await readFile(new URL("../examples/sst5-levels.json", import.meta.url), "utf8"));
const capturedRows = JSON.parse(await readFile(new URL("./fixtures/sst5-answer.json", import.meta.url), "utf8"));

test("score accepts the captured continuous Score answer and rounds half up", async () => {
  const result = await scoreText({
    text: capturedText,
    levels,
    apiKey: "fixture-key",
    fetchImpl: createFakeFetch(capturedRows),
    model: "fake",
  });
  assert.equal(result.score, 0.07);
  assert.equal(result.level, levels[0]);
  assert.equal(result.confidence, 0.94);
  assert.equal(result.model, "fake");
});

test("score applies measured round-half-up normalization", async () => {
  const result = await scoreText({
    text: capturedText,
    levels: SST5_LEVELS,
    ask: async () => ({
      ok: true,
      score: 1.5,
      confidence: 0.8,
      legend: Object.fromEntries(SST5_LEVELS.map((level, i) => [String(i), level])),
      probabilities: { "0": 0, "1": 0.5, "2": 0.5, "3": 0, "4": 0 },
      latencyMs: 7,
      model: "fake",
    }),
  });
  assert.equal(result.score, 1.5);
  assert.equal(result.level, SST5_LEVELS[2]);
});

test("score sends the exact SST-5 instruction, levels, and text state", async () => {
  let seen;
  const result = await scoreText({
    text: capturedText,
    levels: SST5_LEVELS,
    ask: async (options) => {
      seen = options;
      return {
        ok: true,
        score: 4,
        confidence: 0.8,
        legend: Object.fromEntries(SST5_LEVELS.map((level, i) => [String(i), level])),
        probabilities: { "0": 0, "1": 0, "2": 0, "3": 0.1, "4": 0.9 },
        latencyMs: 7,
        model: "fake",
      };
    },
  });
  assert.equal(result.level, SST5_LEVELS[4]);
  assert.deepEqual(seen.state, { text: capturedText });
  assert.equal(seen.instructions, SST5_INSTRUCTIONS);
  assert.deepEqual(seen.criteria, [...SST5_LEVELS]);
});

test("score rejects oversized text before asking", async () => {
  let asked = false;
  await assert.rejects(
    scoreText({
      text: "x".repeat(100_000),
      levels,
      ask: async () => {
        asked = true;
        return { ok: true, score: 0, confidence: 1, legend: {}, probabilities: {}, latencyMs: 0, model: "fake" };
      },
    }),
    PreflightError,
  );
  assert.equal(asked, false);
});

test("score rejects non-finite and out-of-range values", async () => {
  for (const score of [Number.NaN, -0.1, 5]) {
    await assert.rejects(
      scoreText({
        text: capturedText,
        levels,
        ask: async () => ({
          ok: true,
          score,
          confidence: 1,
          legend: {},
          probabilities: {},
          latencyMs: 0,
          model: "fake",
        }),
      }),
      /invalid value/,
    );
  }
});
