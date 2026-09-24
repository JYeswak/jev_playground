# Top-k recall on the full Banking77 test split: does a short list cover the truth? (bead `jev-zfn`)

ChoiceBanking77 (background agent of pane 1), 2026-09-24. Offline lane: no calls. Everything is
computed from rows already committed by `jev-4jf`.

## Preregistered (committed at `644a179`, before the scorer was first run on the real rows)

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

Offline, 2026-09-24, 0 calls. Re-score: `python3 work/choice-banking77/score_topk.py`. There are 4
zero-mass Haiku rows (ids 453, 1698, 2197, 3058).

| k | Jev recall (Wilson 95%) | Haiku recall (Wilson 95%) | Jev-only / Haiku-only | Holm p |
|---:|---|---|---|---:|
| 1 | 2,465 (80.0%, 78.6-81.4) | 2,231 (72.4%, 70.8-74.0) | 354 / 120 | 1.5e-27 |
| 2 | 2,708 (87.9%, 86.7-89.0) | 2,523 (81.9%, 80.5-83.2) | 255 / 70 | 7.5e-26 |
| 3 | **2,804 (91.0%, 90.0-92.0)** | 2,602 (84.5%, 83.2-85.7) | 245 / 43 | 5.1e-35 |
| 5 | 2,879 (93.5%, 92.5-94.3) | 2,660 (86.4%, 85.1-87.5) | 265 / 46 | 5.9e-38 |

Dropping the 4 zero-mass rows from both arms (N = 3,076) moves no recall by more than 0.1 point and
changes no conclusion; that table is printed by the scorer. Jev's lead holds at every k.

**Top-1 under the tie rule vs the committed pick.**
- Jev: 2,465 vs 2,467. Only 4 Jev rows have a tied top probability.
- Haiku: 2,231 vs 2,267. On 113 Haiku rows the top probability is tied (the model tends to write
  round numbers). The pessimistic rule counts the 36 rows where Haiku's committed pick won a tie
  against the truth as misses.

**Why no list reaches 95% (descriptive, printed by the scorer after the bar).** Jev puts exactly
0 probability on the true intent in 181 of 3,080 rows (5.9%). Haiku does so in 352 (11.4%). Under
the tie rule those rows are ranked last, so no probability-ranked list shorter than all 77 can
reach them. Jev's ceiling is therefore 2,899/3,080 (94.1%), and its top 5 already reaches 2,879.

**Short-list curve** (top-1 if the arm's `confidence` >= t, otherwise its top 3 goes to a human;
the human branch assumes the human picks the truth when it is shown). Selected rows; the scorer
prints all 16.

| Arm | t | Auto-routed (accuracy) | Wrong auto-routes | To human (truth in list) | Total success |
|---|---:|---|---:|---|---:|
| Jev | 0 (always auto) | 3,080 (80.0%) | 615 | 0 | 80.0% |
| Jev | 0.9 | 2,094 (92.5%) | 157 | 986 (81.5%) | 89.0% |
| Jev | 0.95 | 1,855 (94.8%) | 96 | 1,225 (83.0%) | 90.1% |
| Jev | 0.99 | 1,383 (97.0%) | 42 | 1,697 (85.7%) | 90.7% |
| Jev | 1.01 (always list) | 0 | 0 | 3,080 (91.0%) | 91.0% |
| Haiku | 0.9 | 1,911 (86.4%) | 259 | 1,169 (74.6%) | 81.9% |
| Haiku | 0.95 | 980 (90.5%) | 93 | 2,100 (81.6%) | 84.4% |
| Haiku | 1.01 (always list) | 0 | 0 | 3,080 (84.5%) | 84.5% |

**Decision: NOT SUFFICIENT** (fixed rule: Jev top-3 recall >= 95%; measured 91.0%). A top-3 list
catches 91 of 100 messages, and at 77 intents no probability-ranked list can reach 95%, because Jev
gives the truth zero mass on 5.9% of messages. What the curve does support: at t = 0.99, Jev
auto-routes 45% of messages at 97.0% accuracy (42 wrong) and hands the rest to a human with a top-3
list that contains the truth 85.7% of the time. Haiku is worse at every k and at every threshold.
With the same list, its best total success is 84.5% versus Jev's 91.0%.

