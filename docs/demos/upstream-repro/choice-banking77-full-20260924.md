# Choice vs an LLM on the full Banking77 test split: 77 intents, N=3080 (bead `jev-4jf`)

ChoiceBanking77 (background agent of pane 1), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`.
Pattern: intent routing (`docs-mirror/typesafe/patterns/intent-routing.md`), the Choice primitive.
Follows `jev-k3k` (`choice-banking77-20260924.md`), which found a 10-intent WIN (384/400 vs 362/400,
p = 2.7e-5). Its NO-CLAIM names the full task as unmeasured; this run measures it.

## Preregistered (committed before the first call)

**Question.** Does one Jev Choice over all 77 Banking77 intents route the whole public test split
as accurately as Haiku 4.5 answering the same Choice through the vendor's adapter? Is its
confidence usable as a "send to a human" gate at 77-way?

**Corpus.** Same pinned source as `jev-k3k`: `PolyAI-LDN/task-specific-datasets` at
`9d081458ff52e53cf7e848f414e6e9344e4e6696`, `banking_data/test.csv`, sha256
`d12d6e3bc4c3103966ae786dc435913c0c563dfa328f5a3646d0e62cfeeb474d` (CC-BY-4.0). All 77 intents and
all 3,080 test rows (40 per intent), in file order, in `work/choice-banking77/full.jsonl`. Rebuild
and diff: `python3 work/choice-banking77/sample.py --set full --check`. The labels are PolyAI's.

**Option-count cap, checked before any call.** The vendor documents the cap verbatim:
"A Choice question accepts up to 255 options" (`docs-mirror/typesafe/primitives/choice.md:355`;
also `cookbooks/semantic_find.md:138`). The adapter has no upper cap in source, only a floor of two
criteria (`system_one_adapter/_schema.py:30-32, 64-65`). Its README gives Anthropic's default
output limit as 4,096 tokens (`README.md:61`). At `jev-k3k`'s measured ~10 output tokens per label,
77 labels need roughly 800, well inside that limit. **77 < 255, so the primary variant is the
single 77-option Choice in both arms, with no hierarchy.**

**Declared fallback, only if a cap fires.** If either arm rejects requests for option count, schema
size or output length, the error is kept verbatim (runner keeps 1,000 chars) and quoted here, and
no single-Choice verdict is reported for that arm. The fallback is the two-stage hierarchical
Choice (`docs-mirror/typesafe/cookbooks/hierarchical_classification.md`). Its grouping and bar
will be committed in a separate preregistration before any fallback call. No fallback call is made
under this bar.

**The question, identical in both arms, and the same as `jev-k3k`'s.** State
`{"customer_message": <text>}`. One Choice named `intent`, with instructions `"The primary intent of
this customer banking message"`. Criteria: the 77 intent names humanized (underscores to spaces,
lowercased, so `Refund_not_showing_up` becomes `refund not showing up`), in case-insensitive
alphabetical order, each undescribed (`None`). Runner: `work/choice-banking77/run.py --set full`.

**Arms** (settings unchanged from `jev-k3k`).
- **Jev:** `typesafe-sdk-python` `TypeSafeClient`, `model="jev-1.13.0"`, 8 concurrent.
- **Incumbent:** `system-one-adapter-python` with `anthropic/claude-haiku-4-5`,
  `llm_answer_mode="probabilities"`, `normalize_probabilities=True`, structured outputs, default
  `RetryPolicy`, default `max_tokens`, 8 concurrent. Each row also records the adapter's
  `n_retries`, `max_error`, and, when the adapter renormalized, the sum of Haiku's raw probability
  map (`rawSum`). That makes the cause of any flat answer observable instead of inferred.
- **Constant:** majority intent. All 77 are tied at 40, so always-`activate_my_card` scores 40/3080
  (1.3%). `prevalence-check.mjs` shows the same 40/3080 for its own tie pick.

**Primary measure.** Top-1 accuracy over all 3,080 rows. Rows still failing after one resume pass
are scored wrong and counted in a Failed column. A run with more than 1% failed rows (30) in either
arm is reported as failed, with no verdict. Wilson 95% intervals are reported.

**Paired test.** McNemar exact (two-sided binomial on discordant pairs) on per-row correctness.

**Pass rule, unchanged from `jev-k3k`.**
- **Feasibility:** an arm below 50% accuracy means the harness is being measured, not the model;
  no verdict.
- **LOSE** if Jev does not beat the constant, or trails Haiku by more than 3.0 percentage points
  (93 rows of 3,080).
- **WIN** if Jev has more Jev-only-correct than Haiku-only-correct rows and McNemar p < 0.05.
- **NON-INFERIOR** otherwise.
- Jev **PASSES** on WIN or NON-INFERIOR. On LOSE, a `NEGATIVE_EVIDENCE.md` row with a retry
  condition is written, and no wording, threshold, margin or option list is changed.

**Confidence-gated coverage (reported, thresholds fixed now: 0.5, 0.7, 0.9).** For each threshold:
coverage (rows at or above it, of 3,080) and accuracy among those rows. The primary table uses each
arm's own returned `confidence`. A descriptive table applies one formula,
`(p_max - 1/77)/(1 - 1/77)`, to both arms' probabilities. No verdict depends on coverage.

**Descriptive sensitivity, declared now** (it was added after the fact in `jev-k3k`). Rows an arm
answers with an exactly flat distribution are shown two ways: dropped from both arms, and credited
to that arm as correct, each with its McNemar p. The verdict uses the preregistered scoring only.

**Also reported.** Latency p50/p95 (nearest rank, client wall clock, 8 concurrent), summed tokens
in/out, the model string each response reports, and the top confusions per arm.

**Stated before running:** 3,080 Jev requests and 3,080 Haiku requests, plus retries of failed rows
only. Spend is not capped (AGENTS.md, Live Call Budget Gate) and is reported.

**NO-CLAIM.** One run per arm, one model version each, one prompt wording, undescribed options.
Not measured: options with written descriptions, run-to-run variance (bead `jev-qbc` measures
this separately), Haiku in discrete mode, other LLMs, and published Banking77 fine-tuned
state of the art, which trains on the train split.

## Results

Pending: no call has been made at the commit that introduces this section.
