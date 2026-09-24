# omp-jev-review applicability gate — the 686-commit draw (bead jev-deep-kit-8q7.6)

- **Draw:** non-merge commits reachable from `02f6c5b~1`
  (`docs/demos/upstream-repro/jev-review-real-diffs-20260919.md:19`,
  added in `02f6c5b`). `git rev-list --no-merges 02f6c5b~1` = **686**,
  not 669 — the receipt's "669" does not reproduce; 17-commit difference
  recorded here, not chased.
- **Method:** (1) `isThinDiff` over all 686 keyless
  (`/tmp/ompfit/draw1.mjs`→`draw686.mjs` logic); (2) live noul
  applicability gate on every substantial diff through the REAL tool path
  (`ompJevReview` + injected diff runner + fake Host, `JEV_SCORE_REGISTER`
  redirected to /tmp so the repo register is untouched); (3) incumbent =
  always-scores (construction: the legacy path scores whenever readDiff
  and ask succeed — no gate existed).
- **Live spend:** 567 gate calls + 125 scoring calls = 692 Jev calls,
  model `jev-1.13.0` on all scored rows. Key via infisical (never printed).

## Numbers

| step | result |
|---|---|
| draw | 686 non-merge commits |
| empty diffs | 0 |
| thin (`isThinDiff`, keyless) | 119 → `applicable:false`, zero Jev calls by construction |
| substantial, live gate | 567: **442 refused, 125 scored** |
| refusal reasons | 439 `low-applicability` + 3 `thin-on-rerun` (see truncation note) |
| refusal noul buckets | 0.0–0.1: 377 · 0.2: 45 · 0.3: 12 · 0.4: 5 (86% at ≤0.1 — confident, not borderline) |
| scored latency | n=125, p50 189 ms, p95 420 ms (as recorded in decision rows) |

## What the gate refuses

File-level: refused diffs touch .md ×410, .json ×112, .tsv ×42;
scored diffs touch .sh ×97, .mjs ×66, .ts ×36. Diff-level code-touch
(.ts/.mts/.mjs/.js/.py/.sh/.rs/.go):
**refused 4/439, scored 118/125.** The gate separates code from
non-code almost perfectly — for a code-review tool, these refusals are
mostly correct behavior, not gate errors.

## Truncation interaction (finding, not bar-moving)

3 census-substantial diffs refused as `thin-diff` at run time: the tool
slices diffs to `MAX_DIFF` 12000 chars (`readDiff`), and truncation can
drop the counted changed lines below 10. Census used full diffs; the tool
sees truncated ones. The bar's `<10 lines` metric is ambiguous across
that slice — recorded, not reinterpreted.

## Verdict: BAR FAILED as written

`notes/deep/w74-bars.md`: "any substantial refusal fails it" — 439
substantial refusals (4 code-touching). Reported honestly; the bar is not
moved. The actionable subset is the 4 code-touching refusals; whether the
bar should be re-tiered to code-touching diffs is a follow-up bead, not
this receipt.

## Boundary

Live calls only for the gate (1 per substantial diff) and scoring where
it applied. No key printed. `thin-diff` refusals spent zero calls.
Incumbent always-scores is a construction argument, not a re-measured
arm. NO-CLAIM: a 78% refusal rate on this repo's history is not a
calibration claim — the draw is docs-heavy by construction.
