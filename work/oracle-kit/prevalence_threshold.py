#!/usr/bin/env python3
"""Prevalence-conditioned Bayes threshold t*(π). Frozen priors only.

PREREGISTERED 2026-09-20, before any print. Receipts (do not invent π):
  docs/demos/upstream-repro/prevalence-retrofit-20260919.md
  docs/demos/upstream-repro/dcg-block-rate-prior-20260919.md
  docs/demos/upstream-repro/math-and-next-level-20260919.md §1.2 / §4(b)

Math:
  t*(π) = L_FP (1-π) / (L_FP (1-π) + L_FN π)
  FP/TP ≈ (1-π) FPR / (π TPR)

NO-CLAIM: does not invent a population π for jev-review or skillranker.
Does not retune a live hook. Does not promote anyone.
"""
from __future__ import annotations

import sys

# --- frozen priors (committed receipts). Integers only; ratios computed. ---
FOREMAN_POS = 30
FOREMAN_N = 186449
# Retrofit operating-point identity: 80% recall → ~24 TP vs ~55,791 FP ≈ 1:2300
FOREMAN_TPR = 0.80
FOREMAN_TP = 24
FOREMAN_FP = 55791

DCG_BLOCK = 488
DCG_ALLOW = 49661
DCG_N = DCG_BLOCK + DCG_ALLOW  # 50149

# Declared losses BEFORE printing. Binary act/pass. c_A is the abstain cost.
# Signed set we would actually consider for a nag-vs-miss trade.
SIGNED = ((1, 1, 0.5), (1, 2, 0.5), (10, 1, 0.5))


def t_star(pi: float, l_fp: float, l_fn: float) -> float:
    if pi <= 0.0 or pi >= 1.0:
        raise ValueError(f"no Bayes threshold at pi={pi}: both classes required")
    if l_fp <= 0 or l_fn <= 0:
        raise ValueError("losses must be positive")
    denom = l_fp * (1.0 - pi) + l_fn * pi
    return (l_fp * (1.0 - pi)) / denom


def implied_ratio(t: float, pi: float) -> float:
    """L_FN / L_FP implied by a shipped threshold at prior π."""
    if t <= 0.0 or t >= 1.0:
        raise ValueError(f"threshold {t} is not an interior Bayes cut")
    return ((1.0 - t) / t) * ((1.0 - pi) / pi)


def main(argv: list[str]) -> int:
    selftest = "--selftest" in argv
    errors: list[str] = []

    pi_foreman = FOREMAN_POS / FOREMAN_N
    pi_dcg = DCG_BLOCK / DCG_N
    negs = FOREMAN_N - FOREMAN_POS
    fpr_from_quote = FOREMAN_FP / negs
    fp_tp = FOREMAN_FP / FOREMAN_TP
    fp_tp_identity = ((1.0 - pi_foreman) * fpr_from_quote) / (pi_foreman * FOREMAN_TPR)

    print("prevalence_threshold — frozen priors only")
    print(f"  foreman pi = {FOREMAN_POS}/{FOREMAN_N} = {pi_foreman:.8f} ({100 * pi_foreman:.4f}%)")
    print(f"  dcg     pi = {DCG_BLOCK}/{DCG_N} = {pi_dcg:.8f} ({100 * pi_dcg:.4f}%)")
    print()
    print("1:2300-class identity (quoted 24 TP vs 55,791 FP at 80% recall):")
    print(f"  FP/TP = {FOREMAN_FP}/{FOREMAN_TP} = {fp_tp:.3f}  (~1:{fp_tp:.0f} ≈ 1:2300)")
    print(f"  FPR recovered from that quote: {FOREMAN_FP}/{negs} = {fpr_from_quote:.6f}")
    print(f"  (1-π)FPR/(π TPR) = {fp_tp_identity:.3f}  (must equal {fp_tp:.3f})")
    if abs(fp_tp_identity - fp_tp) > 1e-9:
        errors.append("FP/TP identity does not recover 55791/24")

    print()
    print("t*(π) at declared losses (L_FP, L_FN, c_A):")
    t_f = t_star(pi_foreman, 1, 1)
    print(f"  foreman  L_FP=L_FN=1  c_A=0.5  t* = {t_f:.8f}  (= 1-π = {1 - pi_foreman:.8f})")
    if abs(t_f - (1.0 - pi_foreman)) > 1e-12:
        errors.append("equal-loss t* is not 1-π")

    for l_fn in (1, 10, 100):
        t = t_star(pi_dcg, 1, l_fn)
        print(f"  dcg      L_FP=1 L_FN={l_fn:<3} c_A=0.5  t* = {t:.8f}")

    print()
    # planted: π=0.5 recovers t* = L_FP / (L_FP + L_FN)
    t_half = t_star(0.5, 1, 1)
    t_half_2 = t_star(0.5, 1, 3)
    print(f"planted: pi=0.5 L_FP=1 L_FN=1 → t* = {t_half:.3f} (want 0.500)")
    print(f"planted: pi=0.5 L_FP=1 L_FN=3 → t* = {t_half_2:.3f} (want 0.250)")
    if abs(t_half - 0.5) > 1e-12 or abs(t_half_2 - 0.25) > 1e-12:
        errors.append("pi=0.5 did not recover L_FP/(L_FP+L_FN)")

    # planted: π=0 refuses
    refused = False
    try:
        t_star(0.0, 1, 1)
    except ValueError as exc:
        refused = "both classes required" in str(exc)
        print(f"planted: pi=0 refuses ({exc})")
    if not refused:
        errors.append("pi=0 did not refuse")

    print()
    print("shipped cuts are not Bayes under the signed triples at these priors:")
    for name, pi, shipped in (("foreman", pi_foreman, 0.80), ("compaction-needed~0.90", 0.90, 0.50)):
        implied = implied_ratio(shipped, pi)
        near = []
        for l_fp, l_fn, _c in SIGNED:
            t = t_star(pi, l_fp, l_fn)
            if abs(t - shipped) < 1e-6:
                near.append((l_fp, l_fn, t))
        print(f"  {name}: shipped {shipped:.2f} ⇒ implied L_FN/L_FP = {implied:.1f}")
        print(f"           signed triples t* = " +
              ", ".join(f"({l_fp},{l_fn})→{t_star(pi, l_fp, l_fn):.4f}" for l_fp, l_fn, _ in SIGNED))
        if near:
            errors.append(f"{name} shipped {shipped} matched a signed triple {near}")

    print()
    print("NO-CLAIM: π for jev-review and skillranker stays PREVALENCE-UNKNOWN.")
    print("NO-CLAIM: no live hook retuned. promoted=0 untouched.")

    if errors:
        print("FAIL: " + "; ".join(errors), file=sys.stderr)
        return 2
    if selftest:
        print("prevalence_threshold --selftest: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
