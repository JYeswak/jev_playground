#!/usr/bin/env python3
"""Check that every NUMBER a STATUS verdict cites can be opened in the receipt it cites.

WHY THIS EXISTS. `lane-status.sh` proves a cited receipt EXISTS and that its bytes still match the
pinned digest. Both checks pass on `demo-1-route-backtest` — and its receipt does not contain the
number the verdict is named after. Pane 3 found that by hand (scalar-audit-20260918T125247Z.json,
3230032, finding MISPOINTED-RECEIPT-DEMO1): "the number is derivable; the pointer is wrong. Same
defect class as the column just fixed: CONTROL DOES NOT SUPPORT THE CLAIM AS CITED."

Existence and integrity are the wrong questions for that defect. A receipt can exist, hash exactly,
and still not contain the claim — which is the lane's own thesis (open the cited control) applied to
the lane's own state of record. This is the mechanical form of it.

WHAT IT IS NOT. It cannot rule that a number is WRONG, only that it cannot be opened LITERALLY in the
receipt cited for it. A legitimate rounding (0.0447% reported as 0.045%) is reported too, because a
rounded citation is exactly as unopenable as a mispointed one, and which of the two it is requires a
judgement this script must not make. Every hit is a ROW FOR A PANE TO RULE ON, not a verdict.

Single digits are ignored: `4of5` and `T1` are structure, not measurement, and matching them would
fire on every row — the detector that fires on everything discriminates nothing, which was the first
version of lane-status's existence check and was wrong.

EXIT  0 every cited numeral opens in its receipt · 12 at least one does not · 2 usage/environment
"""
import os
import re
import sys
from pathlib import Path

REPO = Path(os.environ.get("JEV_REPO", Path(__file__).resolve().parent.parent))
STATUS = Path(os.environ.get("JEV_STATUS", REPO / "docs/demos/STATUS.tsv"))

# Decimals and multi-digit integers only. See the docstring on single digits.
NUMERAL = re.compile(r"\d+\.\d+|\d{2,}")


def variants(tok: str):
    """Forms that are the SAME citation, not a different claim.

    Thousands separators only. NOT rounding, NOT unit changes, NOT scaling — folding those in would
    let the gate accept a number the receipt does not actually state, which is the whole defect.
    """
    out = {tok}
    if "." not in tok and len(tok) > 3:
        out.add(f"{int(tok):,}")
    return out


def opens(tok: str, blob: str) -> bool:
    """Digit-bounded match. A SUBSTRING TEST IS NOT AN OPENING.

    FOUND BY THIS GATE'S OWN FIRST REAL USE. After pane 3 ruled demo-1's reason should be repriced to
    `0.0447pct`, the hit CLOSED — and it closed for the wrong reason: `0.0447` matched
    `0.044756498000000006`, a PER-TURN DOLLAR AMOUNT in an unrelated field. The number the verdict
    cites is a PERCENTAGE the receipt never states; a coincidental prefix of a different quantity was
    being accepted as the control.

    That is a predicate satisfiable by unrelated text — the seventh instance of that class this lane
    has caught inside its own instruments, and the first one I built the instrument to catch. A digit
    on either side means this is a different number, so the match is rejected.
    """
    return re.search(r"(?<![0-9])" + re.escape(tok) + r"(?![0-9])", blob) is not None


def main() -> int:
    if not STATUS.exists():
        print(f"verify-reason-numerals: missing {STATUS}", file=sys.stderr)
        return 2

    unsupported, checked, rows_with_numerals = [], 0, 0
    for lineno, line in enumerate(STATUS.read_text().splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        if f[0] == "candidate" or len(f) < 10:
            continue
        cand, receipt, reason = f[0], f[5], f[6]
        toks = sorted(set(NUMERAL.findall(reason)))
        if not toks:
            continue
        rows_with_numerals += 1
        p = REPO / receipt
        if not p.is_file():
            # lane-status owns absence; reporting it here too would double-count one defect.
            unsupported.append((cand, receipt, "<receipt absent>", "n/a"))
            continue
        blob = p.read_text(errors="replace")
        for t in toks:
            checked += 1
            if not any(opens(v, blob) for v in variants(t)):
                unsupported.append((cand, receipt, t, reason))

    print("REASON NUMERALS vs CITED RECEIPTS")
    print(f"  rows carrying a numeral: {rows_with_numerals}   numerals checked: {checked}")
    print(f"  variants folded: thousands separators only (rounding is NOT folded, by design)")
    if unsupported:
        for cand, receipt, tok, reason in unsupported:
            print(f"  UNOPENABLE {cand}: '{tok}' does not appear in {receipt}")
            if reason != "n/a":
                print(f"             reason column: {reason}")
        print(f"UNOPENABLE: {len(unsupported)} cited numeral(s) cannot be opened in their receipt.")
        print("A PANE MUST RULE on each: mispointed receipt, rounded citation, or absent measurement.")
        return 12
    print("OK: every numeral cited in a verdict reason appears in the receipt cited for it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
