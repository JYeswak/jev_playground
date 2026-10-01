#!/usr/bin/env python3
"""Round-3 v2 tasks k09-k12."""

import os

ROOT = "work/thinking-duel-hard3"
T = os.path.join(ROOT, "v2")
G = os.path.join(ROOT, "grading2")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


w(
    f"{T}/k09/prompt.md",
    """# Task k09: unified diff applier

Work in $PWD. `patcher.py` has `apply_patch(original, diff)` applying a
subset of unified diff: `---/+++` headers (ignored), `@@ -a,b +c,d @@`
hunks, ` ` context, `-` removals, `+` additions. Hunk positions refer to the
ORIGINAL (not shifted) file; multiple hunks apply top-down with an offset
accumulator. Mismatched context raises ValueError. shipped code ignores
offsets and never validates. Fix it, stdlib only. Verify yourself.
""",
)
w(
    f"{T}/k09/patcher.py",
    """def apply_patch(original, diff):
    lines = original.split('\\n')
    for dl in diff.split('\\n'):
        if dl.startswith('+') and not dl.startswith('+++'):
            lines.append(dl[1:])
    return '\\n'.join(lines)
""",
)
w(
    f"{G}/k09.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from patcher import apply_patch
orig = 'a\\nb\\nc\\nd\\ne\\n'
diff = ('--- f\\n+++ f\\n@@ -2,2 +2,3 @@\\n b\\n-c\\n+C\\n+c2\\n d\\n'
        '@@ -5,1 +6,1 @@\\n-e\\n+E\\n')
got = apply_patch(orig, diff)
assert got == 'a\\nb\\nC\\nc2\\nd\\nE\\n', repr(got)
try:
    apply_patch(orig, '--- f\\n+++ f\\n@@ -2,1 +2,1 @@\\n-X\\n')
    raise SystemExit('k09 FAIL no raise')
except ValueError:
    pass
assert apply_patch('x\\n', '') == 'x\\n'
print('k09 PASS')
""",
)

w(
    f"{T}/k10/prompt.md",
    """# Task k10: thread-safe token bucket

Work in $PWD. `bucket.py` has `Bucket(rate, burst, now=time.monotonic)`
with `take(n=1)` returning True (and deducting) iff at least n tokens are
available, else False without deducting. Tokens refill continuously at
`rate` per second up to `burst`; all methods thread-safe via a lock; time
comes only from `now()`. shipped code races and over-refills. Fix it,
stdlib only. Verify with a fake clock and threads.
""",
)
w(
    f"{T}/k10/bucket.py",
    """import time, threading
class Bucket:
    def __init__(self, rate, burst, now=None):
        self.rate = rate
        self.burst = burst
        self.now = now or time.monotonic
        self.tokens = burst
        self.last = self.now()
        self.lock = threading.Lock()
    def take(self, n=1):
        self.tokens = min(self.burst, self.tokens + (self.now() - self.last) * self.rate)
        self.last = self.now()
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False
""",
)
w(
    f"{G}/k10.py",
    """import sys, threading
sys.path.insert(0, SYS_PATH)
from bucket import Bucket
t = [0.0]
b = Bucket(10.0, 5.0, now=lambda: t[0])
assert b.take(5) is True and b.take(1) is False
t[0] = 0.2
assert b.take(2) is True and b.take(1) is False
t[0] = 100.0
assert b.take(5) is True and b.take(1) is False
t2 = [0.0]
b2 = Bucket(1000.0, 1000.0, now=lambda: t2[0])
wins = [0]
def grab():
    for _ in range(200):
        if b2.take(1):
            wins[0] += 1
ths = [threading.Thread(target=grab) for _ in range(5)]
[x.start() for x in ths]
[x.join() for x in ths]
assert wins[0] == 1000, wins
print('k10 PASS')
""",
)

w(
    f"{T}/k11/prompt.md",
    """# Task k11: markdown table parser

Work in $PWD. `mdtable.py` has `parse(text)` returning a list of dicts from
the FIRST markdown table in text: header row, delimiter row (`---`, `:--`,
`--:`, `:-:`), data rows; cells split on unescaped `|` (escaped `\\|` stays
literal); rows with fewer cells pad with None, extra cells truncate;
leading/trailing pipes tolerated; returns [] if no table. shipped code
splits naively and misaligns. Fix it, stdlib only. Verify yourself.
""",
)
w(
    f"{T}/k11/mdtable.py",
    """def parse(text):
    for i, line in enumerate(text.split('\\n')):
        if '|' in line:
            header = [c.strip() for c in line.strip('|').split('|')]
            rows = []
            for dl in text.split('\\n')[i + 2:]:
                if '|' not in dl:
                    break
                rows.append(dict(zip(header, [c.strip() for c in dl.strip('|').split('|')])))
            return rows
    return []
""",
)
w(
    f"{G}/k11.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from mdtable import parse
doc = 'intro\\n| a | b |\\n|---|---|\\n| 1 | x\\\\|y |\\n| 2 |\\n| 3 | z | w |\\nend\\n'
rows = parse(doc)
assert rows == [{'a': '1', 'b': 'x|y'}, {'a': '2', 'b': None}, {'a': '3', 'b': 'z'}], rows
assert parse('no table here') == []
assert parse('| h |\\n| :- |\\n| v |') == [{'h': 'v'}]
print('k11 PASS')
""",
)

w(
    f"{T}/k12/prompt.md",
    """# Task k12: versioned dependency resolver

Work in $PWD. `resolver.py` has `resolve(index, reqs)` where index maps
package -> sorted ascending version list, and reqs maps package ->
(min_version, max_exclusive_or_None). Return a dict package -> version
picking the MAXIMUM version satisfying all constraints, or None if
unsatisfiable. Single-version packages: only that version qualifies.
shipped code picks minima and ignores unsatisfiability. Fix it, stdlib only
(plain version-string compare by numeric parts). Verify yourself.
""",
)
w(
    f"{T}/k12/resolver.py",
    """def _t(v):
    return tuple(int(x) for x in v.split('.'))
def resolve(index, reqs):
    out = {}
    for pkg, (lo, hi) in reqs.items():
        cands = [v for v in index.get(pkg, []) if _t(v) >= _t(lo) and (hi is None or _t(v) < _t(hi))]
        if not cands:
            return None
        out[pkg] = cands[0]
    return out
""",
)
w(
    f"{G}/k12.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from resolver import resolve
idx = {'a': ['1.0.0', '1.5.0', '2.0.0'], 'b': ['0.9.0']}
assert resolve(idx, {'a': ('1.0.0', '2.0.0')}) == {'a': '1.5.0'}
assert resolve(idx, {'a': ('3.0.0', None)}) is None
assert resolve(idx, {'zzz': ('1.0.0', None)}) is None
assert resolve(idx, {'a': ('1.0.0', None), 'b': ('0.1.0', '1.0.0')}) == {'a': '2.0.0', 'b': '0.9.0'}
assert resolve({'a': ['1.0.0']}, {'a': ('2.0.0', None)}) is None
print('k12 PASS')
""",
)

print("authored r3c3")
