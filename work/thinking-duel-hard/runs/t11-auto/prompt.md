# Task t11: dependency order with cycle report

Work in $PWD. `topo.py` has `order(deps)` where deps maps node -> list of
nodes it depends on. Return `(ok, result)`: ok True with a valid topological
list (dependencies before dependents), or ok False with the list of nodes
forming a cycle (in dependency order, first node repeated at the end).
Deterministic: iterate nodes and deps in sorted order. It is wrong. Fix it,
standard library only. Verify yourself.
