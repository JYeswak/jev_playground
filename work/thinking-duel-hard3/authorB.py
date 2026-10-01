#!/usr/bin/env python3
"""Round-3 tasks h09-h16."""

import os

ROOT = "work/thinking-duel-hard3"
T = os.path.join(ROOT, "tasks")
G = os.path.join(ROOT, "grading")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


# h09: CSV with delimiter + NULLs
w(
    f"{T}/h09/prompt.md",
    """# Task h09: delimited export with NULLs

Work in $PWD. `delim.py` has `write_delim(path, rows, delim='|', none_as='')`
(rows = list of lists of str|None). It must round-trip through a reader
splitting on delim with quoting: fields containing delim, quotes, newlines,
or equal to none_as must be quoted with `"` and inner quotes doubled; None
writes as none_as UNLESS none_as is empty, in which case None writes as the
quoted empty field `\"\"` distinct from empty string... precisely: None ->
none_as if none_as else '""'; empty string -> '' unquoted unless it equals
none_as (then quoted). `read_delim` inverts it. shipped code is wrong. Fix
both directions, stdlib only. Verify round-trips yourself.
""",
)
w(
    f"{T}/h09/delim.py",
    """def write_delim(path, rows, delim='|', none_as=''):
    with open(path, 'w') as fh:
        for row in rows:
            fh.write(delim.join('' if v is None else v for v in row) + '\\n')

def read_delim(path, delim='|', none_as=''):
    rows = []
    for line in open(path):
        rows.append(line.rstrip('\\n').split(delim))
    return rows
""",
)
w(
    f"{G}/h09.py",
    """import sys, tempfile, os
sys.path.insert(0, SYS_PATH)
from delim import write_delim, read_delim
rows = [['a', 'b|c', 'd"e', 'f\\ng', None, ''], ['x|y', 'NULL', None]]
for delim, none_as in [('|', ''), (';', 'NULL'), ('\\t', 'NA')]:
    fd, p = tempfile.mkstemp(suffix='.txt')
    os.close(fd)
    write_delim(p, rows, delim, none_as)
    back = read_delim(p, delim, none_as)
    assert back == [['a', 'b|c', 'd"e', 'f\\ng', None, ''], ['x|y', 'NULL', None]], (delim, none_as, back)
    os.unlink(p)
print('h09 PASS')
""",
)

