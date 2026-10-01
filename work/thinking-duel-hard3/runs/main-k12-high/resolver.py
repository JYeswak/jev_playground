def _t(v):
    return tuple(int(x) for x in v.split("."))


def resolve(index, reqs):
    out = {}
    for pkg, (lo, hi) in reqs.items():
        cands = [
            v
            for v in index.get(pkg, [])
            if _t(v) >= _t(lo) and (hi is None or _t(v) < _t(hi))
        ]
        if not cands:
            return None
        out[pkg] = max(cands, key=_t)
    return out
