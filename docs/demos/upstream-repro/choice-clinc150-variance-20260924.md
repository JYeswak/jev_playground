# Do jev-qw8's CLINC150 verdicts hold on 3 x 3 runs? (bead `jev-kvw`)

ScoreSST5 (background agent of pane 1, AmberWillow), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`,
Haiku `anthropic/claude-haiku-4-5` through `system-one-adapter-python` at `adffc2e`.

## Preregistered (committed before the first call)

**Question.** jev-qw8 (`choice-clinc150-20260924.md`, JevVariance, commits `e0950ce`, `2842340`) is a
README headline measured once per arm, on 750 rows from the CLINC150 `auto_and_commute` domain: 15
intents plus 300 out-of-scope rows. It published two primary verdicts:

- **overall correct: NON-INFERIOR** (Jev 688, Haiku 681; 21 vs 14; McNemar p = 0.311);
- **handled at peak probability ≥ 0.60: WIN** (Jev 685, Haiku 650; 47 vs 12; p = 5.1e-6).

Three other single-run wins did not survive re-runs tonight: R88 (Yelp MAE), R89 (SciFact AUC/ECE)
and R90 (FEVER AUC/Brier). Do these two survive?

**Runs.** Everything is unchanged from jev-qw8: `work/choice-clinc150/subset.jsonl`, the same question,
labels, state and concurrency. The new runs go through `work/choice-clinc150/run-variance.py`, which
imports `run.py` and calls its own `run_jev` and `run_haiku` (structured outputs) with only the output
path changed. `run.py` is not edited, because JevVariance's jev-pm3 run is using it.

| Run | File | Status |
|---|---|---|
| J1 | `rows-jev.jsonl` | committed (`2842340`) |
| J2, J3 | `rows-jev-run2.jsonl`, `rows-jev-run3.jsonl` | new |
| H1 | `rows-haiku.jsonl` | committed (`2842340`) |
| H2, H3 | `rows-haiku-run2.jsonl`, `rows-haiku-run3.jsonl` | new |

A run with failed rows gets one resume pass. Rows that still fail are scored wrong, as `score.py`
already does.

**Scorer.** `python3 work/choice-clinc150/variance.py`. It imports this unit's own `score.py` and uses
its `preds`, `correct`, `gate`, `handled` and `verdict` unchanged. Each pairing is scored under both
Haiku readings (as shipped; zero-mass = none), keeping the worse label for Jev, exactly as `score.py`
does.

- **Step 1 (run before this bar was written):** it re-derives J1 x H1 and exits 4 unless that
  reproduces the published labels. It did: overall NON-INFERIOR (688 / 681, 21 vs 14, p = 0.311);
  handled WIN (685 / 650, 47 vs 12, p = 5.13e-6).
- It issues no verdict unless all 9 pairings are present (exit 5).

**Headroom from the committed run** (J1 x H1, answer changes each placed adversarially):

- The handled WIN ends after **17** changes.
- The overall NON-INFERIOR becomes a LOSE (more than 3 points behind) after **30**.

**The rule, fixed now** (the jev-x5k / jev-hg8 all-pairings rule). Every Jev run is paired with every
Haiku run, giving 3 x 3 = 9 pairings.

- **Handled at ≥ 0.60 WIN:** it stands only if it is WIN on all 9 pairings, else it is RETRACTED. The
  count of WIN pairings is reported either way.
- **Overall NON-INFERIOR:** it stands only if every pairing is NON-INFERIOR or better, else it is
  RETRACTED. A WIN on some pairings does not upgrade the published label.
- **PASS:** it is RETRACTED if any pairing, on either primary measure, is LOSE or NOT-SCORED (NOT-SCORED
  means in-scope accuracy below 50% on either arm).
- **Any retraction** gets a `NEGATIVE_EVIDENCE.md` row with a retry condition.
- **Described, not ruled on:** per-run numbers, and the answer changes and gate-outcome changes
  between runs of the same arm.

No question, gate or threshold changes after a run is seen.

**Stated before running:** 1,500 Jev requests (J2, J3) and 1,500 Haiku requests (H2, H3). Latency and
tokens are reported per run.

**NO-CLAIM.** One domain (auto_and_commute), 15 intents, one question. Three runs per arm is a small
sample of each model's variation. JevVariance's full 150-intent set (jev-pm3) is not touched or
measured here.

## Results

Pending the live runs.
