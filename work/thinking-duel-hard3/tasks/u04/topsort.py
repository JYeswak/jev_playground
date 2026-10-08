from collections import defaultdict


def lex_topo(nodes, edges):
    succ = defaultdict(list)
    for a, b in edges:
        succ[a].append(b)
    visited = set()
    order = []

    def dfs(n):
        visited.add(n)
        for m in succ[n]:
            if m not in visited:
                dfs(m)
        order.append(n)

    for n in nodes:
        if n not in visited:
            dfs(n)
    return order[::-1]
