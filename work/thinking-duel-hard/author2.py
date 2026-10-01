#!/usr/bin/env python3
"""Tasks t07-t12."""

import os

ROOT = "work/thinking-duel-hard"
T = os.path.join(ROOT, "tasks")
G = os.path.join(ROOT, "grading")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


# t07: deterministic seeded shuffle reproducing a fixed sequence (bug: wrong LCG)
w(
    f"{T}/t07/prompt.md",
    """# Task t07: deterministic shuffle

Work in $PWD. `shuffle.py` has `order(n, seed)` returning a permutation of
`range(n)` that must be DETERMINISTIC across runs and Python versions for
the same seed, and a uniform shuffle (Fisher-Yates). It currently uses
`random.Random(seed).shuffle`, whose output is version-dependent. Reimplement
with an inline integer LCG (no `random` module): state = (1103515245 * state
+ 12345) % 2**31, j = state % (i + 1), iterating i from n-1 down to 1.
Verify determinism yourself.
""",
)
w(
    f"{T}/t07/shuffle.py",
    """import random
def order(n, seed):
    xs = list(range(n))
    random.Random(seed).shuffle(xs)
    return xs
""",
)
w(
    f"{G}/t07.py",
    """import sys
assert sorted(order(n, s)) == list(range(n)) if False else True
from shuffle import order
def ref(n, seed):
    xs = list(range(n))
    s = seed % 2**31
    for i in range(n - 1, 0, -1):
        s = (1103515245 * s + 12345) % 2**31
        j = s % (i + 1)
        xs[i], xs[j] = xs[j], xs[i]
    return xs
import shuffle as shmod
import inspect
assert 'random' not in inspect.getsource(shmod), 'must not use random module'
for n, s in [(0, 1), (1, 1), (5, 42), (12, 42), (52, 7), (100, 12345)]:
    assert order(n, s) == ref(n, s), (n, s)
    assert sorted(order(n, s)) == list(range(n))
print('t07 PASS')
""",
)

# t08: redacted prefix logger (bug: cut before scrub)
w(
    f"{T}/t08/prompt.md",
    """# Task t08: redacted command prefix

Work in $PWD. `prefix.py` has `redact(cmd, home, secret_re)` returning at
most the first 200 chars of the command with `home` replaced by `~` and
every `secret_re` match replaced by `[REDACTED]`. Critical: scrub BEFORE
cutting, so a secret straddling char 200 is still fully removed. It is
wrong. Fix it, standard library only (`secret_re` is a compiled pattern).
Verify yourself, including a straddling secret.
""",
)
w(
    f"{T}/t08/prefix.py",
    """def redact(cmd, home, secret_re):
    short = cmd.replace(home, '~').strip()[:200]
    return secret_re.sub('[REDACTED]', short)
""",
)
w(
    f"{G}/t08.py",
    """import sys, re
sys.path.insert(0, SYS_PATH)
from prefix import redact
sec = re.compile(r'sk-[a-z]{20,}')
assert redact('ls /tmp', '/home/u', sec) == 'ls /tmp'
assert redact('export K=sk-abcdefghijklmnopqrst dir', '/home/u', sec) == 'export K=[REDACTED] dir'
home = '/Users/josh'
cmd = 'x' * 190 + ' sk-abcdefghijklmnopqrstuvwxyz tail'
got = redact(cmd, home, sec)
assert len(got) <= 200, len(got)
assert 'sk-' not in got, got
assert got.endswith('[REDACTED]') or '[REDACTED]' in got, got
cmd2 = 'cd ' + home + '/proj && echo hi'
assert redact(cmd2, home, sec) == 'cd ~/proj && echo hi', redact(cmd2, home, sec)
print('t08 PASS')
""",
)

# t09: CSV exporter quoting (multi-file: exporter + cli)
w(
    f"{T}/t09/prompt.md",
    """# Task t09: CSV export quoting

Work in $PWD. `csvexp.py` has `write_csv(path, rows)` (rows = list of lists
of str) and `cli.py` reads a JSON array-of-arrays from stdin and writes CSV
to stdout. Fields containing commas, quotes, or newlines must round-trip
through any RFC-4180 reader. Quoting is currently broken. Fix the exporter
(standard library only), keep the `cli.py` interface. Verify with a
round-trip yourself.
""",
)
w(
    f"{T}/t09/csvexp.py",
    """def write_csv(path, rows):
    with open(path, 'w') as fh:
        for row in rows:
            fh.write(','.join(row) + '\n')
""",
)
w(
    f"{T}/t09/cli.py",
    """import json, sys
from csvexp import write_csv
rows = json.load(sys.stdin)
write_csv('/tmp/t09-out.csv', rows)
print(open('/tmp/t09-out.csv').read(), end='')
""",
)
w(
    f"{G}/t09.py",
    """import sys, csv, io, json, subprocess
sys.path.insert(0, SYS_PATH)
from csvexp import write_csv
import tempfile, os
rows = [['a', 'b,c', 'd"e', 'f\ng'], ['plain', '', 'x']]
fd, p = tempfile.mkstemp(suffix='.csv')
os.close(fd)
write_csv(p, rows)
back = list(csv.reader(open(p)))
assert back == rows, back
os.unlink(p)
proc = subprocess.run([sys.executable, 'cli.py'], input=json.dumps(rows), capture_output=True, text=True, cwd=SYSCWD)
assert proc.returncode == 0, proc.stderr
assert list(csv.reader(io.StringIO(proc.stdout))) == rows
print('t09 PASS')
""",
)

