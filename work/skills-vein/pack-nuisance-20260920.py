#!/usr/bin/env python3
"""Pack nuisance: FIRE rate (scope-exact) + BIND sample build.

PREREGISTERED DECISION RULE (before measuring either number):
  BIND-WHOLE (fraction of sampled real edits where ANY clause of that
  type's doctrine would actually have applied):
    bind >= 40% -> KEEP the rule whole.
    20% <= bind < 40% -> NARROW: cut every clause binding <10% on its own.
    bind < 20% -> CUT the rule or redesign the trigger (conductor instinct
    ~20% adopted as the cut line).
  Defense: a once-per-session injection costs one attention tax per firing
  session; its expected value is fire_rate x bind_rate sessions helped.
  At .md fire 21% x bind 40% ~= 8% of sessions helped per injection. Below
  20% bind the rule mostly spends attention to restate doctrine at work
  that needs none of it -- the firing-is-not-applying noise. A clause
  under 10% bind is dead weight inside a 12-line context budget: cut it,
  do not defend the pack whole. Thresholds REPORTED for Jev at
  t in {0.5,0.7,0.9}, never selected here.
  BUDGET: 3 types x 25 edits = 75 hand labels (all rows) + <=75 live Noul
  calls, model jev-1.13.0, offline fake proof first.

FIRE (part A): per rule file, parse scope globs from its frontmatter and
  match with fnmatch (measured 2026-09-20: omp scope `*.rs` fires on bare,
  nested-relative, and absolute paths; edit with NO path stays quiet).
  Session fires if >=1 edit/write call carries a matching path. Denominator:
  sessions with >=1 toolCall of any kind. Edit-tool pathless calls are
  invisible to scope matching -- counted in NO-CLAIM, excluded from fire.
BIND sample (part B): 25 real edit/write calls per type, uniform without
  replacement over matching calls, seed 20260920. Artifact excerpt = path
  + up to 2000 chars of args input/content. Clause attribution comes from
  hand labels only (Jev judges any-bind: one Noul per row).
NO-CLAIM: hand labels are one labeller (me); Jev-vs-me agreement is a
  by-product, not validation; recall unmeasured; cross-session transfer
  invisible as before.
"""

import fnmatch
import json
import os
import random
import re
from collections import Counter
from datetime import datetime, timezone

OMP_ROOT = "/Users/josh/.omp"
RULES = {
    "rs": "/Users/josh/.agents/rules/ft-rs-doctrine.md",
    "sh": "/Users/josh/.agents/rules/ft-sh-doctrine.md",
    "md": "/Users/josh/.agents/rules/ft-md-doctrine.md",
}
SEED = 20260920
N_PER_TYPE = 25
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pack-nuisance-binds-20260920.jsonl")

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_scope(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read(800)
    m = re.search(r"^scope:\s*(.+)$", text, re.M)
    specs = []
    for part in m.group(1).split(","):
        part = part.strip()
        mm = re.match(r"tool:(\w+)\((.+)\)", part)
        if mm:
            specs.append((mm.group(1).lower(), mm.group(2)))
    return specs


scopes = {t: parse_scope(p) for t, p in RULES.items()}
print(f"scopes={scopes} ts={ts}")

files = []
for dirpath, _d, filenames in os.walk(OMP_ROOT):
    for fn in filenames:
        if fn.endswith(".jsonl"):
            files.append(os.path.join(dirpath, fn))
print(f"corpus_files={len(files)}")

sessions_any = 0
fire_sessions = Counter()
candidates = {t: [] for t in RULES}  # (fp, path, excerpt)

for fp in sorted(files):
    seen_any = False
    fired = set()
    calls = []
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
                    args = c.get("arguments") or {}
                    path = args.get("path") or args.get("file") or ""
                    if not isinstance(path, str):
                        path = ""
                    calls.append((name, path, args))
    except OSError:
        continue
    if seen_any:
        sessions_any += 1
    for name, path, args in calls:
        if not path:
            continue
        for t, specs in scopes.items():
            for tool, glob in specs:
                if name == tool and fnmatch.fnmatch(path, glob):
                    fired.add(t)
                    blob = json.dumps(args, sort_keys=True)
                    excerpt = (path + "\n" + blob)[:2000]
                    candidates[t].append((fp, path, excerpt))
                    break
    for t in fired:
        fire_sessions[t] += 1

print(f"sessions_with_calls={sessions_any}")
for t in RULES:
    n = fire_sessions[t]
    print(
        f"FIRE-{t}: sessions={n} rate={n / sessions_any * 100:.2f}% "
        f"candidate_calls={len(candidates[t])}"
    )

rng = random.Random(SEED)
sampled = {}
for t in RULES:
    pool = candidates[t]
    k = min(N_PER_TYPE, len(pool))
    sampled[t] = rng.sample(pool, k) if pool else []
    print(f"SAMPLE-{t}: {len(sampled[t])} seed={SEED}")

rows = []
for t in RULES:
    for fp, path, excerpt in sampled[t]:
        rows.append(
            {
                "type": t,
                "session": os.path.basename(fp),
                "path": path[:160],
                "excerpt": excerpt,
            }
        )
with open(OUT, "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, sort_keys=True) + "\n")
print(f"rows={len(rows)} out={OUT}")
