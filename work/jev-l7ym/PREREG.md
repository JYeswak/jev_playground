# jev-l7ym widened log measurement preregistration

reach-mode: mcnemar

## Universe

Use only non-authored omp session JSONL under `~/.omp/profiles/*/agent/sessions/**/*.jsonl`, selected by filesystem mtime within a fixed seven-day window at run time. The unit is one direct `find` tool execution with both its recorded `tool_execution_start` and `toolResult` present. Host-tool `find` calls nested inside `eval` are a separate telemetry source and are reported as excluded because their ranked result and next-tool sequence are not present in the session row shape.

## Outcome and comparator

The observed outcome is the first returned hit read, edited, or written in the next ten tool calls. The Jev rank is the recorded `hits` array order. The no-Jev comparator is the same returned hit set sorted by `(len(rel), rel)` because the pre-rerank order is absent from the recorded result details. A ranked result with no matched next-ten file use is retained in the denominator for no-use reporting but excluded from top-1/top-3 hit-rate denominators.

## Bar, fixed before the widened run

- Minimum analyzable matched windows: **100**.
- Minimum discordant paired outcomes for a McNemar comparison: **20**.
- `bar-reachable.py --mode mcnemar` is used on the derived aggregate fixture. Its reachability result is feasibility only: it must not be read as a ranking verdict.
- If either minimum is missed, report **UNDERPOWERED** and make no ranking ruling. Exact two-sided McNemar p is reported for the paired top-1 outcomes when the window exists; Wilson intervals are reported for actual and baseline top-1/top-3 rates.

## Boundary

This is an observational association study. It does not establish that Jev caused the next file use, and it does not treat model-usage rows as additional independent ranking outcomes. API calls are outside this log-only run; the source corpus was not authored by the scorer.
