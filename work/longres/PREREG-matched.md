# PREREG — matched-miss comparison (bead jev-dau5)

Frozen 2026-10-02 before any held-2 call. The locked bar rewarded
recklessness (baseline "saves" by dropping 31 needed rows); this answers the
right question instead — and does NOT move the old bar post-hoc (that verdict
stands as reported).

## Fresh slice

150 fresh long results (fit 50 + eval 100), seed 20261007, excluding every
file in corpus.json dev+held. Same >=10k definition, 3-probe labels, same
pool scan. `work/longres/corpus2.json`.

## Method (frozen)

1. Fit baseline size threshold T* on fit-50: smallest T with miss <= 0.04
   (Jev's held-1 rate); ties -> highest T. Tool gate unchanged.
2. Score both on eval-100: Jev Choice (same frozen question/state) + baseline
   at T*. Report miss both arms (Wilson) and savings both arms (drop 100%,
   summarize (len-400)/len, on UNREFERENCED rows only).
3. Decision (preregistered): Jev WINS iff savings_Jev >= savings_baseline on
   eval-100 (both misses reported alongside; a win with higher miss is
   reported as qualified, not clean).
## Reconciliation (prewritten)

0.59M chars = savings summed over the 65 unreferenced HELD-1 rows (sample
total). ~14.5M tok/week = per-row mean scaled to estimated weekly
unreferenced volume. Sample vs population extrapolation — different
denominators; exact arithmetic lands in EVAL.

## Caps

<= 150 Choice calls, $0.012 cap (~$0.005 expected), stop 401/402/403, 20 s
timeout, checkpointed. Runner reads CORPUS/OUT env (defaults corpus.json /
choice-rows.jsonl). NO-CLAIM beyond sampled long results.
