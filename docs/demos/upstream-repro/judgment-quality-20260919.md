# What Jev is measurably good and bad at — five benchmarks, recomputed

**Date:** 2026-09-19 · **Level:** `[oracle]` · Clones untouched (`git status --porcelain` clean in all five).

Every earlier pass in this lane ran upstream test suites and recorded that they passed. That
proves their code compiles. This recomputes the **judgment-quality figures from committed
per-item data** with independent scorers, and re-measures live where no per-item data ships.

## Good, and the numbers are ours

| claim | measured |
|---|---|
| zero-label classification matches a trained classifier | Jev **0.9833** vs TF-IDF logreg **0.9839** on 18,514 emails; McNemar over the 466 disagreements **p = 0.677** — a statistical tie against ~14,800 in-domain labels |
| holds under distribution shift where the trained model collapses | TF-IDF **0.73 / 0.70 / 0.73** on shifted mail vs Jev **0.97–0.99** on the identical items |
| score tails are actionable | of 8,333 emails scored <0.1, **0.12%** are spam; of 7,016 scored ≥0.9, **99.93%** are |
| prompt injection with deployment context | acc **0.9653**, AUC **0.9927** (without context, recall drops **20.2 pp**) |
| reranking | nDCG@10 **0.692** vs Cohere Pro 0.691; best-in-field on negation (NevIR **71.2%** vs 67.0%) |
| cost | **$0.038**/1k emails; **$1.28** for 6,257 agent traces |

## Bad, and this is the part that changes how we build

- **Never take the monolithic verdict.** On phishing, Jev's end-to-end answer is **63.8%** (AUROC
  0.70) — while *the same call's* `sig_free_hosting` sub-question scores **AUROC 0.96**. A two-line
  domain regex beats the verdict by **27 points** (McNemar **p = 1.5e-8**). The model is fine; the
  question shape is not.
- **Calibration is the recurring weakness.** Code-vulnerability ECE **0.19** at 71.5% absolute
  despite **89%** pairwise; 694 vs 150 false positives against logreg at the same 0.50 cut; the
  0.5–0.6 band only **38%** positive. Pick thresholds from your own labels; never assume 0.5.
- **Asking strategy dominates model choice.** Five prompt shapes on identical passages spread
  nDCG **0.580 → 0.692**. A criteria prompt tuned on one spam corpus **lost 1.6 points** on
  another — tuning transferred negatively.
- **It cannot type what it cannot read.** Agent-failure error class: **33%** accuracy, macro-F1
  **23.7**, ECE **0.287** on a 17-code taxonomy.

## Two headline framings that flatter the model, found by recomputing

1. **The rerank "tie" is a weighting artefact.** Dataset-macro gives Jev −Cohere = **+0.0009**. A
   per-query paired bootstrap (5,000 resamples, n=1,617) gives **−0.0184, 95% CI [−0.026, −0.011]**:
   per query, Cohere Pro is significantly ahead.
2. **`Who = 73.4` and `All = 31.3` use different denominators.** Who is a macro over the 5
   multi-agent frameworks only; the 4,507 single-agent traces where Jev scores **100% by
   construction** are excluded from Who — and included in All. Pooled, Who is **83.3**.

## The rule these five agree on

**Decompose the decision into narrow typed questions, combine them in our own code, keep a dumb
baseline, and pick thresholds from labels — never take the verdict.**

## NO-CLAIM

Four of five are offline recomputations of committed probabilities: they validate the arithmetic
and the corpus, **not** that a fresh API run reproduces those probabilities. The phishing figure is
a live 500-email seeded subset (25% of the benchmark, ±4 pp), not the full split. The
agent-failure per-axis booleans came from the pinned scorer, which is not installed here. One
model version (`jev-1.13.0`), one run each.
