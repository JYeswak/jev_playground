"""Semver range intersection (buggy starter)."""

import re


def _strip_tag(tok):
    return re.sub(r"-.*$", "", tok)


def _nums(tok):
    t = _strip_tag(tok).lstrip("v").strip()
    parts = t.split(".")
    out = []
    for p in parts:
        if p in ("x", "X", "*"):
            break
        out.append(int(p))
    while len(out) < 3:
        out.append(0)
    return tuple(out[:3])


def _bounds(r):
    r = r.strip()
    if r in ("", "*", "x", "X"):
        return None
    if re.search(r"\s+-\s+", r):
        a, b = re.split(r"\s+-\s+", r)
        return (_nums(a), _nums(b))
    if r.startswith("^"):
        v = _nums(r[1:])
        return (v, (v[0] + 1, 0, 0))
    if r.startswith("~"):
        v = _nums(r[1:])
        return (v, (v[0], v[1] + 1, 0))
    if re.fullmatch(r"v?\d+(\.\d+)?(\.\d+)?([xX*]|\.([xX*]))?", r):
        t = _strip_tag(r).lstrip("v").strip()
        bits = t.split(".")
        if any(p in ("x", "X", "*") for p in bits):
            n = next(i for i, p in enumerate(bits) if p in ("x", "X", "*"))
            base = [int(bits[i]) if i < len(bits) and bits[i] not in ("x", "X", "*") else 0 for i in range(3)]
            hi = list(base)
            hi[n] += 1
            for k in range(n + 1, 3):
                hi[k] = 0
            return (tuple(base), tuple(hi))
        v = _nums(r)
        if len(bits) >= 3:
            return (v, v)
        if len(bits) == 2:
            return (v, (v[0], v[1] + 1, 0))
        return (v, (v[0] + 1, 0, 0))
    lo, hi, lo_inc, hi_inc = (0, 0, 0), None, True, False
    for tok in re.split(r"[\s,]+", r):
        m = re.match(r"(>=|<=|>|<|==|=)?(.*)$", tok)
        op, v = m.group(1) or "=", _nums(m.group(2))
        if op == ">=":
            lo = max(lo, v)
        elif op == ">":
            lo = max(lo, v)
        elif op == "<=":
            hi = v if hi is None else min(hi, v)
        elif op == "<":
            hi = v if hi is None else min(hi, v)
        else:
            lo, hi = max(lo, v), v if hi is None else min(hi, v)
    return (lo, hi if hi is not None else (9999, 0, 0))


def intersects(r1, r2):
    b1, b2 = _bounds(r1), _bounds(r2)
    if b1 is None or b2 is None:
        return True
    (lo1, hi1), (lo2, hi2) = b1, b2
    lo, hi = max(lo1, lo2), min(hi1, hi2)
    return bool(lo < hi or lo == hi)
