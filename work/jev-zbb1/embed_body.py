import json, math, os, urllib.request


def embed(text):
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/embeddings",
        data=json.dumps({"model": "nomic-embed-text", "prompt": text[:3000]}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["embedding"]


def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


S = os.path.expanduser("~/.claude/skills")
vecs = []
for child in sorted(os.listdir(S)):
    p = os.path.join(S, child, "SKILL.md")
    if not os.path.isfile(p):
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    vecs.append((child, embed(child + "\n" + t[:2500])))
json.dump(
    {
        "model": "nomic-embed-text+body",
        "skills": [{"name": n, "vec": v} for n, v in vecs],
    },
    open("work/jev-zbb1/vectors_body.json", "w"),
)
dev = json.load(open("work/jev-zbb1/dev.jsonl"))
rec = 0
for row in dev:
    q = embed(row["prompt"][:2000])
    top = sorted(vecs, key=lambda nv: -cos(q, nv[1]))[:20]
    hit = row["target"] in [n for n, _ in top]
    rec += hit
    print(row["id"], row["target"], hit, flush=True)
print("body recall@20: %d/20" % rec)
