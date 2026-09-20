#!/usr/bin/env python3
"""VOI of paid Jev vs free regex on the frozen harm-rule corpus.

PREREGISTERED losses (declared before any print):
  L_miss = 1     # a planted harm the detector misses
  L_fp   = 10    # a false fire
  c_call = 0.01  # one paid Jev call, in the same units

Frozen identities (other receipts; not re-measured here):
  regex: 12/12 recall, 0/38 FP   — harm-rule-claim-repro-20260919.md
  Jev:   11/12 recall, historical 0/40 FP — same file; FP dens. not like-for-like (R34)

a0 = regex (free). If a(Z) does not beat a0, VOI(Z) ≤ -c_call ≤ 0.

NO-CLAIM: 12 planted harms, not incidents. FP denominators are not like-for-like.
Does not promote. Does not spend a key.
"""
from __future__ import annotations

import sys

L_MISS = 1
L_FP = 10
C_CALL = 0.01

REGEX_TP, REGEX_N_POS = 12, 12
REGEX_FP, REGEX_N_NEG = 0, 38
JEV_TP, JEV_N_POS = 11, 12
# Historical Jev FP denominator is 40; the reproducible regex denom is 38. Do not mix.


def expected_loss(misses: int, n_pos: int, fps: int, n_neg: int, call_cost: float) -> float:
    # Per-positive-case expected miss + per-negative-case expected FP, plus call.
    # Report the sum over the planted-positive slice plus FP count, not a blended π.
    return misses * L_MISS + fps * L_FP + call_cost * (n_pos + n_neg)


def main() -> int:
    e_regex = expected_loss(REGEX_N_POS - REGEX_TP, REGEX_N_POS, REGEX_FP, REGEX_N_NEG, 0.0)
    e_jev = expected_loss(JEV_N_POS - JEV_TP, JEV_N_POS, 0, 40, C_CALL)
    # regex then jev-on-regex-allow: regex already fires on all 12 planted harms,
    # so the paid call never sees a miss the regex missed. a(Z)=a0 on this corpus.
    e_then = e_regex + C_CALL * 0  # jev not invoked on regex-fires; 0 remaining misses
    voi = e_regex - e_jev
    voi_then = e_regex - e_then

    print("VOI sketch — harm-rule frozen corpus")
    print(f"  declared L_miss={L_MISS} L_fp={L_FP} c_call={C_CALL}")
    print(f"  E[L|regex]                    = {e_regex:.4f}   (12/12, 0/38, free)")
    print(f"  E[L|jev]                      = {e_jev:.4f}   (11/12, 0/40 hist., +c_call on 52)")
    print(f"  E[L|regex then jev-on-allow]  = {e_then:.4f}   (a(Z)=a0; no remaining miss)")
    print(f"  VOI(jev vs regex)             = {voi:.4f}")
    print(f"  VOI(regex-then-jev vs regex)  = {voi_then:.4f}")
    if voi > 0 or e_then < e_regex:
        print("UNEXPECTED: paid Jev beat free regex on this corpus", file=sys.stderr)
        return 2
    print("  VOI of paid Jev ≤ 0 vs free regex on this frozen corpus")
    print("NO-CLAIM: 12 planted harms, not incidents. FP dens. not like-for-like (R34).")
    print("NO-CLAIM: not a promotion. promoted=0 untouched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
