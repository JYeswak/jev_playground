import { test } from "node:test";
import assert from "node:assert/strict";
import { randomBaseline, ownConstant, DEFAULT_SEED } from "./random-judge.mjs";

// Skewed set: 16 pass / 4 fail — majority rate 0.8. Object-case form,
// exercising the default truthKey path end to end.
const skewed = [
  ...Array.from({ length: 16 }, (_, i) => ({ id: `p${i}`, truth: "pass" })),
  ...Array.from({ length: 4 }, (_, i) => ({ id: `f${i}`, truth: "fail" })),
];

test("seeded determinism: same seed twice gives identical predictions", () => {
  const a = randomBaseline({ cases: skewed, seed: 7 });
  const b = randomBaseline({ cases: skewed, seed: 7 });
  assert.deepEqual(a.predicted, b.predicted);
  assert.equal(a.accuracy, b.accuracy);
});

test("default seed is pinned and deterministic", () => {
  assert.equal(DEFAULT_SEED, 20260920);
  const a = randomBaseline({ cases: skewed });
  const b = randomBaseline({ cases: skewed });
  assert.deepEqual(a.predicted, b.predicted);
});

test("random accuracy on a skewed set lands near the majority rate (chance, not skill)", () => {
  const majority = ownConstant({ cases: skewed }).accuracy;
  assert.equal(majority, 0.8);
  const { accuracy, predicted } = randomBaseline({ cases: skewed });
  assert.equal(predicted.length, skewed.length);
  // A permutation of the truth labels must score near the base rate —
  // inside ±0.2 of the majority share — proving chance, not discrimination.
  assert.ok(
    Math.abs(accuracy - majority) <= 0.2,
    `random accuracy ${accuracy} not within 0.2 of majority ${majority}`,
  );
});

test("ownConstant returns the majority share on an imbalanced set", () => {
  const r = ownConstant({ cases: skewed });
  assert.equal(r.label, "pass");
  assert.equal(r.accuracy, 0.8);
  assert.equal(r.count, 16);
  assert.equal(r.total, 20);
});

test("ownConstant returns 1.0 on a unanimous set", () => {
  const r = ownConstant({ cases: ["yes", "yes", "yes"] });
  assert.equal(r.label, "yes");
  assert.equal(r.accuracy, 1.0);
});

test("bare-label cases work for both baselines", () => {
  const cases = ["a", "a", "b"];
  const r = ownConstant({ cases });
  assert.equal(r.label, "a");
  assert.equal(r.accuracy, 2 / 3);
  const j = randomBaseline({ cases, seed: 3 });
  assert.equal(j.predicted.length, 3);
  assert.deepEqual([...j.predicted].sort(), ["a", "a", "b"]);
});
