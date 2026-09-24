# jev-deep-kit-8q7.8 receipt — structured criteria variant (2026-09-23, pane 4 MistyTurtle)

Bead `jev-deep-kit-8q7.8`. Bar in `notes/deep/w74-bars.md` (TopazRaven,
committed before any live call — do not move it): {what,includes}+focus
matches-or-beats the current shape on the held-out lingspam split by logreg
OOF AUROC; fails on any regression or on gain in the focus-free negative.

Prevalence, before any labelled live call
(`node work/jev-prevalence-first/prevalence-check.mjs
work/jev-question-writing/w74-lingspam-split.jsonl --truth label`, exit 0):

```
set: /tmp/w74-split.jsonl rows=580 labelled=580
own-constant: always-ham 483/580 (majority share 83.3%)
verdict: DEFERRED — no model scores; a question on this set must beat always-ham 483/580
```

Split: lingspam parts 9+10 (580 rows, 97 spam, 16.7%), frozen in
`work/jev-question-writing/w74-lingspam-split.jsonl` before any call. Shapes
fixed verbatim (zero fitting in this build), so no leakage channel exists
from row reuse; OOF folds hold out within the comparison. Variant =
`spam_structured_focus` (spam_noul.py:137-144, SPAM_BOUNDARY :110-132);
incumbent = `spam_generic_criteria` (spam_noul.py:56-64); focus-free =
`spam_plain` ± focus sentence. Sanctioned caller `askJevBundle`
(accepts typed question objects; `askJev` takes strings only and would have
silently dropped the criteria — checked work/jev-client/src/index.ts:65,431).
Smoke (2 rows): all four shapes numeric, model jev-1.13.0 — Noul criteria
maps score 200 (curate-422 risk cleared for this shape).


## Results (2026-09-23, model jev-1.13.0, 580 rows × 4 shapes, 580 bundle calls + 2 smoke)

Latency p50 169ms / p95 415ms. Cost unstated (usage not captured — NO-CLAIM).
Scores: `/tmp/w74-main.jsonl` (rows), analysis `/tmp/w74-oof.py` (port of
spam_noul.py:333-343, 5-fold StratifiedKFold OOF on logit scores).

| shape | acc | OOF AUROC |
|---|---|---|
| current (generic criteria) | 0.8741 | 0.9884 |
| variant (structured+focus) | 0.9190 | 0.9848 |
| plain (bare, reference only) | 0.9603 | 0.9972 |
| plain_focus (negative arm) | 0.9414 | 0.9904 |

Gap variant−current: −0.0035 at fold seeds 0, 1, 2 (−0.0035/−0.0034/−0.0034:
stable, not fold noise). Focus-free gain (plain_focus−plain): −0.0068 —
no gain, negative arm passes.

Post-run prevalence verdicts
(`--score <shape> --truth label --positive spam`, both exit 3):
variant 533/580 vs 483+72 → WEAK; current 507/580 vs 483+49 → WEAK.
Neither beats constant+near; the variant pays more for uncertainty
(72 near rows vs 49).

## Verdict: FAIL vs the bar

The bar requires match-or-beat on OOF AUROC with no regression. −0.0035 is
a regression, stable across three fold seeds. The bar is not moved.
Secondary, not chased: the bare question outranks both structured shapes
here (0.9972), and accuracy order (variant +4.5pp) disagrees with AUROC
order — both recorded for a future unit, not this one.

## Boundary

One split (parts 9+10), one model version, single run per arm. The clone
author's "1000 mistakes" may overlap this split — both shapes face the same
rows and neither was tuned here, but overlap would favor the variant, which
still lost. Usage/cost not captured. No Rust (RCH note n/a).
