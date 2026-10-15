import test from "node:test";
import assert from "node:assert/strict";
import {
  ADOPTION_MAX_MINUTES,
  DROPPED_UNLABELLED_MAX,
  checkAdoption,
  checkDroppedUnlabelled,
} from "../src/ship/stage-exit.ts";

// Receipt-bound stage-exit gates (jev-uzq1.2 rework for LavenderDune 3523).
// Every check takes a receipt artifact with source provenance; bare numbers
// and caller belief booleans are refused. NO-CLAIM: cutoff checks only.
// Keyless: no model, network, or Infisical use.

const SOURCE = {
  path: "work/uzq1/stage-receipt.json",
  sha256: "a".repeat(64),
  collectedAt: "2026-10-15T11:00:00Z",
};

test("29 positives with receipt provenance passes eligibility only", () => {
  assert.deepEqual(
    checkDroppedUnlabelled({ outcomePositives: 29, window: "14d", source: SOURCE }),
    { eligible: true, scope: "cutoff-check-only" },
  );
});

test("exactly 30 and 31 positives fail the strict cutoff", () => {
  for (const outcomePositives of [30, 31]) {
    assert.throws(
      () => checkDroppedUnlabelled({ outcomePositives, window: "14d", source: SOURCE }),
      /cutoff/,
    );
  }
});

test("bare numbers without receipt source are refused", () => {
  assert.throws(
    () => checkDroppedUnlabelled({ outcomePositives: 29, window: "14d" }),
    /provenance is required/,
  );
  assert.throws(
    () => checkDroppedUnlabelled({ outcomePositives: 29, window: "14d", source: {} }),
    /source field/,
  );
  assert.throws(
    () =>
      checkDroppedUnlabelled({
        outcomePositives: 29,
        window: "14d",
        source: { ...SOURCE, sha256: "xyz" },
      }),
    /64 hex/,
  );
});

test("unstated or different window fails", () => {
  for (const window of ["", "7d", "30d"]) {
    assert.throws(
      () => checkDroppedUnlabelled({ outcomePositives: 5, window, source: SOURCE }),
      /window must be/,
    );
  }
});

test("stranger-adopts receipt under 60 minutes passes", () => {
  assert.deepEqual(checkAdoption({ elapsedMinutes: 42, source: SOURCE }), {
    eligible: true,
  });
});

test("negative elapsed minutes fail", () => {
  assert.throws(
    () => checkAdoption({ elapsedMinutes: -1, source: SOURCE }),
    /negative/,
  );
});
test("missing receipt or 60+ minutes fail", () => {
  assert.throws(() => checkAdoption({ elapsedMinutes: 10 }), /provenance is required/);
  assert.throws(
    () => checkAdoption({ elapsedMinutes: 60, source: SOURCE }),
    /bound/,
  );
  assert.throws(
    () => checkAdoption({ elapsedMinutes: 95, source: SOURCE }),
    /bound/,
  );
});