**Boundary / NO-CLAIM.** Offline over one run per arm, one wording, undescribed options. The human
branch is modeled as perfect picking from a shown list, not observed. The zero-truth-mass and tie
counts are descriptive and were added to the scorer after the bar; the bar's tables are unchanged by
that addition (the output diffs clean apart from the new lines). A non-author re-score is pending,
and the bead stays open.

## Non-author verification — Verifier3

Verifier3 (background agent of pane 1, Anthropic model), 2026-09-24. Not the author. Everything ran
in a fresh `git clone --local` of `a128796` under `/tmp`. No call was made.

| Check | Command | Result |
|---|---|---|
| Rows predate the bar; bar predates scoring | `git log --format='%h %ad' --` rows, scorer, receipt | both row files are unchanged since `5839235` (Haiku) and `3c473ae` (Jev frozen), 21:02 −0600. Bar and scorer came at `644a179` (21:15:03), results at `2a70fd1` (21:16:04). The rows were public before the bar, so "bar before scoring" rests on the author's statement and on the next check. |
| Bar and scorer unedited in substance | `git diff 644a179 2a70fd1`; the `644a179` scorer run on the same rows and its output diffed against HEAD's | the bar lost only its `Pending` line and got its commit id in the heading. The scorer gained 19 lines of descriptive printout. The bar version's output differs from HEAD's by exactly the two added lines (zero-truth-mass and tie counts): every preregistered table is byte-identical. |
| Re-score reproduces | `python3 work/choice-banking77/score_topk.py` (rc 0, no key) | every Results number matches. Recall at 1/2/3/5: Jev 2,465 / 2,708 / 2,804 / 2,879, Haiku 2,231 / 2,523 / 2,602 / 2,660. Discordant counts 354/120, 255/70, 245/43, 265/46, with Holm p 1.5e-27, 7.5e-26, 5.1e-35 and 5.9e-38. The zero-mass-dropped table moves nothing by more than 0.1 point. There are 181 and 352 zero-truth rows and 4 and 113 tied rows. All 16 curve rows match. **NOT SUFFICIENT** (91.0% < 95%). |
| Independent recompute | own script: pessimistic rank = 1 + #others with p ≥ p(truth) | recall at k is identical on both arms. At t = 0.99, Jev auto-routes 1,383 (1,341 correct, 42 wrong), and 1,697 go to a human with the truth in the list on 1,454, total 2,795. Haiku gives 944 / 854 / 90 / 2,136 / 1,748 / 2,602. All identical. |
| 10 seeded rows by hand | `random.Random(24)` over the 3,080 ids: 685, 693, 747, 795, 894, 1568, 2387, 2747, 2792, 2917 | on 8 rows both arms rank the truth first. i 894: Jev gives `supported_cards_and_currencies` 0.0, so rank 77 (a zero-mass-truth row), and Haiku gives it 0.05, rank 3. i 2917: Jev's truth is at 0.01, tied with `transaction_charged_twice`, so the pessimistic rule gives rank 3, not 2. Haiku ranks it 1 at 0.85. Each hand rank agrees with the scorer's rule. |
| Zero-mass handling | scorer output | the 4 Haiku `rawSum == 0` rows (453, 1698, 2197, 3058) are reported, and every table is shown with and without them, as the bar and bead require. |
| NO-CLAIM vs what ran | receipt vs rows | one run per arm and one wording, offline. The human branch is modeled as perfect picking, and the receipt says so. The post-bar descriptive lines are disclosed. `NEGATIVE_EVIDENCE.md` R86 exists with a retry condition. |

**Verdict: CONFIRMED** (clean-clone keyless re-score, `[oracle]`). NOT SUFFICIENT stands. Jev's recall
is higher than Haiku's at every k. Scratch left at `/tmp/v3-zfn.cA9b` (not deleted).
