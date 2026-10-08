# Task u04: lexicographically-smallest topological order

Work in $PWD. `topsort.py` has `lex_topo(nodes, edges)`. It is wrong. Fix it, standard library only. Verify yourself with diamonds, duplicate edges, and cycles.

Rules: return a topological order of `nodes` (every `(a, b)` in `edges` has `a` before `b`) that is the lexicographically smallest among all valid orders; every edge endpoint is in `nodes`. Raise `ValueError` on any cycle (including self-loops). `lex_topo([], []) == []`.
