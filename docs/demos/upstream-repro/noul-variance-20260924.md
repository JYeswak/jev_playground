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

## Result

NOT_RUN. Filled in after the six new runs.
