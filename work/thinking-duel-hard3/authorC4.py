#!/usr/bin/env python3
"""Round-3 v2 tasks k13-k16."""

import os

ROOT = "work/thinking-duel-hard3"
T = os.path.join(ROOT, "v2")
G = os.path.join(ROOT, "grading2")


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


w(
    f"{T}/k13/prompt.md",
    """# Task k13: chunked base64 decoder

Work in $PWD. `b64x.py` has `decode_chunks(chunks)` decoding base64 text
arriving in ARBITRARY chunks (chunk boundaries may split anywhere, even
inside `%`-escapes... no escapes: raw base64 alphabet plus whitespace which
must be ignored). Padding `=` only valid at the very end; `=` elsewhere or
missing terminal padding raises ValueError; non-alphabet chars (besides
whitespace) raise ValueError. shipped code joins-then-decodes without
validating padding placement. Fix it, stdlib `base64` allowed. Verify with
odd splits yourself.
""",
)
w(
    f"{T}/k13/b64x.py",
    """import base64
def decode_chunks(chunks):
    return base64.b64decode(''.join(chunks))
""",
)
w(
    f"{G}/k13.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from b64x import decode_chunks
assert decode_chunks(['TWFu']) == b'Man'
assert decode_chunks(['T', 'W', 'F', 'u']) == b'Man'
assert decode_chunks(['TWFu\\n M', 'YW4=']) == b'ManMan'
for bad in [['TW=u'], ['TWF'], ['TW==u==='], ['T!Fu']]:
    try:
        decode_chunks(bad)
        raise SystemExit('k13 FAIL accepted')
    except ValueError:
        pass
try:
    decode_chunks(['TWFu', 'TWFu'])
    raise SystemExit('k13 FAIL midpad')
except ValueError:
    pass
print('k13 PASS')
""",
)

w(
    f"{T}/k14/prompt.md",
    """# Task k14: interval union and gaps

Work in $PWD. `ivl.py` has `union(intervals)` merging overlapping [lo, hi)
half-open intervals (adjacent [1,2)+[2,3) merge ONLY if `merge_adjacent`
is True, default False) returning sorted disjoint lists, and `gaps(merged,
span)` returning the gaps within [span_lo, span_hi). Empty input -> [].
shipped code merges adjacent always and miscomputes gaps. Fix it, stdlib
only. Verify yourself.
""",
)
w(
    f"{T}/k14/ivl.py",
    """def union(intervals, merge_adjacent=False):
    ivs = sorted(intervals)
    out = []
    for lo, hi in ivs:
        if out and lo <= out[-1][1]:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return [tuple(x) for x in out]
def gaps(merged, span):
    return []
""",
)
w(
    f"{G}/k14.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from ivl import union, gaps
assert union([(5, 6), (1, 3), (2, 4)]) == [(1, 4), (5, 6)]
assert union([(1, 2), (2, 3)]) == [(1, 2), (2, 3)]
assert union([(1, 2), (2, 3)], merge_adjacent=True) == [(1, 3)]
assert union([]) == []
assert gaps([(1, 4), (5, 6)], (0, 8)) == [(0, 1), (4, 5), (6, 8)]
assert gaps([], (2, 5)) == [(2, 5)]
assert gaps([(0, 8)], (0, 8)) == []
print('k14 PASS')
""",
)

w(
    f"{T}/k15/prompt.md",
    """# Task k15: mini template renderer

Work in $PWD. `tmpl.py` has `render(template, ctx)` with `{{name}}`
substitution, `{% if name %}...{% endif %}` conditionals (truthiness of
ctx value, nestable), and `{{name|escape}}` HTML-escaping (`&<>"'`). Unknown
names render as empty string; `{% if %}` on missing/empty is false. shipped
code regex-replaces without nesting or escaping. Fix it, stdlib only
(`html.escape` allowed). Verify nested + escaping yourself.
""",
)
w(
    f"{T}/k15/tmpl.py",
    """import re
def render(template, ctx):
    out = re.sub(r'\\{\\{(\\w+)\\}\\}', lambda m: str(ctx.get(m.group(1), '')), template)
    return out
""",
)
w(
    f"{G}/k15.py",
    """import sys
sys.path.insert(0, SYS_PATH)
from tmpl import render
assert render('hi {{n}}', {'n': 'ann'}) == 'hi ann'
assert render('hi {{missing}}!', {}) == 'hi !'
assert render('{% if a %}x{% endif %}', {'a': 1}) == 'x'
assert render('{% if a %}x{% endif %}', {}) == ''
assert render('{% if a %}1{% if b %}2{% endif %}3{% endif %}', {'a': 1, 'b': 1}) == '123'
assert render('{% if a %}1{% if b %}2{% endif %}3{% endif %}', {'a': 1}) == '13'
assert render('{{h|escape}}', {'h': '<a>&'}) == '&lt;a&gt;&amp;'
print('k15 PASS')
""",
)

w(
    f"{T}/k16/prompt.md",
    """# Task k16: reservoir sampler

Work in $PWD. `rsv.py` has `sample(stream, k, seed)` returning k items
uniformly sampled from an arbitrary iterable in ONE pass with O(k) memory
(reservoir sampling, Algorithm R) using an inline LCG only (no `random`
module): state = (1103515245 * state + 12345) % 2**31, j = state %
(item_index + 1) with 1-based item_index; if j < k replace reservoir[j].
Deterministic per seed. shipped code uses `random` (version-dependent).
Reimplement. Verify determinism and uniformity roughly yourself.
""",
)
w(
    f"{T}/k16/rsv.py",
    """import random
def sample(stream, k, seed):
    xs = list(stream)
    return random.Random(seed).sample(xs, k)
""",
)
w(
    f"{G}/k16.py",
    """import sys, inspect
sys.path.insert(0, SYS_PATH)
from rsv import sample
import rsv as shmod
assert 'random' not in inspect.getsource(shmod), 'no random module'
def ref(stream, k, seed):
    res = []
    s = seed % 2**31
    for idx, x in enumerate(stream, 1):
        s = (1103515245 * s + 12345) % 2**31
        j = s % idx
        if len(res) < k:
            res.append(x)
        elif j < k:
            res[j] = x
    return res
assert sample(iter(range(10)), 3, 42) == ref(iter(range(10)), 3, 42)
assert sample((x for x in range(100)), 5, 7) == ref((x for x in range(100)), 5, 7)
assert len(sample(iter(range(5)), 5, 1)) == 5
from collections import Counter
c = Counter()
for s in range(200):
    c.update(sample(range(20), 2, s))
assert min(c.values()) > 0, 'coverage'
print('k16 PASS')
""",
)

print("authored r3c4")
