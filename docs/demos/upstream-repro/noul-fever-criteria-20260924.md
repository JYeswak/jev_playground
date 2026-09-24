# Does the SciFact criteria lift replicate on FEVER? Criteria ablation, same 400 claims (bead `jev-5jp`)

ScoreSST5 (background agent of pane 1, AmberWillow), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Question.** On SciFact, Noul outcome criteria `{true, false}` lifted claim verification by the
preregistered rule, and only in probability quality: Brier −0.0065 with the decisions unchanged (bead
`jev-k2q`, `noul-scifact-criteria-20260924.md`, verified). The tool-call gate agreed in direction
(`jev-deep-kit-8q7.12`). The injection flag disagreed (R82). A second claim set tells whether the lift
belongs to Noul claim verification or to SciFact. Same design as jev-k2q, on the committed FEVER
sample.

**Corpus.** Unchanged from bead `jev-wx5` (`noul-fever-20260924.md`, which holds provenance and
constants): `work/noul-fever/sample.jsonl`, 400 FEVER `paper_dev` claims with their evidence text
(sha256 `7f9f03cc…5a7734d6`; 146 SUPPORTS, 121 REFUTES, 133 NEI; truth = SUPPORTS). Same state
`{"claim", "title", "abstract"}`.

**Arms** (all `jev-1.13.0`, official `typesafe_sdk` 0.7.0, `RetryPolicy()`, concurrency 8, runner
`work/noul-scifact/run.py <arm> work/noul-fever`):

| Arm | Rows file | Question |
|---|---|---|
| criteria, committed | `work/noul-fever/rows-jev.jsonl` (`aadd4d8`, sha256 `8de7c43a…4c706acd7`) | `QUESTION`: instructions *"Does the abstract support the claim?"*; `true`: *"The abstract states the claim or directly implies that it is true"*; `false`: *"The abstract contradicts the claim, or does not address what the claim asserts"* |
| **no criteria (ablation), new** | `work/noul-fever/rows-jev-nocriteria.jsonl` | `QUESTION_NO_CRITERIA`: the same instructions, no `criteria` |
| **criteria, same-time rerun, new** | `work/noul-fever/rows-jev-rerun.jsonl` | `QUESTION` again, run beside the ablation (timing control) |

Both question objects are the ones jev-k2q used, unchanged in `run.py` since `30eb285`.

**Metrics, tests and pass rule: identical to jev-k2q**, from the same scorer
(`python3 work/noul-scifact/compare-criteria.py work/noul-fever`). The scorer is edited in this commit
only to take a data directory and to list gold labels from the sample. On SciFact its output is
unchanged; re-run it with no argument to check. The rules:

- Decision noul > 0.5. Accuracy by McNemar exact. AUC, Brier and 10-bin ECE by paired bootstrap
  (2,000 resamples, `random.Random(20260924)`, 95% percentile interval of criteria minus
  no-criteria). Alpha 0.05, two-sided. A failed row is incorrect and enters at 0.5.
- **LIFT**: at least one WIN and no LOSE across the four metrics. **HURT**: any LOSE. **NO EFFECT**:
  all four TIE.
- **Primary** = committed criteria rows vs ablation. **Control** = same-time rerun vs ablation. If the
  control disagrees with the primary, the verdict is **not robust to run timing** and the control's
  reading governs any claim. **Noise floor** = committed vs rerun, reported, not ruled on.
- **Replication** (the question this bead asks): the SciFact lift replicates if the primary and the
  control both read LIFT. It fails to replicate on NO EFFECT or HURT.
- A `NEGATIVE_EVIDENCE.md` row is written on HURT or NO EFFECT, with a retry condition.
- Per gold label (SUPPORTS / NEI / REFUTES): counts, mean noul and a within-label McNemar,
  descriptive only.

No wording, criteria or cut changes after an answer is seen.

**Stated before running:** 800 new Jev requests (400 ablation, 400 rerun), no Haiku calls, with
latency p50/p95 and reported tokens per arm.

**NO-CLAIM.** One more set, one criteria wording, one model version. A replication on FEVER makes two
claim sets, not a law about Noul, and nothing here covers Score or Choice.

## Results

Pending the live run.
