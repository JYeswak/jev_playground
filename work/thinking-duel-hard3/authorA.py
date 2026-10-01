#!/usr/bin/env python3
"""Round-3 tasks h01-h08: prompt + buggy starter + hidden tests."""

import os

ROOT = "work/thinking-duel-hard3"
T = os.path.join(ROOT, "tasks")
G = os.path.join(ROOT, "grading")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


# h01: rotated sorted array, leftmost of duplicates
w(
    f"{T}/h01/prompt.md",
    """# Task h01: leftmost search in rotated array

Work in $PWD. `rotsearch.py` has `leftmost_rot(a, x)`: `a` is a rotated
sorted list (possibly with duplicates) or -1 if absent; return the leftmost
index of `x` in `a`, or -1. Duplicates make pure log-time impossible; an
O(n) worst case on all-duplicate input is acceptable, but strictly-correct
results are required. shipped code is wrong. Fix it, stdlib only. Verify.
""",
)
w(
    f"{T}/h01/rotsearch.py",
    """def leftmost_rot(a, x):
    for i, v in enumerate(a):
        if v == x:
            return i
    return -1
""",
)
w(
    f"{G}/h01.py",
    """import sys, random
sys.path.insert(0, SYS_PATH)
from rotsearch import leftmost_rot
def ref(a, x):
    try: return a.index(x)
    except ValueError: return -1
random.seed(101)
for _ in range(400):
    n = random.randint(0, 15)
    base = sorted(random.randint(0, 6) for _ in range(n))
    k = random.randint(0, n) if n else 0
    a = base[k:] + base[:k]
    for x in [random.randint(0, 7) for _ in range(3)]:
        assert leftmost_rot(a, x) == ref(a, x), (a, x)
assert leftmost_rot([2, 2, 2, 2], 2) == 0
assert leftmost_rot([], 1) == -1
print('h01 PASS')
""",
)

# h02: retry with HTTP-date Retry-After + cap + 501 permanent
w(
    f"{T}/h02/prompt.md",
    """# Task h02: retry with date-valued Retry-After

Work in $PWD. `retrypy.py` has `fetch_with_retry(call, retries=5, now=None,
sleeper=None)` where `call(attempt)` returns `(status, headers, body)` or
raises `TransientError`; `now()` gives epoch seconds (default `time.time`).
Rules: retry only {429,502,503,504} + TransientError; `Retry-After` may be
delta-seconds OR an HTTP date (parse with `email.utils.parsedate_to_datetime`,
wait = max(0, date - now)); else backoff 0.1*2**attempt with total sleep
capped at 2.0s; 501 and other 4xx/5xx raise `PermanentError` at once; 200
returns body. shipped code is wrong. Fix it. Verify yourself.
""",
)
w(
    f"{T}/h02/retrypy.py",
    """import time
class TransientError(Exception): pass
class PermanentError(Exception): pass
TRANSIENT = {429, 502, 503, 504}
def fetch_with_retry(call, retries=5, now=None, sleeper=None):
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
    f"{G}/h02.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from retrypy import fetch_with_retry, TransientError, PermanentError
import email.utils, calendar
sl = []
now = [1000.0]
def slp(s): sl.append(s)
assert fetch_with_retry(lambda a: (200, {}, 'ok'), now=lambda: now[0], sleeper=slp) == 'ok'
sl.clear()
try:
    fetch_with_retry(lambda a: (501, {}, None), now=lambda: now[0], sleeper=slp)
    raise SystemExit('h02 FAIL')
except PermanentError:
    pass
assert sl == [], sl
sl.clear()
dt = email.utils.formatdate(now[0] + 3, usegmt=True)
calls = iter([(503, {'Retry-After': dt}, None), (200, {}, 'd')])
assert fetch_with_retry(lambda a: next(calls), now=lambda: now[0], sleeper=slp) == 'd'
assert len(sl) == 1 and abs(sl[0] - 3.0) < 0.01, sl
sl.clear()
def flaky(a):
    if a < 4: raise TransientError()
    return (200, {}, 'late')
assert fetch_with_retry(flaky, now=lambda: now[0], sleeper=slp) == 'late'
assert sum(sl) <= 2.0 + 1e-9, sl
try:
    fetch_with_retry(lambda a: (500, {}, None), retries=2, now=lambda: now[0], sleeper=lambda s: None)
    raise SystemExit('h02 FAIL 500')
except PermanentError:
    pass
print('h02 PASS')
""",
)

