def build(node, _params=None):
    top = _params is None
    if top:
        _params = []
    if len(node) == 2 and node[0] in ("and", "or"):
        _, children = node
        parts = [build(c, _params)[0] for c in children]
        return ("(" + (" %s " % node[0].upper()).join(parts) + ")", _params)
    if len(node) == 2 and node[0] == "not":
        s, _ = build(node[1], _params)
        return ("(NOT " + s + ")", _params)
    col, op, val = node
    if op not in ("=", "!=", "<", ">", "<=", ">=", "LIKE"):
        raise ValueError("bad op: %r" % (op,))
    _params.append(val)
    return ("%s %s $%d" % (col, op, len(_params)), _params)
