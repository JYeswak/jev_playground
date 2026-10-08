
# 2026-09-20 — the arc: what we built, what we refused, and why

> Two-minute read for a stranger. Numbers carry denominators; refutations
> outnumber wins 12-to-5 and that is the point. Nothing here is published —
> public is Joshua's call. Detail lives in `NEGATIVE_EVIDENCE.md` (R63–R67),
> `docs/NEEDS.md`, and the receipts cited per row.

## The arc in five beats

1. **Built** a file-type doctrine pack from a 221-repo mirror: five rules
   (`ft-{rs,sh,md,py,json}-doctrine`) injecting hard-won threads once per
   session per file type. Shipped, live-fired in fresh sessions, selftest green.
2. **Measured** it binding **1 time in 75 real edits** (rs 0/25, sh 1/25
   borderline, md 0/25, preregistered bar 20%) — and **disabled all five the
   same day**, reversibly, no file deleted (R64).
3. **Tried the rescue**: gap-conditioned predicates for every surviving
   thread. Zero survivors — unsafe 6 occurrences, newtype 32, oracle 5,
   error 114 with 0/20 bind (R65, R66).
4. **Named the reason**: EXPOSURE, not delivery. A rule pays only when we
   hit the gap it guards, and our gap profile is narrow. The six omp
   builtins already hold the entire shippable Rust surface.
5. **Closed the recursion**: the highest-exposure defect (proxy read as
   quantity) has no detectable signal either — proxies abundant
   (2,315 / 671 / 2,009), bind 0/20 on all three — so review owns it (R67).

## Five measurement errors, each caught, each named

| error | caught by |
|---|---|
| 1-second process/mtime gap read as "missing rules" (all five bound) | re-measurement, reported not re-verified |
| QUIET probe under `repeatMode: once` read as "rule absent" | P3 validation (present-and-suppressed, not missing) |
| 3 days of one repo read as "the fleet barely writes Rust" | Joshua — `rs` is top-two fleet-wide |
| posted body length 6282 read as "body clean" (opened DRAFT-NOT-SUBMITTED) | external review, reported not re-verified |
| 818 `unsafe`-churn commits read as danger (was `forbid` churn; real count 2) | conductor re-measurement with `-S'unsafe {'` / `-S'unsafe fn'` (witnessed in R66, not re-run) |
Three of the five are one shape: a number without its denominator. Every
number in this repo now states one.

## What shipped and stayed

- Four live defect rules with fire/quiet arms, suite 84/0:
  `absence-from-one-probe`, `bash-glob-silenced`, `bash-pipe-exit`,
  `bash-structural-def-search`.
- Power caveat (NEEDS #6, same day as this arc): two of the four are
  shipped-on-underpowered-estimate pending relabel to n=77
  (`absence-from-one-probe`, `bash-structural-def-search`), and
  `bash-callsite-grep-exclusion` was DISABLED — its observed FP 6/20 is
  exactly the 0.30 bar, so no sample size can certify it. BH across the
  family (m=17, q=0.05) changed no decision.
- `scripts/exposure-check.sh` — one-screen exposure with denominators,
  raw-vs-real counts, and a RED arm (would have stopped the 818).
- `consumer-check` (NEEDS #2, `4f04a48`).
- An upstream filing whose repro a second party re-ran (skillranker#4).
- A withdrawal when a synthetic repro failed (R54) — reported, not buried.
- The thread table and doctrine extractions stay on disk: the THREADS were
  never the defect, only the delivery mechanism.

## The boundary for the next agent

Before wiring any skill into a rule, run
`scripts/exposure-check.sh --pattern <gap> [--not <confounder>]` and clear
50 occurrences with denominators. If the class is proxy-shaped, read R67
first — it is closed. If it binds under 20% on 20 hand-labelled real edits,
cut the clause, not the standard.
