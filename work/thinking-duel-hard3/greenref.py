#!/usr/bin/env python3
"""Reference fixes for h01-h16 GREEN check (written to /tmp/g3/<t>/)."""

import os, shutil


def put(tid, fname, text):
    d = f"/tmp/g3/{tid}"
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, fname), "w").write(text)


put(
    "h01",
    "rotsearch.py",
    """def leftmost_rot(a, x):
    for i, v in enumerate(a):
        if v == x:
            return i
    return -1
""",
)

put(
    "h02",
    "retrypy.py",
    """import time
from email.utils import parsedate_to_datetime
class TransientError(Exception): pass
class PermanentError(Exception): pass
TRANSIENT = {429, 502, 503, 504}
def _wait(headers, attempt, now, total):
    ra = headers.get('Retry-After')
    if ra is not None:
        try:
            return max(0.0, float(ra))
        except (ValueError, TypeError):
            pass
        try:
            dt = parsedate_to_datetime(ra)
            ts = dt.timestamp()
            return max(0.0, ts - now())
        except (ValueError, TypeError):
            pass
    return min(0.1 * (2 ** attempt), max(0.0, 2.0 - total))
def fetch_with_retry(call, retries=5, now=None, sleeper=None):
    slp = sleeper or time.sleep
    nowfn = now or time.time
    total = 0.0
    for attempt in range(retries):
        try:
            status, headers, body = call(attempt)
        except TransientError:
            status, headers, body = 503, {}, None
        if status == 200:
            return body
        if status in TRANSIENT:
            w = _wait(headers, attempt, nowfn, total)
            slp(w)
            total += w
            continue
        raise PermanentError(status)
    raise PermanentError('exhausted')
""",
)

put(
    "h03",
    "census.py",
    """import json
from collections import Counter
def summarize(path):
    counts = Counter()
    think = 0
    for line in open(path, errors='replace'):
        if '\\x00' in line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if not isinstance(row, dict):
            continue
        msg = row.get('message')
        if not isinstance(msg, dict) or msg.get('role') != 'assistant':
            continue
        content = msg.get('content')
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get('type') == 'toolCall' and isinstance(item.get('name'), str):
                counts[item['name']] += 1
            th = item.get('thinking')
            if isinstance(th, str):
                think += len(th)
    return {'calls': dict(counts), 'think_chars': think}
""",
)

put(
    "h04",
    "ac.py",
    """def agresti_coull(k, n, z=1.96):
    nt = n + z * z
    pt = (k + z * z / 2) / nt
    half = z * (pt * (1 - pt) / nt) ** 0.5
    return (pt - half, pt + half)
""",
)

put(
    "h05",
    "runbox.py",
    """import os, signal, subprocess, threading
def run(cmd, timeout):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True)
    out_chunks, err_chunks = [], []
    def drain(pipe, store):
        try:
            for line in iter(pipe.readline, ''):
                store.append(line)
        except Exception:
            pass
        finally:
            try: pipe.close()
            except Exception: pass
    ts = [threading.Thread(target=drain, args=(p.stdout, out_chunks)),
          threading.Thread(target=drain, args=(p.stderr, err_chunks))]
    for t in ts: t.start()
    try:
        rc = p.wait(timeout=timeout)
        for t in ts: t.join(timeout=5)
        return (rc, ''.join(out_chunks) + ''.join(err_chunks))
    except subprocess.TimeoutExpired:
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        p.wait()
        for t in ts: t.join(timeout=5)
        return (124, ''.join(out_chunks) + ''.join(err_chunks))
""",
)

put(
    "h06",
    "touches.py",
    """import fnmatch
def _hit(value, hit):
    if value == hit or value.endswith('/' + hit) or hit in value:
        return True
    if any(c in hit for c in '*?['):
        return (fnmatch.fnmatchcase(value, hit)
                or fnmatch.fnmatchcase(value, '*/' + hit))
    return False
def touched_ranks(value, hits):
    if not value:
        return []
    return sorted({i + 1 for i, h in enumerate(hits) if h and _hit(value, h)})
""",
)

put(
    "h07",
    "subset.py",
    """def sample_k(n, k, seed):
    xs = list(range(n))
    out = []
    s = seed % 2**31
    for i in range(n - 1, n - k - 1, -1):
        s = (1103515245 * s + 12345) % 2**31
        j = s % (i + 1)
        xs[i], xs[j] = xs[j], xs[i]
        out.append(xs[i])
    return out
""",
)

put(
    "h08",
    "prefix.py",
    """def redact(cmd, home, patterns):
    s = cmd.replace(home, '~').strip()
    for pat in patterns:
        s = pat.sub('[REDACTED]', s)
    if len(s) <= 200:
        return s
    cut = s[:200]
    idx = cut.rfind('[REDACT')
    if idx != -1 and '[REDACTED]' not in cut[idx:]:
        return s[:idx].rstrip()
    return cut
""",
)

