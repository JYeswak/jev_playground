# Classifier-family marginal cost preregistration

**Decision locked:** 2026-10-06, before the second family contract commit (`kit/contracts/<family>.json`).

## Question

Do the second and third contracted classifier families cost no more to take from contract to ship verdict than the first family, across elapsed time, touched files, commits, agent sessions/turns, recorded model calls, and recorded spend?

## Ceiling

For each axis, family 2 and family 3 must be **at or below 1.00× family 1**. This is the conservative interpretation of “makes the next one cheap”: neither successive family may cost more than the first on any measured axis. No averaging across axes, families, or missing data. A zero baseline is undefined and fails the comparison; missing source data is an error, never zero.

The ceiling is fixed before the second contract commit. It will not be changed after seeing family costs. `measure.py` checks Git commit ancestry, not timestamps, and refuses a late preregistration.

## Measurement boundary

A family begins at the first commit adding `kit/contracts/<family>.json`; it ends at the first commit adding `work/ship/<family>/SHIP.md`. The first three families are ordered by ship-verdict commit. The window includes both endpoint commits. Git-derived axes are elapsed wall seconds, unique changed paths, and commit count. Agent sessions, completed assistant responses (the recorded-turn proxy), model calls, and spend are derived only from records attributable to the family’s bead IDs and whose timestamps fall inside that window. Each reported value must name its source commit, bead, or log path. Direct Jev input cost uses the pinned rate in `docs-mirror/typesafe/models.md:11-18`; omp model-usage rows use their recorded cost.

No extrapolation, interpolation, fixed-path sample answer, or unrecorded estimated cost. A missing start/end commit, missing attributable spend record, malformed source, or insufficient set of three shipped families refuses the measurement.

## Current state

At preregistration time, `kit/contracts/screen.json` is the only family contract found, and `work/ship/` does not exist. No family-cost result is claimed. The second contract is not yet present, so chronology is feasible. Until three ship verdicts and complete telemetry exist, the mission clause “makes the next one cheap” is **NOT MET / UNMEASURED**.
