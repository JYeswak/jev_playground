import json
import subprocess
from datetime import datetime

IDS = [36956512317, 36956490063, 36957221975, 36960806376, 36960815329]
walls = []
for r in IDS:
    p = subprocess.run(
        ["gh", "run", "view", str(r), "--json", "jobs"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    d = json.loads(p.stdout)
    info = {}
    for j in d.get("jobs", []):
        n = j.get("name")
        try:
            s = datetime.fromisoformat(j["startedAt"].replace("Z", "+00:00"))
            e = datetime.fromisoformat(j["completedAt"].replace("Z", "+00:00"))
            info[n] = (round((e - s).total_seconds()), j.get("conclusion"))
        except Exception:
            info[n] = ("?", j.get("conclusion"))
    print(r, info)
    mx = max((v[0] for v in info.values() if isinstance(v[0], int)), default=0)
    tot = sum(v[0] for v in info.values() if isinstance(v[0], int))
    walls.append((mx, tot))
import statistics

print(
    "wall median:", statistics.median(w[0] for w in walls), sorted(w[0] for w in walls)
)
print(
    "runner-sec median:",
    statistics.median(w[1] for w in walls),
    sorted(w[1] for w in walls),
)
