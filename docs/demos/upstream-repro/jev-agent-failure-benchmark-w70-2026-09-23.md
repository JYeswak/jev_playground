# jev-agent-failure-benchmark — W7.0 receipt (2026-09-23)

Clone: `TokenTrim/jev-agent-failure-benchmark` at `/Users/josh/Developer/jev/jev-agent-failure-benchmark`.
Profile: seat/benchmark (T1–T8 + T10). Live model: `jev-1.13.0`.
T4 bar committed at `fec3f95` (`docs/demos/upstream-repro/w70-prereg-p5.md`), predates all live calls below. Bar is not moved.
Full 6,257-trace run explicitly out of scope (cost); N=300 sample re-asked live on the agent axis.

T4 bar (verbatim from prereg): "N=300 sample (`sample --n 300`) re-asked live on the agent axis.
PASS if the 95% Wilson lower bound of Jev agent-accuracy exceeds the majority-agent floor on the same 300 rows."

## T1–T10

| id | test | result |
|---|---|---|
| T1 | Pin and environment | PASS — pin `4d46af795a4a4409940a65857da73e45abaea2db` (`4d46af7`), date 2026-09-22, license Apache-2.0 (`LICENSE:1-4`). `git status` before and after: only pre-existing `M uv.lock` (unrelated resolver churn, untouched by this run). Outer repo `/Users/josh/Developer/jev` at `07041c2`. `OMP_PROFILE=muse`, `PI_PROFILE=muse`, `PI_CODING_AGENT_DIR=/Users/josh/.omp/profiles/muse/agent`, host `Joshs-Mac-Studio.local` (darwin 25.5.0 arm64). Runtimes: clone `.venv` Python 3.14.2, pytest 9.1.1, httpx 0.28.1, numpy 2.5.3; `whowhen-eval @ 14369dcb` (`pyproject.toml:14`, `uv.lock:964`). Dataset `data/text.jsonl` present: 72 MB, 6,257 rows, rev `0bd196c8a040841c4ae167ab33cc8151de246f1f` (`src/jevbench/dataset.py:19`, `README.md:53`). Sample: `stratified_sample(n=300, seed=20240517, floor=20)` → 300 ids: alfagent 27, debate 30, dylan 23, macnet 26, magentic-one 38, mathchat 41, metagpt 22, smolagents 93 (139 Who-scored multi-agent rows). |
| T2 | Own suite, fresh | PASS — `.venv/bin/python -m pytest -q`: **20 passed, 0 skipped in 3.17 s** (all 7 files: candidates 4, jev_backend 2, leakage 1, metrics 6, pricing 3, sampling 4). Zero skips: `data/text.jsonl` present so the 2 `needs_dataset` tests ran (`tests/conftest.py:10`). Planted defect in `/tmp` copy only (`/tmp/jev-afb-t2/src/jevbench/pricing.py:43`, `cost_usd → 999999.0`): suite turns RED — `2 failed, 18 passed` (`test_jev_output_is_free`, `test_llm_input_and_output`). Clone tree never edited. |
| T3 | Claim inventory (≥5, file:line) | PASS — 8 claims inventoried below. |
| T4 | Live Jev on its own question (agent axis, N=300) | **PASS** — 300/300 completed, 0 errored, wall 10.6 s. Agent raw on Who-scored rows: **111/139 = 0.7986, Wilson95 [0.7243, 0.8568], LB = 0.7243** vs majority-agent floor **27/139 = 0.1942** (`orchestrator`, 11 distinct GT agents). LB (0.7243) > floor (0.1942). Clone's own recipe beside it: Who 0.7833 / When 0.7576 / What 0.2426 / All 0.2957 (`metrics.accuracy`, framework-averaged). Arm: N=300 (139 scored), prevalence 19.4%, cost 300 calls / 1,657,028 input tok / **$0.0696** (@ $0.042/MTok input-only), p50 **0.442 s** / p95 **0.963 s** (min 0.264, max 3.287). |
| T5 | Floor arms (same 300 rows) | PASS — majority-agent constant 27/139 = **0.1942**; cheapest lexical rule (first candidate agent in transcript order, offline via `candidate_agents`, no live calls) 77/139 = **0.5540**. Jev LB 0.7243 clears both; no floor tie, seat not refused. |
| T6 | Incumbent arm | SPLIT — (a) gpt-5.4 live re-ask: **NOT-RUN** (four fields below). (b) grok-4 substitute, RECORDED: `xai/grok-4.20-0309-non-reasoning`, temp 0, official `build_prompt` + `parse_all_at_once` flow, N=60 T8 subset (35 ma rows), prevalence 20.0% (`orchestrator` 7/35): agent-acc **23/35 = 0.6571** vs Jev r1 **28/35 = 0.8000** on same rows; McNemar discordant 6v1, **p = 0.1306 (ns at n=35)**. Cost 60 calls / 321,452 in + 8,213 out tok (unpriced — no xAI row in `pricing.py:22-30`). Latency p50 **2.293 s** / p95 **3.025 s** (max 34.399). 0 errors, 0 parse warnings. |
| T7 | Calibration (bins with counts) | PASS — agent axis, multi-agent rows only (n=139): ECE **0.0545**. Bins: 0.3–0.4 n=4 conf 0.373 acc 0.250; 0.4–0.5 n=13 conf 0.452 acc 0.615; 0.5–0.6 n=16 conf 0.555 acc 0.625; 0.6–0.7 n=19 conf 0.653 acc 0.737; 0.7–0.8 n=21 conf 0.755 acc 0.810; 0.8–0.9 n=22 conf 0.850 acc 0.818; 0.9–1.0 n=44 conf 0.969 acc 0.977. All-rows (n=300) ECE 0.0254 but 205/300 sit in 0.9–1.0 (single-agent trivial rows inflate it) — reported for transparency, multi-agent table rules. |
| T8 | Stability (60-row subset, 3× + reword) | PASS — stratified sub60 (seed 99, trimmed to exactly 60; 35 ma rows; N, prevalence 20.0%, cost/latency per arm recorded). r2: 60 calls, 371,443 tok, $0.0156, p50 0.386 / p95 0.502. r3: $0.0156, p50 0.438 / p95 0.922. r4-reword (`_AGENT_Q` → "Which agent first made the decisive mistake that caused this run to fail?", identical state+candidates): $0.0156, p50 0.404 / p95 0.612. 3×-any-flip **3/60 = 0.050** (ma: 3/35 = 0.086; pairwise r1v2 2, r1v3 1, r2v3 3). Framing flip **2/60 = 0.033** (ma: 2/35 = 0.057). ma agent-acc r1 28/35 = 0.800, r2 0.800, r3 0.771, r4 0.743. |
| T9 | Fault behaviour | NA — benchmark profile (T1–T8+T10); no SDK/client surface in this clone. (`JevBackend.predict` records rather than raises, `backends/jev.py:127-133`, noted not ruled.) |
| T10 | Verdict | **FLOOR — T4 PASS.** See verdict block. |

