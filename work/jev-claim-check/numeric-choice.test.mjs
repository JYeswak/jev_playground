/**
 * Offline tests for numeric-choice.mjs (bead jev-25r). No key, no network.
 * Run: node --test work/jev-claim-check/numeric-choice.test.mjs
 *
 * The comparison decides every verdict, so its boundaries are the contract: a claim may round the
 * evidence, never the other way round, and a changed digit never matches.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { equalsValue, optionsFor, maskAt, mutate7 } from "./numeric-choice.mjs";
import { mutateV2 } from "./numeric-v2.mjs";
import { mutate } from "./numeric.mjs";

test("equalsValue: exact, thousands commas, and the claim rounding the evidence", () => {
  assert.equal(equalsValue("75/219", "75/219"), true);
  assert.equal(equalsValue("1,145", "1145"), true);
  assert.equal(equalsValue("0.068", "0.0684"), true);
  assert.equal(equalsValue("96%", "96.0%"), true);
  assert.equal(equalsValue("2.6e-13", "2.6e-13"), true);
});

test("equalsValue: a changed digit, the evidence rounding the claim, or a unit mismatch never match", () => {
  assert.equal(equalsValue("79/219", "75/219"), false);
  assert.equal(equalsValue("0.063", "0.0684"), false);
  assert.equal(equalsValue("0.6846", "0.68"), false);
  assert.equal(equalsValue("96%", "96"), false);
  assert.equal(equalsValue("240", "940"), false);
});

test("options: every evidence number once, in order, dates blanked, plus not_stated", () => {
  const { classes, byLabel } = optionsFor("Run 2026-09-24T02:57Z: 500 (A) + 200 (B) + 240 (T8) = 940 requests; 500 again.");
  assert.deepEqual(Object.values(byLabel), ["500", "200", "240", "940"]);
  assert.ok("not_stated" in classes);
  assert.match(classes[Object.keys(byLabel).find((l) => byLabel[l] === "240")], /240 \(T8\)/);
});

test("the masked question is identical for an original and its plant, so one call serves both", () => {
  assert.equal(maskAt("Live 75/219 top-1", 5, "75/219"), maskAt("Live 79/219 top-1", 5, "79/219"));
  assert.equal(maskAt("Live 75/219 top-1", 5, "75/219"), "Live [N] top-1");
});

test("mutate7 always changes the value and never equals an earlier round's plant", () => {
  for (const t of ["4", "75/219", "0.068", "1,145", "96.0%", "9"]) {
    assert.notEqual(mutate7(t), t, t);
    assert.notEqual(mutate7(t), mutateV2(t), t);
    assert.notEqual(mutate7(t), mutate(t), t);
  }
});
