# Do Noul's calibration wins survive re-runs of both arms? SciFact and FEVER, every Jev run x every Haiku run (bead `jev-hg8`)

VerifySST5 (background agent of pane 1), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`.

## Preregistered (committed before any new call)

**Question.** Two committed Noul units report Jev beating Claude Haiku 4.5 on calibration-style
metrics with accuracy tied. `jev-x5k` ([receipt](haiku-variance-20260924.md), R89) re-ran Haiku
only on SciFact and retracted AUC and ECE. Yelp's MAE fell to TIE on 3x3 pairings (R88). FEVER's
three wins have never been re-run on either arm. Jev's run-to-run variance on Noul has never been
measured either. The README still cites these wins. Does each verdict hold on every pairing of a
Jev run with a Haiku run?

| Set | Verdicts under test (committed, Jev J1 x Haiku H1) | Committed at |
|---|---|---|
| SciFact, `jev-9er` ([receipt](noul-scifact-20260924.md)) | accuracy McNemar 19 vs 9 (TIE); AUC, Brier, ECE bootstrap WIN; PASS. AUC and ECE already retracted by R89 on Haiku re-runs | `83a7295` |
| FEVER, `jev-wx5` ([receipt](noul-fever-20260924.md)) | accuracy McNemar 6 vs 3 (TIE); AUC, Brier, ECE bootstrap WIN; PASS | `aadd4d8` |

**Runs per set.** All in `work/noul-scifact` or `work/noul-fever`, through the one runner
`work/noul-scifact/run.py <arm> [data_dir]`, with the question frozen at `15b0371`.

| Arm | Run | File | Status |
|---|---|---|---|
| Jev | J1 | `rows-jev.jsonl` | committed (`83a7295` / `aadd4d8`) |
| Jev | JR | `rows-jev-rerun.jsonl` | committed by `jev-k2q` (`6ac0092`) / `jev-5jp` (`a752d2d`). Same question: input tokens equal J1's on 400/400 rows in both sets. Run beside the no-criteria arm, about an hour after J1, so it is not an independent time slot (ScoreSST5's note). |
| Jev | J2, J3 | `rows-jev-run2.jsonl`, `rows-jev-run3.jsonl` | **new**, arms `jev-run2` / `jev-run3` added in this commit (the unchanged Jev path with `QUESTION`) |
| Haiku | H1 | `rows-haiku.jsonl` | committed |
| Haiku | H2, H3 | `rows-haiku-run2.jsonl`, `rows-haiku-run3.jsonl` | SciFact: committed by `jev-x5k` (`752b38b`); FEVER: **new** |

New calls: FEVER Haiku 2 x 400, Jev 2 x 400 on each set. That is 2,400 calls, plus any resume
passes (at most one per run). Concurrency 8, adapter `adffc2e` with the same settings as before.
Haiku rows record `probabilityError` and `originalProbabilities`. Within a set, run 3 starts after
run 2 ends. The three streams (FEVER Haiku, SciFact Jev, FEVER Jev) run side by side. A row still
failed is incorrect and enters at noul 0.5, per the units' rule.

**Scorer.** `python3 work/noul-variance/score.py` (stdlib, no key, no network). Every metric, the
bootstrap (2,000 resamples, `random.Random(20260924)`) and the correctness rule are imported from
`work/noul-scifact/score.py`, the scorer both units committed. It exits 1 unless J1 x H1 reproduces
the committed numbers, and it does on both sets (12/12 checks: counts, accuracy verdict, and all
three metric verdicts). `--bar` prints the reproduction and the headroom only.

**The rule, fixed now.** Every Jev run is paired with every Haiku run: 4 x 3 = 12 pairings per set.
- **Each WIN (AUC, Brier, ECE vs Haiku)** stands only if it is WIN on all 12 pairings, else it is
  RETRACTED. The count of WIN pairings is reported either way. SciFact AUC and ECE are already
  retracted by R89, and the pairings that retracted them (J1 x H2, J1 x H3) are among the 12. So
  they cannot come back here; they are re-reported with Jev's variance added.
- **PASS** is RETRACTED if any pairing gives Haiku a significant win (LOSE) on accuracy, AUC,
  Brier or ECE. It is also RETRACTED if any Jev run fails part 1 of the pass rule (accuracy WIN
  over always-no, AUC interval above 0.5, Brier WIN over the base rate).
- **FEVER's second scoring** follows its bar: in any pairing whose Haiku run has rows flagged by
  adapter debug (rescaled, or zero-mass), the comparison is repeated with those rows dropped. A
  LOSE in either scoring counts. The committed H1 has 0 flagged rows.
- **Accuracy** is committed as TIE in both sets. It is reported as a count of WIN / TIE / LOSE
  pairings, and only a LOSE matters (through PASS).
- **Headroom** for accuracy not-LOSE, from J1 x H1: the fewest answer changes in either arm that
  turn it into a LOSE, each placed adversarially. SciFact 18, FEVER 9. The bootstrap verdicts have
  no row-count headroom, so the pairing rule alone decides them.
- **Described, not ruled on:** decision flips at > 0.5, rows moved by more than 0.10, mean absolute
  noul change between runs of the same arm, and each arm's metric range across its runs.

Any retraction gets a `NEGATIVE_EVIDENCE.md` row with a retry condition. It is reported to the
owning units' author (ScoreSST5) and to ReadmeStrangerRun, who owns the README's citations. No
other unit's receipt is edited.

**NO-CLAIM.** Four Jev runs (one not at an independent time) and three Haiku runs per set, within
about an hour, one wording, one Jev version, one adapter version and one Haiku model. This measures
run-to-run variance, not variance across days, prompts or versions.

## Result (live, 2026-09-24 03:28-03:30 UTC, bar at `5167fe8`)

Six new runs: 2,400 calls (FEVER Haiku 2 x 400; Jev 2 x 400 on each set), 2,400 answered, 0 failed,
0 resume passes. Every Jev row reports `jev-1.13.0` and every Haiku row `anthropic/claude-haiku-4-5`.
Each new run's input tokens equal its arm's run 1 on every row (SciFact Jev 293,734; FEVER Jev
158,899; FEVER Haiku 231,100 per run), so the prompts were identical. The adapter flagged 0 FEVER
Haiku rows (rescaled or zero-mass) in all three runs, so FEVER's second scoring never triggered.
New rows (sha256 prefixes): SciFact `rows-jev-run2` `5e9f521b`, `rows-jev-run3` `603f0558`; FEVER
`rows-jev-run2` `e52ae71a`, `rows-jev-run3` `f8fbafc8`, `rows-haiku-run2` `2d21c3f5`,
`rows-haiku-run3` `a3b1ebc1`. Re-score, no key (about 60 s, 72 bootstraps):
`python3 work/noul-variance/score.py`.

**Verdict per metric per set** (12 pairings each: Jev J1, JR, J2, J3 x Haiku H1, H2, H3):

| Set | Metric | Committed (J1 x H1) | WIN pairings | LOSE pairings | Under the bar |
|---|---|---|---:|---:|---|
| SciFact | accuracy | TIE (19 vs 9) | 0 (12 TIE) | 0 | TIE throughout |
| SciFact | AUC | WIN | 8/12 | 0 | **RETRACTED** (as R89) |
| SciFact | Brier | WIN | **12/12** | 0 | **HOLDS** |
| SciFact | ECE | WIN | 5/12 | 0 | **RETRACTED** (as R89) |
| SciFact | PASS | PASS | every Jev run passes part 1 | 0 | **HOLDS** |
| FEVER | accuracy | TIE (6 vs 3) | 0 (12 TIE) | 0 | TIE throughout |
| FEVER | AUC | WIN | 4/12 | 0 | **RETRACTED** (new) |
| FEVER | Brier | WIN | 9/12 | 0 | **RETRACTED** (new) |
| FEVER | ECE | WIN | **12/12** | 0 | **HOLDS** |
| FEVER | PASS | PASS | every Jev run passes part 1 | 0 | **HOLDS** |

Every pairing's full intervals are in the scorer's output. The pattern:
- **SciFact AUC** is TIE with every Jev run against H2 (e.g. J1 x H2 −0.0021 to +0.0393) and WIN
  against H1 and H3.
- **SciFact ECE** is WIN against H1 on all four Jev runs, and TIE in 7 of the 8 pairings against H2
  and H3.
- **FEVER AUC** is WIN only in J1 x H1, J1 x H2, JR x H1 and J3 x H1.
- **FEVER Brier** is TIE in the three pairings with J1, JR and J3 against H3, the best Haiku run
  (Brier 0.0556). J2 x H3 is WIN with an upper bound of −0.00001, the thinnest WIN in the table.
- **SciFact Brier and FEVER ECE** clear 0 on every pairing: the least-good SciFact Brier interval
  is −0.0393 to −0.0050, and FEVER ECE is −0.0345 to −0.0019.

No retracted metric ever turns into a Haiku win. Every interval's midpoint favours Jev.

**Where the variance comes from.** Jev barely moves between runs. On SciFact the four Jev runs
differ by 0 to 2 decisions, and the mean |noul change| is 0.006 to 0.008. On FEVER they differ by
0 to 3 decisions, mean change 0.004. Jev's metric ranges are AUC 0.001 / 0.004, Brier 0.0006 /
0.0003 and ECE 0.0037 / 0.0019 (SciFact / FEVER). Haiku moves more: 9 to 12 SciFact decisions and
4 to 7 FEVER decisions between runs, mean change 0.048 to 0.051 / 0.018 to 0.020. Its ranges are
AUC 0.011 / 0.005, Brier 0.0069 / 0.0026 and ECE 0.0145 / 0.0085. Most of the retractions come from
the incumbent's re-runs, but not all. With Haiku held at its committed H1 run, Jev's four runs
agree on every verdict on SciFact. On FEVER they agree except AUC: J2 x H1 is TIE, so Jev's
variance alone would have retracted FEVER AUC. Against H2, J1 alone is WIN on SciFact ECE and
FEVER AUC where JR, J2 and J3 are TIE. Against H3, J2 alone is WIN on FEVER Brier where the other
three are TIE. These metrics sit close enough to 0 that either arm's re-run can move them.

**Accuracy headroom was not approached.** SciFact pairings run from 17-20 Jev-only against 8-11
Haiku-only (headroom 18 changes to a LOSE). FEVER runs from 5-8 against 3-6 (headroom 9).

**Latency and tokens per new run** (p50 / p95 ms; input / output tokens): SciFact Jev 140 / 366 and
150 / 380 (293,734 / 8,000 each); FEVER Jev 134 / 312 and 132 / 289 (158,899 / 8,000 each); FEVER
Haiku 657 / 1,230 and 646 / 1,129 (231,100 / 4,763 and 4,807).

**Negative evidence.** FEVER AUC and Brier are `NEGATIVE_EVIDENCE.md` R90 with a retry condition.
SciFact AUC and ECE were already R89; this unit confirms them with Jev's variance added. The
verdicts went to ReadmeStrangerRun when they landed, and to ScoreSST5, who owns `jev-9er` and
`jev-wx5`. Their receipts are not edited.

**Spend.** 2,400 calls. Jev: 1,600 calls, 905,266 input / 32,000 output tokens. Haiku: 800 calls,
462,200 input / 9,570 output tokens, about $0.51 at $1 / $5 per million `[INFERENCE: list price,
not a bill]`. Jev's billed units were not read.

**Boundary (NO-CLAIM).** 4 Jev runs x 3 Haiku runs per set, all within about an hour. JR is not an
independent time slot. One wording, one Jev version, one adapter version (`adffc2e`), one Haiku
model. The retracted metrics are "not robust to re-runs", not "Haiku is as good": every pairing's
direction favours Jev. What survives is one calibration metric per set, SciFact Brier and FEVER
ECE. Awaiting a non-author spot-check before the bead closes.
