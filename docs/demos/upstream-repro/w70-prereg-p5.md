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

## Amendment A (committed before any jevcal/Janus live call, 2026-09-23)

> T4 bar (jevcal, proposed 2026-09-23, no live call yet): corpus = the clone's own
> bundled `src/jevcal/examples/support/tickets.jsonl` (N=400 rows, labeled by
> construction, generator seed 20260918; prevalence is_urgent-true 147/400 = 36.8%,
> department sales/billing/technical 136/134/130, frustration 0/1/2 = 125/214/61);
> questions = `support/questions.yaml` with the model pinned to `jev-1.13.0` at call
> time (the file names `jev-latest`; the pin is recorded in the run receipt, the file
> is not edited); command `jevcal run --provider typesafe` over all 400 rows, one
> request per row with all 3 questions per request (cost ceiling: 400 Jev calls).
> Record N, prevalence, call count, total cost, and p50/p95 per-request latency.
> PASS iff `compile` reports status `ok` (not `holdout_miss`, not `no_threshold`) on
> all three questions AND each question's held-out accepted accuracy >= its target
> minus 0.02 (targets: is_urgent 0.97, department 0.95, frustration 0.95).
> Accuracy-vs-floor is explicitly NOT the bar.

> **T4 bar — Janus:** live `jev-1.13.0` re-asked on the clone's own frozen corpora,
> protocol frozen here before the first call. Arm A: full `data/banking77_500.jsonl`
> (N=500; gold prevalence: top class `pending_top_up` 12/500 = 2.4%, 77 classes,
> 1–12 rows/label). Arm B: seeded subsample of `data/wos_500.jsonl` — ids sorted
> ascending, `random.Random(7).sample(ids, 200)` (sha16 `d81755532e0f93e`; first ids
> 212, 512, 1276, …; committed-cache Jev accuracy on these 200: 109/200 = 54.50%;
> subsample majority `MAE/Materials Engineering` 5/200 = 2.5%). Same prompt build as
> the clone's runners (`experiments/run_jev.py` + `experiments/tasks.py` question
> assembly) at pinned `jev-1.13.0`; no DeepSeek calls (T4 is the Jev arm only).
> Record per arm: N, gold prevalence, per-row cost (input/output tokens → USD at the
> API's answered rates), total cost, p50/p95 decision latency. Cost ceiling: $2.00
> (expected ≈ $0.15 at the clone's measured rates). PASS iff live Jev accuracy lands
> within ±5 pts of committed cache on BOTH arms: Arm A in [72.8, 82.8]%
> (committed 77.80%) AND Arm B in [49.5, 59.5]% (committed 54.50%). Otherwise FAIL.
> Floors computable keylessly on the same rows (T5, no API): always-majority constant
> (Arm A 2.40%, Arm B 2.50% — computed 2026-09-23 from committed gold labels) plus a
> token-overlap lexical rule over `data/*.labels.json` descriptions; a floor tie refuses
> the seat per W7.0 T5. Stability (T8: same rows ×3 + one reword) rides on the same live calls.
