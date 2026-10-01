def build(node):
    kind = node[0]
    if kind in ("and", "or"):
        parts = [build(c)[0] for c in node[1]]
        return ("(" + (" %s " % kind.upper()).join(parts) + ")", [])
    if kind == "not":
        s, _ = build(node[1])
        return ("(NOT " + s + ")", [])
    col, op, val = node
    return ("%s %s %r" % (col, op, val), [])