# h03: census counting calls + thinking chars, skip binary
w(
    f"{T}/h03/prompt.md",
    """# Task h03: session census with thinking totals

Work in $PWD. `census.py` has `summarize(path)` returning

assistant `toolCall` items (type exactly `toolCall`, string `name`) plus the
total length of all `thinking` strings in assistant messages. Must skip
malformed lines, non-dict rows, non-assistant messages, and lines containing
NUL bytes, all silently. shipped code is wrong. Fix it, stdlib only. Verify.
""",
)
w(
    f"{T}/h03/census.py",
    """import json
from collections import Counter
def summarize(path):
    counts = Counter()
    think = 0
    for line in open(path):
        row = json.loads(line)
        for item in row['message']['content']:
            if item.get('type') == 'toolCall':
                counts[item.get('name')] += 1
            think += len(item.get('thinking', ''))
    return {'calls': dict(counts), 'think_chars': think}
""",
)
w(
    f"{G}/h03.py",
    """import sys, tempfile, os
sys.path.insert(0, SYS_PATH)
from census import summarize
lines = [
 '{"message": {"role": "assistant", "content": [{"type": "toolCall", "name": "read"}, {"type": "thinking", "thinking": "abc"}]}}',
 'junk{',
 '[1,2]',
 '{"message": {"role": "user", "content": [{"type": "toolCall", "name": "read"}, {"type": "thinking", "thinking": "zz"}]}}',
 '{"message": {"role": "assistant", "content": [{"type": "toolCall"}, {"type": "thinking", "thinking": 5}]}}',
 'has\\x00nul',
 '{"message": {"role": "assistant", "content": "plain"}}',
]
fd, p = tempfile.mkstemp(suffix='.jsonl')
with os.fdopen(fd, 'w') as fh:
    fh.write('\\n'.join(lines) + '\\n')
got = summarize(p)
assert got == {'calls': {'read': 1}, 'think_chars': 3}, got
os.unlink(p)
print('h03 PASS')
""",
)

# h04: Agresti-Coull interval vs reference
w(
    f"{T}/h04/prompt.md",
    """# Task h04: Agresti-Coull interval

Work in $PWD. `ac.py` has `agresti_coull(k, n, z=1.96)` returning `(lo, hi)`:
tilde_n = n + z^2, tilde_p = (k + z^2/2) / tilde_n,
half = z * sqrt(tilde_p * (1 - tilde_p) / tilde_n), return
(tilde_p - half, tilde_p + half). It is wrong. Fix it to match reference to
1e-9 with outputs inside [0, 1] within 1e-9 slop. stdlib only. Verify.
""",
)
w(
    f"{T}/h04/ac.py",
    """def agresti_coull(k, n, z=1.96):
    p = k / n
    half = z * (p * (1 - p) / n) ** 0.5
    return (p - half, p + half)
""",
)
w(
    f"{G}/h04.py",
    """import sys, math
sys.path.insert(0, SYS_PATH)
from ac import agresti_coull as ac
def ref(k, n, z=1.96):
    nt = n + z * z
    pt = (k + z * z / 2) / nt
    h = z * math.sqrt(pt * (1 - pt) / nt)
    return (pt - h, pt + h)
for k, n in [(5, 350), (0, 350), (268, 300), (0, 5), (3, 9), (99, 100)]:
    a, b = ac(k, n), ref(k, n)
    assert abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9, (k, n, a, b)
    assert -1e-9 <= a[0] <= a[1] <= 1 + 1e-9, (k, n, a)
print('h04 PASS')
""",
)

# h05: runner with merged streaming + grandchild kill
w(
    f"{T}/h05/prompt.md",
    """# Task t05b: streaming runner with process-tree kill

Work in $PWD. `runbox.py` has `run(cmd, timeout)` returning
`(exit_code, merged)` where merged is stdout+stderr interleaved in arrival
order as text. It must enforce the timeout (exit 124), never deadlock when
either pipe floods, and kill the whole process tree including grandchildren
(start_new_session + killpg). shipped code returns separate streams, leaks
grandchildren, and can deadlock. Fix it, stdlib only. Verify with flooding
and sleepy-grandchild commands.
""",
)
w(
    f"{T}/h05/runbox.py",
    """import subprocess
def run(cmd, timeout):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return (p.returncode, out + err)
    except subprocess.TimeoutExpired:
        return (124, '')
""",
)
w(
    f"{G}/h05.py",
    """import sys, time
sys.path.insert(0, SYS_PATH)
from runbox import run
code, merged = run(['echo', 'hi'], 5)
assert code == 0 and merged.strip() == 'hi', (code, merged)
t = time.time()
code, merged = run(['python3', '-c', 'import subprocess,time;subprocess.Popen(["sleep","30"]);time.sleep(30)'], 1)
dt = time.time() - t
assert code == 124 and dt < 10, (code, dt)
import subprocess as sp
left = sp.run(['pgrep', '-f', 'sleep 30'], capture_output=True, text=True).stdout.strip()
assert left == '', left
t = time.time()
code, merged = run(['python3', '-c', 'import sys; sys.stderr.write("e"*200000); print("o"*200000)'], 10)
assert code == 0 and merged.count('e') == 200000 and merged.count('o') == 200000, (code, len(merged))
print('h05 PASS')
""",
)

