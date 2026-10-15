import test from "node:test";
import assert from "node:assert/strict";
import {
  ADOPTION_MAX_MINUTES,
  DROPPED_UNLABELLED_MAX,
  DROPPED_UNLABELLED_WINDOW,
  checkAdoption,
  checkDroppedUnlabelled,
} from "../src/ship/stage-exit.ts";

// DROPPED-UNLABELLED cutoff + stranger-adopts bound (jev-uzq1.2).
// NO-CLAIM: cutoff checks only; not ship, L3, or value proof.
// Keyless: no model, network, or Infisical use.

test("29 positives in the 14-day window passes eligibility only", () => {
  assert.deepEqual(checkDroppedUnlabelled({ outcomePositives: 29, window: "14d" }), {
    eligible: true,
    scope: "cutoff-check-only",
  });
});

test("exactly 30 positives fails the strict cutoff", () => {
  assert.throws(
    () => checkDroppedUnlabelled({ outcomePositives: 30, window: "14d" }),
    /reach the 30 cutoff/,
  );
});

test("31 positives fails the strict cutoff", () => {
  assert.throws(
    () => checkDroppedUnlabelled({ outcomePositives: 31, window: "14d" }),
    /reach the 30 cutoff/,
  );
});

test("unstated or different window fails", () => {
  for (const window of [undefined, null, "", "7d", "30d"]) {
    assert.throws(
      () => checkDroppedUnlabelled({ outcomePositives: 5, window }),
      /window must be/,
    );
  }
});

test("non-count positives fail", () => {
  for (const outcomePositives of [undefined, null, NaN, 2.5, -1, "29"]) {
    assert.throws(
      () => checkDroppedUnlabelled({ outcomePositives, window: "14d" }),
      /non-negative integer/,
    );
  }
});

test("stranger-adopts receipt under 60 minutes passes", () => {
  assert.deepEqual(checkAdoption({ receiptPresent: true, elapsedMinutes: 42 }), {
    eligible: true,
  });
});

test("missing receipt or 60+ minutes fails", () => {
  assert.throws(
    () => checkAdoption({ receiptPresent: false, elapsedMinutes: 10 }),
    /receipt missing/,
  );
  assert.throws(
    () => checkAdoption({ receiptPresent: true, elapsedMinutes: 60 }),
    /bound/,
  );
  assert.throws(
    () => checkAdoption({ receiptPresent: true, elapsedMinutes: 95 }),
    /bound/,
  );
});

test("constants match the source clauses", () => {
  assert.equal(DROPPED_UNLABELLED_MAX, 30);
  assert.equal(DROPPED_UNLABELLED_WINDOW, "14d");
  assert.equal(ADOPTION_MAX_MINUTES, 60);
});
