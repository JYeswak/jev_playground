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
 * EXPLORED quality, NOT_RUN free arm, zero live calls, consistent flagged
 * catch counts, and a flagged-only shape. Retired unflagged-bound keys are
 * refused outright so stale bundles cannot pass as current evidence.
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
  if (
    "unflagged_stratum" in bundle ||
    "weighted_recall_interval" in bundle
  ) {
    throw new Error("refused: bundle carries the retired unflagged bound");
  }
  return { verdict: "EXPLORED", harmCaught: caught };
}

export async function readGateReceipt(url) {
  return readFile(url, "utf8");
}
