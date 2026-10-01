#!/usr/bin/env python3
"""GREEN references k09-k16 -> /tmp/g3k/."""

import os


def put(tid, fname, text):
    d = f"/tmp/g3k/{tid}"
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, fname), "w").write(text)


put(
    "k09",
    "patcher.py",
    """def apply_patch(original, diff):
    orig = original.split('\\n')
    if orig and orig[-1] == '':
        orig.pop()
    out = []
    oi = 0
    for line in diff.split('\\n'):
        if line.startswith('---') or line.startswith('+++') or line == '':
            continue
        if line.startswith('@@'):
            import re
            m = re.match(r'@@ -(\\d+)(?:,(\\d+))? \\+(\\d+)(?:,(\\d+))? @@', line)
            old_start = int(m.group(1)) - 1
            while oi < old_start:
                out.append(orig[oi])
                oi += 1
            continue
        if line.startswith(' '):
            if oi >= len(orig) or orig[oi] != line[1:]:
                raise ValueError('context mismatch')
            out.append(orig[oi])
            oi += 1
        elif line.startswith('-'):
            if oi >= len(orig) or orig[oi] != line[1:]:
                raise ValueError('removal mismatch')
            oi += 1
        elif line.startswith('+'):
            out.append(line[1:])
        else:
            raise ValueError('bad hunk line')
    while oi < len(orig):
        out.append(orig[oi])
        oi += 1
    text = '\\n'.join(out)
    if original.endswith('\\n'):
        text += '\\n'
    return text
""",
)

put(
    "k10",
    "bucket.py",
    """import time, threading
class Bucket:
    def __init__(self, rate, burst, now=None):
        self.rate = rate
        self.burst = burst
        self.now = now or time.monotonic
        self.tokens = float(burst)
        self.last = self.now()
        self.lock = threading.Lock()
    def take(self, n=1):
        with self.lock:
            now = self.now()
            self.tokens = min(float(self.burst), self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= n:
                self.tokens -= n
                return True
            return False
""",
)

put(
    "k11",
    "mdtable.py",
    """def _cells(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|') and not line.endswith('\\\\|'):
        line = line[:-1]
    cells, cur, esc = [], '', False
    for c in line:
        if esc:
            cur += c
            esc = False
        elif c == '\\\\':
            esc = True
        elif c == '|':
            cells.append(cur.strip())
            cur = ''
        else:
            cur += c
    cells.append(cur.strip())
    return cells
def parse(text):
    lines = text.split('\\n')
    for i, line in enumerate(lines):
        if '|' not in line:
            continue
        if i + 1 >= len(lines):
            continue
        d = lines[i + 1].strip()
        parts = [p.strip() for p in d.strip('|').split('|')]
        if not parts or any(not __import__('re').match(r'^:?-{1,}:?$', p) for p in parts):
            continue
        header = _cells(line)
        rows = []
        for dl in lines[i + 2:]:
            if '|' not in dl:
                break
            vals = _cells(dl)
            row = {}
            for j, h in enumerate(header):
                row[h] = vals[j] if j < len(vals) else None
            rows.append(row)
        return rows
    return []
""",
)

put(
    "k12",
    "resolver.py",
    """def _t(v):
    return tuple(int(x) for x in v.split('.'))
def resolve(index, reqs):
    out = {}
    for pkg, (lo, hi) in reqs.items():
        cands = [v for v in index.get(pkg, [])
                 if _t(v) >= _t(lo) and (hi is None or _t(v) < _t(hi))]
        if not cands:
            return None
        out[pkg] = max(cands, key=_t)
    return out
""",
)

put(
    "k13",
    "b64x.py",
    """import base64
ALPHA = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')
def decode_chunks(chunks):
    text = ''.join(chunks)
    body = ''.join(c for c in text if not c.isspace())
    if not body:
        return b''
    if any(c not in ALPHA and c != '=' for c in body):
        raise ValueError('bad char')
    pad = len(body) - len(body.rstrip('='))
    core = body.rstrip('=')
    if pad > 2 or '=' in core:
        raise ValueError('bad padding')
    if (len(core) + pad) % 4 != 0:
        raise ValueError('bad length')
    try:
        return base64.b64decode(body, validate=False)
    except Exception as e:
        raise ValueError(str(e))
""",
)

put(
    "k14",
    "ivl.py",
    """def union(intervals, merge_adjacent=False):
    ivs = sorted(intervals)
    out = []
    for lo, hi in ivs:
        if out and (lo < out[-1][1] or (merge_adjacent and lo == out[-1][1])):
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return [tuple(x) for x in out]
def gaps(merged, span):
    slo, shi = span
    out = []
    cur = slo
    for lo, hi in merged:
        if lo > cur:
            out.append((cur, min(lo, shi)))
        cur = max(cur, hi)
        if cur >= shi:
            break
    if cur < shi:
        out.append((cur, shi))
    return out
""",
)

put(
    "k15",
    "tmpl.py",
    """import html as _html
def _find_end(s, start):
    depth = 0
    i = start
    while i < len(s):
        if s.startswith('{% if', i):
            depth += 1
            i = s.index('%}', i) + 2
        elif s.startswith('{% endif %}', i):
            if depth == 0:
                return i
            depth -= 1
            i += len('{% endif %}')
        else:
            i += 1
    raise ValueError('unclosed if')
def _render(s, ctx):
    out = []
    i = 0
    while i < len(s):
        if s.startswith('{{', i):
            j = s.index('}}', i)
            expr = s[i+2:j].strip()
            if expr.endswith('|escape'):
                name = expr[:-7].strip()
                out.append(_html.escape(str(ctx.get(name, '')), quote=True))
            else:
                out.append(str(ctx.get(expr, '')))
            i = j + 2
        elif s.startswith('{% if', i):
            j = s.index('%}', i)
            name = s[i+5:j].strip()
            end = _find_end(s, j + 2)
            body = s[j+2:end]
            if ctx.get(name):
                out.append(_render(body, ctx))
            i = end + len('{% endif %}')
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)
def render(template, ctx):
    return _render(template, ctx)
""",
)

put(
    "k16",
    "rsv.py",
    """def sample(stream, k, seed):
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
""",
)

print("green k09-k16 written")
