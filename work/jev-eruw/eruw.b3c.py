import json

d = json.load(open("var/agent-tmp/eruw.items.json"))
for name in ("dev", "test"):
    items = d[name]
    n = len(items)
    ab = sum(1 for it in items if it["answer"] == "none") / n
    r1 = sum(1 for it in items if it["cands"][0][0] == it["answer"]) / n
    print("%s n=%d abstain=%.4f rank1always=%.4f" % (name, n, ab, r1))
    best = (ab, 1.0)
    for tau in [0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95]:
        ok = (
            sum(
                1
                for it in items
                if (
                    (it["cands"][0][0] if it["rank1j"] >= tau else "none")
                    == it["answer"]
                )
            )
            / n
        )
        if ok > best[0]:
            best = (ok, tau)
    print("  B3best=%.4f at tau=%s" % best)
