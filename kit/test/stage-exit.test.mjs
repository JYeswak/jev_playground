import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  ADOPTION_MAX_MINUTES,
  DROPPED_UNLABELLED_MAX,
  checkAdoption,
  checkDroppedUnlabelled,
  loadStageReceipt,
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

test("absent canonical stage receipt refuses eligibility", async () => {
  const missing = new URL("../../work/uzq1/stage-receipt.json", import.meta.url);
  await assert.rejects(loadStageReceipt(missing), /missing or unreadable/);
});

test("valid receipt artifact loads for checks", async () => {
  const dir = mkdtempSync(join(tmpdir(), "stage-exit-"));
  const file = join(dir, "stage-receipt.json");
  writeFileSync(file, JSON.stringify({ outcomePositives: 12 }), "utf8");
  assert.deepEqual(await loadStageReceipt(new URL(`file://${file}`)), {
    outcomePositives: 12,
  });
});

test("malformed receipt artifact fails", async () => {
  const dir = mkdtempSync(join(tmpdir(), "stage-exit-"));
  const file = join(dir, "stage-receipt.json");
  writeFileSync(file, "{not json", "utf8");
  await assert.rejects(loadStageReceipt(new URL(`file://${file}`)), /not valid JSON/);
});
