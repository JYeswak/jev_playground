# Task h16: next cron fire time

Work in $PWD. `cronx.py` has `next_fire(expr, after)` where expr is
`MIN HOUR` with fields `*`, `*/k`, `a-b`, `a,b` (minute 0-59, hour 0-23)
and `after` is a naive datetime; return the next datetime strictly after
`after` matching both fields (same-day, next-day, etc.). shipped code is
wrong on wraps and steps. Fix it, stdlib datetime only. Verify yourself.
