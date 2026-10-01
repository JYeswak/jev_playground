# Task h07: deterministic random subset

Work in $PWD. `subset.py` has `sample_k(n, k, seed)` returning k distinct
indices from range(n) in selection order, deterministic across runs and
Python versions for the same seed, uniform (partial Fisher-Yates), using an
inline integer LCG only (no `random` module): state = (1103515245 * state +
12345) % 2**31, j = state % (i + 1), iterating i from n-1 down to n-k, and
collecting the element swapped into position i. shipped code uses `random`
(version-dependent). Reimplement. Verify determinism yourself.
