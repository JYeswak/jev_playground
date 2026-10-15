/**
 * Stage-exit source gates for jev-uzq1 (jev-uzq1.2).
 *
 * Pure definition layer only: DROPPED-UNLABELLED strict cutoff (< 30
 * outcome positives in the specified 14-day window) and stranger-adopts
 * time bound (< 60 minutes). No service calls, no network, no clock.
 */

export const DROPPED_UNLABELLED_WINDOW = "14d";
export const DROPPED_UNLABELLED_MAX = 30;
export const ADOPTION_MAX_MINUTES = 60;

function fail(message: string): never {
  throw new Error(`stage-exit refused: ${message}`);
}

export type DroppedUnlabelledInput = {
  outcomePositives: number;
  window: string;
};

export type DroppedUnlabelledVerdict = {
  eligible: true;
  scope: "cutoff-check-only";
};

/** Strict cutoff: fewer than 30 positives in exactly the 14-day window. */
export function checkDroppedUnlabelled(input: DroppedUnlabelledInput): DroppedUnlabelledVerdict {
  if (!Number.isInteger(input.outcomePositives) || input.outcomePositives < 0) {
    fail("outcome positives must be a non-negative integer");
  }
  if (input.window !== DROPPED_UNLABELLED_WINDOW) {
    fail(`window must be ${DROPPED_UNLABELLED_WINDOW}, got ${input.window}`);
  }
  if (input.outcomePositives >= DROPPED_UNLABELLED_MAX) {
    fail(`outcome positives ${input.outcomePositives} reach the ${DROPPED_UNLABELLED_MAX} cutoff`);
  }
  return { eligible: true, scope: "cutoff-check-only" };
}

export type AdoptionInput = {
  elapsedMinutes?: number;
  receiptPresent: boolean;
};

/** Stranger-adopts receipt: present with elapsed time under 60 minutes. */
export function checkAdoption(input: AdoptionInput): { eligible: true } {
  if (!input.receiptPresent) fail("stranger-adopts receipt missing");
  if (typeof input.elapsedMinutes !== "number" || !Number.isFinite(input.elapsedMinutes)) {
    fail("elapsed minutes must be a finite number");
  }
  if (input.elapsedMinutes >= ADOPTION_MAX_MINUTES) {
    fail(`elapsed ${input.elapsedMinutes} minutes reaches the ${ADOPTION_MAX_MINUTES}-minute bound`);
  }
  return { eligible: true };
}
