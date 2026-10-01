def order(deps):
    state = {}
    out = []
    all_nodes = set(deps)
    for v in deps.values():
        all_nodes.update(v)

    def visit(n, stack):
        st = state.get(n, 0)
        if st == 2:
            return None
        if st == 1:
            return stack[stack.index(n) :]
        state[n] = 1
        stack.append(n)
        for d in sorted(deps.get(n, [])):
            c = visit(d, stack)
            if c is not None:
                return c
        stack.pop()
        state[n] = 2
        out.append(n)
        return None

    for n in sorted(all_nodes):
        if state.get(n, 0) == 0:
            c = visit(n, [])
            if c is not None:
                return (False, c + [c[0]])
    return (True, out)