### T3 claim inventory

1. "Jev outperforms GPT-5.4 on every axis — for ~$1.28 total" (`README.md:11-12`) — **PARTIAL.** Direction confirmed live on the agent axis (Who 0.783 vs paper gpt-5.4 0.557; Wilson LB clears floors; substitute grok 0.657 numerically below). Full 6,257 table and paper baselines not re-measured here. Maintainer-numbers tier (all Jev figures maintainer-measured; baselines paper Table 4, independent).
2. Table row 73.4 / 76.4 / 23.7 / 31.3 (`README.md:18`, `RESULTS.md:5`) — **PARTIAL.** Re-asked Who on N=300 = 0.783 vs claimed 0.734: same ballpark but above the claimed CI [70.5, 76.2], explained by the stratified floor design oversampling small frameworks vs the population run. When/What/All reported, not ruled.
3. "The like-for-like axis is What" (`README.md:24-26`, `RESULTS.md:10`) — **DEMONSTRATED** by construction: Jev gets enumerated agent/step candidates (`backends/jev.py:103-120`), LLMs free-generate; What uses the same 17-code taxonomy for both (`backends/jev.py:47-56`).
4. "Ground-truth labels never enter Jev's input" (`README.md:39-40`) — **DEMONSTRATED**: `test_leakage.py:13-44` passes in the fresh T2 run; payload asserts no `ground_truth`/answer (`test_jev_backend.py:59`).
5. Resumable run, failures recorded not dropped (`README.md:68-70`, `runner.py:24-39,61-99`) — **PARTIAL.** Record path demonstrated live (300 JSONL records, schema matches official recipe). Resume-skip path (`done_trace_ids`) code-only, not exercised (0 errors to resume from).
6. "$1.28 for 6,257 traces (30,497,481 input tok @ $0.042/MTok, output free)" (`RESULTS.md:8`, `pricing.py:22-24`) — **DEMONSTRATED** as arithmetic + rate card: 30.5M × 0.042 = $1.281. Our measured density (1.657M tok / 300 → ~34.6M projected) is the same order; full-run token total not re-measured.
7. "Mode-confidence ECE 0.287" (`RESULTS.md:10`) — **STALE.** Not re-measured (this run calibrated the agent axis: ECE 0.0545 ma-only). Prior number stands unconfirmed.
8. Failures are injected, not natural; dataset CC-BY-4.0 `Leoxx/whowhen_pro` (`README.md:74-75,82-85`, `RESULTS.md:10`) — **DEMONSTRATED** as attribution/disclosure; upstream design, correctly caveated in-repo ("not natural production incidents", "not a leaderboard submission", `README.md:74-78`).

