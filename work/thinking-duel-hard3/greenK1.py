#!/usr/bin/env python3
"""GREEN references k01-k08 -> /tmp/g3k/."""

import os


def put(tid, fname, text):
    d = f"/tmp/g3k/{tid}"
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, fname), "w").write(text)


put(
    "k01",
    "kmerge.py",
    """import heapq
def merge(streams, key=None):
    key = key or (lambda x: x)
    heap = []
    iters = [iter(s) for s in streams]
    for i, it in enumerate(iters):
        try:
            v = next(it)
            heapq.heappush(heap, (key(v), i, v, it))
        except StopIteration:
            pass
    out = []
    while heap:
        _, i, v, it = heapq.heappop(heap)
        out.append(v)
        try:
            nv = next(it)
            heapq.heappush(heap, (key(nv), i, nv, it))
        except StopIteration:
            pass
    return out
""",
)

put(
    "k02",
    "qs.py",
    """def _pct(s):
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == '%' and i + 2 < len(s) + 1:
            hx = s[i+1:i+3]
            try:
                out.append(int(hx, 16))
                i += 3
                continue
            except ValueError:
                pass
        out.extend(c.encode('latin-1'))
        i += 1
    return bytes(out).decode('utf-8')
def parse(qs):
    if qs.startswith('?'):
        qs = qs[1:]
    if qs == '':
        return []
    out = []
    for seg in qs.split('&'):
        if '=' in seg:
            k, v = seg.split('=', 1)
            out.append((_pct(k.replace('+', ' ')), _pct(v.replace('+', ' '))))
        else:
            out.append((_pct(seg.replace('+', ' ')), None))
    return out
""",
)

put(
    "k03",
    "sjoin.py",
    """import os
def safe_join(base, *parts):
    rel = [p.lstrip('/') for p in parts]
    p = os.path.normpath(os.path.join(base, *rel))
    if p != base and not p.startswith(base.rstrip('/') + '/'):
        raise ValueError('traversal')
    return p
""",
)

put(
    "k04",
    "money.py",
    """def split(cents, weights):
    if not weights:
        raise ValueError('empty')
    if any(not isinstance(w, int) or w <= 0 for w in weights):
        raise ValueError('weights')
    total = sum(weights)
    base = [(cents * w) // total for w in weights]
    rem = [(cents * w) % total for w in weights]
    short = cents - sum(base)
    idx = sorted(range(len(weights)), key=lambda i: (-rem[i], i))
    for i in idx[:short]:
        base[i] += 1
    return base
""",
)

put(
    "k05",
    "flaky.py",
    """def find_flaky(results, lo=0.05, hi=0.95, min_runs=10):
    out = []
    for name, runs in results.items():
        if len(runs) < min_runs or not runs:
            continue
        fails = sum(1 for r in runs if not r)
        rate = fails / len(runs)
        if lo <= rate <= hi:
            out.append(name)
    return sorted(out)
""",
)

put(
    "k06",
    "wrap.py",
    """import unicodedata
def _w(ch):
    if unicodedata.combining(ch):
        return 0
    if unicodedata.east_asian_width(ch) in ('W', 'F'):
        return 2
    return 1
def _dw(s):
    return sum(_w(c) for c in s)
def wrap(text, width):
    if not text:
        return []
    lines, cur, curw = [], '', 0
    for word in text.split(' '):
        ww = _dw(word)
        if ww > width:
            if cur:
                lines.append(cur)
                cur, curw = '', 0
            if all(unicodedata.east_asian_width(c) in ('W', 'F') for c in word):
                chunk, chunkw = '', 0
                for c in word:
                    if chunkw + 2 > width:
                        lines.append(chunk)
                        chunk, chunkw = '', 0
                    chunk += c
                    chunkw += 2
                if chunk:
                    cur, curw = chunk, chunkw
            else:
                lines.append(word)
            continue
        add = (1 if cur else 0) + ww
        if curw + add > width:
            lines.append(cur)
            cur, curw = word, ww
        else:
            cur = (cur + ' ' + word) if cur else word
            curw += add
    if cur:
        lines.append(cur)
    return lines
""",
)

put(
    "k07",
    "semver.py",
    """def _t(v):
    return tuple(int(x) for x in v.split('.'))
def _caret(v):
    M, m, p = _t(v)
    if M > 0:
        return ((M, m, p), (M + 1, 0, 0))
    if m > 0:
        return ((0, m, p), (0, m + 1, 0))
    return ((0, 0, p), (0, 0, p + 1))
def _range(r):
    # Returns (lo, hi, hi_inclusive). Exact pins include their point.
    if r == '*':
        return ((0, 0, 0), None, False)
    if r[0] == '^':
        return _caret(r[1:]) + (False,)
    if r[0] == '~':
        M, m, p = _t(r[1:])
        return ((M, m, p), (M, m + 1, 0), False)
    if r[:2] == '>=':
        return (_t(r[2:]), None, False)
    if r[0] == '<':
        return ((0, 0, 0), _t(r[1:]), False)
    t = _t(r)
    return (t, t, True)
def intersect(a, b):
    (l1, h1, i1), (l2, h2, i2) = _range(a), _range(b)
    lo = max(l1, l2)
    if h1 is None:
        hi, incl = h2, i2
    elif h2 is None:
        hi, incl = h1, i1
    elif h1 < h2:
        hi, incl = h1, i1
    elif h2 < h1:
        hi, incl = h2, i2
    else:
        hi, incl = h1, i1 and i2
    if hi is not None and (lo > hi or (lo == hi and not incl)):
        return None
    return (lo, hi)
""",
)

put(
    "k08",
    "where.py",
    """def build(node, _counter=None):
    if _counter is None:
        _counter = [0]
    kind = node[0]
    if kind in ('and', 'or'):
        parts, params = [], []
        for c in node[1]:
            s, p = build(c, _counter)
            parts.append(s)
            params.extend(p)
        return ('(' + (' %s ' % kind.upper()).join(parts) + ')', params)
    if kind == 'not':
        s, p = build(node[1], _counter)
        return ('(NOT ' + s + ')', p)
    col, op, val = node
    _counter[0] += 1
    return ('%s %s $%d' % (col, op, _counter[0]), [val])
""",
)

print("green k01-k08 written")