# t10: TTL LRU cache (bug: expiry not checked on get; no size bound)
w(
    f"{T}/t10/prompt.md",
    """# Task t10: TTL LRU cache

Work in $PWD. `ttlcache.py` has `TTLCache(capacity, ttl, now=time.monotonic)`
with `get(k)`/`put(k, v)`. It must: evict least-recently-used beyond
capacity; expire entries older than ttl seconds (using `now()`); return None
for missing/expired keys; refresh recency on get and put. It is wrong. Fix
it, standard library only. Verify yourself with a fake clock.
""",
)
w(
    f"{T}/t10/ttlcache.py",
    """import time
from collections import OrderedDict
class TTLCache:
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
    f"{G}/t10.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from ttlcache import TTLCache
t = [100.0]
c = TTLCache(2, 10.0, now=lambda: t[0])
c.put('a', 1)
c.put('b', 2)
assert c.get('a') == 1
c.put('c', 3)
assert c.get('b') is None and c.get('a') == 1 and c.get('c') == 3
t[0] = 111.0
assert c.get('a') is None and c.get('c') is None
c.put('d', 4)
t[0] = 115.0
assert c.get('d') == 4
t[0] = 130.0
assert c.get('d') is None
print('t10 PASS')
""",
)

# t11: topo sort with cycle path (bug: wrong cycle report / misses order)
w(
    f"{T}/t11/prompt.md",
    """# Task t11: dependency order with cycle report

Work in $PWD. `topo.py` has `order(deps)` where deps maps node -> list of
nodes it depends on. Return `(ok, result)`: ok True with a valid topological
list (dependencies before dependents), or ok False with the list of nodes
forming a cycle (in dependency order, first node repeated at the end).
Deterministic: iterate nodes and deps in sorted order. It is wrong. Fix it,
standard library only. Verify yourself.
""",
)
w(
    f"{T}/t11/topo.py",
    """def order(deps):
    visited = {}
    out = []
    def visit(n, stack):
        if visited.get(n):
            return None
        if n in stack:
            return stack[stack.index(n):]
        stack.append(n)
        for d in deps.get(n, []):
            c = visit(d, stack)
            if c:
                return c
        stack.pop()
        visited[n] = True
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
    f"{G}/t11.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from topo import order
ok, res = order({'a': ['b'], 'b': ['c'], 'c': []})
assert ok and res == ['c', 'b', 'a'], res
ok, res = order({'a': ['b'], 'b': ['a']})
assert not ok and res[0] == res[-1] and set(res[:-1]) == {'a', 'b'}, res
ok, res = order({'m': ['n', 'o'], 'n': ['o'], 'o': []})
assert ok and res.index('o') < res.index('n') < res.index('m'), res
ok, res = order({'x': ['y'], 'y': ['z'], 'z': ['y']})
assert not ok and res[0] == res[-1] and set(res[:-1]) == {'y', 'z'}, res
ok, res = order({})
assert ok and res == []
ok, res = order({'s': ['s']})
assert not ok and res == ['s', 's'], res
print('t11 PASS')
""",
)

# t12: bead-row markdown parser (bug: misses statuses, greedy titles)
w(
    f"{T}/t12/prompt.md",
    """# Task t12: bead row parser

Work in $PWD. `beads.py` has `parse_rows(text)` returning a list of
`{'id':..., 'title':..., 'status':...}` for lines shaped like
`- [x] jev-1234 | Some title here`. Status maps: `[x]` closed, `[ ]` open,
`[~]` in_progress, `[-]` deferred. Titles may contain `|` and brackets.
Malformed lines are skipped. It is wrong. Fix it, standard library only.
Verify yourself.
""",
)
w(
    f"{T}/t12/beads.py",
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
    f"{G}/t12.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from beads import parse_rows
text = ('- [x] jev-1234 | Fix the thing\\n'
        '- [ ] jev-99 | Title with | pipe and [brackets]\\n'
        '- [~] jev-100 | In flight\\n'
        '- [-] jev-101 | Parked\\n'
        'not a row\\n'
        '- [x] broken-noid\\n')
rows = parse_rows(text)
assert rows == [
 {'id': 'jev-1234', 'title': 'Fix the thing', 'status': 'closed'},
 {'id': 'jev-99', 'title': 'Title with | pipe and [brackets]', 'status': 'open'},
 {'id': 'jev-100', 'title': 'In flight', 'status': 'in_progress'},
 {'id': 'jev-101', 'title': 'Parked', 'status': 'deferred'},
], rows
print('t12 PASS')
""",
)

print("authored2")
