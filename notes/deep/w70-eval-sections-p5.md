# W7.0 EVAL sections — pane 5 group (STAGING: EVAL.md was reservation-held; pane 1 append)

## EVAL — jev-rerank-bench W7.0 (SELF)

T1–T8+T10 at `cd9a35b`. Committed cache re-scores byte-identically; live rubric reproduces cache 28/30 (bar ≥24/30, N=30 seed 20260923, $0.017876, p50 397.9ms/p95 992.7ms); floors beaten (top-1 10/30 nDCG 0.3811 vs live 15/30 0.4958); Cohere Pro tied (12/30, McNemar p=0.4531, $0.075). Live spend 45 Jev + 30 Cohere. Receipt: `docs/demos/upstream-repro/jev-rerank-bench-w70-2026-09-23.md`. NO-CLAIM beyond the 30 rows + cache re-score.

## EVAL — jev-benchmark W7.0 (FLOOR, seat REFUSED)

T1–T8+T10 at `daf02b3`. Live 52/60 in bar range [52,58]; majority floor 18/60 stated; one-pass lexical cascade 58/60 BEATS live Jev and committed 55/60 → class-A/B task, seat REFUSED for escalation-routing claims. Haiku substitute 49/60 (grok-4 route 404'd); McNemar p=0.146 n.s. T7 weakly observable (1.000-mass 36/56). Receipt: `docs/demos/upstream-repro/jev-benchmark-w70-2026-09-23.md`.

## EVAL — jev-agent-failure-benchmark W7.0 (FLOOR)

T1–T8+T10 at `4d46af7`. N=300 sample: Jev agent 111/139=0.799, Wilson LB 0.7243 > floor 0.1942 → T4 PASS. Lexical-first 0.554, no tie. gpt-5.4 NOT-RUN (401 + no in-clone backend); grok substitute 23/35 vs Jev 28/35, p=0.13 ns. ECE 0.0545 (n=139). 480 Jev calls ($0.1164). Receipt: `docs/demos/upstream-repro/jev-agent-failure-benchmark-w70-2026-09-23.md`.

## EVAL — typesafe-ai-benchmark W7.0 (SELF)

T1–T8+T10 at `e94fcda`. Live 7/7 fixture verdicts match (bar ≥5/7), 35/35 sub-verdicts, 7 calls ≈$0.000121, p50 219.5ms/p95 562.7ms. Floors below (9/12, 16/17, 4/6 vs 35/35). Qwen/Cerebras NOT-RUN (key not held). T7 not observable at N=7. 3× flips 0/28. Receipt: `docs/demos/upstream-repro/typesafe-ai-benchmark-w70-2026-09-23.md`.

## EVAL — awesome-typesafe W7.0 (catalogue PASS)

T1+T3 at `c2d5cf9`. 8/8 benchmark-claiming entries assessed: 7 clone-candidates + 1 catalogue-only (Judge-vs-Dimensions post). jevcal + Janus URLs resolve (cloned by sibling agents this wave). OpenJev link stale (redirects to SemIf — flag for catalogue owner). Zero Jev calls. Receipt: `docs/demos/upstream-repro/awesome-typesafe-w70-2026-09-23.md`.

## EVAL — jevcal W7.0 (T1–T3 earned, T4 proposed)

NEW CLONE abhixhek/jevcal@`ae8f314` (2026-09-18, MIT). pytest 24/0/0; plant turns RED. 8 claims (5 demonstrated, 2 partial, 1 aspirational). T9: 5 fault arms refuse as ProviderError. T4 bar proposed (400-row tickets.jsonl, PASS = status ok on all 3 questions + held-out ≥ target−0.02) — committed bar amendment required before any live call. Receipt: `docs/demos/upstream-repro/jevcal-w70-2026-09-23.md`.

## EVAL — Janus W7.0 (T1–T3 earned, T4 proposed)

NEW CLONE FirasSX914/Janus@`9cb66c4` (2026-09-18, Release 0.3.1, MIT). pytest 38/0/0; plant flips verdict. 8 claims recomputed keylessly (7 demonstrated, 1 partial). T4 bar proposed (Banking77 N=500 ±5pts of 77.80% AND WoS-200 ±5pts of 54.50%, ceiling $2.00) — committed bar amendment required before any live call. Receipt: `docs/demos/upstream-repro/janus-w70-2026-09-23.md`.
