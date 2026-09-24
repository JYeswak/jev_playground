# Do Noul outcome criteria lift claim verification? SciFact ablation, same 400 pairs (bead `jev-k2q`)

ScoreSST5 (background agent of pane 1, AmberWillow), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first call)

**Corrected premise.** The bead text asks to *add* Noul criteria `{true, false}` to the jev-9er
question and compare against the committed "cookbook-wording" rows. Those rows already carry
criteria: the jev-9er question (`work/noul-scifact/run.py` `QUESTION`, frozen at `15b0371`) is the
vendor cookbook's instructions **plus** a `true` and a `false` outcome description. There is no
criteria-free baseline to add criteria to. ScoreSST5 corrected the premise and pane 1 agreed
(2026-09-24): the same question, whether outcome criteria lift claim verification, is answered by the
**ablation**, keeping the instructions and removing the criteria, compared against the committed
criteria rows.

**Why it matters.** Criteria were the lane's largest effect so far (tool-call gate catch 41/100 to
78/100, `jev-deep-kit-8q7.12`), and RULE 14 records that no Noul here used them before that. One
public set tests whether the effect is general or specific to the gate.

**Corpus.** Unchanged from jev-9er: `work/noul-scifact/sample.jsonl`, 400 SciFact claim/abstract pairs
(sha256 `424caf18…088ed33`; 146 SUPPORT, 93 CONTRADICT, 161 NEI; truth = SUPPORT). Same state
`{"claim", "title", "abstract"}`. Provenance, sampler and constants:
`docs/demos/upstream-repro/noul-scifact-20260924.md`.

**Arms** (all `jev-1.13.0`, official `typesafe_sdk` 0.7.0, `RetryPolicy()`, concurrency 8):

| Arm | Rows file | Question |
|---|---|---|
| criteria, committed | `rows-jev.jsonl` (`83a7295`, run 2026-09-24T02:31Z) | instructions *"Does the abstract support the claim?"*; `true`: *"The abstract states the claim or directly implies that it is true"*; `false`: *"The abstract contradicts the claim, or does not address what the claim asserts"* |
| **no criteria (ablation), new** | `rows-jev-nocriteria.jsonl` | the same instructions, `criteria` absent (`QUESTION_NO_CRITERIA` in `run.py`) |
| **criteria, same-time rerun, new** | `rows-jev-rerun.jsonl` | the committed question again, run right beside the ablation |

The rerun is a control added by the author. The committed rows are about an hour older than the
ablation, so without it any difference could be run-to-run or time-of-day drift in the service
rather than the criteria.

**Metrics and tests.** Identical to jev-9er and imported from `work/noul-scifact/score.py`: decision
noul > 0.5; accuracy by McNemar exact; AUC (Mann-Whitney), Brier and 10-bin ECE by paired bootstrap
(2,000 resamples, `random.Random(20260924)`, 95% percentile interval of criteria minus no-criteria);
alpha 0.05, two-sided; a failed row is incorrect and enters at 0.5. Scorer:
`work/noul-scifact/compare-criteria.py`.

**Pass rule** (per metric, criteria vs ablation: WIN = criteria significantly better):
- **LIFT**: at least one WIN and no LOSE on accuracy, AUC, Brier and ECE.
- **HURT**: any LOSE. A mix of WIN and LOSE counts as HURT.
- **NO EFFECT**: all four TIE.
- **Primary** = committed criteria rows vs ablation (what the bead asks for). **Control** = same-time
  rerun vs ablation. If the control reads differently from the primary, the verdict is reported as
  **not robust to run timing**, and the control's reading takes precedence for any claim about
  criteria. **Noise floor** = committed vs rerun on the same question, reported, not ruled on.
- A `NEGATIVE_EVIDENCE.md` row is written if the verdict is HURT or NO EFFECT (the hypothesis under
  test is that criteria lift claim verification the way they lifted the gate).
- Per gold label (SUPPORT / CONTRADICT / NEI): counts, mean noul and a within-label McNemar,
  descriptive only.

No wording, criteria or cut is changed after an answer is seen.

**Stated before running:** 800 new Jev requests (400 ablation, 400 rerun), no Haiku calls. Latency
p50/p95 and reported tokens per arm.

