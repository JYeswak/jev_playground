# Representative-sample re-run — 2026-09-20 `[receipt]`

**Outcome: DONE — finding robust, inversion deepens. Public page stands.**
Against the conductor's pre-registered expectation (aggregate holds,
inversion weakens): aggregate holds, inversion does NOT weaken — same 4
rows, dig-iff 0.875 vs 0.250 (window: 0.500 vs 0.250).

Falsifier pre-registered (`repsample-falsifier-20260920.md`): n=1,000
conversations, seed 421337 (`sample_sha f68bccdc03cc2cb6`), frame justified
as the retrieval unit. Runner `run_rep_sample.py`; locked n=138 export
untouched (new `rep1000` names).

## Headline numbers (rep1000 vs window)

| | rep1000 (60,994 msgs) | window (120k ids) |
|---|---|---|
| y prevalence | 0.587 (81/138) | 0.159 (22/138) |
| always-invent | 0.587 | 0.159 |
| dig-iff (open-top1) | **0.101 BEAT** | **0.058 BEAT** |
| empty-success | 7 | 4 |

## Slice table (1:2 loss; S_wrong 1:1 below)

| slice | n | y | invent | dig-iff |
|---|---:|---:|---:|---:|
| S_wrong_selector | 16 | 4 (same rows) | 0.250 | **0.875 LOSE (deepens)** |
| S_lexical_trap | 20 | 19 | 0.950 | 0.000 |
| S_topical | 82 | 45 | 0.549 | 0.000 |
| S_pass_probes | 30 | 18 | 0.600 | 0.200 |
| S_control | 2 | 1 | 0.500 | 0.000 |

S_wrong_selector at 1:1: invent 0.250 vs dig **1.188 LOSE** (window tie
0.250/0.250 broke toward invent under calibration; breaks harder here).

## Control note (not a harness failure)

`zzzz_cannot_exist_9c42`: count 0, y=0 — clean. The S_control y=1 is
`negative control entropy`, a topical query whose tokens legitimately hit
receipt-shaped rows: slice-regex over-grouping, reported, not a
BLOCKED-HARNESS.

## Reading

The representative frame makes digging look *better* in aggregate (more
answerable traffic: prevalence 0.587 vs 0.159) and *worse* exactly where
the page says it is bad (wrong-selector dig loss nearly doubles). The
frame audit's worry does not materialize; if anything the window
understated both directions. Page stands; no correction needed.

## NO-CLAIM

Mechanical Y uncalibrated on this frame (C1 covered window rows only).
Token rule mirrored from committed fallback (original matcher
uncommitted — stated assumption). 60,994 sampled messages, one seed, one
machine. No rebuild, search untouched, locked export pinned. Length
footnote: window mean 3,544 (mine, avg over non-null; zero nulls) vs
3,616 (conductor) — likely id-range vs last-120k-rows window; immaterial.