# h10: TTL + LFU
w(
    f"{T}/h10/prompt.md",
    """# Task h10: TTL LFU cache

Work in $PWD. `c.py` has `Cache(capacity, ttl, now=time.monotonic)` with
`get(k)`/`put(k, v)`. Eviction beyond capacity removes the
least-frequently-used entry (ties -> least recently used); entries older
than ttl (by `now()`) are expired on access and never returned; get and put
both count as a use and refresh recency; put on an existing key updates the
value and counts as a use. shipped code is plain TTL LRU and wrong. Fix it,
stdlib only. Verify with a fake clock.
""",
)
w(
    f"{T}/h10/c.py",
    """import time
from collections import OrderedDict
class Cache:
    def __init__(self, capacity, ttl, now=None):
        self.cap = capacity
        self.ttl = ttl
        self.now = now or time.monotonic
        self.d = OrderedDict()
    def get(self, k):
        if k not in self.d:
            return None
        v, _ = self.d[k]
        self.d.move_to_end(k)
        return v
    def put(self, k, v):
        self.d[k] = (v, self.now())
        self.d.move_to_end(k)
        while len(self.d) > self.cap:
            self.d.popitem(last=False)
""",
)
w(
    f"{G}/h10.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from c import Cache
t = [0.0]
c = Cache(2, 100.0, now=lambda: t[0])
c.put('a', 1)
c.put('b', 2)
c.get('a'); c.get('a')
c.get('b')
c.put('c', 3)
assert c.get('a') == 1 and c.get('c') == 3 and c.get('b') is None
c.put('d', 4)
assert c.get('c') is None and c.get('d') == 4 and c.get('a') == 1
t[0] = 200.0
assert c.get('a') is None and c.get('d') is None
print('h10 PASS')
""",
)

# h11: lexicographically smallest topo order (Kahn + heap)
w(
    f"{T}/h11/prompt.md",
    """# Task h11: smallest topological order

Work in $PWD. `topo.py` has `order(deps)` (node -> deps list) returning
`(ok, result)`: ok True with the LEXICOGRAPHICALLY SMALLEST valid
topological order (dependencies before dependents), or ok False with a
cycle list (first node repeated at end). Nodes not keys but listed as deps
count as dependency-free nodes. shipped code is wrong. Fix it, stdlib only.
Verify yourself.
""",
)
w(
    f"{T}/h11/topo.py",
    """def order(deps):
    visited = {}
    out = []
    def visit(n, stack):
        if visited.get(n):
            return None
        visited[n] = True
        if n in stack:
            return stack[stack.index(n):]
        stack.append(n)
        for d in deps.get(n, []):
            c = visit(d, stack)
            if c:
                return c
        stack.pop()
        out.append(n)
        return None
    for n in deps:
        c = visit(n, [])
        if c:
            return (False, c + [c[0]])
    return (True, out)
""",
)
w(
    f"{G}/h11.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from topo import order
ok, res = order({'b': [], 'a': []})
assert ok and res == ['a', 'b'], res
ok, res = order({'c': ['a'], 'b': ['a'], 'a': []})
assert ok and res == ['a', 'b', 'c'], res
ok, res = order({'z': ['a'], 'a': []})
assert ok and res == ['a', 'z'], res
ok, res = order({'m': ['n']})
assert ok and res == ['n', 'm'], res
ok, res = order({'a': ['b'], 'b': ['a']})
assert not ok and res[0] == res[-1] and set(res[:-1]) == {'a', 'b'}, res
ok, res = order({'x': ['y', 'z'], 'y': ['w'], 'z': ['w'], 'w': []})
assert ok and res == ['w', 'y', 'z', 'x'], res
print('h11 PASS')
""",
)

