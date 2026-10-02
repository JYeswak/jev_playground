import json

dev = [json.loads(l) for l in open("work/zezf/h3h4dev.jsonl") if l.strip()]
for d in ["h3", "h4"]:
    sub = [r for r in dev if r["design"] == d]
    print(d, "n=%d" % len(sub))
    best = None
    for cut in [round(x * 0.02, 2) for x in range(0, 51)]:
        if d == "h3":
            pred = ["long" if (r.get("noul") or 0) >= cut else "short" for r in sub]
        else:
            pred = ["long" if (r.get("p_long") or 0) >= cut else "short" for r in sub]
        tp = sum(1 for p, r in zip(pred, sub) if p == "long" and r["label"] == "pos")
        fn = sum(1 for p, r in zip(pred, sub) if p == "short" and r["label"] == "pos")
        fp = sum(1 for p, r in zip(pred, sub) if p == "long" and r["label"] == "neg")
        tn = sum(1 for p, r in zip(pred, sub) if p == "short" and r["label"] == "neg")
        sens = tp / (tp + fn) if tp + fn else 0
        spec = tn / (tn + fp) if tn + fp else 0
        j = sens + spec - 1
        if (
            best is None
            or j > best[0] + 1e-9
            or (abs(j - best[0]) < 1e-9 and cut < best[1])
        ):
            best = (j, cut, sens, spec)
    print(
        "  Youden argmax: cut=%.2f J=%.4f sens=%.3f spec=%.3f"
        % (best[1], best[0], best[2], best[3])
    )
