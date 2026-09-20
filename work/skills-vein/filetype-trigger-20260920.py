#!/usr/bin/env python3
"""File-type trigger + noise budget for per-type ROUTING rules.

PREREGISTERED BAR (written before the ranking is seen):
  A once-per-session routing rule is acceptable at ANY fire rate IF its
  content is specific enough to change an action, and unacceptable at ANY
  rate if it is generic advice. The test is the TEXT, not the rate: the
  text must name a TOOL, a COMMAND, or a CHECK the reader would otherwise
  skip. Generic advice ("write clean code", "test your changes") fails at
  2% and at 60% alike.
  Why different from the 5% defect bar: a DEFECT rule asserts "you made a
  mistake" on every fire, so each false fire is a false accusation and
  precision is the axis (brief step 6). A ROUTING rule fires once per
  session and points (brief: KIND routing, precision not its axis); its
  cost is one attention tax per session and its value is one
  otherwise-skipped action. Rate still matters as BUDGET context: a type
  touched in 60% of sessions spends reader attention constantly, so its
  content must clear the bar by more; a type at 2% is dead weight unless
  its threads are uniquely valuable. Rate prioritizes and retires; only
  the content test ships or kills.
  RETIRE-CONDITION per type: threads-per-type never materialize from P2,
  or the text degrades to generic advice on review.

MEASURE (this script):
  Corpus: all *.jsonl under /Users/josh/.omp (count + timestamp quoted).
  Considered calls: assistant toolCall items with name in {edit, write}
    exactly (other mutating names, if any, reported as a limit, not added).
  Type: lowercase suffix after the final dot of the path basename, from
    arguments.path else arguments.file; no-dot files bucket as <noext>
    with top basenames listed separately.
  A session touches T if >=1 edit/write call carries T.
  Denominator: sessions with >=1 toolCall of any kind (a session with no
    calls cannot fire). Raw file count also reported.
  Output: ranking ext -> sessions + pct of denominator.
  Nomination (judgment on the ranking, next step): 3-5 types to carry
    rules first. No rule text is written here.
NO-CLAIM: edit/write tool names are the harness surface today; other
  writers (apply_patch-style, computer actions) are not counted.
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

OMP_ROOT = "/Users/josh/.omp"
MUTATING = {"edit", "write"}

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

files = []
for dirpath, _d, filenames in os.walk(OMP_ROOT):
    for fn in filenames:
        if fn.endswith(".jsonl"):
            files.append(os.path.join(dirpath, fn))
print(f"corpus_files={len(files)} ts={ts}")

sessions_any = 0
type_sessions = Counter()
noext_names = Counter()
tool_names = Counter()
edit_write_calls = 0
nopath_keys = Counter()
device_paths = Counter()

for fp in sorted(files):
    seen_any = False
    seen_types = set()
    try:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") != "message":
                    continue
                msg = obj.get("message") or {}
                if msg.get("role") != "assistant":
                    continue
                for c in msg.get("content") or []:
                    if not isinstance(c, dict) or c.get("type") != "toolCall":
                        continue
                    name = str(c.get("name") or "").lower()
                    if not name:
                        continue
                    seen_any = True
                    tool_names[name] += 1
                    if name not in MUTATING:
                        continue
                    args = c.get("arguments") or {}
                    path = args.get("path") or args.get("file") or ""
                    if not isinstance(path, str) or not path:
                        seen_types.add("<nopath>")
                        nopath_keys[tuple(sorted(str(k) for k in args.keys()))] += 1
                        continue
                    # BUGFIX 2026-09-20 (before any nomination): "://" paths are
                    # harness devices (xd://report_issue, xd://recall, MCP
                    # routes), not file types. Counted separately, excluded.
                    if "://" in path:
                        device_paths[path.split("://")[0]] += 1
                        continue
                    edit_write_calls += 1
                    base = path.rsplit("/", 1)[-1]
                    if "." in base:
                        seen_types.add("." + base.rsplit(".", 1)[-1].lower())
                    else:
                        seen_types.add("<noext>")
                        noext_names[base.lower()] += 1
    except OSError:
        continue
    if seen_any:
        sessions_any += 1
    for t in seen_types:
        type_sessions[t] += 1

print(f"sessions_with_calls={sessions_any} edit_write_calls={edit_write_calls}")
print("ranking (sessions, pct of sessions_with_calls):")
for ext, n in type_sessions.most_common(40):
    print(f"  {ext:12s} {n:5d} {n / sessions_any * 100:6.2f}%")
print("top_noext_basenames=" + json.dumps(noext_names.most_common(15)))
print("top_tool_names=" + json.dumps(tool_names.most_common(15)))
print("nopath_argkeys=" + json.dumps([list(k) for k, v in nopath_keys.most_common(10)]))
print("device_paths=" + json.dumps(dict(device_paths)))
mut = {
    k: v
    for k, v in tool_names.items()
    if ("edit" in k or "write" in k or "patch" in k or "apply" in k)
    and k not in MUTATING
}
print("other_mutating_names=" + json.dumps(mut))
