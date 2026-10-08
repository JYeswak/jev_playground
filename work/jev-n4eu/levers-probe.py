import json
from collections import Counter

rows = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/gate-observe.jsonl")
    if line.strip()
]
bad = [r for r in rows if "nonauth" in str(r.get("error", "")).lower() or "unauth" in str(r.get("error", "")).lower() or " 40" in str(r.get("error", ""))]
print("auth rows:", len(bad))
hours = Counter(r.get("ts", "")[:13] for r in bad)
print(hours.most_common(6))
if bad:
    print("latest:", max(r.get("ts", "") for r in bad))
cap = [r for r in rows if r.get("error") == "NOT_RUN reason=daily-cap"]
print("cap by day:", Counter(r.get("ts", "")[:10] for r in cap))
unc = [r for r in rows if (r.get("error") or "").startswith("NOT_RUN reason=unconfigured")]
print("unconfigured by day:", Counter(r.get("ts", "")[:10] for r in unc))