**NO-CLAIM.** One set, one wording of criteria, one model version. This measures criteria on top of
these instructions; it says nothing about other criteria wordings, or about criteria on Score or
Choice.

## Results

Bar committed at `30eb285` (2026-09-24T02:37:06Z). Both new arms started at 02:37:15Z, 400/400
answered each, 0 error rows. Rows: `work/noul-scifact/rows-jev-nocriteria.jsonl` (sha256
`8ee29bdb…ea50f2e`), `work/noul-scifact/rows-jev-rerun.jsonl` (sha256 `608ecc64…4545a8041`), plus the
committed `rows-jev.jsonl`. Re-score with no key (about 20 s): `python3 work/noul-scifact/compare-criteria.py`.

| Arm | Correct at >0.5 | Accuracy | AUC | Brier | ECE | p50 / p95 latency | Tokens in / out |
|---|---:|---:|---:|---:|---:|---|---|
| criteria, committed | 361/400 | 90.2% | 0.962 | 0.0709 | 0.0431 | 140 / 219 ms | 293,734 / 8,000 |
| **no criteria (ablation)** | 362/400 | 90.5% | 0.958 | 0.0774 | 0.0612 | 165 / 363 ms | 276,134 / 8,000 |
| criteria, same-time rerun | 361/400 | 90.2% | 0.961 | 0.0711 | 0.0440 | 159 / 379 ms | 293,734 / 8,000 |

Paired, first arm minus second (WIN = the criteria arm is significantly better):

| Pair | Accuracy (McNemar) | AUC diff 95% | Brier diff 95% | ECE diff 95% | Reading |
|---|---|---|---|---|---|
| **primary**: committed criteria vs ablation | TIE (3 vs 4, p = 1) | **WIN** (+0.0007 to +0.0072) | **WIN** (−0.0107 to −0.0021) | TIE (−0.0331 to +0.0023) | **LIFT** |
| **control**: same-time rerun vs ablation | TIE (3 vs 4, p = 1) | TIE (−0.0004 to +0.0060) | **WIN** (−0.0107 to −0.0017) | TIE (−0.0335 to +0.0036) | **LIFT** |
| noise floor: committed vs rerun | TIE (0 vs 0) | TIE (−0.0004 to +0.0031) | TIE (−0.0017 to +0.0011) | TIE (−0.0119 to +0.0091) | same |

**Pass rule applied.** Primary reads LIFT (two WINs, no LOSE); the control also reads LIFT, so the
verdict is robust to run timing. The noise floor is flat: the same question an hour apart gave the
same 361 correct and moved no metric significantly. No `NEGATIVE_EVIDENCE.md` row: the trigger (HURT
or NO EFFECT) did not fire.

By SciFact gold label (correct at >0.5 / mean noul), descriptive:

| Gold | Rows | Criteria, committed | No criteria | Criteria, rerun | McNemar committed vs ablation |
|---|---:|---|---|---|---|
| SUPPORT | 146 | 131 (89.7%) / 0.843 | 134 (91.8%) / 0.849 | 131 (89.7%) / 0.843 | 1 vs 4, p = 0.375 |
| CONTRADICT | 93 | 89 (95.7%) / 0.086 | 88 (94.6%) / 0.101 | 89 (95.7%) / 0.085 | 1 vs 0, p = 1 |
| NEI | 161 | 141 (87.6%) / 0.168 | 140 (87.0%) / 0.215 | 141 (87.6%) / 0.169 | 1 vs 0, p = 1 |

**Verdict** (`[live]`, N=400 per arm, 2026-09-24). By the preregistered rule, the outcome criteria
**lift** claim verification here. The lift is real but small, and it is a lift in probability quality,
not in decisions. Brier improves by about 0.0065 (8% relative) in both the primary and the control;
AUC improves by 0.004 in the primary only. At the 0.5 cut the two questions make almost the same calls:
7 of 400 rows differ, 3 against 4. The mechanism is visible in the gold-label table. The `false`
description names "does not address what the claim asserts", and with it Jev's mean probability on
the NOT ENOUGH INFO rows drops from 0.215 to 0.168 without changing which side of 0.5 they fall on.

