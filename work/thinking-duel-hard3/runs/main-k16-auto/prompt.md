# Task k16: reservoir sampler

Work in $PWD. `rsv.py` has `sample(stream, k, seed)` returning k items
uniformly sampled from an arbitrary iterable in ONE pass with O(k) memory
(reservoir sampling, Algorithm R) using an inline LCG only (no `random`
module): state = (1103515245 * state + 12345) % 2**31, j = state %
(item_index + 1) with 1-based item_index; if j < k replace reservoir[j].
Deterministic per seed. shipped code uses `random` (version-dependent).
Reimplement. Verify determinism and uniformity roughly yourself.
