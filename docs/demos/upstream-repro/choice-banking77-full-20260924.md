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

## Second preregistration: the cap fired (committed before any prompted-mode call)

**What happened under the first bar (`909278f`).** The Jev arm answered 3,080/3,080 with 0 failed
rows (`rows-full-jev.jsonl`, committed with this section). The scorer was not run on those rows
before this commit, so Jev's accuracy was not known when this variant was chosen. The Haiku arm
with native structured outputs was rejected on every request. All 993 requests sent before the
run was cancelled got the same response, verbatim:

> `TypeSafeBadRequestError: 400 The compiled grammar is too large, which would cause performance
> issues. Simplify your tool schemas or reduce the number of strict tools.`

(`rows-full-haiku.jsonl`, 993 error rows, kept as the cap's evidence. The run was cancelled because
the rejection was deterministic.) Under the first bar there is **no single-Choice verdict for the
structured-output Haiku arm**, as declared.

**Declared deviation from the first bar's fallback.** The first bar named the two-stage
hierarchical Choice as the fallback. The cap that fired is not an option-count cap: 77 is under the
vendor's documented 255, and Jev answered every row. It is Anthropic's limit on the compiled
constrained-decoding grammar for a strict schema with 77 probability properties. A hierarchy would
change the question for both arms. Turning off native structured output for Haiku alone keeps the
question identical. This variant is therefore run instead, and hierarchical is not run under this
bead (see NO-CLAIM).

**The variant.** `work/choice-banking77/run_prompted.py`: same state, same single 77-option
Choice, same adapter, model and `probabilities` mode, `normalize_probabilities=True`, default
`RetryPolicy`, 8 concurrent. The only differences are `structured_outputs=False` (the adapter puts
the output JSON schema in the system prompt and validates the reply) and
`n_retry_malformed_structure=1` (one corrective retry on malformed output; its tokens are counted).
Rows: `rows-full-haiku-prompted.jsonl`. A row that is still malformed or failing after that retry
and one resume pass is scored wrong.

**Bar, unchanged in every other respect.** Jev's rows are the ones committed here, not re-run. The
pass rule, 3.0 pp margin, McNemar test, 50% feasibility floor, 1% failed-row limit (30), coverage
thresholds (0.5, 0.7, 0.9) and the declared flat-row sensitivity all apply exactly as in the first
bar, to Jev vs Haiku-prompted. Score: `python3 work/choice-banking77/score.py --set full-prompted`.

## Results

Run 2026-09-24, 02:4x to 03:0xZ. Jev: 3,080/3,080 answered on the first pass under `909278f`, with
0 failed rows. Haiku (prompted JSON, second bar `3c473ae`): 3,080/3,080 answered, 0 failed rows.
The run was resumed several times after the harness stopped earlier processes (558 rows were done
before the final supervised process), and each id appears once. Rows: `rows-full-jev.jsonl` and
`rows-full-haiku-prompted.jsonl`. Re-score with no key:
`python3 work/choice-banking77/score.py --set full-prompted`.

| Arm | Correct | Accuracy | Wilson 95% | p50 / p95 latency | Tokens in / out |
|---|---:|---:|---|---|---|
| Jev `jev-1.13.0` (3,080 of 3,080 responses report it) | **2,467/3,080** | **80.1%** | 78.7-81.5% | 153 / 299 ms | 2,943,330 / 2,323,516 |
| Haiku 4.5, adapter, prompted JSON | 2,267/3,080 | 73.6% | 72.0-75.1% | 3,967 / 7,074 ms | 6,400,493 / 3,020,130 |
| Haiku 4.5, adapter, native structured output | 0 answered: 993/993 rejected with the grammar cap above | | | | |
| Constant: always-`activate_my_card` | 40/3,080 | 1.3% | | | |

**Paired (Jev vs Haiku-prompted):** both correct 2,141, Jev-only 326, Haiku-only 126, McNemar exact
p = 1.7e-21.

**Confidence-gated coverage, each arm's own `confidence` (thresholds fixed in the first bar).**
Cell = rows at or above the threshold, of 3,080, then accuracy among them.

