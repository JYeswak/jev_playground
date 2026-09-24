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

Bar committed at `cc559c6`; the scorer was written and first run after it. Level: offline
arithmetic on committed rows ([test]); no model call, $0 spend. Full output:
`work/confidence-cascade/out-subset.txt`. Re-score and diff, no key:
`python3 work/confidence-cascade/cascade.py | diff - work/confidence-cascade/out-subset.txt`.

### 10 intents, N = 400 (`jev-k3k` rows, `jev-1.13.0` vs Haiku 4.5 via the adapter, 2026-09-24)

The scorer reproduces the parent receipt's arms (Jev 384/400, Haiku 362/400) and finds the same
14 flat Haiku rows from the probabilities alone (Jev right on 10 of them).

**Policy A, primary, all 400 rows.** Selected grid points; every row of the grid is in the output
file. Latency and tokens are means per request; `$` is [INFERENCE] from list prices.

| t | Correct | Escalated | ms/req | tokens/req | $/1k req | correct per s | correct per 1k tok | Pareto |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 0.00 to 0.25 (Jev alone; no row escalates) | **384/400** | 0 | 163 | 506 | 0.016 | 2,362.6 | 759.2 | lat, tok |
| 0.30 | 383/400 | 2 (0.5%) | 168 | 511 | 0.023 | 2,282.0 | 749.8 | |
| 0.50 | 381/400 | 13 (3.2%) | 199 | 539 | 0.063 | 1,915.0 | 707.4 | |
| 0.70 | 377/400 | 28 (7.0%) | 241 | 576 | 0.116 | 1,565.7 | 654.2 | |
| 0.90 | 372/400 | 52 (13.0%) | 305 | 637 | 0.201 | 1,219.6 | 584.2 | |
| 0.95 | 370/400 | 63 (15.8%) | 340 | 665 | 0.241 | 1,088.6 | 556.7 | |
| 1.00 | 362/400 | 112 (28.0%) | 499 | 788 | 0.416 | 724.8 | 459.6 | |
| always | 362/400 | 400 (100%) | 1,350 | 1,511 | 1.436 | 268.2 | 239.5 | |
| Haiku alone | 362/400 | (no Jev call) | 1,187 | 1,006 | 1.420 | 304.9 | 360.0 | |

Accuracy falls monotonically as `t` rises: every escalation costs more and loses rows. The only
Pareto-efficient points, for latency and for tokens, are Jev alone (and the grid points up to 0.25,
which escalate nothing and are the same point).

**Why.** Jev's confidence does find its own errors, but Haiku is worse on those same rows. The
3 Haiku-only-correct rows carry Jev confidence 0.46, 0.61 and 0.74, so reaching all three needs
`t >= 0.75`. By then the cut also escalates Jev-only-correct rows: all 25 of them have Jev
confidence below 1.0. On the rows each cut escalates, Jev is right more often than Haiku:

| Cut | Rows escalated | Jev right on them | Haiku right on them | Flat Haiku rows among them |
|---|---:|---:|---:|---:|
| 0.50 | 13 | 8 | 5 | 5 |
| 0.70 | 28 | 15 | 8 | 6 |
| 0.90 | 52 | 37 | 25 | 9 |
| 1.00 | 112 | 96 | 74 | 14 |

**Checks from the bar.** Best point within the 25% cap: Jev alone, 384/400. 2-fold (even/odd
`i`): both folds pick `t = 0.00`; out-of-fold cascade 384 vs Jev alone 384 (+0). McNemar at the
best point: no discordant rows, p = 1.

**Flat Haiku rows dropped (sensitivity, N = 386).** Same shape. Jev alone 374/386 is still the
best and the only Pareto point; the next best is 373/386 at `t = 0.30` to `0.50` (2 to 8 rows
escalated). Even with no flat rows, Haiku is right less often than Jev on escalated rows: at 0.90,
43 escalated, Jev right on 32, Haiku on 25. 2-fold: +0. The verdict is the same either way.

**Policy B (descriptive): keep the higher own-confidence answer.** It limits the damage but never
helps: best 383/400 (`t = 0.30` to `0.50`), and 379/400 when every row escalates. Flat rows
dropped: best 373/386, against 374 for Jev alone.

**Verdict, 10 intents: NOT USEFUL.** Under the bar at `cc559c6`, no Jev-first cascade beats Jev
alone on this set. The most accurate point within the 25% escalation cap is Jev alone (384/400),
and every escalating point has fewer correct rows at more cost. So no cascade beats both single
arms on accuracy per unit cost. Jev alone has 7.7x Haiku's correct rows per second of mean
latency (2,362.6 vs 304.9) and 2.1x per 1,000 tokens (759.2 vs 360.0). On this set the
confidence gate from the vendor pattern should hand off to a human, as in the parent receipt
(28 rows at 0.7, 99.2% accurate above the cut). Handing off to Haiku does not help. This matches
the prediction in the bar: the ceiling was +3 rows, and the cut needed to reach them costs more
rows than it gains.

### Full 77 intents, N = 3,080

Pending: waiting for ChoiceBanking77 to commit the finished prompted Haiku run and its score
(`jev-4jf`). The prompted rows have not been read by this scorer.
