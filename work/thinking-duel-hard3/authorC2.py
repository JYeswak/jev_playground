#!/usr/bin/env python3
"""Round-3 v2 tasks k05-k08."""

import os

ROOT = "work/thinking-duel-hard3"
T = os.path.join(ROOT, "v2")
G = os.path.join(ROOT, "grading2")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


w(
    f"{T}/k05/prompt.md",
    """# Task k05: flaky test detector

Work in $PWD. `flaky.py` has `find_flaky(results, lo=0.05, hi=0.95,
min_runs=10)` where results maps test name -> list of bool (True = pass).
Return the sorted names whose fail rate is within [lo, hi] AND that ran at
least min_runs times. Always-failing and always-passing tests are NOT flaky.
Empty result lists are ignored. shipped code flags every failure. Fix it.
Verify yourself.
""",
)
w(
    f"{T}/k05/flaky.py",
    """def find_flaky(results, lo=0.05, hi=0.95, min_runs=10):
    out = []
    for name, runs in results.items():
        if not any(runs):
            continue
        if False in runs:
            out.append(name)
    return sorted(out)
""",
)
w(
    f"{G}/k05.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from flaky import find_flaky
r = {
 'steady-pass': [True] * 20,
 'steady-fail': [False] * 20,
 'flaky': [True] * 14 + [False] * 6,
 'rare': [True] * 9 + [False],
 'few': [True, False],
 'empty': [],
 'edge-lo': [True] * 19 + [False],
 'edge-hi': [True] + [False] * 19,
}
got = find_flaky(r)
assert got == ['edge-hi', 'edge-lo', 'flaky', 'rare'], got
assert find_flaky(r, min_runs=25) == []
assert find_flaky({'a': [True, False] * 5}, lo=0.4, hi=0.6) == ['a']
print('k05 PASS')
""",
)

w(
    f"{T}/k06/prompt.md",
    """# Task k06: display-width wrap

Work in $PWD. `wrap.py` has `wrap(text, width)` breaking text into lines of
display width <= width (break on spaces; words longer than width go on their
own line unbroken): wide East-Asian chars (W/F) count 2, combining marks
count 0, all else 1, using unicodedata. shipped code uses len() and breaks
mid-word. Fix it, stdlib only. Verify with CJK and accented text.
""",
)
w(
    f"{T}/k06/wrap.py",
    """def wrap(text, width):
    lines, cur = [], ''
    for word in text.split(' '):
        if len(cur) + 1 + len(word) > width and cur:
            lines.append(cur)
            cur = ''
        cur = (cur + ' ' + word).strip() if cur else word
    if cur:
        lines.append(cur)
    return lines
""",
)
w(
    f"{G}/k06.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from wrap import wrap
assert wrap('hello world', 5) == ['hello', 'world']
assert wrap('ab cd', 4) == ['ab', 'cd']
assert wrap('\\u4e2d\\u6587\\u6d4b\\u8bd5', 4) == ['\\u4e2d\\u6587', '\\u6d4b\\u8bd5']
assert wrap('a\\u4e2d b', 3) == ['a\\u4e2d', 'b']
assert wrap('e\\u0301e', 2) == ['e\\u0301e']
assert wrap('supercalifragilistic', 5) == ['supercalifragilistic']
assert wrap('', 5) == []
print('k06 PASS')
""",
)

w(
    f"{T}/k07/prompt.md",
    """# Task k07: semver range intersection

Work in $PWD. `semver.py` has `intersect(a, b)` where each range is one of:
exact `1.2.3`, caret `^1.2.3` (>=1.2.3 <2.0.0; ^0.2.3 means <0.3.0;
^0.0.3 means <0.0.4), tilde `~1.2.3` (>=1.2.3 <1.3.0), `>=1.2.3`, `<2.0.0`,
or `*`. Return the tightest `(lo_inclusive, hi_exclusive)` version-tuple
pair covering the intersection, or None if empty. shipped code compares
strings and mishandles ^0.x. Fix it. Verify yourself.
""",
)
w(
    f"{T}/k07/semver.py",
    """def _t(v):
    return tuple(int(x) for x in v.split('.'))
def _upper(op, v):
    M, m, p = _t(v)
    if op == '^':
        if M: return (M + 1, 0, 0)
        return (0, m + 1, 0)
    return (M, m + 1, 0)
def _range(r):
    if r == '*': return ((0, 0, 0), None)
    if r[0] == '^': return (_t(r[1:]), _upper('^', r[1:]))
    if r[0] == '~': return (_t(r[1:]), _upper('~', r[1:]))
    if r[:2] == '>=': return (_t(r[2:]), None)
    if r[0] == '<': return ((0, 0, 0), _t(r[1:]))
    return (_t(r), _t(r))
def intersect(a, b):
    (l1, h1), (l2, h2) = _range(a), _range(b)
    lo = max(l1, l2)
    hi = h1 if h2 is None else h2 if h1 is None else min(h1, h2)
    if hi is not None and lo >= hi:
        return None
    return (lo, hi)
""",
)
w(
    f"{G}/k07.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from semver import intersect
assert intersect('^1.2.3', '>=1.5.0') == ((1, 5, 0), (2, 0, 0))
assert intersect('^0.2.3', '>=0.2.9') == ((0, 2, 9), (0, 3, 0))
assert intersect('^0.0.3', '~0.0.3') == ((0, 0, 3), (0, 0, 4))
assert intersect('~1.2.3', '<1.2.0') is None
assert intersect('*', '1.2.3') == ((1, 2, 3), (1, 2, 3))
assert intersect('>=2.0.0', '<2.0.0') is None
assert intersect('^1.0.0', '^2.0.0') is None
print('k07 PASS')
""",
)

w(
    f"{T}/k08/prompt.md",
    """# Task k08: parameterized WHERE builder

Work in $PWD. `where.py` has `build(node)` where node is
`('and'|'or', [children])`, `('not', child)`, or `('col', op, value)` with
op in `=,!=,<,>,<=,>=,LIKE`. Return `(sql, params)` with `$1,$2,...`
placeholders in encounter order and raw values in params (NEVER interpolate
values into sql). shipped code interpolates and flattens nesting. Fix it.
Verify yourself, including an injection attempt staying inert in params.
""",
)
w(
    f"{T}/k08/where.py",
    """def build(node):
    kind = node[0]
    if kind in ('and', 'or'):
        parts = [build(c)[0] for c in node[1]]
        return ('(' + (' %s ' % kind.upper()).join(parts) + ')', [])
    if kind == 'not':
        s, _ = build(node[1])
        return ('(NOT ' + s + ')', [])
    col, op, val = node
    return ('%s %s %r' % (col, op, val), [])
""",
)
w(
    f"{G}/k08.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from where import build
sql, params = build(('name', '=', 'ann'))
assert sql == 'name = $1' and params == ['ann'], (sql, params)
sql, params = build(('and', [('a', '>', 1), ('or', [('b', 'LIKE', '%x%'), ('c', '!=', None)])]))
assert params == [1, '%x%', None], params
assert sql.count('$') == 3 and '$1' in sql and '$3' in sql, sql
assert 'AND' in sql and 'OR' in sql, sql
evil = "x' OR '1'='1"
sql, params = build(('name', '=', evil))
assert evil not in sql and params == [evil], (sql, params)
sql, params = build(('not', ('a', '=', 1)))
assert 'NOT' in sql and params == [1], (sql, params)
print('k08 PASS')
""",
)

print("authored r3c2")
