# What ten Jev repositories say when you actually run them

Written for someone who does not work on this lane. Every line below was produced by running
somebody else's code on somebody else's data, and every claim links to the receipt that produced it.
We patched none of these repositories; five defects went upstream as reports.

This page exists because a reviewing pane ruled that upstream evidence *"is not USER shipping until
promoted into a clear stranger-consumable surface"*
([`honesty-window-buckets-20260918.md`](honesty-window-buckets-20260918.md)). Receipts in a folder
are not a surface. This is the promotion.

## The short version

**A plain-English question with no labels is competitive with a classifier trained on thousands of
them, and the gap widens on mail the classifier was not trained for.** Elaborating the question makes
it worse. Jev is fast and cheap enough to ask per item, and it trails general models on aggregate
workflow scores, so the interesting question is never *"is it better"* but *"where does a typed
judgment beat a trained model or a hand-written rule."*

## What each run returned

| Repo | Finding | Receipt |
|---|---|---|
| `jev-spam-eval` | Ling-Spam: **0.9857** with zero labels against **0.9941** for TF-IDF on 2,300 labels. Same accuracy to four decimals, **opposite failure shapes**: 2 false negatives and 39 false positives against 40 and 1 | [lingspam](lingspam-20260918.md) |
| `jev-spam-eval` (OOD) | on mail unlike the training mail the labelled model collapses: **91.3% against 70.3%** on recent phishing, **97.00% against 72.51%** on modern mail | [ood](jev-spam-eval-ood-20260918.json) |
| three corpora | **elaborating a question costs accuracy.** Ling-Spam plain 98.57% against structured 97.01% (p=1.4e-9); a **names-only** question beats an elaborated one 98.58% to 97.00% (p=.0064); one comparison is directional only (p=.50) | [criteria-inversion](criteria-inversion-20260918.md) |
| `jev-rerank-bench` | one benchmark, two answers: the committed cache puts Jev at **0.692 against Cohere Pro 0.691, inside noise at p=.910**, while a fresh run over 1,383 pairs gives **+4.2 points at p=.002** | [rerank](jev-rerank-bench-20260918.json) |
| `jev-benchmark` | its author reports the two model versions *"not separable at this sample size"*. Pairing the runs shows **zero discordant pairs and identical choices on 60/60**, so **no increase in n on that task set can separate them.** Four of five shared misses are one confusion | [pairing](jev-benchmark-pairing-20260918.md) |
| `jev-phishing-bench` | the keyless floor reproduces **exactly** (0.9165 / 0.8350 / 0.0020) | [phishing](phishing-20260918.md) |
| `typesafe-ai-benchmark` | **7/7** documented offline examples green, after a missing install step that its docs omit | [benchmark-examples](benchmark-examples-20260918.md) |
| `jev-mcp` | three Jev tools live inside a coding harness: **9/9 unit, 4/4 end-to-end**. Without a key the live tests **skip and say so** rather than counting as passes | [mcp](jev-mcp-20260918.md) |
| `fast-jev-compaction` | **29/29** tests; a live run took 21 messages to 7, saving **87.1% of characters** in one request at 1,277 ms | [compaction](fast-jev-compaction-20260918.json) |
| `foreman` | **57/58**. It is a per-worker *supervisor*: there is no queue concept, so a worker idle **while work is ready** reads as finished | [foreman](foreman-20260918.md) |
| `s1-rs` | both examples run offline against a `FakeClient`: typed questions in, `nearest=Annoyed expected=1.20` and `urgent p=0.97` out. Blocked all day by a **misdiagnosed** obstacle, not by Rust | [s1-rs](s1-rs-20260918.md) |
| `bicameral` | the System 2 writes / System 1 judges split is real, with two differences worth copying: **judgment is a pluggable interface**, and its degraded path **falls back to pattern rules rather than passing work through unjudged** | [bicameral](bicameral-20260918.md) |

## Three things worth taking from these, whoever you are

1. **Ask the short question.** Across three paired comparisons the elaborated question never won, and
   the shortest one won outright where it was tested. `jev-spam-eval`'s own README says its headline
   came from a question *"written after reading the mistakes in 1,000 sampled emails"*, which is the
   same effect from the tuning side. That makes this a confirmation rather than a discovery.
2. **Pair your runs before blaming your sample size.** Two aggregate scores that match can hide
   either agreement or noise. `jev-benchmark` has both result files on disk; pairing them takes a
   dozen lines and answers a question its own caveat leaves open.
3. **Decide what your degraded path does before you need it.** `bicameral` falls back to patterns.
   Reading that sent us to our own commit hook, where one lane refused a missing checker and another
   silently permitted the commit. A fail-open path that never fires is indistinguishable from a
   correct one until the day it matters.

## What none of this establishes

- **No head-to-head we ran is ours.** These are other people's harnesses and corpora; we reproduced
  and re-analysed, and where we disagree with an author it is stated against their own data.
- **Vendor-reported aggregates are attributed, not verified.** TypeSafe's dashboard is quoted at
  67.8% against 74.1% for the best comparator from secondary write-ups; we did not read the dashboard.
- **Twelve of the twenty-two repositories cloned here are unrun**, listed row by row in the root
  [`README.md`](../../../README.md). `s1-rs` is blocked on a platform mismatch, not a finding.
- **Live figures cost real calls** and were run once. Nothing here is a reliability measurement, and
  no figure on this page should be read as a benchmark of the current model.