| Arm | >= 0.5 | >= 0.7 | >= 0.9 |
|---|---|---|---|
| Jev | 2,930 (95.1%), 82.6% | 2,581 (83.8%), 87.4% | 2,094 (68.0%), 92.5% |
| Haiku-prompted | 2,595 (84.3%), 78.7% | 2,450 (79.5%), 80.3% | 1,911 (62.0%), 86.4% |

The descriptive single-formula table (`(p_max - 1/77)/(1 - 1/77)`), printed by the scorer, differs
from Jev's own by at most 9 rows per cell, and Haiku's rows are identical. So Jev's unpublished
confidence again behaves like the adapter's formula. At 77 intents, no threshold is a hands-off
gate: even at 0.9, Jev is wrong on 157 of the 2,094 rows it would auto-route (7.5%).

**Declared sensitivity.** 5 Haiku rows came back flat. In 4 of them Haiku's raw map summed to 0,
observed here via `rawSum` rather than inferred; the fifth was a model-asserted uniform. Dropping
those 5 rows: 2,466 vs 2,267 of 3,075, p = 2.5e-21. Crediting them to Haiku: 2,467 vs 2,272,
p = 2.5e-20. Both are WIN. Jev returned no flat rows.

**Adapter behaviour, observed.** Haiku's raw probability map needed renormalizing on 706 of 3,080
rows (raw sums from 0 to 1.95). 4 rows used the one corrective retry for malformed JSON, and 0
rows had a transient retry.

**Where each arm goes wrong** (scorer, top confusions). Both arms mostly confuse near-synonymous
intents. Jev: `get_physical_card` read as `change_pin` 31 times, `order_physical_card` as
`get_physical_card` 26, `reverted_card_payment?` as `declined_card_payment` 16,
`beneficiary_not_allowed` as `failed_transfer` 15, `why_verify_identity` as `verify_my_identity` 13.
Haiku: `get_physical_card` read as `passcode_forgotten` 26 times, `card_arrival` as
`card_delivery_estimate` 16, `card_swallowed` as `atm_support` 16.

**Verdict: WIN, PASS (second bar, `3c473ae`).** On the full public Banking77 test split, one Jev
Choice over 77 undescribed intent names routes 80.1% of 3,080 messages correctly: 6.5 points above
Haiku 4.5 answering the same Choice through the vendor's adapter (73.6%), McNemar p = 1.7e-21, at
about 1/26 of Haiku's median latency. Two findings qualify the headline:
- The single 77-option Choice does not run at all through the adapter's native structured-output
  mode for Haiku. Anthropic rejects the grammar, so the incumbent needed the prompted-JSON variant,
  a deviation declared in the second bar before any prompted call.
- Accuracy falls from 96.0% at 10 intents (`jev-k3k`) to 80.1% at 77. The gap to Haiku holds
  (+5.5 then +6.5 points), but 77-way routing is not accurate enough to act on without a gate or
  better-described options.

Under the first bar, the structured-output Haiku arm has no verdict, as declared.

**Spend.** Jev: 3,080 calls, 2,943,330 input / 2,323,516 output tokens. Haiku: 993 structured
calls rejected with a 400 (no tokens were returned; [INFERENCE] not billed), then 3,080 prompted
calls, 6,400,493 input / 3,020,130 output tokens (adapter totals, including the 4 corrective
retries). [INFERENCE] At the cookbook list prices in `docs-mirror/typesafe/llms-full.txt` (Haiku 4.5
$1.00/$5.00 per 1M; Jev listed at $0.042/$0.00 for `jev-1.12`, assumed unchanged for 1.13), that is
about $0.12 for Jev and $21.50 for Haiku. This is not a billing readout.

