# jev-11qz BAR (fixed 2026-10-01, before implementation; bead jev-11qz)

Source: duel COD #1 (work/duel-20261001/WIZARD_IDEAS_COD.md section 1),
bead acceptance. Constraints: frozen Noul question + CUT=0.5, no nimble,
no history pruning, daily cap unchanged (200), memo preserved.

## Serial baseline (live jev-1.13.0, s47b sessions e42fe1b1/bf1c7377, 20-item turns)

walls 2.71s / 2.95s / 3.69s / 4.00s; median ~3.3s.

## WIN iff all hold

1. Recorded-transport replay: every eligible-span decision identical to the
   serial incumbent, and every non-memory byte of the returned prompt
   identical.
2. Fresh live sessions (jev-1.13.0, ~20 uncached memories each):
   median filter wall time <= 1.65s (-50% vs 3.3s serial baseline);
   p95 added latency <= 1.5s; >= 90% of items resolve within the 1.5s budget
   (unresolved keep, logged); daily cap still 200.
3. Planted: a changed source span and an ambiguous (duplicated) span are
   kept, and only the validated recall occurrence is ever removed.
4. Spend stated (live calls bounded, checkpointed per call).

NO-CLAIM: drop precision (held-out bar stands, untouched by this change).
