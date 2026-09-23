# W7.0 EVAL sections (pane 4 MistyTurtle) — for pane 5 to append to EVAL.md

Held here because the Agent Mail DB is in recovery and pane 5 is sole EVAL.md
writer until 05:00Z. Foreman + sec-bench landed; phishing + spam sections
will be appended to this file as those runs land.

## foreman W7.0 (2026-09-23) [test]

Clone `foreman @ 2c43982` (thruwire, MIT). jev HEADs: bar `9e8199b`, run
`fcbb050`, receipt `679e5f4`. Receipt
`docs/demos/upstream-repro/foreman-w70-20260923.md` (+ frozen rows
`foreman-w70-rows-20260923.jsonl`).
Suite `PYTHONPATH=src uv run pytest tests/ -q` → 1 failed, 57 passed, exit 1
(lead 57/58 reproduced); /tmp plant (stuck_threshold 0.80→0.99) → RED.
T4 N=12 self-authored vignettes (labels frozen pre-call), prevalence 25%x4:
11/12 = 0.9167 CI [0.6152, 0.9979]; floors always-FINISH 3/12,
always-ESCALATE 3/12, lexical 12/12 → bar (lower-CI > floor) fails →
REFUSED class FLOOR. Latency p50 0.195 / p95 0.330 s; API unpriced. T6
haiku-4-5 via adapter: 9/12, McNemar p=0.5 (inseparable at N=12). T7 not
observable (single bin, zero negatives). T8 48/48 stable. Pane-4 re-runs:
suite, plant, floor row-by-row, incumbent tally.
Boundary: self-authored vignettes, no live Codex run, API cost unpriced.

## jev-sec-bench W7.0 (2026-09-23) [test]

Clone `jev-sec-bench @ fdb16b9` (Gaurav-Gosain, MIT, Go 1.27.1). jev HEADs:
bar `9e8199b`, receipt per commit. Receipt
`docs/demos/upstream-repro/jev-sec-bench-w70-20260923.md`.
`go test -race -count=1 ./...` green uncached; /tmp plant
(metrics_test.go:25 TP!=1→2) → FAIL TestConfusionCounts. T4 INJECTION n=662
prev 39.73%: 640/662 = 0.9668 CI [0.9501, 0.9791], AUC 0.9926, p50 191ms
p95 379ms; tokens 439330/23170 EXACT match committed. CODE n=400 prev 50%:
284/400 = 0.7100 CI [0.6628, 0.7540], pairs 178/200 reproduced. Floors beaten
on both (inj 0.6027/0.6329; code 0.5000/0.5625). T6 haiku-4-5 584/662 =
0.8822, McNemar p=2.6e-13 (injection only). T7 decile bins with counts
(inj ECE 0.0684; code ECE 0.1792). T8 flips 0 repeats; reword 6/150 + 2/120.
Verdict SPLIT: injection INCUMBENT (certified these-662-only), code SELF but
REFUSED (absolute 0.70 bar). Pane-4 re-runs: suite, plant, `ls cmd`
(runner-absence confirmed), all accuracies + token sums from fresh rows.
T3: 5 demonstrated, 1 partial, 1 disproven (`-bench all` runner absent).
NOT-RUN: code LLM arm; live ablation; RunAudit e2e (retries in receipt).
Boundary: public-corpus leakage caveat; single runs; fixed 0.5 cut.

## jev-phishing-bench W7.0 (2026-09-23) [test]

Clone `upstream/anisselbd/jev-phishing-bench @ 1d56e8c` (no LICENSE). jev
HEADs: bar `9e8199b`, run 2026-09-23T03:38Z. Receipt
`docs/demos/upstream-repro/jev-phishing-bench-w70-20260923.md`. Corpus 2000
rows recounted. Status clean before/after. No committed suite; /tmp plant
(`registered_domain`->'') drops floor 0.9165->0.6055. T4 full 2000 calls
(1999 ok): verdict 0.6298 CI [0.6084, 0.6507], p50 195ms, $0.0769. Floor
same rows 0.9165 CI [0.9035, 0.9278] -> REFUSED class A. T6 haiku-4-5
400 shared rows 0.7475, McNemar p=1.3e-5 (incumbent better). T7 ECE 0.1611
observable. T8 flips ~2.4%, reword agree ~0.80. Pane-4 re-runs: status,
corpus count, committed metrics, raw tallies (1259/2000, 1257/2000,
haiku 299/400), analyzer (T4/T5/T6 lines reproduced keyless).
Boundary: one transient 520 row; public-corpus leakage caveat.
