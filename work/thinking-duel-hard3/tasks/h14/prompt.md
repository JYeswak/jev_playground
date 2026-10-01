# Task h14: exponential histogram buckets

Work in $PWD. `hist.py` has `bucket_bounds(base, n)` returning n+1
boundaries `[base**0, base**1, ..., base**n]` (base > 1) and `assign(v,
bounds)` returning the bucket index i with bounds[i] <= v < bounds[i+1],
or -1 if v is below bounds[0] or at/above bounds[-1]... precisely: values
equal to the LAST boundary belong to the last bucket (index n-1); values
below bounds[0] or above bounds[-1] return -1. shipped code has an edge
error. Fix it, stdlib only. Verify yourself.
