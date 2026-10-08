# R2 scores: MUSE2 on LUNA's 30 (2026-10-02)

Scorer: MUSE2 (muse-spark-1.3). Scale 0–1000: smartness + real-world usefulness for humans and coding agents + implementability + utility-vs-complexity. Calibration: 850+ exceptional, 700–849 strong, 500–699 mixed, 300–499 weak, <300 poor. I am direct where an idea is weak; agreement where earned.

## Table

| # | Idea | Score |
|---|------|-------|
| 1 | Shared daily admission budget ($0.25 ceiling) | 550 |
| 2 | Gate-cascade timeout accounting | 700 |
| 3 | Two-stage memory keep gate (structural) | 820 |
| 4 | Bounded memory request construction | 500 |
| 5 | Cross-profile usage ledger | 400 |
| 6 | CI fingerprint cache | 450 |
| 7 | CI critical-path parallelism audit | 500 |
| 8 | Deterministic CI failure grouping | 550 |
| 9 | Beads ready-list incremental refresh | 400 |
| 10 | Close-evidence field lint | 650 |
| 11 | Daily query projection cache | 350 |
| 12 | Agent-start context budget report | 600 |
| 13 | Static context dedup (byte-identical) | 700 |
| 14 | TTSR cost-by-rule visibility | 550 |
| 15 | TTSR dedup by trigger coverage | 500 |
| 16 | Hook startup discovery census | 450 |
| 17 | Single daily inventory conformance | 650 |
| 18 | Find value sampling by downstream action | 600 |
| 19 | Exact find-query cache + invalidation | 650 |
| 20 | Find result payload trimming | 700 |
| 21 | Auto-thinking hard-task monitor | 550 |
| 22 | Auto-thinking byte-identical dedupe | 500 |
| 23 | Local gate batch amortization | 400 |
| 24 | Shell parse once, share AST | 350 |
| 25 | Command-log privacy aggregation | 450 |
| 26 | Screen coalescing by event ID | 600 |
| 27 | Webscreen shadow sample tiering | 500 |
| 28 | Idle-notification debounce | 700 |
| 29 | Dispatch from Beads readiness only | 750 |
| 30 | CI changed-path advisory wave | 600 |

## Top 5, scored with reasons

**#3 Two-stage keep gate — 820 (best).** Only idea that directly attacks the largest measured waste on the board (keep precision ~0.22, ~4-in-5 kept memories irrelevant) through the one door R137 left open (structural change, not wording). Bars are strict and complete (0.42 keep, 0.90 drop, known-good retention, token delta), cost is bounded ($0.02 pilot), and the planted valuable-old-memory negative guards the obvious AND-policy failure. Deduct: 2× judgment volume on every item is real money against a $0.32/day budget, and conjunctions classically trade recall for precision — the drop guard covers it, but the pilot could still burn cash proving nothing.

**#29 Dispatch from readiness only — 750.** Zero blocked/closed dispatches in a 30-day replay is checkable this week, and the 8qu6 double-claim tonight proves the failure mode is live, not theoretical. Deterministic, no model, no new spend. Deduct: median idle-with-ready improvement depends on conductor behavior, not just the handoff; cache-staleness negative is doing heavy lifting.

**#13 Static context dedup — 700** (tie). Byte-identical-only makes it safe by construction; the AGENTS trim proved context volume moves cost. Deduct: the ≥2% bar is a guess until the census runs — if duplication is already squeezed, this is a week for nothing. Census-first ordering is correct.

**#20 Find payload trimming — 700** (tie). Biggest native surface, output tokens are the cost, recall-held bar keeps it honest. Deduct: serialization changes touch every consumer; 10% is modest for the blast radius.

**#28 Idle-notification debounce — 700** (tie). Fleet noise is real operator pain; keeping the 10/10 recall + 0/10 false-page baseline as the gate is exactly right. Deduct: one poll interval of added delay, and duplicate pages may be re-notifications with new information rather than pure dupes — the transition-based definition needs care.

## Their top-5 order, assessed

**#1 Budget ceiling (550) ranked first is wrong.** A $0.25 ceiling below the observed $0.32 while required calls "must never be denied" means the ceiling binds only on optional work it cannot identify without the very ledger it proposes to build — circular. r8dp already showed caps saturate; a machine-wide atomic budget across processes is the hardest distributed-systems item on this list disguised as accounting. Demote below #3 and #5.

**#2 Two-stage keep as their #2: agree**, would rank it first.

**#3 Find cache, #4 CI fingerprint, #5 context dedup:** #5 deserves higher than fifth (only deterministic idea with persistent daily payoff); #4 is the weakest of their five — no repeated-failure prevalence cited, and a 30-day census that finds nothing still cost the month. Swap #4 and #5.

## Weakest five (honest cuts)

- **#11 projection cache (350):** br is local SQLite; query time was never shown to matter, and stale-cache risk on issue state is the worst failure mode on the list for the least payoff.
- **#24 shared AST (350):** shell-parse microseconds dressed as a lever; 25% of nothing is nothing, and a misparse fails closed into blocked work.
- **#5 ledger (400), #9 ready refresh (400), #23 batching (400):** observability or unmeasured micro-optimizations; #23 adds queueing risk to a safety path for latency nobody demonstrated.
- **#16 startup census (450), #25 privacy aggregation (450), #6 CI fingerprint (450):** fine hygiene, but none moves cost, latency, or safety this quarter.

## Overall

Strong list, honest costing (ceilings labeled as ceilings, $0-new-spend discipline throughout), and the exclusion section does real work — no refuted designs smuggled back. Main weaknesses: several bars assume baselines that don't exist yet (repeat rates, duplicate volumes, failure prevalence), so the list front-loads censuses while ranking as if savings were measured; and #1 mistakes a coordination mechanism for savings. Best idea (#3) is genuinely the best next experiment on this machine. Mean of my scores: ~548 — a solid, unspectacular slate lifted by three good ideas.
