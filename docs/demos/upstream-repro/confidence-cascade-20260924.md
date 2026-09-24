# Confidence-routing cascade from committed rows: Jev first, Haiku below a cut (bead `jev-cav`)

ConfidenceCascade (background agent of pane 1), 2026-09-24. Offline lane: no model call is made.
Pattern: confidence-gated routing (`docs-mirror/typesafe/patterns/confidence-routing.md`), here
used to decide when to pay for a second, slower model instead of when to hand off to a human.

## Preregistered (committed before the scorer exists or any cascade number is computed)

**Question.** On rows where both arms already answered the same Choice, does a cascade that
answers with Jev when Jev's own `confidence >= t` and escalates to Haiku otherwise beat both
single arms: more rows right than either, and more rows right per unit of cost?

**Inputs, frozen.** Bead `jev-k3k` rows, committed: `work/choice-banking77/subset.jsonl` (400
Banking77 test rows, 10 intents), `rows-jev.jsonl` (Jev `jev-1.13.0`), `rows-haiku.jsonl` (Haiku
4.5 through `system-one-adapter-python`). Each row carries `choice`, `confidence`,
`probabilities`, `latencyMs` and `usage.{input,output}_tokens`. No row is re-run or edited.

**Already known before this bar (from `choice-banking77-20260924.md`).** Jev 384/400, Haiku
362/400, both-correct 359, Jev-only 25, Haiku-only 3. So the best any Jev-first cascade that takes
Haiku's answer can do is 387/400 (Jev plus the 3 Haiku-only rows), and only if it escalates
those 3 rows and no row Jev gets right that Haiku gets wrong. Prediction, stated now: the gain
over Jev alone is at most 3 rows, and it costs a Haiku call on every escalated row.

**Routing rule (policy A, primary).** For threshold `t`: if Jev's `confidence >= t`, answer with
Jev's `choice`; else escalate and answer with Haiku's `choice`. Jev always runs first, so an
escalated row pays for both calls.

**Grid, fixed now.** `t` in {0.00, 0.05, ..., 1.00} (21 values), plus `always` (escalate every
row). `t = 0.00` is Jev alone. Haiku alone (no Jev call) is reported as its own row.

**Metrics per grid point.**
- Correct / N and accuracy (a row is correct when the answering arm's `choice` equals the label).
- Escalated / N (share of rows sent to Haiku).
- Mean latency per request, ms: Jev's recorded `latencyMs`, plus Haiku's recorded `latencyMs` on
  escalated rows. This is a sequential-sum model of recorded wall clocks (both measured at 8
  concurrent, at different times), not a measured cascade.
- Mean tokens per request: Jev's input + output tokens, plus Haiku's input + output tokens
  (adapter totals) on escalated rows.
- Descriptive only, [INFERENCE]: dollars per 1,000 requests at the list prices the parent receipt
  used (Haiku 4.5 $1.00 in / $5.00 out per 1M tokens; Jev $0.042 in / $0.00 out per 1M, listed for
  `jev-1.12` and assumed for 1.13). Not a billing readout; no verdict uses it.
- Correct per unit cost: correct rows divided by mean latency (per second) and by mean tokens
  (per 1,000 tokens).
- Pareto marks: among all grid points and both single arms, a point is Pareto-efficient for a
  cost measure when no other point has at least its correct count at no more cost, strictly
  better on one. Marked separately for latency and for tokens.

**What counts as a useful cascade (primary, policy A, all 400 rows, flat rows scored as recorded).**
- **USEFUL** if some grid point with escalation share <= 25% (100 rows) has strictly more correct
  rows than the better single arm, **and** the 2-fold check below also gains at least one row over
  Jev alone out of fold.
- **BEATS BOTH PER UNIT COST** if some USEFUL point also has more correct rows per second of mean
  latency **and** per 1,000 mean tokens than each single arm.
- **NOT USEFUL** otherwise. If the most accurate point within the 25% cap is Jev alone, it says so.
- **2-fold check, against picking `t` in sample.** Fold A = rows with even `i`, fold B = odd `i`.
  On each fold pick the grid point (escalation <= 25% of that fold) with the most correct rows,
  ties to the lower escalation share; apply it to the other fold. Report summed out-of-fold correct
  against Jev alone on the same rows.
- Significance: McNemar exact, cascade vs Jev alone, at the in-sample best point. With a ceiling of
  3 rows no p below 0.05 is reachable (3 discordant rows give p = 0.25); the p is reported, not
  used.

**Flat Haiku rows (bead `jev-mly`).** 14 Haiku rows are an exactly uniform distribution
(confidence 0.0; argmax falls on the first label). The scorer finds them from the probabilities
(every value equal), not from a hard-coded list. Reported two ways: as recorded (primary, scored
wrong, as `jev-k3k` preregistered), and dropped from every arm (sensitivity). The verdict uses the
primary scoring; the sensitivity is shown beside it and cannot change the verdict.

**Policy B (secondary, descriptive, no verdict).** Same escalation, but after escalating keep
whichever answer carries the higher own-`confidence` (ties to Jev). This is a common cascade
design and is the one that would ignore a flat Haiku answer (confidence 0). The two arms'
confidence formulas differ (Jev's is unpublished; the adapter's is `(p_max - 1/k)/(1 - 1/k)`), so
comparing them is an assumption the parent receipt found roughly holds on this set.

**Full 77-intent repeat (bead `jev-4jf`).** If ChoiceBanking77 commits a finished prompted Haiku
run with its own score (`rows-full-haiku-prompted.jsonl`, second preregistration in
`choice-banking77-full-20260924.md`), the same grid, metrics, rule, 2-fold check and flat-row
sensitivity are applied to `full.jsonl` + `rows-full-jev.jsonl` + `rows-full-haiku-prompted.jsonl`,
with the escalation cap at 25% of 3,080 (770). A row an arm failed (no `choice`) counts as wrong;
a failed Jev row escalates. Those rows are not read before that commit.

**Re-score, no key:** `python3 work/confidence-cascade/cascade.py` (and `--set full` for the
repeat).

**NO-CLAIM.** Offline arithmetic on one recorded run per arm. The cascade's latency and tokens are
sums of separately recorded calls, not a deployed cascade. Ten alphabetical intents of 77. One
Haiku configuration (probabilities mode, adapter). Says nothing about cascading the other way
(Haiku first), about other second models, or about run-to-run variance.

## Results

Pending: the scorer is committed after this bar.
