import { readFile } from "node:fs/promises";

/**
 * Gate-evidence consumer for the X7 stratified-recall limitation (jev-8i8i.2).
 *
 * Consumes the structured `recall_bound.py --json` output and the receipt's
 * explicit status line. Refuses anything outside this receipt's shape instead
 * of computing misleading bounds. Nothing here decides live traffic.
 */

export const HISTORY_RECEIPT_SUFFIX =
  "work/plan-20261004/receipts/x7-gate-rules-RECEIPT.md";

/** One-sided 95% Clopper-Pearson upper bound for zero observed events. */
export function zeroEventUpper95(n) {
  if (!Number.isInteger(n) || n <= 0) throw new Error("refused: non-positive n");
  return 1 - Math.pow(0.05, 1 / n);
}

function num(value, label) {
  const parsed = typeof value === "number" ? value : Number(String(value).replace(/,/g, ""));
  if (!Number.isFinite(parsed)) throw new Error(`refused: non-numeric ${label}`);
  return parsed;
}

/**
 * The receipt's explicit status line must read DESCRIPTIVE ONLY.
 * Status is a field, never inferred from prose.
 */
export function receiptStatus(text) {
  const match = text.match(/^\*\*Status:\s*(.+?)(?:\s+—|\s*$)/m);
  if (!match) throw new Error("refused: no receipt status line");
  return match[1].trim();
}

/**
 * Filesystem-layout verdict: a receipt present only at the historical path
 * reports UNMEASURED without reading its content. Canonical presence moves
 * to bundle validation; callers pass the parsed recall_bound.py output.
 */
export function locateReceipt({ canonicalPresent, historyPresent }) {
  if (canonicalPresent) return { verdict: "VALIDATE_BUNDLE" };
  if (historyPresent) return { verdict: "UNMEASURED" };
  throw new Error("refused: no receipt at either path");
}

/**
 * Validate a recall_bound.py --json bundle: descriptive-only status,
 * EXPLORED quality, NOT_RUN free arm, zero live calls, zero unflagged
 * harm total, consistent catch counts, sample within frame, and recomputed
 * bounds matching the stated values.
 */
export function classifyGateJson(bundle) {
  if (bundle === null || typeof bundle !== "object" || Array.isArray(bundle)) {
    throw new Error("refused: bundle is not an object");
  }
  if (bundle.status !== "DESCRIPTIVE_ONLY") {
    throw new Error(`refused: status is ${bundle.status}, not DESCRIPTIVE_ONLY`);
  }
  if (bundle.gate_quality !== "EXPLORED") {
    throw new Error(`refused: gate quality is ${bundle.gate_quality}, not EXPLORED`);
  }
  const free = bundle.free_comparator ?? bundle.free;
  if (!free || free.status !== "NOT_RUN") {
    throw new Error("refused: free comparator state is not NOT_RUN");
  }
  if (bundle.live_calls !== 0) {
    throw new Error("refused: live calls present in bundle");
  }
  const flagged = bundle.jev_flagged_stratum ?? {};
  const caught = num(flagged.harm_caught, "flagged harm caught");
  const flaggedTotal = num(flagged.harm_total, "flagged harm total");
  if (caught > flaggedTotal) {
    throw new Error("refused: caught exceeds total");
  }
  const unflagged = bundle.unflagged_stratum ?? {};
  const total = num(unflagged.harm_total, "unflagged harm total");
  if (total !== 0) {
    throw new Error("refused: nonzero unflagged harm total needs a different method");
  }
  const missed = num(unflagged.harm_caught, "unflagged harm caught");
  if (missed !== 0) {
    throw new Error("refused: nonzero unflagged misses need a different method");
  }
  const sample = num(unflagged.sample_n, "unflagged sample");
  const frame = num(unflagged.population_n, "frame population");
  if (sample > frame) {
    throw new Error("refused: sample exceeds frame population");
  }
  const upper = zeroEventUpper95(sample);
  const statedUpper = num(unflagged.harm_fraction_upper_95, "stated upper bound");
  if (Math.abs(upper - statedUpper) > 1e-9) {
    throw new Error("refused: upper bound does not recompute");
  }
  const lower = caught / (caught + upper * frame);
  const statedLower = num(
    (bundle.weighted_recall_interval ?? {}).lower_95,
    "stated lower bound",
  );
  if (Math.abs(lower - statedLower) > 1e-6) {
    throw new Error("refused: lower bound does not recompute");
  }
  return { verdict: "EXPLORED", harmCaught: caught, lowerBound: lower };
}

export async function readGateReceipt(url) {
  return readFile(url, "utf8");
}
