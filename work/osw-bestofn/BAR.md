# LIVE BAR — jev-jy7t.1.2

Fixed before the first live Jev call.

> Jev's pick beats the best single run by >= 3 points (McNemar p < 0.05) and closes >= 30% of the gap to oracle@N.

Operational definitions for the official continuous `result.txt` rewards:

- “points” = mean official reward multiplied by 100;
- McNemar uses paired exact-completion indicators (`result.txt` reward >= 1.0);
- `oracle@N` = per-task maximum official reward across the frozen N=8 pool;
- kill if Jev is no better than the best single run.

No threshold, question wording, candidate ordering, tie-break, or bar changes after the first live
call. No comparator model is run.
