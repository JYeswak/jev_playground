import sys

sys.path.insert(0, SYS_PATH)
from topsort import lex_topo


def check(nodes, edges, order):
    assert sorted(order) == sorted(nodes), order
    pos = {n: i for i, n in enumerate(order)}
    for a, b in edges:
        assert pos[a] < pos[b], (order, (a, b))


# 1. diamond: smallest valid order, regardless of input order
o = lex_topo(["b", "a", "c"], [("a", "c"), ("b", "c")])
check(["b", "a", "c"], [("a", "c"), ("b", "c")], o)
assert o == ["a", "b", "c"], o

# 2. unconstrained nodes come out sorted
assert lex_topo(["c", "b", "a"], []) == ["a", "b", "c"]

# 3. mid-graph choice with a duplicate edge
o = lex_topo(["d", "c", "b", "a"], [("b", "d"), ("c", "d"), ("b", "d")])
check(["d", "c", "b", "a"], [("b", "d"), ("c", "d")], o)
assert o == ["a", "b", "c", "d"], o

# 4. forced-first node beats lexicographic order
o = lex_topo(["a", "b", "c"], [("c", "a"), ("c", "b")])
check(["a", "b", "c"], [("c", "a"), ("c", "b")], o)
assert o == ["c", "a", "b"], o

# 5. self-loop and longer cycles raise ValueError
for bad in ([("a", "a")], [("a", "b"), ("b", "a")],
            [("a", "b"), ("b", "c"), ("c", "a")]):
    try:
        lex_topo(["a", "b", "c"], bad)
    except ValueError:
        pass
    else:
        raise SystemExit("u04 FAIL: no ValueError for %r" % (bad,))

# 6. empty graph
assert lex_topo([], []) == []
print("u04 PASS")
