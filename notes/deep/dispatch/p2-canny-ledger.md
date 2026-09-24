# Pane 2 (RedMaple) — adopt Canny's deterministic ledger as an omp surface in jev

From pane 1 AmberWillow, after `CALLBACK-P2-W70-NEW10-DONE` (`40133aa`). Rules as in
`notes/deep/dispatch/wave-back-on-road.md`.

## Why

Your W7.0 run on Canny: its Jev `claims_done` judgment was right on 9 of 24 real turns, below
always-not-done at 12 of 24 (`docs/demos/upstream-repro/Canny-w70-20260923.md`). The part that
survived is the deterministic ledger ("facts block, judgments only relax": a done-claim is blocked
unless a verify command passed after the last edit, `Canny/src/hook.ts:246-253`). That is exactly our
own failure: agents here say "done" and close beads without a passing check after their last edit.
Mission stages two to four: build the tool from what survived, put it on an omp surface, dogfood it.

## Unit

1. **Measure first.** Score the ledger rule alone (no Jev) on your same 24 labelled turns, and on a
   larger set: label 100+ finished turns from jev's own session transcripts by the same rule you used
   (done iff a verify command passed after the last edit). Run `skill://prevalence-first` on the
   labels and paste its lines. The ledger must beat always-not-done; if it does not, stop and say so.
2. **Build it on an omp surface** in this repo, smallest honest version: a Stop-time check that, when
   the final assistant message claims completion and no test or verify command succeeded after the
   last edit or write tool call in that turn, injects a one-line reminder naming the missing check.
   Advisory, never blocking. Decide the seam (`.omp/hooks/post/`, an extension, or a rule) from
   `omp://hooks.md` and the existing `.omp/hooks/post/session-stop.ts`; extend that hook rather than
   adding a second one if it fits. Tests (L0) with an injected transcript: claims-done-without-check
   fires, claims-done-with-check is silent, no-claim is silent.
3. **L3:** show it firing in a real omp session on a planted bad turn and staying silent on a good
   one, frames pasted. Record calls-per-session cost: zero, since it makes no Jev call.
4. Bead (`br create`, WHAT/WHY/ACCEPTANCE, parent `jev-deep-kit-8q7`, label `jev,w74`), `TESTS.md` row,
   `GATES.md` row if it gates anything, receipt, push. Ask pane 4 or 6 to verify before close.

Also: close `jev-deep-kit-8q7.9` with the command-and-result reason once pane 5 or 6 has appended
your EVAL sections (`notes/deep/w70-eval-sections-p2-new10.md`), or append them yourself if
`EVAL.md` is free. The jev-curate issue draft stays unfiled; filing it is Joshua's call.

Callback `CALLBACK-P2-CANNY-LEDGER-DONE`.
