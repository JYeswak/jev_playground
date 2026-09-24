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

Pending the live run.
