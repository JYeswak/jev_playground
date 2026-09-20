# P3 — non-author review of tonight's four CASS/mail mines

Your honest-idle callback was correct: the graph really is down to a blocked child. But there
**is** in-scope work you did not author — pane 2 produced four rulings tonight and **nobody but me
has checked them.** I verified pieces of each, and I am the one who dispatched them, so my
agreement is same-origin and counts once.

Review these four. You wrote none of them:

1. `docs/demos/upstream-repro/a11-join-yield-20260920.md` — HELD, mail↔cass join, K1 20 paths.
2. `docs/demos/upstream-repro/dig-subset-breakdown-20260920.md` — HELD, the pooled dig BEAT
   (0.058 vs 0.159) **inverts** on `S_wrong_selector` (n=16, 0.500 vs 0.250).
3. `docs/demos/upstream-repro/a12-refusal-result-20260920.md` — REFUSE, refusal fired on the
   slice regex and killed 2 good digs for 2 bad.
4. `docs/demos/upstream-repro/a18-offbus-result-20260920.md` — REFUSE/UNMEASURED, all 20 K1 pairs
   time-disjoint.

## Attack these specifically — finding a defect is the success condition

- **The loss function is doing a lot of work.** `invent-on-y1=1, dig-on-y0=2` is asserted, not
  derived. Does the S_wrong_selector inversion survive a 1:1 loss? At what ratio does it flip
  back? **If the verdict is an artifact of a chosen constant, that is the finding.**
- **`Y` is mechanical** (`cass_dig_y.py`, receipt-shaped / wrong-selector proxy). Sample ~15 rows
  and judge them yourself. If mechanical-Y disagrees with a reading human on the rows that drive
  the inversion, the inversion is about the proxy, not about digging.
- **Slice membership is regex-defined.** Do the five slices overlap? Does a row appear in two?
  Is `S_topical` (n=82) just "everything else"? A residual bucket dressed as a slice would make
  the two winning slices non-independent.
- **A18's disjointness I already reproduced** (mail proj 66 is 2026-08-31→09-01 in MICROseconds,
  cass ws 617 is 2026-06-17→07-27 in MILLIseconds, 35 days apart) — so do not re-derive it.
  Attack instead whether "all 20 pairs disjoint" holds, and whether ±24h was the right window to
  freeze given the eras never meet under any window.
- **A11's K1=20 vs A18's 20 pairs**: same 20? If the join's only usable output is time-disjoint
  from the mail corpus, does A11's HELD still gate A18, or is that gating vacuous?

## Do not

Do not re-run the mines or regenerate the locked export — `exports/cass-dig-rows.jsonl` is pinned
at n=138 and unpinned denominators have drifted on us six times. Read, recompute from the pinned
file, and judge.

## ACCEPTANCE

`docs/demos/upstream-repro/mines-nonauthor-review-20260920.md`: per-mine CONFIRMED / OVERTURNED /
WEAKENED with the command or recomputation that settles each, plus one overall line — **are these
four verdicts safe to publish as the lane's CASS findings?** A clean pass is a real outcome; so
is "the inversion is a loss-function artifact", which would be more valuable.

Do not run formatters or repo-wide gates. Exit codes unpiped. Commit on create.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-MINEREVIEW-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
