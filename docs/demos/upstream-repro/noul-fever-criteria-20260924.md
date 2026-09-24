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

The bar was committed at `e506575` (2026-09-24T03:13:58Z). Both new arms started at 03:14:08Z, and
each answered 400/400 with 0 error rows. Rows: `work/noul-fever/rows-jev-nocriteria.jsonl` (sha256
`098a3aad…482cd3bb0`) and `work/noul-fever/rows-jev-rerun.jsonl` (sha256 `85ec7463…36d799b7`),
scored against the committed `rows-jev.jsonl`. Re-score with no key (about 12 s):
`python3 work/noul-scifact/compare-criteria.py work/noul-fever`.

| Arm | Correct at >0.5 | Accuracy | AUC | Brier | ECE | p50 / p95 latency | Tokens in / out |
|---|---:|---:|---:|---:|---:|---|---|
| criteria, committed | 379/400 | 94.8% | 0.973 | 0.0463 | 0.0376 | 159 / 378 ms | 158,899 / 8,000 |
| **no criteria (ablation)** | 377/400 | 94.2% | 0.971 | 0.0495 | 0.0400 | 150 / 319 ms | 141,299 / 8,000 |
| criteria, same-time rerun | 379/400 | 94.8% | 0.971 | 0.0461 | 0.0365 | 152 / 312 ms | 158,899 / 8,000 |

Paired, first arm minus second (WIN means the criteria arm is significantly better):

| Pair | Accuracy (McNemar) | AUC diff 95% | Brier diff 95% | ECE diff 95% | Reading |
|---|---|---|---|---|---|
| **primary**: committed criteria vs ablation | TIE (2 vs 0, p = 0.5) | TIE (−0.0033 to +0.0089) | **WIN** (−0.0055 to −0.0009) | TIE (−0.0130 to +0.0111) | **LIFT** |
| **control**: same-time rerun vs ablation | TIE (3 vs 1, p = 0.625) | TIE (−0.0029 to +0.0034) | **WIN** (−0.0056 to −0.0013) | TIE (−0.0144 to +0.0090) | **LIFT** |
| noise floor: committed vs rerun | TIE (1 vs 1) | TIE (−0.0017 to +0.0066) | TIE (−0.0006 to +0.0009) | TIE (−0.0047 to +0.0070) | same |

**Pass rule applied.** The primary reads LIFT (Brier WIN, no LOSE). The control also reads LIFT, so the
result does not depend on run timing. Replication clause: both read LIFT, so **the SciFact lift
replicates**. The noise floor is flat. No `NEGATIVE_EVIDENCE.md` row: the trigger (HURT or NO EFFECT)
did not fire.

By FEVER gold label (correct at >0.5 / mean noul), descriptive:

| Gold | Rows | Criteria, committed | No criteria | Criteria, rerun | McNemar committed vs ablation |
|---|---:|---|---|---|---|
| SUPPORTS | 146 | 140 (95.9%) / 0.924 | 139 (95.2%) / 0.924 | 140 (95.9%) / 0.926 | 1 vs 0, p = 1 |
| NEI | 133 | 119 (89.5%) / 0.144 | 118 (88.7%) / 0.170 | 119 (89.5%) / 0.145 | 1 vs 0, p = 1 |
| REFUTES | 121 | 120 (99.2%) / 0.030 | 120 (99.2%) / 0.037 | 120 (99.2%) / 0.031 | 0 vs 0 |

**Verdict** (`[live]`, N=400 per arm, 2026-09-24). The criteria lift **replicates** on a second claim
set, with the same shape as on SciFact. It is a small gain in probability quality, not in decisions.
Brier improves by about 0.0033 (6.5% relative) in both pairs; AUC and ECE do not move significantly.
At the 0.5 cut, 2 to 4 of 400 calls differ. The mechanism matches SciFact: the `false` description,
"does not address what the claim asserts", lowers the mean probability on the not-enough-info rows
(0.170 to 0.144) while SUPPORTS rows stay put (0.924 both ways). Across the two sets, then, criteria on
this Noul are a consistent calibration tweak and never a decision change. The gate's catch-rate jump
(41 to 78 of 100) has not recurred on claim verification. The effect is smaller here than on SciFact
(Brier −0.0033 vs −0.0065), because FEVER starts from a lower Brier (0.0495 vs 0.0774) and leaves less
room.

**Spend.** 800 live Jev calls, 0 errors. Ablation: 141,299 input / 8,000 output tokens. Rerun:
158,899 / 8,000. The criteria cost 44 input tokens per call (17,600 over 400), the same as on SciFact.
No Haiku calls. Jev's billed units were not read.

**Boundary.** Two claim sets now, both English, one criteria wording, one model version. Only Brier
separates, and its intervals sit close to 0 (upper ends −0.0009 and −0.0013). The comparison of effect
size across the two sets, and the lower-starting-Brier explanation, were not preregistered. Nothing
here covers vaguer instructions, other criteria wordings, or Score and Choice. This receipt needs a
re-score from someone other than the author, using the committed rows, before the bead closes.
