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

## Result (live, 2026-09-24 03:18-03:20 UTC, bar at `af2906b`)

Six Haiku runs: 2,600 calls, 2,600 answered, 0 failed, 0 resume passes. Every row reports
`anthropic/claude-haiku-4-5`. Each rerun's input tokens equal run 1's exactly (SST-5 364,917;
SciFact 373,346; Banking77 360,861 per run), so the prompts were byte-for-byte the same. New rows
(sha256 prefixes): `work/score-sst5/rows-haiku-run2.jsonl` `233360b4`, `-run3` `19e13a6a`;
`work/noul-scifact/rows-haiku-run2.jsonl` `7e3b3c0d`, `-run3` `0bdba594`;
`work/choice-banking77/rows-haiku-run2.jsonl` `4acd3add`, `-run3` `ce390868`.
Re-score, no key (about 10 s): `python3 work/haiku-variance/score.py`.

**R1, the verdict on every Haiku run (decides).**

| Verdict | Run 1 | Run 2 | Run 3 | Under the bar |
|---|---|---|---|---|
| SST-5 headline: MAE sign test | 109 / 75, p = 0.0148 WIN | 118 / 72, p = 0.0010 WIN | 112 / 72, p = 0.0039 WIN | **HOLDS** |
| SST-5 accuracy (pass rule: not LOSE) | 89 / 67, p = 0.092 TIE | 98 / 66, p = 0.015 WIN | 97 / 65, p = 0.015 WIN | PASS **HOLDS** |
| SciFact accuracy (pass rule: not LOSE) | 19 / 9, p = 0.087 TIE | 19 / 10, p = 0.136 TIE | 17 / 8, p = 0.108 TIE | no LOSE |
| SciFact AUC, Jev minus Haiku, 95% | +0.0080 to +0.0531 WIN | −0.0021 to +0.0393 TIE | +0.0020 to +0.0449 WIN | **RETRACTED** |
| SciFact Brier, Jev minus Haiku, 95% | −0.0473 to −0.0117 WIN | −0.0401 to −0.0056 WIN | −0.0418 to −0.0071 WIN | **HOLDS** |
| SciFact ECE, Jev minus Haiku, 95% | −0.0646 to −0.0072 WIN | −0.0558 to −0.0011 WIN | −0.0495 to +0.0050 TIE | **RETRACTED** |
| SciFact PASS (no Haiku win on any of the four) | yes | yes | yes | **HOLDS** |
| Banking77 McNemar | 25 / 3, p = 2.7e-5 WIN | 23 / 4, p = 3.1e-4 WIN | 24 / 2, p = 1.1e-5 WIN | **HOLDS** |

