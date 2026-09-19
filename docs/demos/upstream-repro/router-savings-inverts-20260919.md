# The one published savings claim inverts on our own sessions

**Date:** 2026-09-19 · **Level:** `[live]` · Five clones verified untouched (0 dirty entries).

Four of these five repos make **no** accuracy or savings claim, and three say so explicitly.
Exactly one publishes a headline number. That number does not survive contact with a non-strawman
baseline or with a current session log.

## `0xNatoshi/jev-codex-router` — measured on 643 of our real Codex sessions

Replayed with the repo's own `PRICES`, `cost()` and `route_policy()`, n=1199 priced turns
(2026-08-18 → 09-17):

| policy | cost | vs Jev |
|---|---:|---|
| flat `gpt-6-astra` | $10,627.06 | Jev **−23.9%** (cheaper) |
| **Jev adaptive** | **$8,085.48** | — |
| flat `gpt-5.6-sol` | $4,250.83 | Jev **+90.2% more expensive** |
| flat `gpt-5.6-terra` | $2,160.27 | Jev +274.3% |
| flat `gpt-5.6-luna` | $432.05 | Jev +1771.4% |

Jev beats only the all-frontier strawman. It routes **51% of our agentic turns to the frontier
model** (astra 610 · sol 519 · luna 70). An independent n=500 draw agreed: **+75.6%** vs flat-sol.

**The repo's own shipped sample already shows the inversion**: `jev_usd = 349.29` vs
`scenarios_usd["gpt-5.6-sol"] = 348.59`. Adaptive routing buys **nothing** over a one-line static
rule. The advertised **−59.9%** is measured only against `gpt-6-astra` everywhere — a baseline
nobody runs. Four of five flat policies beat Jev on their own data.

### Upstream defect: the published backtest is not reproducible on a current Codex install

`poc/backtest_savings.py:85-86` filters on the literals `token_usage_record` / `turn_token_usage`.
Measured: **0 occurrences in 200 of our session files.** Current Codex writes `event_msg` with
`payload.type == "token_count"`, fields nested under `info.total_token_usage`. Consequence: the
documented `--days 7` yielded **4 usable turns**, `--days 40` yielded **7**, against 643 sessions
containing 2,773 `task_started` events. A schema-correct extractor yields **9,877** — a **1,411×
extraction gap**. With n=4 the tool printed `→ ESTIMATED SAVINGS: 95.9%`.

## Where Jev measured well

- **Commit security triage** (`devanshbatham/commit-miner`, 9-commit fixture with 5 benign
  negative controls): recall **4/4**, false positives **0/5**, CWE exact match **4/4**, separation
  margin **0.83**, AUC **1.000**, **0/80** spurious CWE firings, deterministic on repeat.
- **Worker supervision** (`thruwire/foreman`): **76/76** at the repo's own thresholds. The real
  result is a trap pair — `just_started` and `stuck_loop` both have clean git and no changed
  files; Jev separated them **0.13 vs 0.95** on elapsed time and output repetition.
- **Code review ordering** (`NiazMorshed2007/jev-review`): **12/12** pairs, mean gap **4.59**/10.
- **Task tiering** (the only *pre-existing* labelled set): **11/12 = 91.7%** shipped, **87.5%
  (42/48)** cross-surface, rank correlation **0.909**.

## Two errors that survive prompt engineering

- The same task (`^(a+)+$` catastrophic backtracking, labelled mid-tier) is under-routed by **two
  independently-authored surfaces** — once at confidence **0.91–0.94** (confidently wrong, so no
  gate catches it), once at **0.31–0.32**, which slips past `jev-router`'s `minConfidence: 0.30`
  by **0.01**. The error lives in Jev's judgment, not in either repo's prompt.
- An explicit O(n²)→set-lookup optimization with "Speed up" in the subject scored
  `change_performance = 0.24` and was filed as **Refactor**.

## What nobody measures, including us

**Whether a downgraded turn still completes the task.** Every savings figure in this ecosystem
silently assumes the cheap model succeeds. If Sol fails on those 610 frontier-classified turns,
flat-Sol's cheapness is worthless. Cost is not decision quality.

## Ruling for our lane

Adopt **supervision** and **commit-triage**. Steal `jev-codex-router`'s labelled-set-scored-on-
every-run pattern. **Do not adopt tier routing for cost reasons.** Raise any router's
`minConfidence` above 0.35 — the measured failure sits just above the default.

## NO-CLAIM

The cost table assumes token volumes are invariant to the model chosen and that flat-`sol` would
complete the same work — **unmeasured, including by me.** This proves the savings claim is
measured against a strawman, not that Jev routing is economically wrong in the round.
Prompt-cache invalidation from model switching is unmodelled. Token attribution is a
reconstruction by cumulative-total delta, not Codex's own turn accounting. The 100% scores on
commit-miner/foreman/jev-review are wide-separation smoke tests on fixtures authored by the
agent — discrimination on clear evidence, **not calibration**, and not sensitivity to near-ties.
