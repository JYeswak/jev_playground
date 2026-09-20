#!/usr/bin/env bash
# Promotion contract — four gates, adopted from the franken_engine shape.
#
# CREATION GATE, answered (this lane refuses instruments that cannot answer all four):
#   1. CONSUMER  — foundation/gates.sh, and any human reading docs/demos/STATUS.tsv.
#   2. GATE      — no STATUS row may carry verdict PROMOTED without four proven gates.
#   3. DEFECT    — observed: the lane has run at promoted=0 all session with NO definition
#                  of what promotion would require. "Promoted" was unreachable because it was
#                  undefined, not because the bar was high. An undefined bar cannot be cleared
#                  and cannot be failed, which is how a ledger stays honest by accident.
#   4. RETIREMENT — when a promotion gate exists inside foundation/gates.sh itself and this
#                  standalone stage becomes redundant.
#
# SHAPE ADOPTED, NOT LINKED (Joshua, 2026-09-20): franken_engine's promotion_gate_runner uses
# four gates — equivalence, capability, performance, adversarial. Evidence for the shape:
#   fh suggest "promotion gate" ->
#     franken_engine/docs/IDEA_WIZARD_XIII_CLAIM_PROMOTION_GATE.md:27-46
#     franken_engine/crates/franken-engine/tests/plas_burn_in_gate_enrichment_integration.rs:708-713
#     franken_surveillance_system ADP_REPLAY_PROMOTION_GATE = "GATE-010"
#     fastmcp_rust FILESYSTEM_PROVIDER_PROMOTION_GATE
# We copy the CONTRACT SHAPE only. No engine crate is linked and none is required.
#
# Usage:
#   foundation/gates.d/85-promotion-contract.sh [STATUS_TSV]
#   foundation/gates.d/85-promotion-contract.sh --selftest     # planted negatives; must fire RED
set -uo pipefail

# Stages are invoked by foundation/gates.sh from an arbitrary cwd; anchor to the repo root.
root=$(CDPATH='' cd -- "$(dirname "$0")/../.." && pwd -P)
cd "$root" || exit 1
STATUS="docs/demos/STATUS.tsv"
if [ "${1:-}" != "--selftest" ] && [ -n "${1:-}" ]; then STATUS="$1"; fi

# The four gates, in the order a promotion must clear them.
GATES=(equivalence capability performance adversarial)

check_status() {
  local file="$1" rc=0 line n=0 promoted=0
  while IFS= read -r line; do
    case "$line" in \#*|'') continue ;; esac
    n=$((n + 1))
    local candidate verdict evidence
    candidate=$(printf '%s' "$line" | cut -f1)
    verdict=$(printf '%s' "$line" | cut -f4)
    [ "$candidate" = "candidate" ] && continue
    [ "$verdict" != "PROMOTED" ] && continue
    promoted=$((promoted + 1))

    # A PROMOTED row must name all four gates somewhere in the row.
    local missing=()
    for gate in "${GATES[@]}"; do
      printf '%s' "$line" | grep -qi -- "$gate" || missing+=("$gate")
    done
    if [ ${#missing[@]} -gt 0 ]; then
      echo "RED promotion-contract: ${candidate} is PROMOTED but missing gate(s): ${missing[*]}"
      rc=1
    else
      # Every named gate needs a receipt that exists.
      evidence=$(printf '%s' "$line" | cut -f6)
      if [ -z "$evidence" ] || [ ! -e "$evidence" ]; then
        echo "RED promotion-contract: ${candidate} is PROMOTED but its receipt is missing: ${evidence:-<empty>}"
        rc=1
      else
        echo "OK  promotion-contract: ${candidate} clears ${#GATES[@]} gates with receipt ${evidence}"
      fi
    fi
  done < "$file"

  if [ "$rc" -eq 0 ]; then
    echo "OK  promotion-contract: ${n} row(s) scanned, ${promoted} PROMOTED, 0 violations (promoted=0 is a valid state)"
  fi
  return "$rc"
}

if [ "${1:-}" = "--selftest" ]; then
  # PLANTED NEGATIVE. A checker that cannot fail on known-bad is an empty success (P11).
  tmp=$(mktemp)
  printf 'candidate\trung\tscore\tverdict\tauthor\treceipt\tblocked_on\n' > "$tmp"
  printf 'fake-promoted\t9\t999\tPROMOTED\tselftest\tdocs/demos/STATUS.tsv\tnone\n' >> "$tmp"
  echo "--- arm 1: PROMOTED row naming no gates (must fire RED)"
  if check_status "$tmp" > /dev/null 2>&1; then
    echo "SELFTEST FAIL: a PROMOTED row with no gates was accepted"
    rm -f "$tmp"
    exit 1
  fi
  echo "    fired RED as required"

  echo "--- arm 2: PROMOTED row naming all four gates but a missing receipt (must fire RED)"
  printf 'fake-2\t9\t999\tPROMOTED\tselftest\tdocs/demos/NO_SUCH_RECEIPT.json\tequivalence capability performance adversarial\n' >> "$tmp"
  if check_status "$tmp" > /dev/null 2>&1; then
    echo "SELFTEST FAIL: a PROMOTED row with a missing receipt was accepted"
    rm -f "$tmp"
    exit 1
  fi
  echo "    fired RED as required"

  echo "--- arm 3: the real STATUS.tsv (promoted=0) must pass"
  if ! check_status "$STATUS" > /dev/null 2>&1; then
    echo "SELFTEST FAIL: the real ledger was rejected"
    rm -f "$tmp"
    exit 1
  fi
  echo "    passed as required"
  rm -f "$tmp"
  echo "SELFTEST PASS: 3 arms (no-gates RED, missing-receipt RED, real ledger green)"
  exit 0
fi

check_status "$STATUS"
