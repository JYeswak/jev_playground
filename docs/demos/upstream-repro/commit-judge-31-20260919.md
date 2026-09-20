# Unit 2: 31 real commits through real Jev — no question discriminates (2026-09-19)

Level: `live` — 31 keyed calls (jev-1.13.0 via askJev), zero transport errors.
Truth: `work/omp-jev-commit/labels-31.json`, read from diffs BEFORE scores were seen
(30 recent commits + 48eecdf, the known swept-package case).

## Per-commit table

Full rows in the run output (score/said/truth/HIT per question). Tallies:

- describes: 30/31, but yes on 31/31 — including 0.78 on 48eecdf (truth F).
- overstates: 17/31, yes on 14/31 — all 14 are FPs on accurate receipt-messages.
- omits: 28/31, yes on 2/31 — both FPs (d1f251c 0.50, 0d36407 0.66).

## Disagreement set (the rows that matter)

- 48eecdf (swept route package under a foreman subject): describes 0.78 MISS,
  omits 0.49 MISS by 0.01. The single most important row — a real omission the
  judge waves through on both questions.
- overstates FPs (judge cries overstatement, human disagrees), worst first:
  74d27ad 0.82, 959c321 0.80, b3551a9 0.77, bdd1c9a 0.76, bb50501 0.73,
  d2e815c 0.67, 7e34898 0.65, 1d4e0c8 0.64, 3097181 0.64, 033d61f 0.61,
  1f1cf55 0.61, 0d36407 0.61, cbd1d60 0.56. Fourteen of thirty-one: on
  receipt-style traffic the overstates question is a nag stream.
- omits FPs: d1f251c 0.50, 0d36407 0.66.

## Constant baselines and kit verdicts

- describes: always-yes 30/31. Kit: DEGENERATE (same verdict everywhere).
- overstates: always-no 31/31. Kit: 17/31 vs 31 → WEAK.
- omits: always-no 30/31. Kit: 28/31 vs 30 → WEAK (near count 4 included).

No question beats its own constant. The judge does not hold on real commits; the
hand-built describes 0.11/omits 0.92 that earned its seat does not transfer. Unit 3
is therefore a refusal, filed separately.

NO-CLAIM: the corpus is our own commits, written by us — not independent of the
judge's authors. Labels are one reader's (mine), from diffs, before scores. 31
commits, one session, one model version.
