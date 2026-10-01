import re

_ALLOWED_OPS = {"=", "!=", "<", ">", "<=", ">=", "LIKE"}
_COL_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")


def _build(node, params):
    kind = node[0]
    if kind in ("and", "or"):
        children = node[1]
        parts = [_build(c, params) for c in children]
        return "(" + (" %s " % kind.upper()).join(parts) + ")"
    if kind == "not":
        s = _build(node[1], params)
        return "(NOT " + s + ")"
    if len(node) != 3:
        raise ValueError("bad leaf node: %r" % (node,))
    col, op, val = node
    if op not in _ALLOWED_OPS:
        raise ValueError("bad op: %r" % (op,))
    if not isinstance(col, str) or not _COL_RE.fullmatch(col):
        raise ValueError("bad column: %r" % (col,))
    params.append(val)
    return "%s %s $%d" % (col, op, len(params))


def build(node):
    params = []
    return (_build(node, params), params)
