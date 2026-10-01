#!/usr/bin/env python3
"""Author the 12 hard tasks: prompt.md + starter files under tasks/, hidden tests under grading/."""

import os

ROOT = "work/thinking-duel-hard"
T = os.path.join(ROOT, "tasks")
G = os.path.join(ROOT, "grading")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


# t01: leftmost binary search (bug: returns insertion point check)
w(
    f"{T}/t01/prompt.md",
    """# Task t01: leftmost binary search

Work in $PWD. File `search.py` has `bisect_leftmost(a, x)` returning the
leftmost index of `x` in sorted list `a`, or -1 if absent. It is subtly
wrong on some inputs. Fix it, standard library only. Verify yourself.
""",
)
w(
    f"{T}/t01/search.py",
    """def bisect_leftmost(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo if lo < len(a) and a[lo] == x else -1
""",
)
w(
    f"{G}/t01.py",
    """import random, sys
sys.path.insert(0, SYS_PATH)
from search import bisect_leftmost
def ref(a, x):
    try: return a.index(x)
    except ValueError: return -1
cases = [[], [1], [1,2,2,3], [2,2,2], [1,3,5], list(range(0,100,3))]
random.seed(11)
for _ in range(300):
    n = random.randint(0, 12)
    a = sorted(random.randint(0, 5) for _ in range(n))
    for x in [random.randint(0, 6) for _ in range(4)]:
        assert bisect_leftmost(a, x) == ref(a, x), (a, x)
for a in cases:
    for x in [-1, 0, 1, 2, 3, 5, 99, 100]:
        assert bisect_leftmost(a, x) == ref(a, x), (a, x)
print('t01 PASS')
""",
)

# t02: retry with backoff honoring Retry-After (bug: ignores header, retries 4xx)
w(
    f"{T}/t02/prompt.md",
    """# Task t02: retry policy

Work in $PWD. `retrypy.py` has `fetch_with_retry(call, retries=5)` where
`call(attempt)` returns `(status, headers, body)` or raises
`TransientError`. It must: retry only transient statuses {429,502,503,504}
and TransientError; honor `Retry-After` seconds when present (else
exponential backoff base 0.1s with jitter, capped so total sleep <= 2.0s);
raise `PermanentError` immediately on other 4xx; return body on 200.
It is wrong. Fix it (no real sleeping: use the injected `sleeper(secs)`
callable, default `time.sleep`). Verify yourself.
""",
)
w(
    f"{T}/t02/retrypy.py",
    """import time, random
class TransientError(Exception): pass
class PermanentError(Exception): pass
TRANSIENT = {429, 502, 503, 504}
def fetch_with_retry(call, retries=5, sleeper=None):
    slp = sleeper or time.sleep
    total = 0.0
    for attempt in range(retries):
        try:
            status, headers, body = call(attempt)
        except TransientError:
            status, headers, body = 503, {}, None
        if status == 200:
            return body
        if status in TRANSIENT:
            wait = 0.1 * (2 ** attempt)
            slp(wait)
            total += wait
            continue
        raise PermanentError(status)
    raise PermanentError('exhausted')
""",
)
w(
    f"{G}/t02.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from retrypy import fetch_with_retry, TransientError, PermanentError
sleeps = []
def slp(s):
    assert s >= 0, s
    sleeps.append(s)
# 200 first try
assert fetch_with_retry(lambda a: (200, {}, 'ok'), sleeper=slp) == 'ok'
# 4xx permanent immediately, no sleep
sleeps.clear()
try:
    fetch_with_retry(lambda a: (404, {}, None), sleeper=slp)
    raise SystemExit('t02 FAIL: no raise')
except PermanentError:
    pass
assert sleeps == [], sleeps
# Retry-After honored exactly
sleeps.clear()
calls = iter([(503, {'Retry-After': '1'}, None), (200, {}, 'back')])
assert fetch_with_retry(lambda a: next(calls), sleeper=slp) == 'back'
assert sleeps == [1.0], sleeps
# TransientError retried; total sleep capped <= 2.0
sleeps.clear()
# exhaustion raises
try:
    fetch_with_retry(lambda a: (503, {}, None), retries=3, sleeper=lambda s: None)
    raise SystemExit('t02 FAIL: no exhaust raise')
except PermanentError:
    pass
print('t02 PASS')
""",
)

# t03: JSONL tool-call counter robust to malformed rows
w(
    f"{T}/t03/prompt.md",
    """# Task t03: session tool-call census

Work in $PWD. `census.py` has `count_calls(path)` returning a dict
{tool_name: count} over assistant `toolCall` items in a JSONL session file.
It must skip malformed JSON lines and non-dict rows silently, and count only
items with type exactly `toolCall` and a string `name`. It is wrong. Fix it,
standard library only. A sample file `sample.jsonl` is included. Verify yourself.
""",
)
w(
    f"{T}/t03/census.py",
    """import json
from collections import Counter
def count_calls(path):
    counts = Counter()
    for line in open(path):
        row = json.loads(line)
        msg = row.get('message', {})
        for item in msg.get('content', []):
            if item.get('type') == 'toolCall':
                counts[item.get('name')] += 1
    return dict(counts)
""",
)
w(
    f"{T}/t03/sample.jsonl",
    """{"message": {"role": "assistant", "content": [{"type": "toolCall", "name": "read"}]}}
not json at all
{"message": {"role": "assistant", "content": [{"type": "toolCall", "name": "bash"}, {"type": "text"}]}}
[1,2,3]
{"message": {"role": "user", "content": [{"type": "toolCall", "name": "read"}]}}
{"message": {"role": "assistant", "content": [{"type": "toolCall"}, {"type": "toolCall", "name": 7}]}}
""",
)
w(
    f"{G}/t03.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from census import count_calls
import tempfile, os
body = ('{"message": {"role": "assistant", "content": [{"type": "toolCall", "name": "read"}]}}\n'
        'junk\n'
        '{"message": {"role": "assistant", "content": [{"type": "toolCall", "name": "bash"}, {"type": "toolcall", "name": "read"}]}}\n'
        '[1]\n'
        '{"message": {"role": "assistant", "content": "plain"}}\n'
        '{"message": {"role": "assistant", "content": [{"type": "toolCall"}, {"type": "toolCall", "name": null}]}}\n')
fd, p = tempfile.mkstemp(suffix='.jsonl')
os.write(fd, body.encode())
os.close(fd)
got = count_calls(p)
assert got == {'read': 1, 'bash': 1}, got
os.unlink(p)
print('t03 PASS')
""",
)

