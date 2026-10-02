import json, re, sqlite3

con = sqlite3.connect("/Users/josh/Developer/jev/.beads/beads.db")
con.row_factory = lambda c, r: r
rows = con.execute(
    "SELECT issue_id, author, text FROM comments WHERE text LIKE '%non-author%'"
).fetchall()
print("non-author comments:", len(rows))
NUM = re.compile(r"\d+/\d+|\d+\.\d+|p\s*[=<]\s*[\d.e\-]+|\b\d{2,}%")
ART = re.compile(
    r"(?:[\w.\-]*\/)+[\w.\-]+\.\w+|\b[0-9a-f]{7,40}\b|\b369\d{7}\b|work\/[\w.\-\/]+|scripts\/[\w.\-\/]+|demos\/[\w.\-\/]+"
)
items = []
for issue, author, text in rows:
    t = text or ""
    tl = t.lower()
    if "verified" in tl or "holds" in tl or "exact" in tl or "match" in tl:
        v = "verified"
    elif (
        "differ" in tl
        or "fail" in tl
        or "mismatch" in tl
        or "does not hold" in tl
        or "red" in tl
    ):
        v = "refuted"
    else:
        continue
    nums = NUM.findall(t)
    arts = ART.findall(t)
    if nums and arts:
        m = NUM.search(t)
        s = max(0, m.start() - 200)
        items.append(
            {
                "bead": issue,
                "verdict": v,
                "claim": t[s : m.end() + 200].replace("\n", " ")[:500],
                "artifact": arts[0][:160],
                "numbers": nums[:4],
            }
        )
print("candidate items:", len(items))
from collections import Counter

print(Counter((i["bead"], i["verdict"]) for i in items).most_common(3))
print(Counter(i["verdict"] for i in items))
json.dump(items, open("var/agent-tmp/d8.items.json", "w"))
