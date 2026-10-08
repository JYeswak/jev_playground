# Task u06: ISO-8601 duration parser

Work in $PWD. `durations.py` has `parse_duration(s)` returning total seconds as a float. It is wrong. Fix it, standard library only. Verify yourself with weeks, fractional commas, negatives, and invalid shapes.

Rules: an optional leading `-` negates the whole duration, then `P` followed by date components `<n>Y <n>M <n>W <n>D` in that order and an optional `T` section with `<n>H <n>M <n>S`; `M` before `T` is months (30 days), after `T` minutes. `W` (7 days) must stand alone (`P<n>W` with nothing else). Values are integers or decimals with `.`/`,`; at most one fractional component, and it must be the last one present. Conversions: Y=365d, M=30d, D=86400s, H=3600s, minute=60s. At least one component is required; anything else raises `ValueError`. `PT0S == 0`.
