# W7.3 — What the clones teach about Jev (pane 5, 2026-09-23)

One sentence per finding, each backed by a receipt path and line. A finding seen once says "one run". No sentence without a receipt.

## Where Jev beat an incumbent (T6)

- Rerank: Jev ties Cohere Pro, McNemar b=5/c=2 p=0.4531 at N=30 — one run, no winner either way (`jev-rerank-bench-w70-2026-09-23.md:22`).
- Risk triage: Jev-live 52/60 vs Haiku 49/60, McNemar p=0.146 n.s. — one run, direction only (`jev-benchmark-w70-2026-09-23.md:51`).
- Agent attribution: Jev 28/35 vs grok substitute 23/35, p=0.13 n.s. — one run, underpowered (`jev-agent-failure-benchmark-w70-2026-09-23.md:20`).
- Injection: fresh Jev 640/662 beats fresh Haiku 584/662, discordants 61 Jev-only / 5 Haiku-only, McNemar p=2.6e-13 — one run, certified these-662-only (`jev-sec-bench-w70-20260923.md:20` for 640/662, `:22` for 584/662 and the discordants).
- Spam wording: specified question 20/20 beats a vague hand-written one 15/20, McNemar b=5/c=0 — one run, wording moves 0.25 (`jev-align-w70-20260923.md:29`).

## Where a floor tied or beat it (T5) — the refused seats

- Risk triage is the model refused seat: a one-pass keyword cascade scores 58/60, beating live Jev (52/60) and the committed 55/60, so escalation-routing on this set is class A/B and refused (`jev-benchmark-w70-2026-09-23.md:48`).
- Phishing is refused twice over: regex 91.65% and the Haiku incumbent (paired p=1.3e-5) both beat the Jev verdict 62.98% (`jev-phishing-bench-w70-20260923.md:27`).
- Foreman is refused: lexical floor 12/12 on self-authored vignettes (`foreman-w70-20260923.md:15-18`, pane-4 EVAL text).
- Where floors lost cleanly: rerank (BM25 top-1 10/30 vs live 15/30), agent attribution (majority 0.194, lexical 0.554 vs 0.799), ts-bench (9/12, 16/17, 4/6 vs 35/35), injection/code (0.6027/0.6329 and 0.5000/0.5625 beaten) — one run each (`jev-rerank-bench-w70-2026-09-23.md:20`, `jev-agent-failure-benchmark` T5 row, `typesafe-ai-benchmark-w70-2026-09-23.md` T5 row, `jev-sec-bench-w70-20260923.md:33`).
- jevcal's floors (100.0/87.5/100.0 on a synthetic generator-trivial corpus) prove the corpus is separable by keywords, so its bar tests threshold validity, not discrimination — one run (`jevcal-live-w70-2026-09-23.md:102-112` approx; floors section).

## Calibration at our N (T7)

- Observable with counts: rerank bins spread 2/10/10/8 across four bins at N=30 (`jev-rerank-bench-w70-2026-09-23.md:23`); injection deciles with ECE 0.0684, code ECE 0.1792 with middle bins n≤28 declared not-observable (`jev-sec-bench-w70-20260923.md:23`); Janus bins monotone on both arms (`janus-live-w70-2026-09-23.md:19`).
- Directional only: risk-judgment mass sits 47/56 in the top bin with a wrong answer at 0.98 just under the 1.000 check (`jev-benchmark-w70-2026-09-23.md:28`).
- Not observable: ts-bench at N=7 says so outright; foreman single bin with zero negatives (`typesafe-ai-benchmark-w70-2026-09-23.md` T7 row; pane-4 foreman text).

## Stability (T8 flip rates)

- Zero flips: rerank 0/10 repeats + 0/5 framing; Janus bank 0 on all pairs; agent-attribution 3/60; ts-bench 0/28 repeats; align 0/10; jevcal 0 on urgency/department — one run each (`jev-rerank-bench-w70-2026-09-23.md:24`, `janus-live-w70-2026-09-23.md:20`, `jev-agent-failure-benchmark` T8 row, `typesafe-ai-benchmark` T8 row, `jev-align-w70-20260923.md:31`, `jevcal-live-w70-2026-09-23.md:13`).
- Nonzero but accuracy-neutral: Janus WoS row 3315 flips at conf 0.21–0.26, wrong in all asks (`janus-live-w70-2026-09-23.md:110`); risk-triage row t058 flips while always wrong at low confidence (`jev-benchmark-w70-2026-09-23.md:29`); injection reword moves 6/150 + 2/120 (`jev-sec-bench-w70-20260923.md:36`); phishing reword agreement ~0.80 (`jev-phishing-bench-w70-20260923.md` T8 line).
- Rule of thumb emerging across runs: flips cluster on rows that are wrong at low confidence; confident rows do not flip — one synthesis over seven runs, not a measured claim.

