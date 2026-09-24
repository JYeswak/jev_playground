# Top-k recall on the full Banking77 test split: does a short list cover the truth? (bead `jev-zfn`)

ChoiceBanking77 (background agent of pane 1), 2026-09-24. Offline lane: no calls. Everything is
computed from rows already committed by `jev-4jf`.

## Preregistered (committed before the scorer is first run on the real rows)

**Question.** At 77 intents, flat Jev picks the right intent first 80.1% of the time (`jev-4jf`).
No confidence cut made unattended routing safe, and a keyword hierarchy was worse (`jev-5fm`, R85).
The remaining design question for a routing tool: if the router shows a human a short list, how
often does that list contain the true intent, for Jev and for Haiku?

**Rows (committed, not re-run).** `work/choice-banking77/rows-full-jev.jsonl` (`jev-1.13.0`, frozen
at `3c473ae`) and `rows-full-haiku-prompted.jsonl` (Haiku 4.5 via the adapter, prompted JSON,
`5839235`), both over the 3,080 rows of `full.jsonl`. Every row carries the full 77-label
probability map. The scorer, the synthetic-row smoke test, and this bar were written without
computing any top-k number from these rows.

**Rank rule, fixed now (pessimistic on ties).** The truth's rank is 1 + the number of other labels
whose probability is >= the truth's. A tie never helps. A flat distribution misses at every k < 77.
Top-1 under this rule can differ from the committed `choice` only when the top probability is tied.
The scorer prints both.

**Measures.**
- **Recall at k in {1, 2, 3, 5}:** the share of rows whose truth rank is <= k, of 3,080, with a
  Wilson interval, for each arm.
- **Paired, per k:** McNemar exact on hit/miss, Jev vs Haiku. Holm-adjusted across the four k, and a
  difference is claimed only when the Holm p < 0.05.
- **Smallest k at which recall reaches 95%**, for each arm (descriptive).
- **Zero-mass Haiku rows** (`rawSum == 0`, where the adapter turned an all-zero map into uniform):
  every table is shown on all 3,080 rows, and again with those rows dropped from both arms.

**Short-list curve, thresholds fixed now: 0, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.01.** Policy at
threshold t:
- If the arm's own returned `confidence` is >= t, auto-route its top-1.
- Otherwise show a human that arm's top 3.

For each t the curve reports: rows auto-routed, how many of those are correct, **wrong auto-routes**
(the costly failure), rows sent to a human, how often the truth is in the list shown, and total
success (auto correct plus truth in list), of 3,080. t = 0 is always auto; t = 1.01 is always a
list. "Success" on the human branch assumes the human picks the truth when it is shown. That is an
upper bound, not a measurement.

**Decision, fixed now.** A top-3 short list is worth building into the routing tool if Jev's top-3
recall on all 3,080 rows is >= 95%. Otherwise it is NOT SUFFICIENT as the only fallback.
Jev-vs-Haiku differences are claimed only at Holm p < 0.05. Recall at k is not a user study.

**Re-score:** `python3 work/choice-banking77/score_topk.py` (stdlib, no key).

**NO-CLAIM.** One run per arm, one prompt wording, undescribed options. The human branch is modeled,
not observed. Not measured: list orderings other than by probability, list lengths other than 3 on
the curve, and how actual reviewers behave.

## Results

Pending: the scorer has not been run on the committed rows at the commit that introduces this
section.
