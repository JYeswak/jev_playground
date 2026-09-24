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

The bar was committed at `d2f1b2a` (2026-09-24T03:41:27Z). The runs started at 03:41:40Z, and all
four new runs answered 750/750 on the first pass: 0 failed rows, no resume, 0 zero-mass Haiku rows. Rows
(sha256): `rows-jev-run2.jsonl` `2ac35f56…a18c12fe7`, `rows-jev-run3.jsonl` `33858964…f48c595cc`,
`rows-haiku-run2.jsonl` `5b7c3e75…a29ec0a`, `rows-haiku-run3.jsonl` `a345e4bd…ed5406`. To re-score with
no key (under 1 s): `python3 work/choice-clinc150/variance.py`.

| Run | Overall correct | Handled at peak ≥ 0.60 | In-scope right | OOS said none | p50 / p95 latency | Tokens in / out |
|---|---:|---:|---:|---:|---|---|
| J1 (committed) | 688 | 685 | 395/450 | 293/300 | 173 / 312 ms | 323,870 / 112,429 |
| J2 | 688 | 684 | 394/450 | 294/300 | 139 / 298 ms | 323,870 / 112,437 |
| J3 | 689 | 682 | 396/450 | 293/300 | 140 / 256 ms | 323,870 / 112,429 |
| H1 (committed) | 681 | 650 | 389/450 | 292/300 | 1,260 / 2,155 ms | 800,996 / 81,445 |
| H2 | 680 | 657 | 391/450 | 289/300 | 1,173 / 2,103 ms | 800,996 / 81,407 |
| H3 | 687 | 661 | 393/450 | 294/300 | 1,184 / 2,071 ms | 800,996 / 81,553 |

All 9 pairings, each with the worse-for-Jev label over the two Haiku readings (the readings never
differed, since no Haiku run had a zero-mass row):

| Pairing | Overall: Jev / Haiku, discordant, p | Label | Handled: Jev / Haiku, discordant, p | Label |
|---|---|---|---|---|
| J1 x H1 | 688 / 681, 21 vs 14, 0.311 | NON-INFERIOR | 685 / 650, 47 vs 12, 5.1e-6 | WIN |
| J1 x H2 | 688 / 680, 27 vs 19, 0.302 | NON-INFERIOR | 685 / 657, 45 vs 17, 5.0e-4 | WIN |
| J1 x H3 | 688 / 687, 19 vs 18, 1 | NON-INFERIOR | 685 / 661, 41 vs 17, 2.2e-3 | WIN |
| J2 x H1 | 688 / 681, 20 vs 13, 0.296 | NON-INFERIOR | 684 / 650, 46 vs 12, 8.2e-6 | WIN |
| J2 x H2 | 688 / 680, 26 vs 18, 0.291 | NON-INFERIOR | 684 / 657, 43 vs 16, 5.8e-4 | WIN |
| J2 x H3 | 688 / 687, 18 vs 17, 1 | NON-INFERIOR | 684 / 661, 41 vs 18, 3.8e-3 | WIN |
| J3 x H1 | 689 / 681, 22 vs 14, 0.243 | NON-INFERIOR | 682 / 650, 46 vs 14, 4.2e-5 | WIN |
| J3 x H2 | 689 / 680, 27 vs 18, 0.233 | NON-INFERIOR | 682 / 657, 43 vs 18, 1.9e-3 | WIN |
| J3 x H3 | 689 / 687, 20 vs 18, 0.871 | NON-INFERIOR | 682 / 661, 40 vs 19, 8.6e-3 | WIN |

**Rule applied.**
- The handled-at-0.60 WIN holds on **9/9** pairings: **STANDS**.
- The overall NON-INFERIOR holds on **9/9**: **STANDS**.
- No pairing is LOSE or NOT-SCORED, so the **PASS STANDS**.
- No retraction, so no `NEGATIVE_EVIDENCE.md` row.

**Descriptive: how much each arm moves between its own runs** (labels chosen over the 750 rows):

| Pair of runs | Answers that differ | Gate outcomes that differ |
|---|---:|---:|
| J1 vs J2 / J1 vs J3 / J2 vs J3 | 4 / 2 / 4 | 4 / 5 / 7 |
| H1 vs H2 / H1 vs H3 / H2 vs H3 | 45 / 36 / 41 | 68 / 59 / 56 |

**Verdict** (`[live]`, 3 runs per arm, 9 pairings, 2026-09-24). Both of jev-qw8's published verdicts
survive the all-pairings rule. This is the first headline tonight to hold where R88, R89 and R90 did
not.