put(
    "h09",
    "delim.py",
    """def _enc(v, delim, none_as):
    if v is None:
        return none_as if none_as else '""'
    if v == '' :
        return ('"' + none_as + '"') if v == none_as and none_as else v
    if any(c in v for c in (delim, '"', '\\n', '\\r')) or v == none_as:
        return '"' + v.replace('"', '""') + '"'
    return v
def write_delim(path, rows, delim='|', none_as=''):
    with open(path, 'w', newline='') as fh:
        for row in rows:
            fh.write(delim.join(_enc(v, delim, none_as) for v in row) + '\\n')
def _split(line, delim):
    fields, cur, q = [], '', False
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            if c == '"':
                if i + 1 < len(line) and line[i + 1] == '"':
                    cur += '"'
                    i += 2
                else:
                    q = False
                    i += 1
            else:
                cur += c
                i += 1
        else:
            if c == '"':
                q = True
                i += 1
            elif c == delim:
                fields.append(cur)
                cur = ''
                i += 1
            else:
                cur += c
                i += 1
    fields.append(cur)
    return fields
def read_delim(path, delim='|', none_as=''):
    rows = []
    buf = ''
    with open(path, newline='') as fh:
        text = fh.read()
    for raw in text.split('\\n'):
        rows.append(raw)
    if rows and rows[-1] == '':
        rows.pop()
    out = []
    acc = ''
    recs = []
    for raw in rows:
        acc = raw if not acc else acc + '\\n' + raw
        f = _split(acc, delim)
        if acc.count('"') % 2 == 0:
            recs.append(f)
            acc = ''
    if acc:
        recs.append(_split(acc, delim))
    def dec(v):
        if none_as and v == none_as:
            return None
        if not none_as and v == '""':
            return None
        return v
    return [[dec(v) for v in r] for r in recs]
""",
)

put(
    "h10",
    "c.py",
    """import time
class Cache:
    def __init__(self, capacity, ttl, now=None):
        self.cap = capacity
        self.ttl = ttl
        self.now = now or time.monotonic
        self.d = {}
        self.use = {}
        self.rec = {}
        self.tick = 0
    def _live(self, k):
        e = self.d.get(k)
        if e is None:
            return None
        v, ts = e
        if self.now() - ts > self.ttl:
            self.d.pop(k, None)
            self.use.pop(k, None)
            self.rec.pop(k, None)
            return None
        return v
    def get(self, k):
        v = self._live(k)
        if v is None and k not in self.d:
            return None
        if v is None:
            return None
        self.tick += 1
        self.use[k] = self.use.get(k, 0) + 1
        self.rec[k] = self.tick
        return v
    def put(self, k, v):
        self.tick += 1
        self.d[k] = (v, self.now())
        self.use[k] = self.use.get(k, 0) + 1
        self.rec[k] = self.tick
        while len(self.d) > self.cap:
            victim = min(self.d, key=lambda x: (self.use.get(x, 0), self.rec.get(x, 0)))
            self.d.pop(victim)
            self.use.pop(victim, None)
            self.rec.pop(victim, None)
""",
)

put(
    "h11",
    "topo.py",
    """import heapq
def order(deps):
    nodes = set(deps)
    for ds in deps.values():
        nodes.update(ds)
    indeg = {n: 0 for n in nodes}
    rdeps = {n: [] for n in nodes}
    for n, ds in deps.items():
        for d in set(ds):
            indeg[n] += 1
            rdeps[d].append(n)
    heap = sorted([n for n in nodes if indeg[n] == 0])
    heapq.heapify(heap)
    out = []
    while heap:
        n = heapq.heappop(heap)
        out.append(n)
        for m in rdeps[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)
    if len(out) != len(nodes):
        cyc = sorted(n for n in nodes if indeg[n] > 0)
        return (False, cyc + [cyc[0]])
    return (True, out)
""",
)

put(
    "h12",
    "beads.py",
    """import re
MARKS = {'x': 'closed', ' ': 'open', '~': 'in_progress', '-': 'deferred'}
WORDS = {'closed': 'closed', 'open': 'open', 'in_progress': 'in_progress',
         'in-progress': 'in_progress', 'deferred': 'deferred'}
def parse_rows(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r'- \\[(.)\\] (\\S+) \\| (.*)', line)
        if m:
            mark, bid, title = m.groups()
            if mark not in MARKS:
                continue
            rows.append({'id': bid, 'title': title, 'status': MARKS[mark]})
            continue
        m = re.match(r'- (\\S+) (\\S+): (.*)', line)
        if m:
            word, bid, title = m.groups()
            if word not in WORDS:
                continue
            rows.append({'id': bid, 'title': title, 'status': WORDS[word]})
    return rows
""",
)

put(
    "h13",
    "mpatch.py",
    """import copy
def merge_patch(target, patch):
    t = copy.deepcopy(target)
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    def apply(node, p):
        for k, v in p.items():
            if v is None:
                node.pop(k, None)
            elif isinstance(v, dict) and isinstance(node.get(k), dict):
                apply(node[k], v)
            else:
                node[k] = copy.deepcopy(v)
    apply(t, patch)
    return t
""",
)

put(
    "h14",
    "hist.py",
    """def bucket_bounds(base, n):
    return [base ** i for i in range(n + 1)]
def assign(v, bounds):
    if v < bounds[0] or v > bounds[-1]:
        return -1
    for i in range(len(bounds) - 1):
        if bounds[i] <= v < bounds[i + 1]:
            return i
    return len(bounds) - 2
""",
)

put(
    "h15",
    "pmap.py",
    """from concurrent.futures import ThreadPoolExecutor
def pmap(fn, items, limit):
    items = list(items)
    out = [None] * len(items)
    with ThreadPoolExecutor(max_workers=limit) as ex:
        futs = {ex.submit(fn, x): i for i, x in enumerate(items)}
        try:
            for fut, i in futs.items():
                out[i] = fut.result()
        except BaseException:
            for fut in futs:
                fut.cancel()
            raise
    return out
""",
)

put(
    "h16",
    "cronx.py",
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
    for _ in range(525600 * 2 + 100):
        if t.minute in mins and t.hour in hours:
            return t
        t += timedelta(minutes=1)
    raise ValueError('no fire time')
""",
)

print("fixes written")
