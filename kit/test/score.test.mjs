import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { scoreText, SST5_INSTRUCTIONS, SST5_LEVELS } from "../src/score.ts";
import { createFakeFetch } from "../src/fake.ts";
import { PreflightError } from "../src/preflight.ts";

const text = await readFile(new URL("../examples/sst5-example.txt", import.meta.url), "utf8");
const levels = JSON.parse(await readFile(new URL("../examples/sst5-levels.json", import.meta.url), "utf8"));

function fake(score = 3, model = "fake") {
  return createFakeFetch([
    {
      id: "sst5-i0",
      answers: {
        score: {
          score,
          confidence: 0.98,
          legend: Object.fromEntries(SST5_LEVELS.map((level, i) => [String(i), level])),
          probabilities: { "0": 0, "1": 0.01, "2": 0, "3": 0.99, "4": 0 },
        },
      },
      model,
      usage: { input_tokens: 372, output_tokens: 18 },
    },
  ]);
}

test("score uses captured SST-5 levels and returns the selected level", async () => {
  const result = await scoreText({ text, levels, apiKey: "fixture-key", fetchImpl: fake(), model: "fake" });
  assert.equal(result.score, 3);
  assert.equal(result.level, levels[3]);
  assert.equal(result.confidence, 0.98);
  assert.equal(result.model, "fake");
});

test("score sends the exact SST-5 instruction, levels, and text state", async () => {
  let seen;
  const result = await scoreText({
    text,
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
  assert.deepEqual(seen.state, { text });
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

test("score rejects a malformed level index", async () => {
  await assert.rejects(
    scoreText({
      text,
      levels,
      ask: async () => ({
        ok: true,
        score: 5,
        confidence: 1,
        legend: {},
        probabilities: {},
        latencyMs: 0,
        model: "fake",
      }),
    }),
    /invalid level index/,
  );
});
