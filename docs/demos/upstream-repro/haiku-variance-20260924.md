# Does a verdict survive the incumbent's re-run? Haiku run-to-run variance on three units (bead `jev-x5k`)

VerifySST5 (background agent of pane 1), 2026-09-24. Live lane: Haiku calls only, Jev rows held fixed.

## Preregistered (committed before the first rerun call)

**Question.** Every paired test tonight compares Jev to one Haiku run. `jev-qbc`
([receipt](jev-variance-20260924.md)) re-ran Jev and held Haiku fixed. This unit does the other
half: re-run only the Haiku arm, twice, with the same code, pin, state and question. Does each
Jev-vs-Haiku verdict still hold?

| Unit | Verdicts under test (committed) | Committed at |
|---|---|---|
| SST-5 Score, `jev-zui` ([receipt](score-sst5-20260924.md)) | MAE sign test 109 vs 75, p = 0.0148 (WIN); accuracy McNemar 89 vs 67, p = 0.092 (TIE); PASS | `576e60e` |
| SciFact Noul, `jev-9er` ([receipt](noul-scifact-20260924.md)) | accuracy McNemar 19 vs 9, p = 0.087 (TIE); AUC, Brier and ECE bootstrap WIN; PASS | `83a7295` |
| Banking77 10-intent Choice, `jev-k3k` ([receipt](choice-banking77-20260924.md)) | McNemar 25 vs 3, p = 2.7e-5 (WIN); PASS | `3709ee6` |

**Runs.** The Haiku arm only, two more runs per unit, into new files beside the originals. The
committed `rows-haiku.jsonl` is run 1. No committed row file or receipt of any unit is edited.

- SST-5: `work/score-sst5/run.py haiku work/score-sst5/rows-haiku-run{2,3}.jsonl` (output path from
  `b53a33b`).
- SciFact: `work/noul-scifact/run.py haiku-run{2,3}` writes `rows-haiku-run{2,3}.jsonl`. The two arm
  names are added in this commit and take the unchanged `haiku` call path.
- Banking77: `work/choice-banking77/run.py --out work/choice-banking77/rows-haiku-run{2,3}.jsonl haiku`
  (`--out` from `8851fcd`; the default set is the 10-intent subset).
- Same adapter settings as run 1 in every unit: `system-one-adapter-python` at `adffc2e` (v0.2.0,
  checkout clean), `anthropic/claude-haiku-4-5`, `structured_outputs=True`,
  `llm_answer_mode="probabilities"`, `normalize_probabilities=True`, `RetryPolicy()`, concurrency 8.
  The question objects and state builders are the ones frozen with each unit's bar.
- **Adapter debug is recorded on every new row:** `probabilityError` from
  `debug["probability_errors"][question]` (present only when the raw map was off by more than 1e-6),
  plus `originalProbabilities` (SST-5, SciFact) or `rawSum` / `normError` / `nRetries` (Banking77).
  This commit adds the two SST-5 fields and the Banking77 `probabilityError` field. They are extra
  row keys; the call is unchanged. Run 1 predates them, so its debug is "not recorded".
- Runs are sequential within a unit, so run 3 starts after run 2 ends. The three units run side by
  side. Each run gets at most one resume pass; a row still failed is scored by its unit's own rule
  (SST-5 incorrect with worst error, SciFact incorrect at noul 0.5, Banking77 wrong).

**Scorer.** `python3 work/haiku-variance/score.py` (stdlib, no key, no network). Every metric and
test is imported from the owning unit's committed `score.py`, never restated. It exits 1 unless
Haiku run 1 reproduces the committed numbers above, and it does (9/9 checks). `--bar` prints the
reproduction and the headroom only.

**Headroom, from the committed run 1 before any rerun** (`score.py --bar`): the fewest Haiku
answers that would have to change to break the verdict, each change placed where it hurts Jev
most. It is a lower bound: a run that changes fewer Haiku answers than this cannot move the
verdict.

| Verdict | Run 1 | Headroom (Haiku rows) |
|---|---|---:|
| SST-5 headline: MAE sign test WIN | 109 vs 75 | 4 (0.8% of 500) |
| SST-5 pass rule: accuracy not LOSE | 89 vs 67 | 44 |
| SciFact pass rule: accuracy not LOSE | 19 vs 9 | 18 |
| Banking77 headline: McNemar WIN | 25 vs 3 | 10 (2.5% of 400) |
| Banking77 PASS: not LOSE (Haiku more than 12 rows above Jev's 384) | Haiku 362 | 35 |

The SciFact AUC, Brier and ECE verdicts are bootstrap intervals and have no row-count headroom.
Rule R1 alone decides them.

**Retraction rules, fixed now** (the same shape as `jev-qbc`'s, with Haiku as the arm re-run):

- **R1, the verdict on every Haiku run (decides).** Each unit's committed paired test is re-run with
  the committed Jev rows against Haiku run k, for k = 1, 2, 3.
  - SST-5: the headline "Jev beats Haiku on MAE" HOLDS only if the sign test is WIN on all three
    runs. One run at TIE or LOSE RETRACTS it. PASS is RETRACTED if any run is a LOSE on accuracy or
    MAE. (The constants do not depend on Haiku and are not re-tested.)
  - SciFact: each of the three WINs (AUC, Brier, ECE) HOLDS only if WIN on all three runs, else it is
    RETRACTED. PASS is RETRACTED if any run shows a LOSE on accuracy, AUC, Brier or ECE.
  - Banking77: the headline WIN HOLDS only if all three runs are WIN. Any run at NON-INFERIOR
    DOWNGRADES it to NON-INFERIOR, with PASS kept. Any run at LOSE or below the feasibility floor
    RETRACTS the PASS.
- **R2, flips against headroom (describes).** For each pair of Haiku runs: rows whose answer
  differs (SST-5 rounded level, SciFact decision at > 0.5, Banking77 chosen intent), plus SciFact's
  mean absolute noul change. A pair below the headroom above could not have moved that verdict. A
  pair at or above it means R1 alone decides.
- **R3, spread against the gap (magnitude).** If the range of a Haiku metric across the three runs
  is at least the committed Jev-Haiku gap, that single-run Haiku number is not reported as a point
  estimate; the receipt gives the three-run range instead, whatever R1 says. The gaps: SST-5 MAE
  0.068 and accuracy 22 rows; SciFact accuracy 10 rows, AUC 0.028, Brier 0.0293, ECE 0.0423;
  Banking77 22 rows.
- Flat and zero-mass Haiku rows (`jev-mly`) are scored as shipped in every run, as the units'
  bars fixed. Their count per run is reported.

Any retraction or downgrade gets a `NEGATIVE_EVIDENCE.md` row with a retry condition. It is also
reported to the owning units' authors. No other unit's receipt is edited.

**Spend, planned.** 2 x 500 + 2 x 400 + 2 x 400 = 2,600 Haiku calls, plus any resume calls. No Jev
calls.

**NO-CLAIM.** Three Haiku runs per unit, one evening, one adapter version, one Haiku model. This
measures run-to-run variance of the incumbent's answers only. Jev's variance is `jev-qbc`'s. Nothing
here measures variance across days, prompts or adapter versions.

## Result

NOT_RUN. Filled in after the six runs.
