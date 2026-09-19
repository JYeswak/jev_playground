# What 22 Jev repositories say when you actually run them

Written for someone who does not work on this lane. Every line below was produced by running
somebody else's code on somebody else's data, and every claim links to the receipt that produced it.
We patched none of these repositories. **Every one of the 22 vendored clones has now been run**
(completed 2026-09-19 on Joshua's order: *"stop NOT USING the repos we've downloaded"*), and the
last four taught us more than the first eighteen.

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
| `jev-benchmark` | **corrected 2026-09-18**: its author reports the two model versions *"not separable at this sample size"*. Pairing the runs shows **zero discordant pairs and identical choices on 60/60**, so **no increase in n on that task set can separate them.** Four of five shared misses are one confusion | [pairing](jev-benchmark-pairing-20260918.md) |
| `jev-phishing-bench` | the keyless floor reproduces **exactly** (0.9165 / 0.8350 / 0.0020) | [phishing](phishing-20260918.md) |
| `typesafe-ai-benchmark` | **7/7** documented offline examples green, after a missing install step that its docs omit | [benchmark-examples](benchmark-examples-20260918.md) |
| `jev-mcp` | three Jev tools live inside a coding harness: **9/9 unit, 4/4 end-to-end**. Without a key the live tests **skip and say so** rather than counting as passes | [mcp](jev-mcp-20260918.md) |
| `fast-jev-compaction` | **29/29** tests; a live run took 21 messages to 7, saving **87.1% of characters** in one request at 1,277 ms | [compaction](fast-jev-compaction-20260918.json) |
| `foreman` | **57/58**. It is a per-worker *supervisor*: there is no queue concept, so a worker idle **while work is ready** reads as finished | [foreman](foreman-20260918.md) |
| `s1-rs` | both examples run offline against a `FakeClient`: typed questions in, `nearest=Annoyed expected=1.20` and `urgent p=0.97` out. Blocked all day by a **misdiagnosed** obstacle, not by Rust | [s1-rs](s1-rs-20260918.md) |
| `simple-jev` (open source) | an **open-model implementation of the same interface**, free and keyless. Asked this lane's hardest classification it returned `derived_rollup` at **0.989** in 1.7s | [simple-jev](simple-jev-20260918.md) |
| `jev-sec-bench` | injection detection at **96.5% / AUC 0.9927** over 662 messages, and an ablation that **replicates our framing-leak finding**: recall 74.9% bare against 95.1% with context | [sec-bench](jev-sec-bench-20260918.md) |
| `jev-agent-failure-benchmark` | this lane's own question at **n=6257 with intervals**, against our single runs. Its **leakage test silently skips** without the pinned 73 MB dataset | [agent-failure](agent-failure-benchmark-20260918.md) |
| `jev-review` | a code-quality scorer that returns **`applicable: false`** for dimensions its context cannot support: a refusal-to-score state shipped as contract, not retrofitted | [jev-review](jev-review-20260918.md) |
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

## 2026-09-19 — the last four clones, and what running them cost us in retracted claims

Four repositories sat unrun while this lane built its own versions of their questions. Running them
produced the session's only shipped-code defect **and** forced three retractions of our own work.

### A timeout in `typesafe-sdk-js` kills a default Node process

Their suite reports **189/189 passing with 8 unhandled errors** — Vitest's own warning is that this
"might cause false positive tests". Run file by file, all 8 come from one file, which makes exactly
8 aborted requests: **one leaked rejection per timed-out request.**

Outside their harness entirely — real `node:http`, real global `fetch`, no test doubles — a single
timed-out call gives the caller the correct `APITimeoutError` and then **kills the process**
(`exit 1`, from `client.ts:421`). Repro: [`sdk-js-timeout-crash-repro.mjs`](sdk-js-timeout-crash-repro.mjs),
report: [`sdk-js-timeout-crash-20260919.md`](sdk-js-timeout-crash-20260919.md).

**And the same vendor's Python SDK does not have it.** Identical scenario:
`TypeSafeAPITimeoutError` to the caller, **zero** leaked async errors, process survives
([`sdk-python-20260919.md`](sdk-python-20260919.md)). That control is what turns "async timeouts are
hard" into "this is a defect", and it only exists because the Python clone got run too.

### The vendor's own guidance was in the tree, unread

[`typesafe-ai/skills`](sdk-js-and-skills-20260919.md) is TypeSafe's own instructions for designing
Jev judgments — meaning belongs in `instructions` because question IDs are never sent to the model,
state must be complete, include a no-match outcome. We had spent a day designing judgments without
opening it. Checking our code against it found **nothing to fix**, for the useful reason that we
author no questions at all: we delegate to `fast-jev-compaction`, which already complies.

### Three claims of ours that did not survive contact

| we said | what the control showed |
|---|---|
| the JS SDK's timeout timer leaks | `clearTimeout` is in the `finally`; the caller path is clean. Right impact, **wrong mechanism** |
| `skillranker`'s README documents a CLI that does not exist | our clone is **103 commits stale**; the commands are wired on `origin/main`. **Retracted** ([`skillranker-20260919.md`](skillranker-20260919.md)) |
| a gate run was hanging on our own code | it was a 77s stage against a 60s timeout — **no hang at all** |

No upstream report was filed for the `skillranker` "gap", which is the point of holding reports for
a human: it would have told a maintainer their docs were broken when the defect was our pin.

### What this is worth to someone outside the lane

Four of the six things the sweep produced are things we were about to build ourselves and did not
need to. The pattern is consistent enough to state plainly: **before writing code to answer a
question, check whether a repository you already cloned answers it, and run that instead.**
