/**
 * Stage-exit source gates for jev-uzq1 (jev-uzq1.2).
 *
 * Receipt-bound consumers: every check takes a receipt artifact object
 * carrying its source provenance (path + SHA-256 + collection timestamp).
 * Bare caller-supplied numbers are refused — caller belief is not receipt
 * evidence. No service calls, no network, no clock.
 */

export const DROPPED_UNLABELLED_WINDOW = "14d";
export const DROPPED_UNLABELLED_MAX = 30;
export const ADOPTION_MAX_MINUTES = 60;

function fail(message: string): never {
  throw new Error(`stage-exit refused: ${message}`);
}

export type ReceiptSource = {
  path: string;
  sha256: string;
  collectedAt: string;
};

function assertSource(source: unknown): asserts source is ReceiptSource {
  if (source === null || typeof source !== "object") {
    fail("receipt source provenance is required, not bare numbers");
  }
  const provenance = source as Record<string, unknown>;
  for (const field of ["path", "sha256", "collectedAt"] as const) {
    if (typeof provenance[field] !== "string" || (provenance[field] as string).length === 0) {
      fail(`receipt source field ${field} is required`);
    }
  }
  if (!/^[0-9a-f]{64}$/.test(provenance["sha256"] as string)) {
    fail("receipt source sha256 must be 64 hex characters");
  }
}

export type DroppedUnlabelledReceipt = {
  outcomePositives: number;
  window: string;
  source: ReceiptSource;
};

export type DroppedUnlabelledVerdict = {
  eligible: true;
  scope: "cutoff-check-only";
};

/** Strict cutoff on receipt evidence: <30 positives in exactly the 14d window. */
export function checkDroppedUnlabelled(
  receipt: DroppedUnlabelledReceipt,
): DroppedUnlabelledVerdict {
  assertSource(receipt?.source);
  if (!Number.isInteger(receipt.outcomePositives) || receipt.outcomePositives < 0) {
    fail("outcome positives must be a non-negative integer");
  }
  if (receipt.window !== DROPPED_UNLABELLED_WINDOW) {
    fail(`window must be ${DROPPED_UNLABELLED_WINDOW}, got ${receipt.window}`);
  }
  if (receipt.outcomePositives >= DROPPED_UNLABELLED_MAX) {
    fail(`outcome positives ${receipt.outcomePositives} reach the ${DROPPED_UNLABELLED_MAX} cutoff`);
  }
  return { eligible: true, scope: "cutoff-check-only" };
}

export type AdoptionReceipt = {
  elapsedMinutes: number;
  source: ReceiptSource;
};

/** Stranger-adopts receipt: elapsed time present, finite, non-negative, under 60. */
export function checkAdoption(receipt: AdoptionReceipt): { eligible: true } {
  assertSource(receipt?.source);
  if (typeof receipt.elapsedMinutes !== "number" || !Number.isFinite(receipt.elapsedMinutes)) {
    fail("elapsed minutes must be a finite number");
  }
  if (receipt.elapsedMinutes < 0) {
    fail(`elapsed minutes ${receipt.elapsedMinutes} is negative`);
  }
  if (receipt.elapsedMinutes >= ADOPTION_MAX_MINUTES) {
    fail(`elapsed ${receipt.elapsedMinutes} minutes reaches the ${ADOPTION_MAX_MINUTES}-minute bound`);
  }
  return { eligible: true };
}
