# Task k14: interval union and gaps

Work in $PWD. `ivl.py` has `union(intervals)` merging overlapping [lo, hi)
half-open intervals (adjacent [1,2)+[2,3) merge ONLY if `merge_adjacent`
is True, default False) returning sorted disjoint lists, and `gaps(merged,
span)` returning the gaps within [span_lo, span_hi). Empty input -> [].
shipped code merges adjacent always and miscomputes gaps. Fix it, stdlib
only. Verify yourself.
