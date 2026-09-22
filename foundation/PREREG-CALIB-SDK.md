# PREREG-CALIB-SDK — foundation calibration transport onto the vendored SDK

Committed by P2 BEFORE the first migrated live call in this unit.
A bar written after the numbers is not a bar (R69 law).

## Question this answers

Does the native SDK change our calibration numbers — i.e., was the
hand-rolled urllib wire in `run_calibration.py:44-67` shaping the fourth
oracle's results? `jev-cp2` file 2 (file 1, `measure-framing-flip.mjs`,
verified already routed via `askJevBundle`, zero fetch matches).

## Corpus (mechanical, full — no sampling)

80 rows of `foundation/fixtures/calibration-v1.jsonl` (60 noul + 20
choice), file order. Spend is not a reason to sample: Joshua blanket
approval 2026-09-21 (`9e10788`), restated 2026-09-22. 80 calls, attended
foreground run, key via Infisical (`infisical run --projectId=...`),
interpreter = the SDK clone's own `.venv` python (no pip, no path hacks).

## Migration (transport only; metrics untouched)

- `ask()` builds `Noul(instructions)` / `Choice(instructions, criteria)`
  (fixture options already a MAP) and calls
  `TypeSafeClient(api_key, timeout=30, retry=RetryPolicy(max_retries=2)).system_one`.
  Timeout mirrors TIMEOUT_S; max_retries mirrors MAX_RETRIES. Backoff
  differs by construction (SDK 0.5 doubling to 5.0 + 0.25 jitter vs
  2/4/8 s sleeps) — recorded, not hidden.
- Returns plain dicts in the SAME shape downstream consumes
  (`{"noul": p}` / `{"choice", "confidence"}`); `as_noul`, choice checks,
  error kinds (`timeout`/`http_error`/`malformed`), metrics, bins, sweeps,
  receipt schema: all byte-identical code paths.
- `attempts` semantic change (documented): SDK-opaque — 1 on success,
  policy max+1 (=3) by construction on error. Was per-attempt count.
- Defect fixed in passing: default model `jev-latest` (moving) pinned to
  `jev-1.13.0`; `--model` override kept.

## Old arm (CITED, never re-measured)

Receipt `foundation/runs/20260917T224444Z.json`: ECE 0.061, Brier 0.020,
Noul 58/60, Choice 19/20, threshold ≥0.75 → accuracy 1.0 at ≥90% coverage.
Model resolved `jev-latest → jev-1.13.0` on 2026-09-17.

## Bar (STAND = numbers reproduce; DIVERGE = the wire was shaping results)

1. Migrated run completes on all 80 with fixture sha match (gate 20).
2. ECE, Brier, choice accuracy, threshold sweep REPORTED.
3. AGREE iff same verdict class on ≥76/80 rows AND |ΔECE| ≤ 0.03 AND
   choice_acc within ±1 row of 19/20. Else DIVERGE — the bigger finding
   (report as measured, do not tune).
4. `foundation/gates.sh` green on the new receipt; EVAL row updated.

## NO-CLAIM (same paragraph as every number)

Single run, fixed 0.5 DESCRIBED cut inside sweeps, one model id, one
SDK pin (`0ffd094`). AGREE certifies transport-equivalence on this
fixture only — not the SDK in general. Spend: 80 calls + receipt tokens.
