#!/usr/bin/env python3
"""UNIT 3b Jev pilot BUILD: sample sessions, shortlist skills, build states.

PREREGISTERED (before running):
  SAMPLE: 40 sessions, uniform without replacement from firing sessions
    (sessions with >=1 fired skill under UNIT-3 predicate), seed 20260920.
  SHORTLIST: per sampled session, top 3 fired skills by work_count
    (<=120 pairs). Skills with no SKILL.md description are excluded and
    counted (nodesc_excluded) -- a state needs the description to judge.
  STATE per pair: request (first user text, <=500 chars) + ordered tool
    names (<=60) + files/paths touched (<=20, each <=80 chars) + skill name
    + skill description (frontmatter description: else first paragraph,
    <=300 chars) + work_count.
  LABELS (next step, by hand, all judged pairs): relevant/irrelevant from
    summary + description. Fallback if pairs exceed 120: seeded n=40 subset
    (seed 20260920) -- not expected; cap arithmetic gives <=120.
  BUDGET (stated before spending, live step later): 40 sessions x <=3 =
    <=120 Noul calls, live lane, offline fake-asker wiring test first.
  COMPARISON (identical rows): Jev-positive precision at pane-4 threshold
    vs naive-positive precision (= label rate on shortlist, since every
    shortlisted row is naive-positive by construction). Recall is NOT
    measured (negatives unlabeled) -- NO-CLAIM carried.
  NO-CLAIM carried forward: cross-session consultation invisible; a read in
    an earlier session does not transfer, so unread counts overcount. Report
    read_any_skill per pair to bound the habit direction (not the transfer).
"""

import json
import os
import random
import re
from collections import Counter
from datetime import datetime, timezone

OMP_ROOT = "/Users/josh/.omp"
SKILLS_ROOT = "/Users/josh/.claude/skills"
SEED = 20260920
N_SESSIONS = 40
TOPK = 3
K = 5
OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "skills-jev-pilot-pairs-20260920.jsonl"
)

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

variant_to_skill = {}
alts = []
for n in names:
    for v in {n.lower(), n.lower().replace("-", " ")}:
        if len(v) < 3:
            continue
        alts.append(v)
        key = v.replace(" ", "-")
        if key not in variant_to_skill:
            variant_to_skill[key] = n
alts.sort(key=len, reverse=True)
big = re.compile(
    r"(?<![a-z0-9])(?:" + "|".join(re.escape(a) for a in alts) + r")(?![a-z0-9])"
)


def skill_desc(n):
    # BUGFIX 2026-09-20 (before any labels or Jev calls): the first version
    # accepted a frontmatter `description: >-` with an empty body as the
    # literal description ">-", leaving pairs with no usable description.
    # Spec intent was "real description else first paragraph". Strip the
    # frontmatter block, take a non-empty description: field, else the first
    # non-heading body paragraph. Sample/shortlist logic untouched.
    p = os.path.join(SKILLS_ROOT, n, "SKILL.md")
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            text = fh.read(4000)
    except OSError:
        return None
    body = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)
    for m in re.finditer(r"^description\s*:\s*(.+)$", body, re.M | re.I):
        v = m.group(1).strip()
        if v and v not in (">-", ">", ">+", "|", "|-", "|+"):
            return v[:300]
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("---"):
            return s[:300]
    return None


descs = {n: skill_desc(n) for n in names}
nodesc = sorted(n for n, d in descs.items() if not d)
print(f"skills={len(names)} nodesc={len(nodesc)} ts={ts}")

files = []
for dirpath, _d, filenames in os.walk(OMP_ROOT):
    for fn in filenames:
        if fn.endswith(".jsonl"):
            files.append(os.path.join(dirpath, fn))
print(f"corpus_files={len(files)}")

# pass 1: firing sessions + per-session fired skills (UNIT-3 predicate)
firing = {}
for fp in sorted(files):
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
                    if isinstance(c, dict) and c.get("type") == "toolCall":
                        args = c.get("arguments") or {}
                        calls.append(
                            (
                                str(c.get("name") or "").lower(),
                                json.dumps(args, sort_keys=True).lower(),
                            )
                        )
    except OSError:
        continue
    if len(calls) < 5:
        continue
    read_skills = set()
    for name, blob in calls:
        if name != "read" or "skill" not in blob:
            continue
        m = re.search(r'"path"\s*:\s*"([^"]*)', blob)
        path = m.group(1) if m else ""
        if "skill" not in path:
            continue
        for hit in big.findall(path):
            sk = variant_to_skill.get(hit.replace(" ", "-"))
            if sk:
                read_skills.add(sk)
    work = Counter()
    for name, blob in calls:
        if name == "read" and "skill" in blob:
            continue
        for hit in set(big.findall(blob)):
            sk = variant_to_skill.get(hit.replace(" ", "-"))
            if sk:
                work[sk] += 1
    fired = {s: work[s] for s in work if work[s] >= K and s not in read_skills}
    if fired:
        firing[fp] = fired
print(f"firing_sessions={len(firing)}")

rng = random.Random(SEED)
sampled = rng.sample(sorted(firing), min(N_SESSIONS, len(firing)))
print(f"sampled={len(sampled)} seed={SEED}")


def summarize(fp):
    request, tools, paths = "", [], []
    seen_paths = set()
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
                role = msg.get("role")
                for c in msg.get("content") or []:
                    if not isinstance(c, dict):
                        continue
                    if role == "user" and c.get("type") == "text" and not request:
                        request = c.get("text", "")[:500]
                    if role == "assistant" and c.get("type") == "toolCall":
                        tools.append(str(c.get("name") or ""))
                        args = c.get("arguments") or {}
                        for key in ("path", "command", "file", "dir"):
                            v = args.get(key)
                            if isinstance(v, str) and v not in seen_paths:
                                seen_paths.add(v)
                                if len(paths) < 20:
                                    paths.append(v[:80])
    except OSError:
        pass
    return request, tools[:60], paths


pairs = []
excluded = 0
for fp in sampled:
    top = sorted(firing[fp].items(), key=lambda kv: -kv[1])[:TOPK]
    request, tools, paths = summarize(fp)
    for skill, wc in top:
        if not descs.get(skill):
            excluded += 1
            continue
        pairs.append(
            {
                "session": os.path.basename(fp),
                "skill": skill,
                "work_count": wc,
                "request": request,
                "tools": tools,
                "paths": paths,
                "skill_desc": descs[skill],
            }
        )

with open(OUT, "w", encoding="utf-8") as fh:
    for p in pairs:
        fh.write(json.dumps(p, sort_keys=True) + "\n")
print(f"pairs={len(pairs)} nodesc_excluded={excluded} out={OUT}")
