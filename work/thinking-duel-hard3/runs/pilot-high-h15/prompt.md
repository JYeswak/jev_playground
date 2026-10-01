# Task h15: bounded parallel map

Work in $PWD. `pmap.py` has `pmap(fn, items, limit)` returning results in
input order, running at most `limit` workers at once. On the FIRST exception
it must cancel pending work, wait for in-flight tasks to observe
cancellation (best effort), and re-raise that exception. shipped code runs
unbounded and never cancels. Fix it with stdlib threads
(concurrent.futures), no busy-wait. Verify with slow fns, a raiser, and a
parallelism counter asserting max active <= limit.
