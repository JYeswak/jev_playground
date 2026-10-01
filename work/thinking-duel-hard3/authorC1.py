#!/usr/bin/env python3
"""Round-3 v2 tasks k01-k04."""

import os

ROOT = "work/thinking-duel-hard3"
T = os.path.join(ROOT, "v2")
G = os.path.join(ROOT, "grading2")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


w(
    f"{T}/k01/prompt.md",
    """# Task k01: stable k-way merge

Work in $PWD. `kmerge.py` has `merge(streams, key=None)` merging sorted
input iterables (each already sorted by key) into one sorted list, STABLE:
equal keys keep stream order (lower stream index first). Must not assume
list inputs (any iterable, including generators) and must handle empty
streams. shipped code breaks stability and chokes on generators. Fix it,
stdlib only. Verify yourself.
""",
)
w(
    f"{T}/k01/kmerge.py",
    """def merge(streams, key=None):
    key = key or (lambda x: x)
    out = []
    for s in streams:
        out.extend(s)
    out.sort(key=lambda x: key(x))
    return out
""",
)
w(
    f"{G}/k01.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from kmerge import merge
assert merge([[], [], []]) == []
r = merge([[(1, 'a'), (2, 'b')], [(1, 'c'), (3, 'd')]], key=lambda t: t[0])
assert r == [(1, 'a'), (1, 'c'), (2, 'b'), (3, 'd')], r
def gen(xs):
    yield from xs
r = merge([gen([1, 3]), gen([]), gen([2])])
assert r == [1, 2, 3], r
r = merge([[('x', 2), ('y', 1)]], key=lambda t: t[1])
assert r == [('y', 1), ('x', 2)], r
print('k01 PASS')
""",
)

w(
    f"{T}/k02/prompt.md",
    """# Task k02: query string parser

Work in $PWD. `qs.py` has `parse(qs)` returning a list of (name, value)
pairs IN ORDER, keeping repeats and blank values: `a=&b=1&a=2` ->
`[('a',''),('b','1'),('a','2')]`; `+` decodes to space; `%2B` decodes to a
literal `+`; `%XX` percent-decoding incl UTF-8; a segment without `=` gets
value None; leading `?` stripped. shipped code drops blanks and mangles
`+`. Fix it, stdlib only (no urllib.parse). Verify yourself.
""",
)
w(
    f"{T}/k02/qs.py",
    """def parse(qs):
    out = []
    for seg in qs.split('&'):
        if '=' in seg:
            k, v = seg.split('=', 1)
            out.append((k.replace('+', ' '), v.replace('+', ' ')))
        elif seg:
            out.append((seg, None))
    return out
""",
)
w(
    f"{G}/k02.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from qs import parse
assert parse('a=&b=1&a=2') == [('a', ''), ('b', '1'), ('a', '2')]
assert parse('q=a+b') == [('q', 'a b')]
assert parse('q=a%2Bb') == [('q', 'a+b')]
assert parse('?x=%41%5a') == [('x', 'AZ')]
assert parse('flag') == [('flag', None)]
assert parse('') == []
assert parse('a=%E2%82%AC') == [('a', '\\u20ac')]
assert parse('k=a=b') == [('k', 'a=b')]
print('k02 PASS')
""",
)

w(
    f"{T}/k03/prompt.md",
    """# Task k03: safe path join

Work in $PWD. `sjoin.py` has `safe_join(base, *parts)` returning the joined
absolute path, or raising `ValueError` on traversal outside base. Must
normalize (`.`, `..`, duplicate separators) BEFORE the prefix check, and the
prefix check must be directory-aware (`/tmp/x-evil` is NOT inside `/tmp/x`).
Absolute `parts` elements are treated as relative (strip leading `/`).
Symlinks out of scope. shipped code is bypassable twice over. Fix it,
stdlib only. Verify with traversal and prefix-confusion cases.
""",
)
w(
    f"{T}/k03/sjoin.py",
    """import os
def safe_join(base, *parts):
    p = os.path.join(base, *parts)
    if not p.startswith(base):
        raise ValueError('traversal')
    return p
""",
)
w(
    f"{G}/k03.py",
    """import sys, os
sys.path.insert(0, SYS_PATH)
from sjoin import safe_join
assert safe_join('/tmp/x', 'a', 'b') == '/tmp/x/a/b'
assert safe_join('/tmp/x', '/a') == '/tmp/x/a'
assert safe_join('/tmp/x', 'a/./b//c') == '/tmp/x/a/b/c'
for bad in ['..', '../e', 'a/../../e', '/tmp/x-evil/f']:
    try:
        safe_join('/tmp/x', bad)
    except ValueError:
        continue
    raise SystemExit('k03 FAIL accepted')
try:
    safe_join('/tmp/x', '..')
    raise SystemExit('k03 FAIL dotdot')
except ValueError:
    pass
print('k03 PASS')
""",
)

w(
    f"{T}/k04/prompt.md",
    """# Task k04: exact money split

Work in $PWD. `money.py` has `split(cents, weights)` splitting integer
`cents` across integer `weights` proportionally, returning integer shares
summing EXACTLY to cents (largest-remainder on exact fractional parts, ties
to lower index). Exact integer arithmetic only (no floats). Zero/negative
weights and empty weights raise ValueError. shipped code uses floats and
drifts. Fix it. Verify yourself.
""",
)
w(
    f"{T}/k04/money.py",
    """def split(cents, weights):
    if not weights:
        raise ValueError('empty')
    total = sum(weights)
    out = [int(cents * w / total) for w in weights]
    return out
""",
)
w(
    f"{G}/k04.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from money import split
s = split(100, [1, 1, 1])
assert sum(s) == 100 and s == [34, 33, 33], s
assert split(1, [1, 1]) == [1, 0]
assert split(1000001, [3, 1]) == [750001, 250000]
assert split(10, [7, 2, 1]) == [7, 2, 1]
s = split(10**12 + 7, [1] * 7)
assert sum(s) == 10**12 + 7 and max(s) - min(s) <= 1, s
for bad in ([], [0, 0], [1, -1]):
    try:
        split(10, bad)
        raise SystemExit('k04 FAIL accepted')
    except ValueError:
        pass
print('k04 PASS')
""",
)

print("authored r3c1")