## Thresholds: what fit, what transferred, what did not

- jevcal: per-question thresholds fit on rows t001–t200 (0.75/0.61/0.88) meet the same bar arithmetic on t201–t400 and land within 0.02 of full-run thresholds (0.73/0.61/0.87) — TRANSFER within one corpus, one run (`jevcal-live-w70-2026-09-23.md:14` + fit table).
- What did not transfer: Janus froze the same protocol on two datasets and the threshold (0.67→0.37), the accuracy gap sign, and the route/do-not-route verdict all changed — no routing parameter survived the dataset switch, one run (`janus-w70-2026-09-23.md:47-48`, NO-TRANSFER claim).
- Builder reading, one sentence: fit thresholds per question on your own labelled split and re-check them in CI; never carry a threshold across datasets, tasks, or model versions — one lesson from two runs.

## Transport behaviour (T9)

- The vendored JS SDK leaks timer AbortErrors that exit the host: 189/189 tests pass yet the process exits 1 on 8 unhandled rejections (`typesafe-sdk-js-w70-20260923.md:16` + T1 line).
- Our `work/jev-client` inherited the leak (~1/3 of timeouts killed Node) and now owns the timeout in `guardedFetch`: Node 30/30 + Bun 30/30 hosts survive, regression test failed pre-fix and passes post-fix (`jev-client-w70-20260923.md:24-27,36,50`).
- Faults otherwise refuse closed: timeout/429/malformed/missing-key map to typed errors with the host alive across SDK, adapter, s1-rs, and jevcal surfaces — one run each (adapter/s1-rs/jevcal T9 rows).

- ts-bench: ~$0.000121 for 7 calls (`typesafe-ai-benchmark-w70-2026-09-23.md` T4 row).
- jevcal: $0.0113 input-side for 560 requests (`jevcal-live-w70-2026-09-23.md:101-102`).
- Janus: $0.1274 for 940 requests at $0.042/MTok in (`janus-live-w70-2026-09-23.md:127`).
- Agent attribution: $0.1164 for 480 Jev + 60 grok calls (`jev-agent-failure-benchmark-w70-2026-09-23.md:49`).
- Rerank: $0.02683 (45 Jev) + $0.075 (30 Cohere) (`jev-rerank-bench-w70-2026-09-23.md:26`).
- Phishing upstream rate, not re-measured here: $0.0385/1k Jev vs $0.9295/1k Haiku arm (`jev-phishing-bench-w70-20260923.md:21`, upstream numbers).

## Table: question shape × task class × verdict × receipt

| shape | task class | verdict | receipt |
|---|---|---|---|
| score + choice + noul | passage rerank | SELF | `jev-rerank-bench-w70-2026-09-23.md` |
| choice | tool-call risk triage | FLOOR (refused) | `jev-benchmark-w70-2026-09-23.md` |
| choice ×3 | agent/step/mode attribution | FLOOR | `jev-agent-failure-benchmark-w70-2026-09-23.md` |
| choice + noul + score | synthetic app workloads | SELF | `typesafe-ai-benchmark-w70-2026-09-23.md` |
| choice + noul | banking intent + WoS subject | SELF (no transfer) | `janus-live-w70-2026-09-23.md` |
| choice + noul ×3 | support-ticket thresholding | SELF (transfer within corpus) | `jevcal-live-w70-2026-09-23.md` |
| noul | click-or-not verdict | FLOOR (refused) | `jev-phishing-bench-w70-20260923.md` |
| noul | SMS spam verdict | REFUSED (bar) | `jev-align-w70-20260923.md` |
| noul | injection/code verdict | INCUMBENT / SELF-refused | `jev-sec-bench-w70-20260923.md` |
| choice | foreman escalation vignettes | FLOOR (refused) | `foreman-w70-20260923.md` |
| choice + score + noul | compaction keep/drop | n/a — own demo; live dropped all three calls vs fixture keep (divergence recorded) | `demos/compact/live-receipt.json` |
| noul battery | extraction verification | n/a — own demo; live escalated registration_open_date vs fixture location (divergence recorded) | `demos/cascade/live-receipt.json` |

NO-CLAIM: every row above is one run at its stated N; the table maps what was measured, not what Jev can do.
