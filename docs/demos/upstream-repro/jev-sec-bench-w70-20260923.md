# jev-sec-bench W7.0 fresh run (2026-09-23, pane 4 MistyTurtle)

- jev HEAD at bar commit: `9e8199b`; clone `jev-sec-bench @ fdb16b9`
  (Gaurav-Gosain, MIT, Go 1.27.1). `git status` empty before and after.
- Prior receipts are LEADS, never passes (jev-sec-bench-20260918.md:16-17,
  EVAL.md:286, EVAL.md:1207-1225).

## T4 BAR (preregistered — predates the first live call)

Pinned `jev-1.13.0`; clone's own committed corpora (unauthored). Seat iff
Jev lower-CI ≥ 0.70 AND > floors, per battery.

## Results

| id | status | evidence |
|---|---|---|
| T1 | PASS | SHA/license/status clean; go1.27.1 darwin/arm64; keys via infisical presence-check (3/3 names, no values). |
| T2 | PASS | `go test -race -count=1 ./...` green uncached (37 top-level + subtests, 0 fail/skip). Plant in /tmp copy (metrics_test.go:25 TP!=1→2) → FAIL TestConfusionCounts. Re-run by pane 4: suite green, plant RED. Suite can fail. |
| T3 | PASS | 7 claims: injection numbers recompute EXACT from committed JSON (tp250 fp10 tn389 fn13, AUC 0.9927); fresh run 640/662; ablation bare/context recompute exact (live ablation not re-run); pairs 178/200 committed AND fresh (pair_idomitempty quirk: 2 rows = pair 0; 177/199 dropped); per-class cells exact; calibration 6/10 bins exact (4 middle bins n=5,10,8,15 elided); code 71.5% + 38% label-error partial (fresh 284/400=71.0%); `-bench all` runner DISPROVEN (`ls cmd` = only jev-tui; confirmed by pane 4). |
| T4 | SPLIT | Harness /tmp/seatrun, jev-go v0.1.0, conc 16. INJECTION n=662 prev 39.73%: 640/662 = 0.9668 CI [0.9501, 0.9791], tp250 fp9 tn390 fn13, AUC 0.9926, p50 191ms p95 379ms. Lower-CI ≥ 0.70 MET. CODE n=400 prev 50%: 284/400 = 0.7100 CI [0.6628, 0.7540], AUC 0.7942, pairs 178/200 reproduced, p50 185ms p95 292ms. Lower-CI < 0.70 → code REFUSED (absolute bar; floors beaten). 1874 Jev calls; tokens inj 439330/23170 EXACT match committed. All counts recomputed by pane 4 from /tmp/seatrun rows files. |
| T5 | PASS | Same rows offline: inj majority 0.6027, keyword 0.6329; code majority 0.5000, sink-regex 0.5625. Jev lower-CI beats every floor. Neither battery is class-A/B refusal. |
| T6 | PASS (injection) | Adapter @ adffc2e + haiku-4-5, same state/questions, 662/662 rows: 584/662 = 0.8822 (lead 579/662 within variance; in-tokens 687796 EXACT match). Discordants jev-only 61 / llm-only 5 vs fresh Jev; McNemar p=2.6e-13. Tallied by pane 4 from rows file. Code LLM arm NOT-RUN (scope: injection-only seat). |
| T7 | PASS | Decile bins WITH counts both batteries. Inj ECE 0.0684, bimodal, under-confident extremes. Code ECE 0.1792, top bin overconfident (.95→.80); middle bins n≤28 declared not-observable. |
| T8 | PASS | Seed-7 subsets (inj 150, code 120 pairs): repeats flip 0; reworded flips 6/150 inj (4.0%, -2.7pp), 2/120 code (1.7%). Small nonzero framing sensitivity. |
| T10 | SPLIT | INJECTION = INCUMBENT (beats floors + LLM, paired p≪0.05; SELF numbers reproduced). CODE = SELF but REFUSED (beats floors, pairs reproduced, absolute bar missed, no LLM arm). NOT-RUN with retry: code LLM arm (run haiku over 400 code rows); live no-context ablation (drive 662 bare rows); RunAudit e2e (port audit rules to fresh 400). |

## Boundary

Public corpora may leak into any model's training. Single runs, fixed 0.5 cut, one adapter/SDK pair for T6. Certifies the injection-guard seat on these 662 rows only; code absolute 71.0% below bar. No Rust in clone (RCH note n/a).
