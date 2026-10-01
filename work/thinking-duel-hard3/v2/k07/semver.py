def _t(v):
    return tuple(int(x) for x in v.split("."))


def _upper(op, v):
    M, m, p = _t(v)
    if op == "^":
        if M:
            return (M + 1, 0, 0)
        return (0, m + 1, 0)
    return (M, m + 1, 0)


def _range(r):
    if r == "*":
        return ((0, 0, 0), None)
    if r[0] == "^":
        return (_t(r[1:]), _upper("^", r[1:]))
    if r[0] == "~":
        return (_t(r[1:]), _upper("~", r[1:]))
    if r[:2] == ">=":
        return (_t(r[2:]), None)
    if r[0] == "<":
        return ((0, 0, 0), _t(r[1:]))
    return (_t(r), _t(r))


def intersect(a, b):
    (l1, h1), (l2, h2) = _range(a), _range(b)
    lo = max(l1, l2)
    hi = h1 if h2 is None else h2 if h1 is None else min(h1, h2)
    if hi is not None and lo >= hi:
        return None
    return (lo, hi)
