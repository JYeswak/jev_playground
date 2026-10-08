# Task u11: crontab next-fire time

Work in $PWD. `cronnext.py` has `next_fire(expr, after)` where `expr` is a
5-field cron string `"min hour dom month dow"` and `after` a naive
`datetime`; return the next matching naive `datetime` strictly after
`after` (seconds/microseconds zeroed). It is wrong. Fix it, standard
library only. Verify yourself with a dom-vs-dow OR case, a step value, an
exact-hit `after`, and a `7`-as-Sunday case.

Spec:
- Ranges: minute 0-59, hour 0-23, dom 1-31, month 1-12, dow 0-7 (0 and 7
  both mean Sunday). Each field is `*` or comma-separated parts; each part
  is `*`, `*/n`, `a-b`, `a-b/n`, or a single number. Anything else
  (including out-of-range numbers or non-positive steps) raises ValueError;
  a 5-field split that is not exactly 5 fields also raises ValueError.
- Match: minute, hour, and month must all match. For dom vs dow: if both
  fields are literally `*`, any day matches; if exactly one is `*`, the
  other governs; if both are restricted, a day matching EITHER fires (OR).
- Nonexistent dates (e.g. Feb 30) simply never match. If nothing matches
  within 366 days after `after`, raise ValueError.
