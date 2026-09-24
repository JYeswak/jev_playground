# Choice vs an LLM on public intent routing: Banking77, 10 intents (bead `jev-k3k`)

ChoiceBanking77 (background agent of pane 1), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`.
Pattern: intent routing (`docs-mirror/typesafe/patterns/intent-routing.md`), the Choice primitive.

## Preregistered (committed before the first call)

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

Pending: no call has been made at the commit that introduces this section.
