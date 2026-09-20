#!/usr/bin/env python3
"""UNIT 2 skills-vein: naive name-match ROUTING rule measurement. 2026-09-20.

PREREGISTERED BAR (written before measuring; method step 1):
  Candidate predicate: an assistant-text turn CONTAINS the name of a skill we
  own (skill-dir/entry name, hyphens-as-is or hyphens-as-spaces,
  case-insensitive). Mention count is a CEILING on fires of the real rule
  ("names a domain AND the skill was never read") — read-state is not visible
  from text, so fires <= mentions always.
  REFUSE if ceiling_total < 50 (occurrence floor; even perfect precision
    cannot ship a sub-floor class).
  REFUSE if ceiling_rate > 5% (wallpaper; naive version unshippable, and the
    ranker that could save it is blocked on skillranker issue #4).
  REFUSE if top single session holds > 50% of ceiling fires (concentration;
    precedent: claim-verb class refused at 73% single-session).
  Else: seeded hand-label n=20 for FP and judge as ROUTING (precision is not
    its axis; rate + concentration + retire-condition are).
  RETIRE-CONDITION if shipped: 30-day window under 50 occurrences.

Corpus: all *.jsonl under /Users/josh/.omp (assistant message text only).
Drift note: sessions write while measuring; file count + timestamp quoted.
Seed for any sample: 20260920.
"""

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

OMP_ROOT = "/Users/josh/.omp"
SKILLS_ROOT = "/Users/josh/.claude/skills"
SEED = 20260920

NON_SKILL = {
    ".bundled_manifest",
    ".ripwire-manifest-v1",
    ".curator_state",
    ".curator_backups",
    ".system",
}

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# --- skill names: entries on disk minus dotfiles/manifests ---
names = []
for entry in sorted(os.listdir(SKILLS_ROOT)):
    if entry.startswith(".") or entry in NON_SKILL:
        continue
    names.append(entry)
print(f"skills_on_disk={len(names)} ts={ts}")

# naive predicate arms: literal dirname, and hyphens-as-spaces variant
patterns = []
for n in names:
    variants = {n.lower(), n.lower().replace("-", " ")}
    for v in variants:
        if len(v) < 3:
            continue
        patterns.append(
            (n, re.compile(r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])"))
        )

# --- walk corpus ---
files = []
for dirpath, _dirnames, filenames in os.walk(OMP_ROOT):
    for fn in filenames:
        if fn.endswith(".jsonl"):
            files.append(os.path.join(dirpath, fn))
print(f"corpus_files={len(files)}")

turns = 0
fires = 0
per_skill = Counter()
per_session = Counter()
errors = 0
for fp in sorted(files):
    try:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            session_fire = 0
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
                texts = [
                    c.get("text", "")
                    for c in (msg.get("content") or [])
                    if isinstance(c, dict) and c.get("type") == "text"
                ]
                if not texts:
                    continue
                turns += 1
                blob = "\n".join(texts).lower()
                hit = set()
                for skill, rx in patterns:
                    if rx.search(blob):
                        hit.add(skill)
                if hit:
                    fires += 1
                    session_fire += 1
                    for s in hit:
                        per_skill[s] += 1
            if session_fire:
                per_session[fp] += session_fire
    except OSError:
        errors += 1

rate = (fires / turns * 100) if turns else 0.0
print(
    f"assistant_text_turns={turns} ceiling_fires={fires} rate={rate:.4f}% read_errors={errors}"
)
print(
    f"distinct_skills_mentioned={len(per_skill)} sessions_with_fires={len(per_session)}"
)
print("top_skills=" + json.dumps(per_skill.most_common(10)))
top_sess = per_session.most_common(5)
print("top_sessions=" + json.dumps([(os.path.basename(p), c) for p, c in top_sess]))
if per_session:
    top1 = per_session.most_common(1)[0][1]
    print(f"top1_session_share={top1 / fires * 100:.1f}%")

# --- verdict against the preregistered bar ---
if fires < 50:
    print("VERDICT=REFUSE floor: ceiling below 50 occurrences")
elif rate > 5.0:
    print("VERDICT=REFUSE wallpaper: ceiling rate above 5 percent")
elif per_session and (per_session.most_common(1)[0][1] / fires > 0.5):
    print("VERDICT=REFUSE concentration: top session above 50 percent")
else:
    print("VERDICT=MEASURE-PASS ceiling inside bars; needs seeded FP label")
