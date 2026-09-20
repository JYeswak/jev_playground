#!/usr/bin/env python3
"""UNIT 3 skills-vein: SEQUENCE-window measurement over the toolCall stream.

PREREGISTERED (written before measuring; choosing the window after seeing the
rate is fitting the predicate to the answer):
  WINDOW = one whole session. Justification: the envisioned rule fires once
    per session-task ("you are doing X, read skill S"), so session grain
    matches the rule's firing grain. Turn-grain windows are a named
    follow-up, not measured here.
  Per session S, over its ORDERED toolCall stream (assistant toolCall items):
    READ(s): a read toolCall whose arguments.path contains skill name s AND
      contains "skill" (case-insensitive). D6-compatible ("SKILL in path"),
      attributed per skill. skill:// URIs satisfy this.
    WORK(s): >=K toolCalls in S whose arguments blob matches s's name tokens
      (whole-word, case-insensitive; hyphen and space variants) AND which are
      not themselves reads of s. K=5 preregistered: below 5 is a glance,
      not "substantial work".
    FIRE(s): WORK(s) AND NOT READ(s) at ANY position in S (generous to the
      negative: a read anywhere in-session counts as consulted; fail-safe
      toward REFUSE).
  Session fires if any s fires. Denominator: working sessions (>=5 total
  toolCalls). Rate = firing sessions / working sessions.
  REFUSE if rate > 5% (wallpaper). REFUSE if firing sessions < 50 (floor).
  REFUSE if top single skill > 50% of fires (concentration; precedent:
    claim-verb 73%). Else seeded hand-label n=20 (seed 20260920), judged as
  ROUTING.
  RETIRE-CONDITION if shipped: 30-day window under 50 occurrences.
  D6 replication reported as sanity check (expect ~=1267 reads / ~206
  sessions, drift quoted).

Corpus: all *.jsonl under /Users/josh/.omp. File count + timestamp quoted.
NO-CLAIM: a read in an EARLIER session does not transfer; cross-session
consultation is invisible here. Mapping is naive dirname tokens (same
vocabulary as UNIT 2) applied to tool ARGS not prose; generic-name noise is
the hypothesis under test, not a surprise.
"""

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone

OMP_ROOT = "/Users/josh/.omp"
SKILLS_ROOT = "/Users/josh/.claude/skills"
K = 5
SEED = 20260920

NON_SKILL = {
    ".bundled_manifest",
    ".ripwire-manifest-v1",
    ".curator_state",
    ".curator_backups",
    ".system",
}

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

names = []
for entry in sorted(os.listdir(SKILLS_ROOT)):
    if entry.startswith(".") or entry in NON_SKILL:
        continue
    names.append(entry)
print(f"skills_on_disk={len(names)} K={K} ts={ts}")

# one combined pattern: variant -> skill. normalize spaces to hyphens to key.
variant_to_skill = {}
alts = []
collisions = 0
for n in names:
    for v in {n.lower(), n.lower().replace("-", " ")}:
        if len(v) < 3:
            continue
        alts.append(v)
        key = v.replace(" ", "-")
        if key in variant_to_skill and variant_to_skill[key] != n:
            collisions += 1
            continue
        variant_to_skill[key] = n
alts.sort(key=len, reverse=True)
big = re.compile(
    r"(?<![a-z0-9])(?:" + "|".join(re.escape(a) for a in alts) + r")(?![a-z0-9])"
)
print(f"variants={len(alts)} collisions={collisions}")

files = []
for dirpath, _d, filenames in os.walk(OMP_ROOT):
    for fn in filenames:
        if fn.endswith(".jsonl"):
            files.append(os.path.join(dirpath, fn))
print(f"corpus_files={len(files)}")

working = 0
firing_sessions = 0
fire_skill = Counter()
d6_reads = 0
d6_sessions = 0
toolcalls_total = 0
errors = 0
for fp in sorted(files):
    calls = []  # (name, argsblob, path)
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
                    args = c.get("arguments") or {}
                    blob = json.dumps(args, sort_keys=True).lower()
                    calls.append((str(c.get("name") or "").lower(), blob))
    except OSError:
        errors += 1
        continue
    toolcalls_total += len(calls)
    if len(calls) < 5:
        continue
    working += 1
    # D6 replication: read calls with skill in path
    sess_reads = 0
    read_skills = set()
    for name, blob in calls:
        if name != "read":
            continue
        m = re.search(r'"path"\s*:\s*"([^"]*)', blob)
        path = m.group(1) if m else ""
        if "skill" not in path:
            continue
        sess_reads += 1
        for hit in big.findall(path):
            sk = variant_to_skill.get(hit.replace(" ", "-"))
            if sk:
                read_skills.add(sk)
    if sess_reads:
        d6_reads += sess_reads
        d6_sessions += 1
    # WORK per skill over non-skill-read calls
    work = Counter()
    for name, blob in calls:
        if name == "read" and "skill" in blob:
            continue
        for hit in set(big.findall(blob)):
            sk = variant_to_skill.get(hit.replace(" ", "-"))
            if sk:
                work[sk] += 1
    fired = {s for s, c in work.items() if c >= K and s not in read_skills}
    if fired:
        firing_sessions += 1
        for s in fired:
            fire_skill[s] += 1

rate = (firing_sessions / working * 100) if working else 0.0
print(
    f"toolcalls={toolcalls_total} working_sessions={working} "
    f"firing_sessions={firing_sessions} rate={rate:.4f}% read_errors={errors}"
)
print(f"D6_replication: skill_path_reads={d6_reads} sessions={d6_sessions}")
print(f"distinct_skills_fired={len(fire_skill)}")
print("top_fire_skills=" + json.dumps(fire_skill.most_common(10)))
if fire_skill:
    t1 = fire_skill.most_common(1)[0][1]
    print(f"top1_skill_share={t1 / firing_sessions * 100:.1f}%")

if firing_sessions < 50:
    print("VERDICT=REFUSE floor: fewer than 50 firing sessions")
elif rate > 5.0:
    print("VERDICT=REFUSE wallpaper: rate above 5 percent")
elif fire_skill and (fire_skill.most_common(1)[0][1] / firing_sessions > 0.5):
    print("VERDICT=REFUSE concentration: top skill above 50 percent")
else:
    print("VERDICT=MEASURE-PASS inside bars; needs seeded FP label")
