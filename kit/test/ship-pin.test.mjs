// Pin ship threshold + contract-target checks (jev-2af1.2).
//
// Covers ONLY the two source-description obligations absent from jev-2af1.1:
// N7 cohort-B eligibility at >= 30 outcome positives (PRODUCT.md:227) and the
// kit/contracts/pin.json target (jev-2af1 snapshot comment #2807).
// jev-2af1.1 retains host wiring, L3 and value receipts and extends this file.
// NO-CLAIM: passing here covers the threshold and contract target only; it is
// not ship, L3, or value proof. Keyless: no model, network, or Infisical use.
//
// Contract honesty: pin.json carries NO operating point. Its decision string
// is an explicit UNRESOLVED marker, its daily cap is 0 (zero calls authorized
// — nothing is wired), and the latency value is inert until .1 sets a measured
// budget. .1 replaces marker, cap and budget together with this test.

import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  cohortEligible,
  resolvePinContract,
  COHORT_B_MIN_OUTCOME_POSITIVES,
} from "../src/ship/pin-gate.mjs";

test("29 N7 outcome positives fails cohort eligibility", () => {
  assert.deepEqual(cohortEligible(29), {
    eligible: false,
    reason: "below-cohort-threshold",
    n7OutcomePositives: 29,
    required: 30,
  });
});

test("exactly 30 passes eligibility only, never live/on", () => {
  const result = cohortEligible(30);
  assert.equal(result.eligible, true);
  assert.equal(result.scope, "cohort-eligibility-only");
  assert.ok(!("live" in result) && !("on" in result));
});

test("absent or non-count N7 evidence remains ineligible", () => {
  for (const value of [undefined, null, NaN, 2.5, -1, "30"]) {
    assert.equal(cohortEligible(value).eligible, false);
  }
});

test("gate threshold is bound to the contract bar, not a second constant", async () => {
  const bar = JSON.parse(
    await readFile(new URL("../contracts/pin.json", import.meta.url), "utf8"),
  ).bar;
  assert.equal(bar.min_outcome_positives, COHORT_B_MIN_OUTCOME_POSITIVES);
});

test("pin ship path reads kit/contracts/pin.json as its contract", async () => {
  const contract = await resolvePinContract();
  assert.equal(contract.family, "pin");
});

test("contract carries no operating point: decision unresolved, zero calls authorized", async () => {
  const contract = await resolvePinContract();
  assert.match(contract.question.decision, /UNRESOLVED/);
  assert.equal(contract.budget.daily_call_cap, 0);
});

test("planted missing contract target fails", async () => {
  await assert.rejects(() =>
    resolvePinContract(
      new URL("./fixtures/does-not-exist.json", import.meta.url),
    ),
  );
});

test("planted wrong contract target fails", async () => {
  await assert.rejects(
    () =>
      resolvePinContract(
        new URL("../contracts/screen.json", import.meta.url),
      ),
    /pin/,
  );
});