So the direction of the gate result carries over, and its size does not. On the tool-call gate,
criteria nearly doubled the catch rate (41 to 78 of 100). On SciFact, whose instructions already
name the task precisely, they sharpen the probabilities and leave the decisions alone. The gate-sized
effect is not general on this evidence; a small calibration effect is.

**Spend.** 800 live Jev calls, 0 errors: ablation 276,134 input / 8,000 output tokens, rerun 293,734 /
8,000. The criteria add about 44 input tokens per call (17,600 over 400). No Haiku calls. Jev's billed
units were not read.

**Boundary.** One set, one wording of criteria, one model version, and instructions that were already
specific. The ECE differences are not significant in either pair. Nothing here says criteria help (or
are inert) on vaguer instructions, on other sets, or on Score and Choice. The "no gate-sized effect"
reading is a comparison across two different tasks and was not preregistered. Awaiting a non-author
re-score from the committed rows before the bead closes.

## Non-author verification — VerifySST5

VerifySST5 (background agent of pane 1; not the author), 2026-09-24, keyless, from fresh
`git clone --local` copies at HEAD `1d0e1ad` and at the results commit `6ac0092`. No live call made;
spend $0.

| # | Check | Result |
|---|---|---|
| 1 | `python3 work/noul-scifact/compare-criteria.py` with no key, at `1d0e1ad` and at `6ac0092` | HOLDS. Both exit 0 with byte-identical output. `score.py` changed after the results (`834a569`, jev-wx5 data-dir support), and the output did not move. Every number in both tables and the gold-label table reproduces. Primary: TIE (3 vs 4, p=1), AUC WIN +0.0007 to +0.0072, Brier WIN −0.0107 to −0.0021, ECE TIE, LIFT. Control: Brier WIN only, LIFT. Noise floor: SAME. `NEGATIVE_EVIDENCE row required: NO`. Row sha256 prefixes `8ee29bdb` (ablation) and `608ecc64` (rerun) match the receipt. |
| 2 | Independent recompute from the rows (not through `score.py`) | HOLDS. Accuracy at > 0.5, all-pairs AUC (ties ½) and Brier: committed 361, 0.9622, 0.0709; ablation 362, 0.9584, 0.0774; rerun 361, 0.9610, 0.0711. 400/400 rows per arm, all `model` = `jev-1.13.0`, noul in [0.01, 0.99]. Decisions differ on 7 rows between committed and ablation, and on 0 between committed and rerun. |
| 3 | Each arm asked the question the bar says | HOLDS. `run.py` at `30eb285` builds `QUESTION_NO_CRITERIA = Noul(instructions=QUESTION.instructions)`, and `QUESTION`'s text is unchanged from `15b0371`. The rows confirm it. Every ablation row reports exactly 44 fewer input tokens than its committed twin (the criteria text; 400/400 rows, one constant delta). Every rerun row reports the same input tokens as its committed twin (400/400). |
| 4 | Bar before data | HOLDS. `30eb285` (2026-09-23 20:37:06 −0600) is an ancestor of `6ac0092` (20:38:45 −0600). It contains the bar, `compare-criteria.py` and the `run.py` arms, and neither new rows file. Both rows files are first added in `6ac0092` (`git log --diff-filter=A`). The receipt diff between the two only replaces "Pending the live run." under Results. `compare-criteria.py` and the three rows files are unchanged from then to HEAD. The rows carry no timestamps, so the 02:37:15Z start is the author's statement; the commit order is what is checked. |
| 5 | The rule applied as written | HOLDS. `compare-criteria.py:62-68` returns HURT on any LOSE, LIFT on any WIN otherwise, and NO EFFECT on all TIE, matching "a mix of WIN and LOSE counts as HURT". The control agrees with the primary, so the "not robust to run timing" branch does not apply. The NEGATIVE_EVIDENCE trigger (HURT or NO EFFECT) did not fire. |

Verdict: LIFT reproduces from committed files under an unedited bar, and it is robust to the scorer
change after the results. Re-score: `python3 work/noul-scifact/compare-criteria.py`. NO-CLAIM: this
re-scores committed rows; it does not re-run any arm or measure run-to-run variance beyond the
author's rerun control.
