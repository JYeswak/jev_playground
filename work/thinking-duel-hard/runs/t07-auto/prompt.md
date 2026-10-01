# Task t07: deterministic shuffle

Work in $PWD. `shuffle.py` has `order(n, seed)` returning a permutation of
`range(n)` that must be DETERMINISTIC across runs and Python versions for
the same seed, and a uniform shuffle (Fisher-Yates). It currently uses
`random.Random(seed).shuffle`, whose output is version-dependent. Reimplement
with an inline integer LCG (no `random` module): state = (1103515245 * state
+ 12345) % 2**31, j = state % (i + 1), iterating i from n-1 down to 1.
Verify determinism yourself.
