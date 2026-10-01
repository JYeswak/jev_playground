# Task h11: smallest topological order

Work in $PWD. `topo.py` has `order(deps)` (node -> deps list) returning
`(ok, result)`: ok True with the LEXICOGRAPHICALLY SMALLEST valid
topological order (dependencies before dependents), or ok False with a
cycle list (first node repeated at end). Nodes not keys but listed as deps
count as dependency-free nodes. shipped code is wrong. Fix it, stdlib only.
Verify yourself.
