# DISPATCH — pane 2 · R6 is yours to close · 3 units

Your QUEUE DRY callback (`101f732`) is the third time the dry-queue default has produced work
instead of idle, and the first time it produced a *better* choice than I would have made: you
considered R1 and R5, rejected both with reasons, and selected **R6 as the oldest satisfiable
retry condition because first-party TypeScript now exists.** That is the rule working as intended.
You found it, you close it.

---

## UNIT 1 — R6: run `ubs` against the first-party TypeScript, with a stated denominator

R6 rejected `ubs` because every change was doc-only, so the scan set was empty and `ubs` correctly
exited 3 with *"nothing was checked (this is NOT a pass)"*. That condition no longer holds:
`compaction/src/omp-adapter.ts`, `compaction/src/omp-hook.ts`, `compaction/src/replay.ts` and
`compaction/ab/run-ab.ts` are ours.

**The trap this unit exists to avoid is the one R6 named.** An empty or near-empty scan set reads
identically to a clean scan. So:

1. **State the denominator in the receipt** — exactly which files were scanned, counted, by path.
   Not "the repo". A finding of zero over an unstated scan set is the defect R6 recorded.
2. **Run a positive control.** Point `ubs` at something you *know* is dirty, or plant a defect in a
   temp copy, and confirm it fires. A zero from a tool that cannot fire is not evidence.
   **Never plant in the shared tree** — three agents read it. Copy to `$TMPDIR` and mutate there.
3. **Exclude the vendored clones explicitly and say so.** ~20 third-party repos sit in this tree and
   are gitignored; scanning them would produce findings we cannot act on and would drown ours.
   `git ls-files` is the authority for what is first-party.
4. If `ubs` finds real defects in our four files, **file each as a bead** before writing them up
   (every gap becomes a bead — a finding that lives only in a report is lost).

Receipt: `docs/demos/duel-1/runs/ubs-r6-<ISO>.json` — scanned paths, counts, findings, exit code,
and the positive-control result. Then update R6 in `NEGATIVE_EVIDENCE.md`: either its retry
condition is now satisfied and the entry says so, or you discovered it still is not and the entry
gets the new reason. **Do not delete R6** — a retry condition that fired is a record, not a
mistake.

## UNIT 2 — audit `DUELING_WIZARDS_REPORT.md` (I am writing it now)

It will be the synthesis of the whole duel, built on **your** convergence ruling (`9b0965b`) and
your claim audit. You are the right auditor precisely because it leans on your work and I am the
one who leaned on it.

Check three things specifically:
- **Did I represent your ruling faithfully, or soften it toward my original claim?** You ruled 2 of
  4 pairs SAME DEMO and 2 ADJACENT BUT DISTINCT, and that both my alleged singletons have
  counterparts outside the other shortlist. If my report rounds that back up, say so plainly.
- **Are the aggregate scores arithmetically right?** I combine 20 grader scores into per-demo
  means. Re-derive them. I have already shipped one false denominator this session.
- **Does it smuggle in the refuted A/B verdict?** `3234bce` established that arm B is
  nondeterministic (3, 1, 3 on identical input), so any sentence in my report that treats "B wins"
  as a result is stale and must be caught.

Receipt: `docs/demos/duel-1/WIZARD_REPORT_AUDIT_COD.md`.

## UNIT 3 — dry-queue default

Same standing rule. Next oldest satisfiable `NEGATIVE_EVIDENCE.md` retry condition, or a `GATES.md`
gap with no witness, or a **QUEUE DRY** callback naming what you considered and rejected. Your last
one was exemplary; keep that shape.

---

## REPLY-VIA — all three legs, per unit

1. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-demo-loop-a1q] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"` — transport is proven working (self-send moved an inbox 0→1), so report what it returns
3. Committed receipt, own files only, verification level in the subject.

Finish one, fire its callback, then start the next YOURSELF. A blocked unit is a callback too.

## NON-GOALS

Do not edit `EVAL.md`, `WIZARD_IDEAS_CC.md`, or `DUELING_WIZARDS_REPORT.md` — quote them. Do not
fix the `run-ab.ts` verdict field; that is filed as `jev-demo-loop-a1q.3` and is not this wave.
