import json

rows = [json.loads(l) for l in open("var/agent-tmp/eruw.live.jsonl") if l.strip()]
for cut in [0.5, 0.6, 0.7, 0.8, 0.9]:
    hi = [
        r for r in rows if (r.get("confidence") or 0) >= cut and r["choice"] != "none"
    ]
    ok = sum(1 for r in hi if r["choice"] == r["answer"])
    lo_abstain_rate = sum(1 for r in rows if (r.get("confidence") or 0) < cut) / len(
        rows
    )
    print(
        "conf>=%.1f: picks %d/%d=%.3f abstain-rate=%.3f"
        % (cut, ok, len(hi), ok / len(hi) if hi else 0, lo_abstain_rate)
    )
# what would gated accuracy be (pick iff conf>=cut else none)?
items = json.load(open("var/agent-tmp/eruw.items.json"))["test"]
for cut in [0.7, 0.8, 0.9]:
    ok = 0
    for r in rows:
        pred = r["choice"] if (r.get("confidence") or 0) >= cut else "none"
        if pred == r["answer"]:
            ok += 1
    print("gated-%.1f acc: %d/%d=%.4f" % (cut, ok, len(rows), ok / len(rows)))
