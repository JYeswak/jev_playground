# prevalence-first skill — SPEC (jev-vbh.6, P1)

The skill forces the base-rate question **before any Jev question is written
or quoted**: what does always-answering-the-majority score on this set?

## The mandatory output order

Every verdict the skill produces MUST be preceded, in this order, by:

1. **prevalence cell** — the near-threshold count: how many scores fall within
   ±`NEAR_WINDOW` (0.1) of the threshold (0.5). A verdict decided by 0.04 is a
   verdict the threshold made, not the model.
2. **near-threshold column / own-constant bar** — the majority-label score:
   `best = max(alwaysYes, alwaysNo)` over the set's own truth labels, i.e. what
   a constant classifier achieves without any model call.
3. **verdict, computed last** — via `gradeQuestion` in
   `work/jev-client/measure-kit.mjs` (never hand-claimed):
   `DEGENERATE` if the question says the same thing on every case, else
   `DISCRIMINATES` iff `correct > best_constant + near_threshold_count`,
   else `WEAK`.

`work/jev-prevalence-first/prevalence-check.mjs` enforces this in code: the
near count and the constant bar are computed and printed first; `gradeQuestion`
is called last, and a drift assertion (`local near === kit near`) refuses to
print a verdict if the two arithmetics ever diverge again.

## Authored-vs-real labeling rule

- **Labels are read from diffs BEFORE any score is seen.** The Unit-2 receipt
  (`docs/demos/upstream-repro/commit-judge-31-20260919.md:4-5`) records truth in
  `work/omp-jev-commit/labels-31.json` (30 recent commits + 48eecdf, the known
  swept-package case) prior to scoring.
- **Authored traffic is not independent of the judge's authors.** The corpus is
  our own commits, written by us — NO-CLAIM on transfer (receipt lines 37-39:
  one reader's labels, 31 commits, one session, one model version). A verdict on
  authored traffic gates authored traffic only.
- **Real traffic needs its own denominator.** The bead acceptance names it:
  `harvest-allowed.mjs` regenerates the real-command denominator (77,767), and
  the skill's checklist prints the majority-label score for the set before any
  Jev call is made.

## Why (observed defect, not taste)

- The commit judge said `describes` yes on 31/31 against a 30/31 always-yes
  constant (`commit-judge-31-20260919.md`, `0befea4`) — DEGENERATE.
- Jev fires on 1.90% of real traffic while the old regex fired on 0.036% and
  was wrong all 28 times (`judge-seat-ruling-20260920.md`, `6830ce2`).
- The learnings pass says the five-minute constant check kills bad question
  sets on day one (`commit-learnings-20260920.md`, `bf12406`).

## Proof commands per pass

- P2 (offline): `node --test work/jev-prevalence-first/prevalence-check.test.mjs`
  — 3 arms: unanimous (constant 1.0 → DEGENERATE), skewed (→ DISCRIMINATES),
  one-item-margin-with-near (→ WEAK).
- P3 (recorded): `node work/jev-prevalence-first/p3-commit-31.mjs` — re-orders
  the Unit-2 receipt (near, constant, verdict) from committed truth labels plus
  receipt-recorded scores. Zero Jev calls.
- P4 (live base rates): `bv --robot-triage` (actionable/total + timestamp) and
  §19 0/20 promoted (`0a3bd5f`), both appended to `BASE-RATES.md` with
  timestamps — live-and-moving, not pinned.