### T6 NOT-RUN four fields (gpt-5.4 live arm)

- Command: `curl -s -m 20 https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"` under `infisical run --projectId=42b194c3-…` (key presence checked, value never printed).
- Verbatim output: `{"type": "invalid_request_error", ... "code": "invalid_api_key" }` / `HTTP:401`.
- File:line cause: no runnable LLM arm exists in-clone — `src/jevbench/backends/` holds only `jev.py` + `base.py`; `gpt-5.4` appears solely as paper constants (`src/jevbench/report_vs_paper.py:17-18`) and price rows (`pricing.py:25-29`).
- Two routes tried: (1) OpenAI models-list probe → 401 invalid key (key held, rejected); (2) in-clone backend grep for `openai|gpt-5|anthropic|completion` → no invocable LLM path, only baseline constants. Substitute path taken instead: xAI + Anthropic keys verified live (both HTTP 200 with model lists), grok-4.20-0309-non-reasoning arm run per T6 row above.

### T10 verdict block

- Result class: **FLOOR** (beats both floor arms with margin; live substitute beaten numerically but paired test ns at n=35; paper incumbent not re-asked live — INCUMBENT not earned).
- RULEBOOK tiers: Jev numbers = maintainer-measured (this receipt: independent re-run of the maintainer's own harness); paper baselines = independent (arXiv:2607.09996 Table 4, not re-verified).
- NO-CLAIM line: No claim is made about full-6,257 accuracy, live gpt-5.4 parity, generalization to natural production incidents, latency comparison across models (shared early-access endpoint per `RESULTS.md:10`), or xAI cost (unpriced).
- Totals: 480 Jev calls ($0.0696 + 3×$0.0156 = **$0.1164**) + 60 grok calls (tokens stated, unpriced). Zero errors on all five live arms.

## Boundary

Sample-only verdict: N=300 stratified (floor 20/framework) ≠ population; small frameworks oversampled vs the 6,257 distribution (smolagents 52% in population, 31% in sample), so the 0.783 Who point is not a population estimate. Who is scored on multi-agent rows only (139/300); debate/dylan GT uses `agents[0]` normalization. Paired grok comparison is n=35 (p=0.13, underpowered — direction only). Prior receipts (incl. any 20260918) treated as leads, not passes; nothing herein cites them. Clone tree unmodified (all defects/scratch in `/tmp/jev-afb-t2`, `/tmp/jev-afb-w70`).