# h12: bead parser with word statuses
w(
    f"{T}/h12/prompt.md",
    """# Task h12: bead parser with word statuses

Work in $PWD. `beads.py` has `parse_rows(text)` for lines shaped like
`- [x] jev-1234 | Title` OR `- closed jev-1234: Title` (status word then id
then `:`). Marks: `[x]` closed, `[ ]` open, `[~]` in_progress, `[-]`
deferred; words: closed/open/in_progress/deferred (also `in-progress`).
Titles may contain `|`, `:`, brackets. Malformed lines skipped. shipped code
handles only the first shape and two marks. Fix it, stdlib only. Verify.
""",
)
w(
    f"{T}/h12/beads.py",
    """import re
def parse_rows(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r'- \\[(.)\\] (\\S+) \\| (.*)', line)
        if not m:
            continue
        mark, bid, title = m.groups()
        status = {'x': 'closed', ' ': 'open'}.get(mark, 'open')
        rows.append({'id': bid, 'title': title, 'status': status})
    return rows
""",
)
w(
    f"{G}/h12.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from beads import parse_rows
text = ('- [x] jev-1 | A\\n'
        '- closed jev-2: B: with colon\\n'
        '- [~] jev-3 | C | pipe\\n'
        '- in-progress jev-4: D\\n'
        '- [-] jev-5 | E\\n'
        '- open jev-6: F\\n'
        '- bogus jev-7: G\\n'
        '- [x] noid\\n')
rows = parse_rows(text)
assert rows == [
 {'id': 'jev-1', 'title': 'A', 'status': 'closed'},
 {'id': 'jev-2', 'title': 'B: with colon', 'status': 'closed'},
 {'id': 'jev-3', 'title': 'C | pipe', 'status': 'in_progress'},
 {'id': 'jev-4', 'title': 'D', 'status': 'in_progress'},
 {'id': 'jev-5', 'title': 'E', 'status': 'deferred'},
 {'id': 'jev-6', 'title': 'F', 'status': 'open'},
], rows
print('h12 PASS')
""",
)

# h13: JSON merge-patch RFC 7396
w(
    f"{T}/h13/prompt.md",
    """# Task h13: JSON merge patch

Work in $PWD. `mpatch.py` has `merge_patch(target, patch)` implementing RFC
7396: non-dict patch replaces target; dict patch merges per key with null
values REMOVING the key; arrays replace wholesale (no merge); neither input
is mutated. shipped code is wrong (mutates, mishandles null/arrays).
Fix it, stdlib only (copy inputs first). Verify yourself.
""",
)
w(
    f"{T}/h13/mpatch.py",
    """def merge_patch(target, patch):
    if not isinstance(patch, dict):
        return patch
    for k, v in patch.items():
        if v is None:
            target.pop(k, None)
        elif isinstance(v, dict) and isinstance(target.get(k), dict):
            target[k] = merge_patch(target[k], v)
        else:
            target[k] = v
    return target
""",
)
w(
    f"{G}/h13.py",
    """import sys, copy
sys.path.insert(0, SYS_PATH)
from mpatch import merge_patch
assert merge_patch({'a': 1}, {'a': 2}) == {'a': 2}
assert merge_patch({'a': 1, 'b': 2}, {'a': None}) == {'b': 2}
assert merge_patch({'a': [1]}, {'a': [2, 3]}) == {'a': [2, 3]}
assert merge_patch({'a': {'x': 1, 'y': 2}}, {'a': {'y': None, 'z': 3}}) == {'a': {'x': 1, 'z': 3}}
assert merge_patch([1], {'a': 1}) == {'a': 1}
assert merge_patch({'a': 1}, 5) == 5
t = {'a': {'x': 1}}
p = {'a': {'y': 2}}
t0, p0 = copy.deepcopy(t), copy.deepcopy(p)
merge_patch(t, p)
assert (t, p) == (t0, p0), 'inputs mutated'
assert merge_patch({}, {'a': None}) == {}
print('h13 PASS')
""",
)

# h14: exponential histogram buckets
w(
    f"{T}/h14/prompt.md",
    """# Task h14: exponential histogram buckets

Work in $PWD. `hist.py` has `bucket_bounds(base, n)` returning n+1
boundaries `[base**0, base**1, ..., base**n]` (base > 1) and `assign(v,
bounds)` returning the bucket index i with bounds[i] <= v < bounds[i+1],
or -1 if v is below bounds[0] or at/above bounds[-1]... precisely: values
equal to the LAST boundary belong to the last bucket (index n-1); values
below bounds[0] or above bounds[-1] return -1. shipped code has an edge
error. Fix it, stdlib only. Verify yourself.
""",
)
w(
    f"{T}/h14/hist.py",
    """def bucket_bounds(base, n):
    return [base ** i for i in range(n + 1)]

def assign(v, bounds):
    for i in range(len(bounds) - 1):
        if bounds[i] <= v < bounds[i + 1]:
            return i
    return -1
""",
)
w(
    f"{G}/h14.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from hist import bucket_bounds, assign
b = bucket_bounds(2, 4)
assert b == [1, 2, 4, 8, 16], b
assert assign(1, b) == 0
assert assign(3, b) == 1
assert assign(16, b) == 3
assert assign(0, b) == -1
assert assign(17, b) == -1
assert assign(8, b) == 3
assert assign(15.999, b) == 3
print('h14 PASS')
""",
)