**What moves.** Two of SciFact's three calibration-style wins over Haiku do not survive the
incumbent's re-run: AUC falls to TIE on run 2 and ECE falls to TIE on run 3. In each case Jev is
still ahead in direction (every interval's midpoint favours Jev), but the bar requires WIN on all
three runs. Brier WIN holds on all three. SciFact's PASS is untouched: no run gives Haiku a win on
anything. Everything else holds. SST-5's fragile MAE headline (headroom 4 rows) gets stronger on the
reruns (p 0.001 and 0.004). Its accuracy comparison, TIE on the committed run, is a Jev WIN on both
reruns. That is reported, not claimed: the bar only asks whether it ever becomes a LOSE.

**R2, flips between Haiku runs (describes).**

| Unit | What is compared | Run 1 vs 2 | Run 1 vs 3 | Run 2 vs 3 | Headroom |
|---|---|---:|---:|---:|---|
| SST-5 (500) | rounded level | 85 | 97 | 80 | MAE WIN 4, accuracy not-LOSE 44 |
| SciFact (400) | decision at > 0.5 | 11 | 9 | 12 | accuracy not-LOSE 18 |
| SciFact (400) | noul moved by more than 0.10 (mean abs change) | 44 (0.051) | 41 (0.049) | 41 (0.048) | none (bootstrap verdicts) |
| Banking77 (400) | chosen intent | 22 | 19 | 23 | WIN 10, not-LOSE 35 |

Haiku changes 16 to 19% of SST-5 levels between runs, 20 to 24 times the MAE headline's headroom.
`jev-qbc` measured Jev changing 6 to 8 of 500. So R1 alone decided SST-5 and Banking77, and they
held anyway. Only SciFact's decisions moved less than their headroom.

**R3, spread across the three Haiku runs against the committed gap.** Every Haiku metric's range is
below the Jev-Haiku gap, so the committed single-run Haiku numbers stand as point estimates:
SST-5 correct 241-251 (range 10, gap 22), MAE 0.556-0.584 (0.028, gap 0.068); SciFact correct
351-352 (1, gap 10), AUC 0.934-0.945 (0.011, gap 0.028), Brier 0.0932-0.1002 (0.0069, gap 0.0293),
ECE 0.0708-0.0854 (0.0145, gap 0.0423); Banking77 correct 362-365 (3, gap 22).

**Adapter debug (runs 2 and 3; run 1 predates the fields).**
- SST-5 Score and SciFact Noul: 0 rows with `probabilityError` and 0 with `originalProbabilities`
  in all four runs, so the adapter never renormalized a Haiku map on these two units.
- Banking77 Choice: 89 and 87 rows had the raw map renormalized (raw sums 0.00 to 1.15, 0 retries).
  Among them, 11 and 12 rows had `rawSum == 0`, and they are exactly the flat rows the scorer finds
  (uniform 0.1, `choice` `activate_my_card`, none with that true intent, all scored wrong as shipped).
  So on `jev-k3k`'s inputs the flat answers are now observed, in the adapter's own debug, to be
  all-zero maps. That confirms for runs 2 and 3 the mechanism `jev-mly` found and `jev-k3k`'s
  receipt could only infer for its run 1. The flat rows recur: 16 distinct rows over three runs,
  8 flat in all three, and 12 of run 1's 14 flat again in run 3.

**Latency and tokens per rerun** (p50 / p95 ms; input / output tokens): SST-5 790 / 1,529 and
810 / 1,473 (364,917 / 21,961 and 21,945); SciFact 690 / 1,134 and 663 / 1,150 (373,346 / 4,961 and
4,986); Banking77 1,004 / 1,877 and 1,003 / 1,885 (360,861 / 41,248 and 41,464).

**Negative evidence.** The two retractions are `NEGATIVE_EVIDENCE.md` R89 with a retry condition.
They are reported to the owner of `jev-9er`, ScoreSST5. The `jev-9er` receipt is not edited.

**Spend.** 2,600 Haiku calls through the adapter: 2,198,248 input / 136,565 output tokens. That is
about $2.88 at $1 / $5 per million `[INFERENCE: list price, not a bill]`. No Jev calls.

**Boundary (NO-CLAIM).** Three Haiku runs per unit within about three minutes of each other plus the
original run about 50 minutes earlier. One adapter version (`adffc2e`), one Haiku model, one
evening. Jev is held at one run per unit here (its variance is `jev-qbc`'s, measured on SST-5 and
Banking77 only, not SciFact). No Jev-run x Haiku-run cross-pairings were run. The retracted SciFact
AUC and ECE wins are "not robust to the incumbent's re-run", not "Haiku is as good": the direction
favours Jev in every run. Awaiting a non-author spot-check before the bead closes.

## Non-author verification — ConfidenceCascade

ConfidenceCascade (background agent of pane 1; not the author), 2026-09-24, keyless, from a fresh
`git clone --local` at `abe14d9` into `/tmp/cc-x5k.pyvi9j/jev`. No live call, $0 spend.

| # | Check | Result |
|---|---|---|
| 1 | `env -u TYPESAFE_API_KEY -u ANTHROPIC_API_KEY python3 work/haiku-variance/score.py` in the clone | HOLDS, exit 0. Run 1 reproduces 9/9 committed checks. Every per-run cell of the R1, R2 and R3 tables above reproduces, including SciFact AUC on run 2 (−0.0021 to +0.0393, TIE) and ECE on run 3 (−0.0495 to +0.0050, TIE). R1 prints HOLDS for SST-5 MAE, SST-5 PASS, SciFact Brier, SciFact PASS and Banking77, and RETRACTED for SciFact AUC and ECE. |
| 2 | Input tokens per rerun equal run 1's (summed from the rows) | HOLDS. SST-5 364,917 on all three runs; SciFact 373,346 on all three; Banking77 360,861 on all three. Output tokens differ (SST-5 22,004 / 21,961 / 21,945; SciFact 4,981 / 4,961 / 4,986; Banking77 41,400 / 41,248 / 41,464). Every row reports `anthropic/claude-haiku-4-5`. |
| 3 | Banking77 renormalized-map rows with `rawSum == 0` are the flat rows | HOLDS. Run 2: 11 flat rows (every probability equal) and 11 with `rawSum == 0`, the same set. Run 3: 12 and 12, the same set. All have `probabilityError` 1.0 and `choice` `activate_my_card`, and none has that true intent. Rows with `probabilityError` set: 89 and 87. |
| 4 | Bar before data | HOLDS. `af2906b` (21:18:08 −0600) is an ancestor of `752b38b` (21:22:27 −0600). `af2906b` adds no rerun row files. Between them, `work/haiku-variance/score.py` and the three runners are byte-unchanged. The receipt changes only from `## Result` down. The runner diffs at `af2906b` add debug keys to the rows and the SciFact `haiku-run2/3` arm names; the Haiku call itself is unchanged. |
| 5 | 10 rerun rows, `random.Random(20260925).sample` over all 2,600 rerun rows | HOLDS on 10/10. SST-5 run 3 i=243, run 2 i=498, run 3 i=123: `score` = Σ k·p_k exactly (1.75, 2.99, 0.33), probabilities sum to 1.0, rounded levels 2 / 3 / 0 against labels 1 / 4 / 1 (all scored wrong, consistent with the scorer). SciFact run 2 i=10 noul 0.95 with gold SUPPORT, and run 3 i=116 noul 0.0 with gold NEI (both correct at > 0.5). Banking77 run 2 i=339, i=44 and run 3 i=19, i=383, i=157: `choice` is the argmax, `confidence` equals `(p_max − 1/10)/(1 − 1/10)` (1.0 / 1.0 / 1.0 / 0.7778 / 1.0), and the probabilities sum to 1.0. i=19 was renormalized from `rawSum` 0.1. All five match their true intents. |

Verdict: the receipt's numbers, its two retractions (R89) and its flat-row finding reproduce from
committed files, and the bar was not edited after data. NO-CLAIM: this re-scores committed rows; it
does not re-run Haiku or check the bootstrap seeds beyond the scorer's own output.

## Cross-pairings (9 per unit) — descriptive, added afterwards

MaintFixes, 2026-09-24. `[oracle]` level: offline arithmetic on committed rows, with no call made.
**Descriptive: the `jev-x5k` bar above did not preregister cross-pairings.** Nothing above this
section changes. `jev-qbc` re-ran Jev twice (`rows-jev-run2/-run3.jsonl`) against Haiku run 1, and
this unit re-ran Haiku twice against Jev run 1. That covers 5 of the 9 Jev-run x Haiku-run pairings
per unit. The other four were computed here from those committed rows. `R88` (Yelp) is the case
where a crossing decided the verdict, with 3 of 9 pairings WIN.

Re-score, no key: `python3 work/haiku-variance/cross-pairings.py`. It imports each unit's own
`score.py` (`paired` and `verdict` for SST-5; `arm_stats`, `mcnemar_exact` and the unit's verdict
rule for Banking77). It exits 1 unless the 5 pairings already committed reproduce their receipt's
verdict, counts where stated, and p within rounding. A plant that makes 6 wrong Haiku run-1
Banking77 rows correct turns it red with rc 1, on the three pairings with Haiku run 1.

**SST-5 (500).** MAE uses an exact sign test on per-row absolute error, counted as Jev lower / Haiku
lower. Accuracy uses McNemar exact.

| Jev run | Haiku run | MAE sign test | p | verdict | accuracy McNemar | p | verdict | already committed |
|---|---|---|---:|---|---|---:|---|---|
| 1 | 1 | 109 / 75 | 0.0148 | WIN | 89 / 67 | 0.092 | TIE | yes |
| 1 | 2 | 118 / 72 | 0.0010 | WIN | 98 / 66 | 0.015 | WIN | yes |
| 1 | 3 | 112 / 72 | 0.0039 | WIN | 97 / 65 | 0.015 | WIN | yes |
| 2 | 1 | 108 / 79 | 0.0403 | WIN | 89 / 71 | 0.179 | TIE | yes |
| 2 | 2 | 116 / 75 | 0.0037 | WIN | 97 / 69 | 0.036 | WIN | no |
| 2 | 3 | 110 / 75 | 0.0122 | WIN | 96 / 68 | 0.035 | WIN | no |
| 3 | 1 | 110 / 77 | 0.0190 | WIN | 91 / 69 | 0.097 | TIE | yes |
| 3 | 2 | 118 / 73 | 0.0014 | WIN | 99 / 67 | 0.016 | WIN | no |
| 3 | 3 | 112 / 73 | 0.0051 | WIN | 98 / 66 | 0.015 | WIN | no |

MAE WIN in 9/9 pairings (sign p 0.0010 to 0.0403). Accuracy is never LOSE (0/9).

**Banking77, 10 intents (400).** McNemar counts Jev-only correct / Haiku-only correct. The verdict
rule is the unit's own.

| Jev run | Haiku run | Jev | Haiku | McNemar | p | verdict | already committed |
|---|---|---:|---:|---|---:|---|---|
| 1 | 1 | 384 | 362 | 25 / 3 | 2.7e-05 | WIN | yes |
| 1 | 2 | 384 | 365 | 23 / 4 | 3.1e-04 | WIN | yes |
| 1 | 3 | 384 | 362 | 24 / 2 | 1.0e-05 | WIN | yes |
| 2 | 1 | 384 | 362 | 25 / 3 | 2.7e-05 | WIN | yes |
| 2 | 2 | 384 | 365 | 23 / 4 | 3.1e-04 | WIN | no |
| 2 | 3 | 384 | 362 | 24 / 2 | 1.0e-05 | WIN | no |
| 3 | 1 | 386 | 362 | 26 / 2 | 3.0e-06 | WIN | yes |
| 3 | 2 | 386 | 365 | 24 / 3 | 4.9e-05 | WIN | no |
| 3 | 3 | 386 | 362 | 25 / 1 | 8.0e-07 | WIN | no |

McNemar WIN in 9/9 pairings (p 8.0e-07 to 3.1e-04).

**Rounding note.** For 24 / 2 the exact McNemar p is 704 / 2^26 = 1.049e-5. The Result table above
(line 116) shows it as 1.1e-5, rounded from the scorer's printed 1.05e-05. At two significant figures
it is 1.0e-5. The verdict is unaffected.

**NO-CLAIM.** Three runs per arm, one sample per unit, one wording, one evening. These are the same
committed rows, re-paired; no new call was made. Because the bar did not preregister them, these
pairings can support a statement that the two headlines held across every committed run
combination. They do not extend this unit's verdicts. SciFact is not crossed here: Jev's SciFact
variance was never measured.
