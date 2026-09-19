# README numeric-table claim audit

**Unit:** P2-27 Unit 1
**Scope:** numeric rows in README.md tables, inspected 2026-09-19.

Status meanings:

- `REPRODUCIBLE`: the README names a runnable command or committed artifact sufficient to rerun the row.
- `HISTORICAL-RECEIPT`: a committed receipt records the number, but this audit did not rerun the original external/live arm.
- `DELETED`: the numeric row was removed from README rather than preserve an unsupported number.
- `NOT-REPRODUCIBLE`: the published number has no opened committed reproduction path in this audit.

| README table / row | Numeric claim | Status | First source or reason |
|---|---|---|---|
| What you get / usage-shape | 98.878% | REPRODUCIBLE | `demos/usage-shape/bin/shape.mjs`; `docs/demos/jev-probe/census-20260918.json` |
| What you get / routing-backtest | 0.0447% | REPRODUCIBLE | `demos/routing-backtest/`; README command `cd demos/routing-backtest && npm test` |
| Repo census / jev-ultrafast | 20/20, 0/10, $0.0003 | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/jev-ultrafast-action-choice-20260919.md` |
| Repo census / fast-jev-compaction | 29/29, 87.1% | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/compaction-retention-oracle-20260919.md` |
| Repo census / jev-agent-failure-benchmark | 20/20 | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/agent-failure-benchmark-20260918.md` |
| Repo census / jev-sec-bench | n=662 | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/jev-sec-bench-20260918.md` |
| Repo census / jev-review | 13/13 | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/jev-review-real-diffs-20260919.md` |
| Repo census / typesafe-sdk-js | 189/189, 8 errors | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/sdk-js-timeout-crash-20260919.md` |
| Repo census / typesafe-sdk-python | 534 pass, 50 skipped, 0 errors | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/sdk-python-20260919.md` |
| Repo census / deleted unsupported rows (jev-spam-eval, rerank, phishing, benchmark, typesafe benchmark, s1-rs, routers, mcp, commit-miner, foreman, bicameral, adapter, skillranker, skills, awesome indexes) | formerly published counts and percentages | DELETED | README rows removed because no row-specific committed reproduction or receipt was identified |
| Harm rule / deterministic rule | 12/12, 0/38 | REPRODUCIBLE | `docs/demos/upstream-repro/harm-rule-claim-repro-20260919.md`; `node work/omp-harm-rule/verify-claim.mjs` |
| Harm rule / Jev | 11/12, historical 0/40 | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/harm-rule-shipped-20260919.md`; live model arm is not offline-rerun |
| Harm rule / dumb baseline | 5/12, historical 0/40 | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/harm-rule-shipped-20260919.md`; historical benign denominator unavailable |
| Ensemble / plain + logistic regression | +0.035, 0.0 pp, +1.25 pp | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/judgment-quality-20260919.md` |
| Ensemble / Jev + TF-IDF phishing | +0.107, 4.2 pp, +0.38 pp, n=5,733 | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/jev-sec-bench-20260918.md` |
| Ensemble / with-context + without-context | +0.343, 6.8 pp, -0.60 pp, n=662 | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/jev-sec-bench-20260918.md` |
| Ensemble / logistic regression + naive Bayes | +0.526, 0.8 pp, -0.14 pp | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/judgment-quality-20260919.md` |
| Compaction / six named sessions | 0–108 calls, 0–1 requests, 0–98% saved | HISTORICAL-RECEIPT | `docs/demos/upstream-repro/compaction-retention-oracle-20260919.md` |
| Usage shape / token shares | 98.878%, 0.980%, 0.140%, 0.002% | REPRODUCIBLE | `demos/usage-shape/bin/shape.mjs`; `docs/demos/jev-probe/census-20260918.json` |
| Usage shape / mean and corpus | 341,496 mean; 4,626 files; 4,619 sessions; 488,724 turns | REPRODUCIBLE | `demos/usage-shape/`; `docs/demos/jev-probe/census-20260918.json` |

## NO-CLAIM

This is a one-off disposition audit, not a rerun of every historical number. Historical receipts do
not establish fresh external model behavior. Deleted rows are no longer published numeric claims.
The deterministic harm-rule denominator is now 0/38, not the lost historical 0/40.