# h06: glob-aware ranked touches (fnmatch ** support)
w(
    f"{T}/h06/prompt.md",
    """# Task h06: glob-aware ranked touches

Work in $PWD. `touches.py` has `touched_ranks(value, hits)` returning sorted
unique 1-based ranks where `value` touches a hit. A hit touches when: exact
equality; `value` ends with `/hit`; `hit` is a substring of `value`; OR the
hit contains `*`/`?`/`[` and `fnmatch.fnmatchcase(value, hit)` or
`fnmatchcase(value, '*/' + hit)` is true. Empty value/hit touches nothing.
shipped code mishandles globs and ranks. Fix it, stdlib only. Verify.
""",
)
w(
    f"{T}/h06/touches.py",
    """import fnmatch
def touched_ranks(value, hits):
    ranks = set()
    for i, hit in enumerate(hits):
        if value == hit or value.endswith('/' + hit) or hit in value:
            ranks.add(i + 1)
    return sorted(ranks)
""",
)
w(
    f"{G}/h06.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from touches import touched_ranks
assert touched_ranks('a/b.md', ['b.md']) == [1]
assert touched_ranks('src/x_test.py', ['*_test.py']) == [1]
assert touched_ranks('a/b/c.md', ['*.md', 'b/*.md']) == [1, 2]
assert touched_ranks('nomatch.py', ['*.md']) == []
assert touched_ranks('', ['*']) == []
assert touched_ranks('x', []) == []
assert touched_ranks('a/b.md', ['b.md', 'A/B.MD']) == [1]
print('h06 PASS')
""",
)

# h07: partial Fisher-Yates subset with LCG
w(
    f"{T}/h07/prompt.md",
    """# Task h07: deterministic random subset

Work in $PWD. `subset.py` has `sample_k(n, k, seed)` returning k distinct
indices from range(n) in selection order, deterministic across runs and
Python versions for the same seed, uniform (partial Fisher-Yates), using an
inline integer LCG only (no `random` module): state = (1103515245 * state +
12345) % 2**31, j = state % (i + 1), iterating i from n-1 down to n-k, and
collecting the element swapped into position i. shipped code uses `random`
(version-dependent). Reimplement. Verify determinism yourself.
""",
)
w(
    f"{T}/h07/subset.py",
    """import random
def sample_k(n, k, seed):
    return random.Random(seed).sample(range(n), k)
""",
)
w(
    f"{G}/h07.py",
    """import sys, inspect
sys.path.insert(0, SYS_PATH)
from subset import sample_k
import subset as shmod
assert 'random' not in inspect.getsource(shmod), 'no random module'
def ref(n, k, seed):
    xs = list(range(n))
    out = []
    s = seed % 2**31
    for i in range(n - 1, n - k - 1, -1):
        s = (1103515245 * s + 12345) % 2**31
        j = s % (i + 1)
        xs[i], xs[j] = xs[j], xs[i]
        out.append(xs[i])
    return out
for n, k, s in [(10, 3, 42), (52, 5, 7), (100, 10, 1), (5, 5, 9)]:
    assert sample_k(n, k, s) == ref(n, k, s), (n, k, s)
    assert len(set(sample_k(n, k, s))) == k
print('h07 PASS')
""",
)

# h08: multi-pattern redact with marker integrity
w(
    f"{T}/h08/prompt.md",
    """# Task h08: multi-pattern redact with marker integrity

Work in $PWD. `prefix.py` has `redact(cmd, home, patterns)` returning at
most 200 chars with `home` -> `~` and every match of each compiled pattern
in `patterns` replaced by `[REDACTED]`. Requirements: scrub ALL patterns
before cutting; never cut inside a `[REDACTED]` marker (if the 200-char cut
would split one, end the string before it); secrets straddling char 200 must
be fully removed. shipped code is wrong. Fix it, stdlib only. Verify,
including straddling and adjacent secrets.
""",
)
w(
    f"{T}/h08/prefix.py",
    """def redact(cmd, home, patterns):
    short = cmd.replace(home, '~').strip()[:200]
    for pat in patterns:
        short = pat.sub('[REDACTED]', short)
    return short
""",
)
w(
    f"{G}/h08.py",
    """import sys, re
sys.path.insert(0, SYS_PATH)
from prefix import redact
pats = [re.compile(r'sk-[a-z]{20,}'), re.compile(r'Bearer [A-Za-z0-9]{16,}')]
assert redact('ls', '/h', pats) == 'ls'
got = redact('export A=sk-abcdefghijklmnopqrst B=Bearer ABCDEFGH12345678 end', '/h', pats)
assert got == 'export A=[REDACTED] B=[REDACTED] end', got
cmd = 'x' * 185 + ' sk-abcdefghijklmnopqrstuvwxyz tail here'
got = redact(cmd, '/h', pats)
assert len(got) <= 200 and 'sk-' not in got, got
assert '[REDACT' not in got.replace('[REDACTED]', ''), got
cmd2 = 'x' * 195 + 'sk-abcdefghijklmnopqrstuvwxyz'
got2 = redact(cmd2, '/h', pats)
assert 'sk-' not in got2 and len(got2) <= 200, got2
assert '[REDACT' not in got2.replace('[REDACTED]', ''), got2
print('h08 PASS')
""",
)

print("authored r3a")
