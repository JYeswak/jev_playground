import json
from collections import Counter

rows = [json.loads(l) for l in open("var/agent-tmp/d8.receipt.jsonl") if l.strip()]
print("rows:", len(rows), Counter(r.get("status") for r in rows))


def pred(r):
    if r.get("status") == "no-call":
        return "not-supported"
    c = r.get("choice")
    return "supported" if c == "supports" else "not-supported"


def gold(r):
    return "supported" if r["answer"] == "verified" else "not-supported"


ok = [r for r in rows if r.get("status") in ("ok", "no-call")]
acc = sum(1 for r in ok if pred(r) == gold(r)) / len(ok)
print(
    "accuracy: %d/%d = %.4f (bar 0.65)"
    % (sum(1 for r in ok if pred(r) == gold(r)), len(ok), acc)
)
print(
    "pred dist:",
    Counter(pred(r) for r in ok),
    "gold dist:",
    Counter(gold(r) for r in ok),
)
live = [r for r in rows if r.get("status") == "ok"]
print(
    "live-call acc: %d/%d = %.4f"
    % (
        sum(1 for r in live if pred(r) == gold(r)),
        len(live),
        sum(1 for r in live if pred(r) == gold(r)) / len(live),
    )
)
