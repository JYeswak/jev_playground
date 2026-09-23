# W7.0 preregistration — pane 5 group (seat/benchmark + catalogue)

Committed before the first live call of this group. Bars below decide PASS/FAIL per clone; anything else is reported, not ruled. Model for all live arms: `jev-1.13.0`. Incumbent arm where a key is held: `system-one-adapter-python` via grok-4/Haiku (keys as `work/nev-differential/` found them); otherwise NOT-RUN with the four fields. All live answers recorded with N, prevalence, cost, p50/p95 latency.

## T4 bars (falsifiable, one per clone)

- **jev-rerank-bench**: live spot-check, N=30 rows sampled by the agent from the clone's own corpus (seed recorded), one rubric arm. PASS if live choices reproduce the committed cache on ≥24/30 rows. Cost ceiling: 30 Jev calls.
- **jev-benchmark**: full 60 hand-labelled cases re-asked live. PASS if live accuracy lands in [52,58]/60 (91.7% ±5pts) AND the majority-class floor is stated beside it. Cost ceiling: 60 Jev calls.
- **jev-agent-failure-benchmark**: N=300 sample (`sample --n 300`) re-asked live on the agent axis. PASS if the 95% Wilson lower bound of Jev agent-accuracy exceeds the majority-agent floor on the same 300 rows. Full 6,257 run explicitly NOT attempted (cost). GPT-5.4 arm: NOT-RUN unless an OpenAI key is found without printing; grok-4/Haiku substitute recorded if held.
- **typesafe-ai-benchmark**: the 7 fixture tasks re-asked live through the Jev arm. PASS if ≥5/7 live verdicts match the recorded ones. Qwen/Cerebras arm: NOT-RUN (key not held) with four fields.
- **awesome-typesafe**: catalogue profile (T1+T3 only). No live calls. PASS if every entry claimed as a benchmark names a repo that exists with a runnable suite command, or is marked catalogue-only.
- **jevcal / Janus** (clone at HEAD, pin recorded, then run as new clones): T1–T3 + floors first; T4 bar proposed by the exploring agent from the clone's own corpus and committed as an amendment HERE before any live call. No live call happens under the v1 bars for these two.

## Standing rules for all seven runs

T1 pin+env recorded. T2 own suite fresh with skip counts; planted defect in /tmp copy must turn it RED. T5 floors on the same rows (majority constant + cheapest lexical rule); a floor tie refuses the seat. T7 bins with counts or "not observable". T8: 3× repeat + one reword (applies to live arms; fixture-only arms report n/a with reason). Receipts: `docs/demos/upstream-repro/<clone>-w70-2026-09-23.md` (T1–T10 table + verdict + Boundary). Prior receipts are leads, never passes.
