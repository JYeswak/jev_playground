# Stranger grade: hardening-20260920.md — 2026-09-20 `[pending]`

Author grading own page (weaker check, conductor verifies independently).
Every runnable command executed from repo root, exit codes unpiped.

## Per-command verdicts

| command as written | result |
|---|---|
| `bash scripts/selftest-vgrep.sh` | RUNS — 8 ok, 0 failed, rc=0 |
| `bash scripts/selftest-pinned-denominator.sh` | RUNS — 11 ok, 0 failed, rc=0 |
| `bash scripts/selftest-denominator-sweep.sh` | RUNS — 3 ok, 0 failed, rc=0 |
| `bash scripts/selftest-pin-liveness.sh` | RUNS — 8 ok, 0 failed, rc=0 |

No BROKEN, no RUNS-BUT-DOES-NOT-DEMONSTRATE. Relative links resolve
(`docs/demos/upstream-repro/` → `scripts/` present). Refusal triggers
checkable at NEGATIVE_EVIDENCE.md R46/R47/R48 (appended, not edited).
Arm counts on page match runs (8/11/3; pin-liveness states no count —
correct, its selftest reports 8).

## Is this page true for someone never in this lane?

Yes for everything executable: all four commands work as written. The
session-record numbers (26/8/4/4/4) are trust-me census, presented as
such, with the ledger path to check them. The limits section discloses
exactly what wired does not cover.

## NO-CLAIM

Self-grade; independent verification pending. Fresh-clone caveat
(RULES.md stranger test): selftests run on committed files + pinned
fixtures; the sweep's backtest arm needs `demos/routing-backtest`
dependencies installed (`npm test`).