- **Overall correct is a tie on every pairing.** The margin runs from +1 to +9 rows; the committed
  run's +7 sits near the middle.
- **The abstention WIN holds on all 9.** The margin runs from +21 (J3 x H3, p = 0.0086) to +35 rows,
  against a headroom of 17 changes on the committed run. It is also the widest margin of the nine,
  because H1 is Haiku's lowest handled run (650, vs 657 and 661).
- **Jev is about ten times steadier than Haiku between runs:** 2 to 4 answers change against 36 to 45.

**Spend.** 3,000 live calls, 0 failed. Jev: 1,500 calls, 647,740 input / 224,866 output tokens. Haiku:
1,500 calls, 1,601,992 input / 162,960 output. At Haiku 4.5's list price ($1 / $5 per million) the
Haiku runs come to about $2.42 [INFERENCE]. Jev's billed units were not read.

**Boundary.** One domain, 15 intents, one question, three runs per arm. Neither arm reached the
shippable bar in jev-qw8 (misroute ≤ 2% at ≥ 80% coverage), and this unit does not revisit that. The
run-to-run stability comparison is descriptive and was not preregistered. JevVariance's jev-pm3
full-CLINC150 files were not read, touched or measured. Before close, this needs a keyless re-score
from a fresh clone and a spot-check by someone other than the author.

## Non-author verification — Verifier3

Verifier3 (background agent of pane 1, Anthropic model), 2026-09-24. Not the author. Everything ran
in a fresh `git clone --local` of `035aa8f` under `/tmp`. No call was made.

| Check | Command | Result |
|---|---|---|
| Bar precedes rows | `git show --stat d2f1b2a 0516464`; `stat -f %SB` on the live worktree's rerun files | bar, `variance.py` and `run-variance.py` are at `d2f1b2a` (21:41:27 −0600). The four rerun files were born 21:41:42 to 21:43:41, all after it, and committed at `0516464` (21:46:26). |
| Bar text unedited | `git diff d2f1b2a 0516464 -- <receipt>` | the only removed line is `Pending the live runs.` |
| Same prompt despite a changed `run.py` | per-row comparison of input tokens | `run.py` was refactored after `2842340` for jev-pm3 (`--set`, `haiku-prompted`), and this unit did not edit it. Per-row input tokens are identical to the committed run on 750/750 rows for J2, J3, H2 and H3, so the subset prompt and options are unchanged. Every row reports the pinned model. |
| Re-score reproduces | `python3 work/choice-clinc150/variance.py` (rc 0, no key) | step 1 re-derives J1 × H1 (NON-INFERIOR 688/681, 21 vs 14; WIN 685/650, 47 vs 12, p = 5.13e-06), with headroom 17 / 30. Every number in the per-run and 9-pairing tables matches, as do the flip table (Jev 2–4 answers, Haiku 36–45). Verdicts: **handled WIN 9/9 STANDS, overall NON-INFERIOR 9/9 STANDS, PASS STANDS**. |
| Independent recompute | own script, `choice == intent` per run | overall correct J1–J3 688/688/689 and H1–H3 681/680/687, identical. |
| 10 seeded rows by hand | `random.Random(24)`: 171, 173, 186, 198, 223, 392, 596, 686, 698, 729 | Jev's three runs agree on the label for all 10, with peaks within 0.03. Haiku changes its label on 198 (`schedule_maintenance` → `last_maintenance` → `schedule_maintenance`, peaks 0.34/0.39/0.75) and on 729 (`oos` at 0.85, then `current_location` at 0.50, then `oos` at 0.95). On 198 Jev says `oos` at 0.58 in all three runs. That is below the 0.60 gate, so it is abstained in all three. All hand reads agree with the stored rows. |
| Zero-mass handling | scorer output and row fields | every Haiku rerun row records `probabilityError`/`rawSum`, and the scorer reports 0 zero-mass rows in all six runs. The two Haiku readings therefore coincide, as the receipt states. |
| NO-CLAIM vs what ran | receipt vs rows | one domain, 15 intents plus OOS, 3 runs per arm, one question. The jev-pm3 full set was not touched here. The receipt says the stability comparison was not preregistered. No retraction, so no NE row, which is correct. |

**Verdict: CONFIRMED** (clean-clone keyless re-score, `[oracle]`). Both jev-qw8 verdicts stand on
9/9 pairings. Scratch left at `/tmp/v3-kvw.UIPq` (not deleted).
