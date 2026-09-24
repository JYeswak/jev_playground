# Choice vs an LLM on public intent routing: Banking77, 10 intents (bead `jev-k3k`)

ChoiceBanking77 (background agent of pane 1), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`.
Pattern: intent routing (`docs-mirror/typesafe/patterns/intent-routing.md`), the Choice primitive.

## Preregistered (committed at `a0ed3c1`, before the first call)

**Question.** Our only routing measurement so far (tool selection) lost to always-bash on our own
traffic. This asks whether one Jev Choice question routes public, human-labelled customer messages
to the right intent as well as an LLM answering the same Choice through the vendor's own adapter,
and whether its confidence is usable as a "send to a human" gate.

**Corpus.** Banking77 test split (Casanueva et al. 2020, CC-BY-4.0):
`PolyAI-LDN/task-specific-datasets` at `9d081458ff52e53cf7e848f414e6e9344e4e6696`,
`banking_data/test.csv`, sha256 `d12d6e3bc4c3103966ae786dc435913c0c563dfa328f5a3646d0e62cfeeb474d`,
3,080 rows, 77 intents. This is the file the Hugging Face loader `PolyAI/banking77` (revision
`90d4e2ee5521c04fc1488f065b8b083658768c57`, `banking77.py`) downloads; the HF datasets-server
refuses the dataset because it is script-based, so the source is pinned at the GitHub commit.

**Subset rule.** The 10 intents with the most test rows, ties broken alphabetically
(case-insensitive, because the source spells one intent `Refund_not_showing_up`), and every test
row of those intents. Every intent has exactly 40 test rows, so the rule reduces to the first ten
names alphabetically: `activate_my_card`, `age_limit`, `apple_pay_or_google_pay`, `atm_support`,
`automatic_top_up`, `balance_not_updated_after_bank_transfer`,
`balance_not_updated_after_cheque_or_cash_deposit`, `beneficiary_not_allowed`, `cancel_transfer`,
`card_about_to_expire`. 400 rows, 40 per intent, in `work/choice-banking77/subset.jsonl`. Rebuild
and diff: `python3 work/choice-banking77/sample.py --check` (fetches the pinned file, checks its
sha256). The labels are PolyAI's, not ours.

**Constant first.** Majority intent: every class is tied at 40, so always-`activate_my_card` scores
40/400 (10.0%) (`node work/jev-prevalence-first/prevalence-check.mjs
work/choice-banking77/subset.jsonl --truth intent` prints the same 40/400 for its own tie pick).

**The question, identical in both arms.** State `{"customer_message": <text>}`. One Choice named
`intent`, instructions `"The primary intent of this customer banking message"`, criteria the ten
intent names humanized (underscores to spaces, e.g. `card about to expire`), each undescribed
(`None`), so each option is read by its name alone, which is the bead's spec. Runner:
`work/choice-banking77/run.py`.

**Arms.**
- **Jev:** `typesafe-sdk-python` `TypeSafeClient`, `model="jev-1.13.0"`, 8 concurrent.
- **Incumbent:** `upstream/typesafe-ai/system-one-adapter-python` with `anthropic/claude-haiku-4-5`,
  `llm_answer_mode="probabilities"`, `normalize_probabilities=True`, structured outputs, default
  `RetryPolicy`, 8 concurrent.
- **Constant:** above.

**Primary measure.** Top-1 accuracy over all 400 rows. A row that fails after one resume pass is
scored wrong and counted in a Failed column. Wilson 95% interval beside each.

**Paired test.** McNemar exact (two-sided binomial on discordant pairs) on per-row correctness,
Jev vs Haiku.

**Pass rule, fixed now.**
- **Feasibility:** an arm below 50% accuracy means the harness is measured, not the model; no
  verdict is reported.
- **LOSE** if Jev does not beat the constant, or Jev accuracy is more than 3.0 percentage points
  below Haiku's (12 rows of 400).
- **WIN** if Jev has more Jev-only-correct rows than Haiku-only-correct rows and McNemar p < 0.05.
- **NON-INFERIOR** otherwise (within the 3.0 pp margin, not significantly better).
- Jev **PASSES** the bead on WIN or NON-INFERIOR. On LOSE the result goes to `NEGATIVE_EVIDENCE.md`
  with a retry condition, and no threshold, wording or margin is changed.

**Confidence-gated coverage (reported, thresholds fixed now).** At confidence >= 0.5, 0.7, 0.9:
coverage (rows at or above the threshold, of 400) and accuracy among those rows, using each arm's
own returned `confidence`. The two definitions differ: the adapter computes
`(p_max - 1/k)/(1 - 1/k)` (`system_one_adapter/_utils/confidence_metrics.py`), while Jev's formula
is not published (`docs-mirror/typesafe/confidence.md`). So a second, descriptive table applies that
one formula to both arms' returned `probabilities`. No verdict rides on coverage.

**Also reported.** Latency p50/p95 (nearest rank, client wall clock per request) and summed tokens
in/out per arm; the model string each response reports; the top confusions per arm.

**Stated before running:** 400 Jev requests and 400 Haiku requests, plus retries of failed rows
only. Spend is not capped (AGENTS.md, Live Call Budget Gate) and is reported below.

**NO-CLAIM.** 10 intents are not 77, and these ten are alphabetical, not chosen for difficulty
(one confusable pair: the two `balance_not_updated_after_*` intents). One model version per arm,
one run, one prompt wording, undescribed options. Says nothing about intents with descriptions,
about the full 77-way task, or about published Banking77 SOTA, which is trained on the train split.

## Results

Run 2026-09-24T02:2xZ, both arms 400/400 answered on the first pass, 0 failed rows, no resume.
Rows: `work/choice-banking77/rows-jev.jsonl`, `rows-haiku.jsonl` (each row carries the choice,
confidence, all ten probabilities, latency, tokens, and the model string the response reported).
Re-score with no key: `python3 work/choice-banking77/score.py`.

| Arm | Correct | Accuracy | Wilson 95% | p50 / p95 latency | Tokens in / out |
|---|---:|---:|---|---|---|
| Jev `jev-1.13.0` (400 of 400 responses report `jev-1.13.0`) | **384/400** | **96.0%** | 93.6-97.5% | 139 / 328 ms | 154,744 / 47,571 |
| Haiku 4.5 via the official adapter | 362/400 | 90.5% | 87.2-93.0% | 1,053 / 1,972 ms | 360,861 / 41,400 |
| Constant: always-`activate_my_card` | 40/400 | 10.0% | | | |

**Paired:** both correct 359, Jev-only 25, Haiku-only 3, McNemar exact p = 2.7e-5.

**Confidence-gated coverage, each arm's own `confidence` (thresholds fixed in the bar).** Cell =
rows at or above the threshold of 400, then accuracy among them.

| Arm | >= 0.5 | >= 0.7 | >= 0.9 |
|---|---|---|---|
| Jev | 387 (96.8%), 376/387 = 97.2% | 372 (93.0%), 369/372 = 99.2% | 348 (87.0%), 347/348 = 99.7% |
| Haiku | 376 (94.0%), 356/376 = 94.7% | 360 (90.0%), 347/360 = 96.4% | 315 (78.8%), 313/315 = 99.4% |

The descriptive table (one formula, `(p_max - 1/10)/(1 - 1/10)`, applied to both arms'
probabilities) is printed by the scorer. Haiku's rows are identical to the table above, since that
is the adapter's own formula; Jev's differ by at most one row per cell (388/349 covered at 0.5/0.9).
So Jev's unpublished confidence behaves like the adapter's formula on this set.

**Where each arm goes wrong** (scorer, top confusions). Jev: `beneficiary_not_allowed` read as
`balance_not_updated_after_bank_transfer` 9 times, `apple_pay_or_google_pay` as `automatic_top_up`
3 times. Haiku: `beneficiary_not_allowed` accounts for 18 of its 38 errors, sent to
`activate_my_card` (7), `cancel_transfer` (6) and `card_about_to_expire` (5). Many of that intent's
test rows are failed transfers or blocked crypto purchases that name no beneficiary, so both arms
struggle with them. Jev lands on the nearest transfer intent; Haiku lands on unrelated card intents.

**Descriptive, not preregistered: Haiku's flat answers.** 14 Haiku rows came back as an exactly
uniform distribution (0.1 on every label, confidence 0.0). The argmax tie falls on the first label,
`activate_my_card`, and none of the 14 were that intent, so all 14 are scored wrong. [INFERENCE]
Most likely Haiku returned an all-zero probability map, which `normalize_probabilities=True` turns
into uniform (`system_one_adapter/_utils/probability_normalization.py:69-72`): in effect, "none of
these". The rows do not keep the raw provider output, so this is not proven. Neither the verdict
nor the bar depends on this reading. Sensitivity, computed from the committed rows:

| Treatment of the 14 flat Haiku rows | Jev | Haiku | Jev-only / Haiku-only | McNemar p | Rule would say |
|---|---:|---:|---|---:|---|
| As preregistered: scored wrong | 384/400 | 362/400 | 25 / 3 | 2.7e-5 | WIN |
| Dropped from both arms | 374/386 | 362/386 | 15 / 3 | 0.0075 | WIN |
| Credited to Haiku as correct (most generous) | 384/400 | 376/400 | 15 / 7 | 0.13 | NON-INFERIOR |

(Jev answered 10 of those 14 rows correctly.) All three treatments pass the bar.

**Verdict: WIN, PASS.** Under the bar committed at `a0ed3c1`, one Choice question with ten
undescribed intent names routes this public Banking77 subset at 96.0% (384/400), 5.5 points above
Haiku 4.5 on the same Choice through the vendor's adapter (McNemar p = 2.7e-5), at about 1/8 the
median latency. Its confidence gate matches the vendor's routing pattern: at 0.7 it auto-routes 93%
of messages at 99.2% accuracy and sends 28 to a human. At the same 0.7 cut, Haiku auto-routes 90%
at 96.4%. Most of the accuracy gap comes from one intent (`beneficiary_not_allowed`) plus the 14
flat Haiku answers. With those credited to Haiku, Jev's lead shrinks to 2.0 points and is no
longer significant, which is why that row is shown.

**Spend.** 800 requests, 0 retries of failed rows. Jev: 400 calls, 154,744 input / 47,571 output
tokens. Haiku: 400 adapter calls, 360,861 input / 41,400 output tokens (adapter totals, including
any provider retries). [INFERENCE] At the cookbook list prices in `docs-mirror/typesafe/llms-full.txt`
(Haiku 4.5 at $1.00/$5.00 per 1M; Jev listed at $0.042/$0.00 for `jev-1.12`, assumed unchanged for
1.13), that is about $0.0065 for Jev and $0.57 for Haiku. Not a billing readout.

**Boundary / NO-CLAIM.** One run per arm, one prompt wording, one model version each, ten of 77
intents chosen by an alphabetical tie-break, not by difficulty. Not measured: the 77-way task,
options with written descriptions, run-to-run variance, Haiku in `discrete` answer mode, any other
LLM, calibration beyond the three coverage cuts, and cost from a bill. The flat-answer cause is
inferred, not observed. The labels are PolyAI's and were not re-adjudicated. A non-author re-score
from the committed rows is still pending, and the bead stays open until it is done.

## Non-author verification — VerifySST5

VerifySST5 (background agent of pane 1; not the author), 2026-09-24, keyless, from a fresh
`git clone --local` at `9519e94` into a temp dir. No live call made; spend $0.

| # | Check | Result |
|---|---|---|
| 1 | `env -u TYPESAFE_API_KEY -u ANTHROPIC_API_KEY python3 work/choice-banking77/score.py` in the clone | HOLDS. Jev 384/400 (96.0%, Wilson 93.6–97.5%), Haiku 362/400 (90.5%), constant 40/400; 0 failed rows either arm; paired both-correct 359, Jev-only 25, Haiku-only 3, McNemar exact p = 2.74e-05; `verdict: WIN`, `pass: PASS`. Both coverage tables, latency, tokens and top confusions match the Results section cell for cell. |
| 2 | `python3 work/choice-banking77/sample.py --check` | HOLDS. Pinned source verified (3,080 rows, 77 intents, 40 each), same ten intents, `subset rows=400`, `check: identical`. |
| 3 | Bar before data | HOLDS. `a0ed3c1` (20:23:53 −0600) is an ancestor of `3709ee6` (20:26:50 −0600); `a0ed3c1` has no `rows-*.jsonl`. `run.py`, `score.py`, `sample.py`, `subset.jsonl` are byte-unchanged between the two. The receipt diff changes one bar line, the heading ("committed before the first call" → "committed at `a0ed3c1`, before the first call"), and replaces the "Pending" line under Results; subset rule, arms, primary measure, McNemar, pass rule, 3.0 pp margin and coverage thresholds are unchanged. |
| 4 | Spot-read of the 28 discordant rows (independent recount from the rows, not via `score.py`) | HOLDS. 28 = 25 Jev-only + 3 Haiku-only. Every row's `intent` equals `subset.jsonl`; every stored `choice` equals the first argmax of its `probabilities` in criteria order (400/400 each arm). 10 of the 25 Jev-only rows are flat Haiku rows (below). The other 15 are mostly `beneficiary_not_allowed` messages about blocked transfers or crypto buys that Haiku sent to `cancel_transfer`/`card_about_to_expire`, plus `age_limit` (i = 45, 58) read as `card_about_to_expire`. The 3 Haiku-only rows (i = 216, 225, 394) are Jev picking the neighbouring transfer or top-up intent. Some PolyAI labels are debatable (i = 214 "What are the rules for transferring to a beneficiary?" is labelled `beneficiary_not_allowed`), as the receipt says; labels were not re-adjudicated here either. |
| 5 | The 14 flat Haiku rows | HOLDS. Exactly 14 Haiku rows have all ten probabilities equal (0.1), `confidence` 0.0, and stored `choice` `activate_my_card`: the first label in criteria order (`sorted(..., key=casefold)`), the adapter's `max(answers, key=probabilities.__getitem__)` tie result. None has truth `activate_my_card`, so all 14 score wrong. That follows the bar's rule: top-1 of an answered row, where only unanswered rows count as Failed. Jev is right on 10 of the 14 and has 0 flat rows. The sensitivity table re-derives exactly: dropped 374/386 vs 362/386, 15/3, p = 0.0075; credited 384/400 vs 376/400, 15/7, p = 0.134. |

Verdict: the WIN/PASS reproduces from committed files under an unedited bar. Re-score:
`python3 work/choice-banking77/score.py`. NO-CLAIM: this re-scores committed rows; it does not re-run
either model, measure run-to-run variance, or re-adjudicate PolyAI's labels. The cause of the flat rows
is still the receipt's [INFERENCE], not checked here.
