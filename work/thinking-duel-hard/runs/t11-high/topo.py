def order(deps):
    visited = {}  # node -> 1=in-stack, 2=done
    out = []
    stack = []

    def visit(n):
        state = visited.get(n, 0)
        if state == 2:
            return None
        if state == 1:
            return stack[stack.index(n) :]
        visited[n] = 1
        stack.append(n)
        for d in sorted(deps.get(n, [])):
            c = visit(d)
            if c is not None:
                return c
        stack.pop()
        visited[n] = 2
        out.append(n)
        return None

    all_nodes = set(deps)
    for vs in deps.values():
        all_nodes.update(vs)
    for n in sorted(all_nodes):
        c = visit(n)
        if c is not None:
            return (False, c + [c[0]])
    return (True, out)
