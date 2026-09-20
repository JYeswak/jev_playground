# P2 — queue of 2: close the enum you found, then land everything on main

Unit 3 verified here: `selftest-rung-demotion.sh` 2/2, `selftest-ruling-closure.sh` 4/4, stage 80
now discovers **21** suites, `rung-demotion.sh` reports `40 row(s) checked, none cite live inputs
without as-of`. Your sha `634dcd2` resolves — I checked it, because your own self-correction on
`8a22c35` is now recorded in R47 as a receiver-side practice.

**Both your results were zeros and both were reported honestly**: 40/40 rows uncovered by the
projector (history predates the instrument — correctly NOT backfilled, since a retro-fitted
closure would carry a falsifier nobody committed in advance), and 0/40 demotions (tripwire, not
alarm). Wiring demotion as a **reporter rather than an auto-editor** was the right instinct:
we built the projector *because* parallel hand-maintained files drift, so a second `STATUS.tsv`
writer would have recreated the defect one layer up.

## Unit 1 — one verdict vocabulary

You surfaced it: callbacks speak `DONE|HELD|REFUSE`, `STATUS.tsv` speaks
`CLEARED|HELD|RULED_OUT`. **Two enums for one concept, hand-translated at every callback all
session.** Same class as the missing `receipt` level — a word we lacked, filled by improvisation.

Rule it, do not just implement it:

- Are they genuinely the same axis? `DONE` may mean *"the unit finished"* while `CLEARED` means
  *"the claim survived"* — **if so they are two different things wearing one slot, and the fix is
  to separate them, not to merge them.** That is the likelier truth and I want it argued.
- If they are one axis, pick the canonical set, record the mapping, and make `emit.mjs` accept
  only canonical verdicts so the closure cannot carry the wrong vocabulary.
- If they are two axes, say so in the closure schema: a unit outcome **and** a claim verdict.

**Measure before changing anything**: how many of tonight's callbacks used which word, and did
any translation lose information? If none did, this is cosmetic and **R50 with a trigger is the
right answer**.

## Unit 2 — land it all on main

The branch is ahead again and by this lane's standard none of the closure work has shipped. PR
it. All four checks at your tip, unpiped: `gates.sh`, `lane-status.sh`, `pin-liveness.sh`,
`denominator-sweep.sh`. No force-push.

Lead the PR body with what a reader gets: **a ruling cannot be emitted without a falsifier**, and
`STATUS.tsv` is becoming a projection instead of a hand-maintained parallel file.

`[receipt]` for result commits. Exit codes unpiped. Commit on create. Finish one, fire its
callback, start the next yourself. When the queue drains: `br ready`, claim the highest-priority
bead you did not author.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED|REFUSE>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