**Boundary / NO-CLAIM.** One run per arm (`jev-qbc` measured Jev run-to-run variance on the
10-intent set only), one model version each, one prompt wording, undescribed options. The Haiku
comparison uses prompted JSON, not native structured output. That setting may help or hurt Haiku,
and that effect is unmeasured. The hierarchical fallback named in the first bar was not run.
Latencies are client wall clock under 8 concurrent requests. Jev ran at the same time as the
rejected structured-output Haiku run, not the prompted one. The labels are PolyAI's and were not re-adjudicated. Not compared against
fine-tuned Banking77 models. A non-author re-score from the committed rows is pending, and the bead
stays open until then.

## Non-author verification — Verifier2

Verifier2 (background agent of pane 1, not an author of this unit), 2026-09-24. Clean
`git clone --local` at `5839235` in `mktemp -d`; no model call.

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Bar order | `git merge-base --is-ancestor` 909278f → 3c473ae → 5839235 | first bar `909278f` (02:31:48Z) before the Jev rows, which are first committed in `3c473ae` (02:34:07Z); second bar `3c473ae` before the prompted Haiku rows `5839235` |
| 2 | Bar text not edited after it was committed | `git diff 909278f 3c473ae` and `git diff 3c473ae 5839235` on this receipt | `3c473ae` only appends the second preregistration and rewords the Pending line; `5839235` only replaces that Pending line with Results. Lines 1-121 are unchanged since their commits |
| 3 | Scorer change at the second bar | `git diff 909278f 3c473ae -- work/choice-banking77/score.py` | only adds the `full-prompted` set (same Jev file, Haiku file `rows-full-haiku-prompted.jsonl`); no rule, margin or test changed; untouched in `5839235` |
| 4 | Prompted variant differs only as declared | read `run_prompted.py` against `run.py` | imports `run` for labels, instructions, model and concurrency; adapter call has `structured_outputs=False` and `n_retry_malformed_structure=1`, otherwise `probabilities` mode, `normalize_probabilities=True`, `RetryPolicy()`, as declared |
| 5 | Rows rebuild | `python3 work/choice-banking77/sample.py --set full --check` | "check: identical", 3080 rows, 77 intents x 40 |
| 6 | Re-score reproduces every headline number | `python3 work/choice-banking77/score.py --set full-prompted` | exit 0; Jev 2467/3080 (80.1%, 78.7-81.5), Haiku 2267/3080 (73.6%, 72.0-75.1), 0 failed each; p50/p95 153/299 and 3967/7074 ms; tokens as in the table; both 2141, Jev-only 326, Haiku-only 126, p = 1.71e-21; coverage tables as printed above (own vs formula differ by at most 9 rows: 2930/2939); 5 flat Haiku rows, dropped p = 2.47e-21, credited p = 2.45e-20; verdict WIN, PASS |
| 7 | My own recompute from the row files | correct = `choice == intent`, joined on `i`; exact binomial McNemar | 3080 unique ids per arm, 0 error rows, models `jev-1.13.0` and `anthropic/claude-haiku-4-5` only; 2467 vs 2267, 326 vs 126, p = 1.71e-21. Structured run: 993 rows, all errors, one distinct message (the grammar-cap 400 quoted above) |
| 8 | Row hand-check | 8 rows by `random.Random(20260924)` (i = 62, 594, 2238, 2288, 2329, 2584, 2706, 2873), both arms | every stored `choice` is the argmax of that row's stored map and maps back to the source intent id; stored confidence tracks the top probability; `Refund_not_showing_up` rows (1760, 1761) come back as the original id in both arms. Rows 62 ("I found my card, I would like to reactivate it", label `card_linking`) and 2706 (label `balance_not_updated_after_bank_transfer`) are wrong in both arms, both picking the same near-synonym |

**Verdict: CONFIRMED** at `[oracle]` level (committed rows, clean clone, N = 3080 per arm,
`jev-1.13.0` vs Haiku 4.5 prompted, 2026-09-24): WIN, PASS under the second bar `3c473ae`, with
the first bar's structured Haiku arm correctly left without a verdict. Not checkable from files: the
claim that the scorer was not run on the Jev rows before the second bar was chosen (commit order
allows it; nothing records it), and the prompted run's start time (rows carry no timestamps). No
live call repeated; the hierarchical fallback was not run by anyone.
