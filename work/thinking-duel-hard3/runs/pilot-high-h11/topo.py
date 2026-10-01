import heapq


def order(deps):
    nodes = set(deps)
    for ds in deps.values():
        for d in ds:
            nodes.add(d)

    # dependents[dep] = set of nodes that directly depend on dep
    dependents = {n: set() for n in nodes}
    indeg = {n: 0 for n in nodes}
    for n, ds in deps.items():
        uniq = set(ds)
        indeg[n] = len(uniq)
        for d in uniq:
            dependents[d].add(n)

    heap = [n for n in nodes if indeg[n] == 0]
    heapq.heapify(heap)
    out = []
    while heap:
        n = heapq.heappop(heap)
        out.append(n)
        for m in dependents[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)

    if len(out) == len(nodes):
        return (True, out)

    # Cycle among nodes not emitted.
    remaining = set(n for n in nodes if indeg[n] > 0)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in remaining}
    stack = []

    def dfs(n):
        color[n] = GRAY
        stack.append(n)
        for d in deps.get(n, []):
            if d not in remaining:
                continue
            if color[d] == GRAY:
                i = stack.index(d)
                return stack[i:]
            if color[d] == WHITE:
                c = dfs(d)
                if c is not None:
                    return c
        stack.pop()
        color[n] = BLACK
        return None

    for n in sorted(remaining):
        if color[n] == WHITE:
            c = dfs(n)
            if c is not None:
                return (False, c + [c[0]])
    # Fallback (should be unreachable): report leftovers as pseudo-cycle.
    leftover = sorted(remaining)
    return (False, [leftover[0], leftover[0]])
