# Does the full Banking77 77-intent WIN hold on three runs of each arm? (bead `jev-384m`)

MaintFixes (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`, incumbent
Claude Haiku 4.5 through `system-one-adapter-python` at `adffc2e` in prompted-JSON mode.

## Preregistered (committed before the first rerun call)

**Why.** `jev-4jf` (`choice-banking77-full-20260924.md`) found a WIN on all 3,080 Banking77 test
queries across 77 intents: Jev 2,467 against Haiku-prompted 2,267, McNemar 326 vs 126,
p = 1.7e-21, PASS. That came from one run per arm. `R88` (Yelp) showed that one run of each arm
can mislead: there, 3 of 9 pairings were WIN. The README states this win, so it gets the same
3 x 3 check as the other published wins (`jev-qbc`, `jev-x5k`, `jev-hg8`, `jev-91u`). The margin
is large, so the expected outcome is HOLDS. That expectation does not change the rule.

**What runs.** Everything is unchanged from `jev-4jf`: the same 3,080 rows (`full.jsonl`), the
same single 77-option Choice (state, question and labels built by `run.py`), and the same settings.
Only the output paths are new, and no committed row file is touched.
- **Jev, runs 2 and 3:** `run.py --set full --out work/choice-banking77/rows-full-jev-run{2,3}.jsonl jev`
  (official `typesafe_sdk`, `jev-1.13.0`).
- **Haiku, runs 2 and 3:** `run_prompted.py --out work/choice-banking77/rows-full-haiku-prompted-run{2,3}.jsonl`.
  This is `jev-4jf`'s declared second-preregistration fallback, with `structured_outputs=False`,
  one corrective retry for malformed JSON, `llm_answer_mode="probabilities"` and normalized
  probabilities. The only code change in this commit is the `--out` flag on `run_prompted.py`
  (the same shape `jev-qbc` gave `run.py` in `8851fcd`). The default path is unchanged.
- **Concurrency:** the four runs go at once, as four processes, each at the runners' own
  `CONCURRENCY = 8`, the same as `jev-4jf`. Latency is client wall clock under that load and is
  descriptive.
- **Resumes:** each runner resumes ids that lack an answer. A run with more than 1% failed rows
  (30, `jev-4jf`'s limit) after resuming is NOT-SCORED.

**Scorer, keyless:** `python3 work/choice-banking77/variance_full.py`. It imports this unit's
`score.py` (`arm_stats`, `mcnemar_exact`, `is_flat`, and the `FEASIBLE`, `MARGIN_PP` and `ALPHA`
constants) and applies `jev-4jf`'s verdict rule unchanged: feasibility floor 50%, the constant
40/3,080, a 3.0 pp margin and McNemar exact. It exits 1 unless run 1 x run 1 first reproduces the
committed numbers. Run before any rerun call, it printed: `run 1 x run 1 reproduces jev-4jf: yes
(Jev 2467, Haiku 2267, McNemar 326 / 126, p = 1.7e-21, WIN)`.

**Headroom from the committed run** (`--bar`). The WIN ends after **151** Haiku answer changes
(4.9% of 3,080), each turning a Jev-only row into both-correct or a both-wrong row into
Haiku-only. The WIN ends when b <= c or McNemar p >= 0.05. A LOSE needs Haiku to gain 293
correct answers, to above 2,559.

**R1, decides: all 9 pairings** (Jev run j against Haiku run h, j and h in 1..3), each scored by
`jev-4jf`'s rule:
- **HOLDS:** WIN in 9/9 pairings. The README sentence stands, and a "held on three runs of each
  arm, 9/9 pairings" clause may be added.
- **DOWNGRADED:** WIN in 5 to 8 of 9, with no LOSE and no NOT-SCORED. The headline becomes "Jev
  routes more correctly in direction, and significantly in a majority of pairings, not all". PASS
  is kept.
- **RETRACTED to NON-INFERIOR:** WIN in fewer than 5 of 9, with no LOSE and no NOT-SCORED. PASS is
  kept.
- **PASS RETRACTED:** any pairing is LOSE or NOT-SCORED.
- Any outcome other than HOLDS gets a `NEGATIVE_EVIDENCE.md` row with a retry condition. No
  wording, option list, margin or threshold changes after an answer is seen.

**R2, describes: flips.** For each pair of runs of the same arm, count the rows whose chosen intent
differs, and compare it with the 151-row headroom.

**Also reported, descriptive.** Per run: answered, failed, correct, accuracy, p50/p95 latency,
input/output tokens, and flat (uniform) Haiku rows. Per pairing, as in `jev-4jf`: McNemar with
Haiku's flat rows dropped, and with them credited to Haiku.

**Stated before running:** 6,160 Jev calls and 6,160 Haiku calls (12,320), plus resumes of failed
rows only. Spend is not capped (AGENTS.md, Live Call Budget Gate) and is reported.
[INFERENCE] At `jev-4jf`'s token counts, the two Haiku runs cost about $43 at list price and the
two Jev runs about $0.25.

**NO-CLAIM.** Three runs per arm within one evening, with one Jev version, one Haiku version, one
adapter version, one wording and undescribed options. The Haiku arm is the prompted-JSON fallback,
not native structured output, which Anthropic rejects for this grammar. HOLDS would show the win is
stable across these runs, not that it transfers to other prompts or models.

## Results (partial, 2026-09-24): Jev complete, Haiku BLOCKED until the provider cap lifts

**Status: no verdict.** All four runs started together at 03:43Z, after the bar `eed9fc3`.
- **Jev, runs 2 and 3:** finished, 3,080/3,080 answered each, 0 failed.
- **Haiku-prompted, runs 2 and 3:** stopped after 290 and 284 answers. Every later request
  returned, verbatim: `TypeSafeBadRequestError: 400 You have reached your specified API usage
  limits. You will regain access on 2026-10-01 at 00:00 UTC.` That is Anthropic's account-level
  spend cap, fleet-wide, and not a Haiku or harness failure. It refused 2,790 rows (run 2) and
  2,796 rows (run 3). Each refused row is recorded in the row file as an `error` row carrying that
  message, which marks the row NOT_RUN.
- **Nothing retried, nothing rerouted.** No other provider stood in for Haiku (the `jev-r3b`
  precedent). Raising the cap is Joshua's call.
- **Resuming:** once access returns, the same two commands (`run_prompted.py --out
  …-run{2,3}.jsonl`) resume exactly the refused ids. The runners skip ids that already have an
  answer.

**Scorer change after data, declared.** The bar applies NOT-SCORED to a run with more than 30
failed rows "after resuming". These runs cannot resume yet. As first run, the scorer would still
have read them as NOT-SCORED and printed "PASS RETRACTED", which is wrong for a run that was
refused before it could finish. `variance_full.py` now marks a pairing **BLOCKED** when an arm's
failed rows exceed the limit and every one of them carries the cap message. Any BLOCKED pairing
makes the whole unit PENDING, with no verdict. R2 flips are now counted over ids answered in both
runs. No rule changes for completed runs, and run 1 x run 1 still reproduces `jev-4jf` exactly.

**Per run** (`python3 work/choice-banking77/variance_full.py`, keyless). Latency is client wall
clock with four runs going at once.

| Run | Arm | Answered | Failed | Correct | Accuracy | p50 / p95 ms | Tokens in / out |
|---|---|---:|---:|---:|---:|---|---|
| 1 (`jev-4jf`) | Jev | 3,080 | 0 | 2,467 | 80.1% | 153 / 299 | 2,943,330 / 2,323,516 |
| 2 | Jev | 3,080 | 0 | 2,472 | 80.3% | 179 / 398 | 2,943,330 / 2,323,504 |
| 3 | Jev | 3,080 | 0 | 2,455 | 79.7% | 168 / 375 | 2,943,330 / 2,323,505 |
| 1 (`jev-4jf`) | Haiku-prompted | 3,080 | 0 | 2,267 | 73.6% | 3,967 / 7,074 | 6,400,493 / 3,020,130 |
| 2 | Haiku-prompted | 290 | 2,790 cap-refused | (partial) | | 3,976 / 7,135 | 601,682 / 282,144 |
| 3 | Haiku-prompted | 284 | 2,796 cap-refused | (partial) | | 3,978 / 7,182 | 588,789 / 278,956 |

**Pairings scorable now: 3 of 9, all against Haiku run 1, all WIN** under `jev-4jf`'s rule:

| Jev run | Haiku run | Jev | Haiku | McNemar | p | verdict |
|---|---|---:|---:|---|---:|---|
| 1 | 1 | 2,467 | 2,267 | 326 / 126 | 1.7e-21 | WIN |
| 2 | 1 | 2,472 | 2,267 | 328 / 123 | 1.4e-22 | WIN |
| 3 | 1 | 2,455 | 2,267 | 315 / 127 | 1.6e-19 | WIN |

With Haiku's 5 flat rows dropped or credited, each of the three stays WIN (largest p 2.1e-18).
The other 6 pairings are BLOCKED. The scorer prints their McNemar counts, but those counts score
cap-refused rows as wrong and mean nothing.

**R2, Jev.** Chosen intent differs between Jev runs on 40, 44 and 48 of 3,080 rows, against the
151-row headroom. Jev's accuracy spans 2,455 to 2,472. The Haiku flips (19 of 290 and 24 of 284
answered in both with run 1) are too partial to read.

**Spend so far.** 6,160 Jev calls: 5,886,660 input / 4,647,009 output tokens. 574 answered Haiku
calls: 1,190,471 input / 561,100 output tokens (adapter totals). [INFERENCE] At list price that is
about $4 for Haiku and $0.25 for Jev. The 5,586 cap-refused calls returned no tokens.

**NO-CLAIM.** No verdict on `jev-384m`. What the three scorable pairings show is only that Jev's
own run-to-run variance does not threaten the WIN against Haiku's committed run 1. They say nothing
about Haiku's variance, which is the half the cap blocked. The bead stays open, blocked on the cap.

## Non-author verification (Jev side only) — Verifier3

Verifier3 (background agent of pane 1, Anthropic model), 2026-09-24. Not the author. Scope was set
by pane 1: the two Jev reruns, Jev's run-to-run stability, and the bar-before-rows order. The Haiku
side is BLOCKED-until-cap (`jev-1y19`) and is not verified here. Everything ran in a fresh
`git clone --local` of `8ab637a` under `/tmp`. No call was made.

| Check | Command | Result |
|---|---|---|
| Bar precedes rows | `git show --stat eed9fc3 c7ae42d`; `stat -f %SB` on the live worktree's rerun files | bar and scorer are at `eed9fc3` (21:42:56 −0600). All four rerun files were born 21:43:20 to 21:43:24, and the Jev files were last written at 21:44:38 and 21:44:43. Rows were committed at `c7ae42d` (21:50:30). |
| Bar text unedited; scorer change | `git diff eed9fc3 c7ae42d` | the only removed receipt lines are `## Results` / `Pending the live runs.` The scorer change after data is declared. It adds a BLOCKED state, taken only when every failed row carries the cap message, and counts R2 flips over ids answered in both runs. Neither change can alter a pairing whose runs completed, and all three Jev × H1 pairings match an independent recompute. |
| Re-score reproduces (Jev side) | `python3 work/choice-banking77/variance_full.py` (rc 0, no key) | run 1 × run 1 reproduces `jev-4jf` (2,467 vs 2,267, 326/126, p = 1.7e-21, WIN), with headroom 151. Jev runs 2 and 3 are 2,472 and 2,455 of 3,080, with 0 failed. Jev × H1 is 328/123 (p = 1.4e-22) and 315/127 (p = 1.6e-19), both WIN, and each stays WIN with H1's 5 flat rows dropped or credited. The unit verdict line reads **PENDING, no verdict (6 BLOCKED, WIN in 3 of 3 scorable)**, as the receipt states. |
| Input tokens per Jev rerun | own script, per row | identical to run 1 on 3,080/3,080 rows for runs 2 and 3, and every row reports `jev-1.13.0`. |
| Independent recompute | own script, `choice == intent` | Jev correct: 2,467 / 2,472 / 2,455. Against H1: 326/126, 328/123, 315/127. Chosen-intent flips between Jev runs are 40, 44 and 48 of 3,080. All identical to the receipt, and every flip count is well under the 151-row headroom. |
| 10 seeded rows by hand | `random.Random(24)`: 685, 693, 747, 795, 894, 1568, 2387, 2747, 2792, 2917 | all three Jev runs choose the same intent on all 10, with confidences within 0.06. i 894 (`supported_cards_and_currencies`) and i 2917 (`cash_withdrawal_charge`) are wrong the same way in all three runs, so the errors are stable too. |
| Cap-refused rows recorded as NOT_RUN | own count | Haiku run 2 has 2,790 error rows and run 3 has 2,796. Every one carries the verbatim cap message, and each file covers all 3,080 ids exactly once. No retry and no substitute provider, as stated. |
| NO-CLAIM vs what ran | receipt | no verdict on `jev-384m`. The three scorable pairings only show that Jev's own variance does not threaten the WIN against Haiku's committed run 1. That matches the rows. |

**Verdict (Jev side): CONFIRMED** (clean-clone keyless re-score, `[oracle]`). The unit is correctly
PENDING. The bead stays open until the Haiku reruns can resume. Scratch left at `/tmp/v3-384m.itSx`
(not deleted).
