_ALLOWED_OPS = {"=", "!=", "<", ">", "<=", ">=", "LIKE"}


def build(node, _params=None, _counter=None):
    if _params is None:
        _params = []
        _counter = [1]

        sql, params = _build(node, _params, _counter)
        return (sql, params)
    return _build(node, _params, _counter)


def _build(node, params, counter):
    kind = node[0]
    if kind in ("and", "or"):
        parts = [_build(c, params, counter)[0] for c in node[1]]
        return ("(" + (" %s " % kind.upper()).join(parts) + ")", params)
    if kind == "not":
        s, _ = _build(node[1], params, counter)
        return ("(NOT " + s + ")", params)
    col, op, val = node
    if op not in _ALLOWED_OPS:
        raise ValueError("bad op: %r" % (op,))
    ph = "$%d" % counter[0]
    counter[0] += 1
    params.append(val)
    return ("%s %s %s" % (col, op, ph), params)
