# Hierarchical Choice vs flat on the full Banking77 test split (bead `jev-5fm`)

ChoiceBanking77 (background agent of pane 1), 2026-09-24. Live lane, Jev pinned `jev-1.13.0`.
Pattern: intent routing via the vendor's hierarchical-classification cookbook
(`docs-mirror/typesafe/cookbooks/hierarchical_classification.md`).

## Preregistered (committed before the first call)

**Question.** On all 3,080 Banking77 test rows, flat 77-way Jev routes 80.1% correctly (`jev-4jf`,
rows `work/choice-banking77/rows-full-jev.jsonl`, frozen at `3c473ae`). The vendor's recipe for
large label sets is a hierarchy: first a parent Choice, then a child Choice. Does it route more
rows correctly than flat, and at what cost in calls, tokens and latency per query?

**Corpus.** `work/choice-banking77/full.jsonl`, the same 3,080 rows and 77 intents as `jev-4jf`
(pinned PolyAI source, sha256 `d12d6e3b...`, rebuild with `sample.py --set full --check`).

**Grouping rule, fixed now** (`GROUP_RULES` in `work/choice-banking77/run_hier.py`; its output is
committed as `work/choice-banking77/hierarchy.json`). An ordered keyword rule over the dataset's own
intent names: the first matching pattern (case-insensitive) assigns the parent, and any unmatched
intent goes to `account and other`.

| Order | Parent | Pattern | Size |
|---:|---|---|---:|
| 1 | top ups | `top_?up\|topping_up` | 10 |
| 2 | cash and atm | `cash\|atm` | 8 |
| 3 | transfers | `transfer\|beneficiary\|receiving_money` | 11 |
| 4 | exchange and currencies | `exchange\|currenc\|fiat` | 6 |
| 5 | payments charges and refunds | `payment\|refund\|charge\|transaction\|direct_debit` | 10 |
| 6 | identity and security | `identity\|verify\|source_of_funds\|pin\|passcode\|compromised\|lost_or_stolen` | 10 |
| 7 | cards | `card` | 16 |
| - | account and other | (no match) | 6 |

Eight parents, 77 intents, no singleton parent. **Disclosure:** the author had seen flat Jev's top
confusions (`jev-4jf` receipt) before writing this rule. Most of those pairs share a parent under it
(`order_physical_card`/`get_physical_card`, `reverted_card_payment?`/`declined_card_payment`,
`beneficiary_not_allowed`/`failed_transfer`, `why_verify_identity`/`verify_my_identity`). The largest
pair, `get_physical_card`/`change_pin`, crosses parents (cards vs identity and security). No
per-row outcome of the hierarchical method is known.

**The questions.** State `{"customer_message": <text>}`, the same as flat. Every Choice uses flat's
instructions, `"The primary intent of this customer banking message"`, so the hierarchy is the only
change. **Root:** a Choice over the 8 parent names, each described by its member intents' humanized
names joined with ", ". **Child:** a Choice over the parent's member intents, humanized and
undescribed, as in flat. Each Choice is its own request with its own single question.

**Search** (the cookbook's method at depth 2, beam width K = 3, EPSILON = 1e-9). Per query, one root
call, then one child call in each of the root's top 3 parents, the three sent in parallel (4 calls
per query). The runner stores all four distributions. `work/choice-banking77/score_hier.py` computes
two routes from them offline:
- **Beam K=3 (primary):** the leaf with the highest geometric-mean edge probability
  `sqrt(p_parent * p_child)` across the three expanded parents.
- **Greedy (secondary):** the root's top parent, then that parent's top child.

**Measures.** Top-1 accuracy over all 3,080 rows, with a Wilson interval. A query that still fails
after one resume pass is scored wrong, and more than 1% failed (30) means no verdict. Also reported:
parent-step accuracy (true parent ranked first, and in the top 3, which is the beam's ceiling), and
per query the calls, mean tokens in/out, and latency p50/p95. Beam latency is the query's wall
clock. Greedy latency is the sum of its two calls' client times. Flat latency is its single call.

**Paired test and verdict (beam vs flat, McNemar exact on per-row correctness).**
- **BEATS FLAT** if beam has more beam-only-correct than flat-only-correct rows and p < 0.05.
- **WORSE THAN FLAT** if the reverse holds with p < 0.05.
- **NO DIFFERENCE** otherwise.
- The hypothesis "hierarchical beats flat" is **SUPPORTED** only on BEATS FLAT. Otherwise it is
  **REFUTED**, and a `NEGATIVE_EVIDENCE.md` row with a retry condition is written. No rule, pattern,
  wording, K or threshold is changed after data.
- Beam below 50% accuracy means the harness is being measured: no verdict.
- Greedy vs flat and beam vs greedy are reported with their p-values, but no verdict rides on them.

**Confidence-gated coverage (reported, thresholds fixed now: 0.5, 0.7, 0.9).** For the hierarchy,
the gate score is the chosen path's geometric-mean edge probability (the cookbook's path score), for
beam and for greedy. For flat, two gates: the chosen leaf's probability (`p_max`) and flat's
returned `confidence`. Each cell is coverage of 3,080, then accuracy among covered rows. No verdict
rides on coverage.

**Caveat, stated before running.** The flat rows come from one earlier run. `jev-qbc` measured
Jev's run-to-run disagreement on the 10-intent set at about 2 in 400 choices. At 77-way it is
unmeasured, and it adds noise to the paired test in both directions.

**Stated before running:** 12,320 Jev calls (3,080 x 4), plus retries of failed queries only. No
Haiku arm. Spend is not capped and is reported.

**NO-CLAIM.** One grouping (a keyword rule over names, not a semantic taxonomy), depth 2, K = 3, one
run, one wording, undescribed children. Not measured: other groupings, other K, parent descriptions
other than member-name lists, and any LLM on the hierarchy.

## Results

Pending: no call has been made at the commit that introduces this section.
