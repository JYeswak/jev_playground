import json, re, statistics

TOK = re.compile(r"[a-z0-9]+")
STOP = set(
    "the a an of to in on for and or is are was were be with from as at by that this it its into Milestone epic task bug chore docs feat fix test tests plan".lower().split()
)


def toks(s):
    return set(t for t in TOK.findall(s.lower())) - STOP


def jac(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


pairs = json.load(open("var/agent-tmp/eruw.pairs.json"))
org = [p for p in pairs if not p["grade_clone"]]
repos = sorted(set(p["repo"] for p in org))
# grouped split: alternate repos by pair count into dev/test
byrepo = {}
for p in org:
    byrepo.setdefault(p["repo"], []).append(p)
ordered = sorted(byrepo.items(), key=lambda kv: len(kv[1]), reverse=True)
dev_repos, test_repos = set(), set()
dn = tn = 0
for repo, ps in ordered:
    if dn <= tn:
        dev_repos.add(repo)
        dn += len(ps)
    else:
        test_repos.add(repo)
        tn += len(ps)
print(
    "dev repos:",
    len(dev_repos),
    "pairs:",
    dn,
    "test repos:",
    len(test_repos),
    "pairs:",
    tn,
)
# universes
unis = {}
for repo in repos:
    f = "/Users/josh/Developer/%s/.beads/issues.jsonl" % repo
    u = {}
    try:
        for line in open(f, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                x = json.loads(line)
            except Exception:
                continue
            if x.get("id") and x.get("title"):
                u[x["id"]] = {"title": x["title"], "status": x.get("status", "")}
    except Exception:
        continue
    unis[repo] = u
linked = set()
for p in org:
    linked.add((p["repo"], p["dup"]))
    linked.add((p["repo"], p["orig"]))
# negatives: high-jaccard non-linked pairs, 2 per positive per repo
import random

random.seed(13)
negs = []
for repo, ps in byrepo.items():
    u = unis[repo]
    ids = [i for i in u if (repo, i) not in linked]
    random.shuffle(ids)
    for p in ps:
        dt = toks(p["dup_title"])
        scored = []
        for i in ids:
            tt = toks(u[i]["title"])
            j = jac(dt, tt)
            if j >= 0.15:
                scored.append((j, i))
        scored.sort(reverse=True)
        for j, i in scored[:2]:
            negs.append(
                {
                    "repo": repo,
                    "dup": p["dup"],
                    "dup_title": p["dup_title"],
                    "cand": i,
                    "cand_title": u[i]["title"],
                    "jacc": round(j, 3),
                    "label": "none",
                }
            )
print("negatives:", len(negs))
json.dump(
    {"dev_repos": sorted(dev_repos), "test_repos": sorted(test_repos), "negs": negs},
    open("var/agent-tmp/eruw.split.json", "w"),
)
# tune tau on dev positives: rank1 jaccard distribution
for split, rs in (("dev", dev_repos), ("test", test_repos)):
    js = []
    for p in org:
        if p["repo"] not in rs:
            continue
        u = unis[p["repo"]]
        dt = toks(p["dup_title"])
        best = 0.0
        for i, e in u.items():
            if i == p["dup"]:
                continue
            best = max(best, jac(dt, toks(e["title"])))
        js.append(best)
    js.sort()
    print(
        split,
        "n=%d" % len(js),
        "jacc p10=%.3f p25=%.3f med=%.3f"
        % (js[len(js) // 10], js[len(js) // 4], statistics.median(js)),
    )
