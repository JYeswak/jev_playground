def order(deps):
    visited = {}
    out = []

    def visit(n, stack):
        if visited.get(n):
            return None
        visited[n] = True
        if n in stack:
            return stack[stack.index(n) :]
        stack.append(n)
        for d in deps.get(n, []):
            c = visit(d, stack)
            if c:
                return c
        stack.pop()
        out.append(n)
        return None

    for n in deps:
        c = visit(n, [])
        if c:
            return (False, c + [c[0]])
    return (True, out)
