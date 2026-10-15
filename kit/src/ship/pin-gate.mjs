// Cohort-B eligibility + contract-target binding for the pin ship path.
//
// SCOPE (jev-2af1.2): the N7 >= 30 outcome-positive threshold and the
// kit/contracts/pin.json target only. Host wiring, both-ways L3 and value
// receipts stay in jev-2af1.1, which extends kit/test/ship-pin.test.mjs.
// The budget ceilings below mirror the screen contract class (same handler
// limits); pin host traffic tuning belongs to .1 measurement, not this gate.

import { readFile } from "node:fs/promises";
import { validateContract } from "../contracts.ts";

export const PIN_FAMILY = "pin";
export const PIN_CONTRACT_PATH = new URL(
  "../../contracts/pin.json",
  import.meta.url,
);
export const COHORT_B_MIN_OUTCOME_POSITIVES = 30;

export function cohortEligible(n7OutcomePositives) {
  if (!Number.isInteger(n7OutcomePositives)) {
    return { eligible: false, reason: "n7-outcome-positives-missing" };
  }
  if (n7OutcomePositives < COHORT_B_MIN_OUTCOME_POSITIVES) {
    return {
      eligible: false,
      reason: "below-cohort-threshold",
      n7OutcomePositives,
      required: COHORT_B_MIN_OUTCOME_POSITIVES,
    };
  }
  return {
    eligible: true,
    scope: "cohort-eligibility-only",
    n7OutcomePositives,
  };
}

export async function resolvePinContract(path = PIN_CONTRACT_PATH) {
  const raw = JSON.parse(await readFile(path, "utf8"));
  const contract = validateContract(raw);
  if (contract.family !== PIN_FAMILY) {
    throw new TypeError(
      `pin contract target must be family '${PIN_FAMILY}'; got '${contract.family}'`,
    );
  }
  return contract;
}