# t04: Wilson interval vs reference values
w(
    f"{T}/t04/prompt.md",
    """# Task t04: Wilson score interval

Work in $PWD. `wilson.py` has `wilson(k, n, z=1.96)` returning `(lo, hi)`
proportions for k successes in n trials. It is wrong. Fix it to the
standard Wilson score interval (no continuity correction), standard library
only. Values must match reference to 1e-9. Verify yourself.
""",
)
w(
    f"{T}/t04/wilson.py",
    """def wilson(k, n, z=1.96):
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5
    return (center - margin / denom, center + margin / denom)
""",
)
w(
    f"{G}/t04.py",
    """import sys, math
sys.path.insert(0, SYS_PATH)
from wilson import wilson
def ref(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)
for k, n in [(5, 350), (0, 350), (268, 300), (1, 1), (0, 10), (7, 13), (499, 1000)]:
    a, b = wilson(k, n), ref(k, n)
    assert abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9, (k, n, a, b)
    assert 0 <= a[0] <= a[1] <= 1, (k, n, a)
print('t04 PASS')
""",
)

# t05: bounded subprocess with timeout, concurrent drain
w(
    f"{T}/t05/prompt.md",
    """# Task t05: bounded subprocess runner

Work in $PWD. `runbox.py` has `run(cmd, timeout)` returning
`(exit_code, stdout, stderr)` (stdout/stderr as str). It must: enforce the
timeout (return exit_code 124 with partial output on expiry), never deadlock
on large stderr while stdout is small (and vice versa), and never leave a
runaway child (kill the process group). It is wrong. Fix it, standard
library only. Verify yourself with slow and chatty commands.
""",
)
w(
    f"{T}/t05/runbox.py",
    """import subprocess
def run(cmd, timeout):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return (p.returncode, out, err)
    except subprocess.TimeoutExpired:
        return (124, '', '')
""",
)
w(
    f"{G}/t05.py",
    """import sys, time
sys.path.insert(0, SYS_PATH)
from runbox import run
code, out, err = run(['echo', 'hi'], 5)
assert (code, out.strip()) == (0, 'hi'), (code, out)
t = time.time()
code, out, err = run(['sleep', '30'], 1)
assert code == 124 and time.time() - t < 10, (code, time.time() - t)
t = time.time()
code, out, err = run(['python3', '-c', 'import sys; sys.stderr.write("x"*300000); print("y"*300000)'], 10)
assert code == 0 and out == 'y' * 300000 + '\n' and err == 'x' * 300000, (code, len(out), len(err))
import subprocess as sp
left = sp.run(['pgrep', '-f', 'sleep 30'], capture_output=True, text=True).stdout.strip()
assert left == '', left
print('t05 PASS')
""",
)

# t06: path suffix matcher (touchedRanks semantics)
w(
    f"{T}/t06/prompt.md",
    """# Task t06: ranked path touches

Work in $PWD. `touches.py` has `touched_ranks(value, hits)` returning the
sorted unique 1-based ranks where `value` touches a hit: exact equality, or
`value` ends with `/hit`, or `hit` is a substring of `value`. Empty hits or
empty value touch nothing. It is subtly wrong. Fix it, standard library
only. Verify yourself.
""",
)
w(
    f"{T}/t06/touches.py",
    """def touched_ranks(value, hits):
    ranks = set()
    for i, hit in enumerate(hits):
        if not hit or not value:
            continue
        if value == hit or value.endswith('/' + hit) or hit in value:
            ranks.add(i)
    return sorted(ranks)
""",
)
w(
    f"{G}/t06.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from touches import touched_ranks
assert touched_ranks('a/b.md', ['b.md']) == [1]
assert touched_ranks('b.md', ['b.md']) == [1]
assert touched_ranks('xb.md', ['b.md']) == [1]
assert touched_ranks('', ['b.md']) == []
assert touched_ranks('x', []) == []
assert touched_ranks('a/b/c.md', ['c.md', 'b/c.md', 'a/b/c.md']) == [1, 2, 3]
assert touched_ranks('/r/src/x.py', ['x.py', 'src/x.py']) == [1, 2]
assert touched_ranks('nomatch', ['other']) == []
print('t06 PASS')
""",
)

print("authored")
