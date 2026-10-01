# Task k01: stable k-way merge

Work in $PWD. `kmerge.py` has `merge(streams, key=None)` merging sorted
input iterables (each already sorted by key) into one sorted list, STABLE:
equal keys keep stream order (lower stream index first). Must not assume
list inputs (any iterable, including generators) and must handle empty
streams. shipped code breaks stability and chokes on generators. Fix it,
stdlib only. Verify yourself.