# h15: bounded parallel pool, first-error cancel
w(
    f"{T}/h15/prompt.md",
    """# Task h15: bounded parallel map

Work in $PWD. `pmap.py` has `pmap(fn, items, limit)` returning results in
input order, running at most `limit` workers at once. On the FIRST exception
it must cancel pending work, wait for in-flight tasks to observe
cancellation (best effort), and re-raise that exception. shipped code runs
unbounded and never cancels. Fix it with stdlib threads
(concurrent.futures), no busy-wait. Verify with slow fns, a raiser, and a
parallelism counter asserting max active <= limit.
""",
)
w(
    f"{T}/h15/pmap.py",
    """def pmap(fn, items, limit):
    return [fn(x) for x in items]
""",
)
w(
    f"{G}/h15.py",
    """import sys, time, threading
sys.path.insert(0, SYS_PATH)
from pmap import pmap
assert pmap(lambda x: x * 2, [1, 2, 3], 2) == [2, 4, 6]
active = 0
peak = [0]
lock = threading.Lock()
def work(x):
    global active
    with lock:
        active += 1
        peak[0] = max(peak[0], active)
    try:
        time.sleep(0.05)
        return x
    finally:
        with lock:
            active -= 1
assert pmap(work, list(range(10)), 3) == list(range(10))
assert peak[0] <= 3, peak
assert peak[0] >= 2, peak
def boom(x):
    if x == 2:
        raise ValueError('bad 2')
    time.sleep(0.3)
    return x
t = time.time()
try:
    pmap(boom, range(6), 3)
    raise SystemExit('h15 FAIL: no raise')
except ValueError:
    pass
assert time.time() - t < 3.0, 'no prompt cancellation'
print('h15 PASS')
""",
)

# h16: cron next fire (minute/hour)
w(
    f"{T}/h16/prompt.md",
    """# Task h16: next cron fire time

Work in $PWD. `cronx.py` has `next_fire(expr, after)` where expr is
`MIN HOUR` with fields `*`, `*/k`, `a-b`, `a,b` (minute 0-59, hour 0-23)
and `after` is a naive datetime; return the next datetime strictly after
`after` matching both fields (same-day, next-day, etc.). shipped code is
wrong on wraps and steps. Fix it, stdlib datetime only. Verify yourself.
""",
)
w(
    f"{T}/h16/cronx.py",
    """from datetime import datetime, timedelta
def _match(field, lo, hi):
    if field == '*':
        return set(range(lo, hi + 1))
    vals = set()
    for part in field.split(','):
        if '/' in part:
            base, step = part.split('/')
            step = int(step)
            r = range(lo, hi + 1) if base == '*' else [int(base)]
            vals.update(r[::step])
        elif '-' in part:
            a, b = part.split('-')
            vals.update(range(int(a), int(b) + 1))
        else:
            vals.add(int(part))
    return vals
def next_fire(expr, after):
    mins = _match(expr.split()[0], 0, 59)
    hours = _match(expr.split()[1], 0, 23)
    t = after + timedelta(minutes=1)
    while True:
        if t.minute in mins and t.hour in hours:
            return t
        t += timedelta(minutes=1)
""",
)
w(
    f"{G}/h16.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from cronx import next_fire
from datetime import datetime as dt
assert next_fire('0 9', dt(2026, 1, 1, 8, 0)) == dt(2026, 1, 1, 9, 0)
assert next_fire('0 9', dt(2026, 1, 1, 9, 0)) == dt(2026, 1, 2, 9, 0)
assert next_fire('*/15 *', dt(2026, 1, 1, 10, 7)) == dt(2026, 1, 1, 10, 15)
assert next_fire('30 23', dt(2026, 1, 1, 23, 45)) == dt(2026, 1, 2, 23, 30)
assert next_fire('0 0', dt(2026, 1, 1, 0, 0)) == dt(2026, 1, 2, 0, 0)
assert next_fire('5 4', dt(2026, 1, 1, 4, 5)) == dt(2026, 1, 2, 4, 5)
assert next_fire('0,30 12', dt(2026, 1, 1, 12, 30)) == dt(2026, 1, 2, 12, 0)
print('h16 PASS')
""",
)

print("authored r3b")
