#!/usr/bin/env python3
"""jev-zbb1: semantic shortlist. Embeds skill name+description with local
nomic-embed-text (Ollama), cosine top-20 per prompt. Keyless/local.
Usage:
  shortlist.py --index [out]     embed roster -> vectors JSON
  shortlist.py --query [out]      dev prompts -> top-20 shortlists JSON
"""

import json
import math
import os
import sys
import urllib.request

OLLAMA = "http://127.0.0.1:11434/api/embeddings"
MODEL = "nomic-embed-text"
SKILLS = os.path.expanduser("~/.claude/skills")


def embed(text):
    req = urllib.request.Request(
        OLLAMA,
        data=json.dumps({"model": MODEL, "prompt": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["embedding"]


def roster():
    out = []
    for child in sorted(os.listdir(SKILLS)):
        p = os.path.join(SKILLS, child, "SKILL.md")
        if not os.path.isfile(p):
            continue
        text = open(p, encoding="utf-8", errors="ignore").read()
        name, desc = child, ""
        for line in text.split("\n"):
            if line.startswith("name:"):
                name = line[5:].strip().strip("\"'")
            elif line.startswith("description:"):
                desc = line[12:].strip().strip("\"'")
                break
        out.append({"name": name, "description": desc})
    return out


def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


if sys.argv[1] == "--index":
    ros = roster()
    vecs = [
        {"name": e["name"], "vec": embed(e["name"] + ": " + e["description"])}
        for e in ros
    ]
    json.dump({"model": MODEL, "skills": vecs}, open(sys.argv[2], "w"))
    print("indexed", len(vecs))
elif sys.argv[1] == "--query":
    idx = json.load(open("work/jev-zbb1/vectors.json"))
    dev = json.load(open("work/jev-zbb1/dev.jsonl"))
    res = []
    for row in dev:
        q = embed(row["prompt"][:2000])
        ranked = sorted(idx["skills"], key=lambda s: -cos(q, s["vec"]))
        res.append(
            {
                "id": row["id"],
                "shortlist": [s["name"] for s in ranked[:20]],
                "target_rank": next(
                    (i for i, s in enumerate(ranked) if s["name"] == row["target"]),
                    None,
                ),
            }
        )
    json.dump(res, open(sys.argv[2], "w"), indent=1)
    rec = sum(1 for r in res if r["target_rank"] is not None and r["target_rank"] < 20)
    print("recall@20: %d/%d" % (rec, len(res)))
