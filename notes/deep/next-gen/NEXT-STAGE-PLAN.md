# Next stage: from research lane to product loop (pane 1 proposal, 2026-09-25)

This plan is the input to a dueling-idea-wizards run. Joshua, 2026-09-25: *"lets move this out
of repeated testing over and over to actually turning this into something relvant and usable"*.

## Why a change is due (measured, 2026-09-25)

- 2,823 commits in 9 days. 1,015 touch only prose, 446 only the bead store and 213 only ledgers.
  Only 799 (28%) touch any code.
- AGENTS.md grew from 1,214 to 1,862 lines in 8 days. The growth is rules added after incidents,
  and they are enforced by prose.
- The four Jev omp tools have no real consumer. Every recorded call was a test (`jev-ja32`).
- Most recent "losses" were our own harness defects, not Jev: the MiniWoB colour field, the
  comma arm list, OSWorld states over the input limit (71% of R112's loss), a grader leak, and
  today scroll-text scored 18/20 where our copy of the scorer said 20/20.
- Today two preregistrations passed the size and answer-offered checks, but their bar could
  not be met: `jev-jjwt` had at most 2 discordant pairs, and Emerald segment 2 was solved by
  the button prior.
- `oracle-kit` has an anytime-valid e-process (from asupersync), and no live runner uses it.
- README is 54,824 B, 48 B under its limit. It is a ledger, not a quickstart.

## The proposal: five moves, in order

1. **Freeze new surfaces.** Finish what is in flight, and open no new benchmark until moves 2-3
   exist.
2. **One experiment kernel instead of N harnesses.** Its preflight turns rules into refusals:
   - state-size gate, answer-offered check, and bar-reachability check (`jev-1ww3`);
   - grader isolation, and the benchmark's own scorer instead of a copy;
   - hashes of the imported modules;
   - a detached launch that survives a pane restart, and resume;
   - the e-process for anytime-valid stopping;
   - one receipt format.
3. **Consumer first.** Put a measured win in a decision that fires every minute: the tool-call
   gate (78/100 caught at 1/300 false alarms) as an omp pre-hook in shadow mode, logging every
   decision. Fleet traffic becomes the labelled data.
4. **A reusable module for strangers.** `jev-kit` (TS + Python) on top of the official SDK:
   - size preflight, validator, and confidence-gate policies with a named fail-safe side;
   - a fake asker for tests, the kernel, and the omp hook as the example.

   It ships with a 5-minute quickstart that the nightly stranger run proves. The README becomes
   a results table generated from receipts.
5. **Games only in the fast-judge shape.** Jev ranks or prunes options for a planner or search
   (Jev-PUCT) and is never the sole policy.

## Success signals

- One Jev decision runs on real fleet traffic daily, with a measured false-alarm rate.
- A stranger goes from clone to first gated decision in under 5 minutes.
- The code share of commits rises from 28%.
- The next harness bug is caught by a preflight refusal, not by a non-author autopsy.
