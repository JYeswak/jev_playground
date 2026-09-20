# MUSE-B delta: two skills added, placeholders fixed (2026-09-20)

## Unit 1 — graph delta

- Verified both WHY cites against the files (not accepted on faith): prevalence
  numbers (commit-judge 31/31 vs 30/31 in `0befea4`'s table; Jev 1.90% vs regex
  0.036%-all-wrong in `6830ce2`) and the register defect (21 packages, one exports
  data, 2,531 calls discarded — `commit-learnings-20260920.md`, `bf12406`).
- `jev-vbh.5` rescoped to Pass 6 only (PRs #9–#15 in #17, #16+#17 merged — the rest
  is shipped; reason recorded in the bead).
- Created `jev-vbh.6` prevalence-first and `jev-vbh.7` silent-register, same
  three-field contract with verified cites.

## Unit 2 — acceptance paths fixed

All `<...-script>` bare filenames replaced with intended repo-relative paths
(`work/omp-jev-compact/compaction-score.mjs`, `work/jev-question-writing/trial.mjs`,
`work/jev-eval-honesty/honesty-check.mjs`, `work/jev-usage-router/trial-choice.mjs`
(existing package), `work/jev-score-register/replay.mjs`), each annotated that the
loop creates it and must list it before depending. vbh.5's house-skill slot is now
an explicit worker-filled parameter with a locate-and-list instruction.

## NO-CLAIM

Bead bodies only; no skill worked yet. Intended paths do not exist until the loops
create them.
