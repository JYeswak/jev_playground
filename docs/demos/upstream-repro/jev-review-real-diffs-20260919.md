# jev-review ordering on real diffs: RULED_OUT (AUC 0.625 < 0.75 bar)

Pane 3 (muse), 2026-09-19, non-author clearance (pane 1's 12/12 on authored
pairs does not count). Harness: `work/p3-calibration/draw.py` (future labels),
`score_review.py` (Score 0-10 expected value + testfile feasibility noul);
outputs `review_scores.jsonl` (committed). Pinned `work/pysdk` env. 22 live
requests, `jev-latest` -> `jev-1.13.0`, run once.

## Preregistered bar (verbatim from the unit brief)

Over >= 20 real commits with >= 6 in the worse class, ADOPT if AUC >= 0.75
separating later-corrected commits from surviving ones. Feasibility
("does this diff touch a test file") through the same pipeline, both classes
present, under 0.80 = HARNESS BLIND, no verdict. Prevalence + usability check
required.

## Draw (no vignettes, no taste)

669 non-merge commits mined with `rg`/`git log`: WORSE = shares a non-ledger,
non-docs code file with a LATER fix/correct/revert/bogus/wrong/supersede/
mistake commit (64 candidates with code overlap, e.g. fcdeca3<-51b147a sharing
oracle.mjs); BETTER = rank>40 from HEAD with zero later-fix code overlap.
Author's own 17 commits excluded win-or-lose. Picked 8 worse + 14 better.
Scores cluster 5.89–7.94, matching pane 1's "absolute scores uncalibrated".

## Result

```
QUALITY AUC=0.625 (better n=14 mean 7.33, worse n=8 mean 7.20)
FEAS AUC=0.939 (n_pos 3/22 — thin but both classes present, bar cleared)
```

Lowest score in the set is fcdeca3 (5.89, the overturned ADOPT) — directionally
right, but the classes overlap almost fully. Prevalence: n/a (constructed
balanced draw, not a population sweep — stated, unlike the foreman case).

## Verdict: RULED_OUT

Bar missed (0.625 < 0.75) with a working arm (feasibility 0.939). No threshold
moved. Two readings, both stated: (1) quality-scores don't separate
later-corrected from surviving commits in this history; (2) the worse-label is
noisy — a later fix touching the same file does not prove the earlier commit
was low quality (it may have been good and later improved), so 0.625 may
UNDERSTATE true quality-discrimination. Reading (2) is a caveat, not a rescue:
a noisier label makes any AUC harder to earn, and it was earned nowhere near
the bar.

## NO-CLAIM

"Later corrected" is a file-overlap proxy for quality, not ground truth; one
repo, one day, one model version, one run each; absolute scores uncalibrated
(confirming pane 1); my 17 commits excluded, stated above.
