# 2026-09-20 — the arc: what we built, what we refused, and why

> Two-minute read for a stranger. Numbers carry denominators; refutations
> outnumber wins and that is the point. Nothing here is published — public is
> Joshua's call. Detail lives in `NEGATIVE_EVIDENCE.md` (R63–R70),
> `docs/NEEDS.md`, and the receipts cited per row.

## The headline

**We ran a paid probabilistic API against deterministic baselines across every
candidate seat we could construct, preregistered the bars before computing n,
and certified zero seats.** The last survivor — a low-noul veto on semantic
rows, 3/6 against a baseline at 0/6 — was retired on arithmetic: at p̂ = 0.50
the Wilson lower bound converges to 0.50 **from below** and never reaches it
(n=100,000 → 0.4969), so the required n is **infinite**. McNemar is invalid at
those cell counts; the exact conditional binomial gives b=3, c=0 → **p=0.25**.
Honest arrival rate of new labelled semantic rows: **0/week** (R69).

That is not a claim about Jev in general, or about corpora unlike ours. It is:
at this fleet's exposure profile and labelling rate, **nothing we tested
certifies.** The surviving artifact is the *necessity gate as process* — run a
deterministic baseline on identical rows first. It has ruled four times and
cost nothing.

**And the same arithmetic killed our own work.** By day's end **eight of the
rules we shipped today were disabled by their own statistics**: five `ft-*`
(0/75 bind), `bash-callsite-grep-exclusion` (FP 6/20 — p̂ *is* the 0.30 bar, so
n=∞), and `absence-from-one-probe` (relabelled to n=77: FP 21/77 = 0.2727,
Wilson [0.186, **0.381**] — the point estimate cleared the bar and the interval
did not). One rule remains live and **uncertified**.

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

## Measurement errors, each caught, each named

| error | caught by |
|---|---|
| 1-second process/mtime gap read as "missing rules" (all five bound) | re-measurement, reported not re-verified |
| QUIET probe under `repeatMode: once` read as "rule absent" | P3 validation (present-and-suppressed, not missing) |
| 3 days of one repo read as "the fleet barely writes Rust" | Joshua — `rs` is top-two fleet-wide |
| posted body length 6282 read as "body clean" (opened DRAFT-NOT-SUBMITTED) | external review, reported not re-verified |
| 818 `unsafe`-churn commits read as danger (was `forbid` churn; real count 2) | conductor re-measurement with `-S'unsafe {'` / `-S'unsafe fn'` (witnessed in R66, not re-run) |
| 19/19 instruments read as "ZERO CONSUMERS" | uniformity treated as symptom, not quantity — 2 refuted by direct probe in one minute (R68) |
| a disable reported done that had **not taken** — verified by probe silence | enumeration in both scopes; the `repeatMode: once` trap **recurring after being documented above** |

Three of the first five are one shape: a number without its denominator. Every
number in this repo now states one.

**The seventh row is the one that matters.** A trap written down in this very
table recurred hours later, in a different pane, on a different rule.
**Documenting a failure mode does not prevent it — only a mechanical check
does.** That is why every disable now requires enumeration in both scopes, and
why the submit hold became a draft-bound single-use token after failing open
twice in one day.

## Two audits found the same bias on independent axes

- **Power** (NEEDS #6): we *refused* with adequate power (0/25 → CI upper
  0.137, cleanly below a 0.20 bar) and *shipped* with inadequate power (4/20 →
  CI upper 0.437 against a 0.30 bar). Benjamini–Hochberg across the family
  (m=17, q=0.05) changed no decision.
- **Provenance** (R70): our **kills** persisted row identities
  (`pane‖session-file‖line-offset → label`, re-openable by a third party); our
  **ships** persisted none. Three rules went live system-wide on numbers nobody
  can audit.

Same direction both times: **rigor applied where it blocked action, relaxed
where it permitted action.** Invisible from inside any single decision — every
individual call looked reasonable, which is why it took two separate audits.

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
