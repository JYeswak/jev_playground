#!/usr/bin/env python3
"""Recompute every README live-smoke cell (calls, same / differs / not compared) from each demo's
committed live-receipt.json rows against the demo's recorded lane, which this script runs keyless.

    python3 work/readme-stranger-run/live-cells.py            # print the table
    python3 work/readme-stranger-run/live-cells.py --write F  # also write it to F (markdown)

Rule: an item differs when any categorical decision the demo prints for it differs between the
lanes (route, action, verdict, pick, label); probabilities and scores alone never count. A demo is
"same" when no item differs, and "not compared" when the two lanes did not judge the same input.
Keyless and offline: the recorded lane makes no API call. Written for jev-lcf's successor unit;
it reads receipts, it never edits them."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_ENV = {
    k: v
    for k, v in os.environ.items()
    if k not in ("TYPESAFE_API_KEY", "JEV_API_KEY", "TYPE_SAFE_AI_KEY")
}
_CACHE = {}


def rc(d):
    return json.loads((ROOT / f"demos/{d}/live-receipt.json").read_text())


def fx(d):
    """The demo's recorded-lane output, run keyless."""
    if d not in _CACHE:
        p = subprocess.run(
            ["node", f"demos/{d}/demo.mjs"],
            cwd=ROOT,
            env=_ENV,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if p.returncode != 0:
            raise SystemExit(
                f"recorded lane of {d} exited {p.returncode}: {p.stderr[-300:]}"
            )
        _CACHE[d] = p.stdout + p.stderr
    return _CACHE[d]


out = {}

r = rc("guard")
f = {
    m[1]: m[0].strip().lower()
    for m in re.findall(r"^\[\s*(\S+)\s*\]\s+(\S+)", fx("guard"), re.M)
}
live = {row["name"]: row["action"] for row in r["rows"]}
out["guard"] = (r["calls"], {k: (f[k], live[k]) for k in live})

r = rc("rag")
f = {
    m[2]: (m[0], m[1])
    for m in re.findall(
        r"^(\S+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+(keep|drop)\s+(\S+)$",
        fx("rag"),
        re.M,
    )
}
f = {k: (v[0], v[1]) for k, v in f.items()}
live = {k: (v["route"], v["verdict"]) for k, v in r["passages"].items()}
out["rag"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("citation")
f = {}
for line in fx("citation").splitlines():
    p = line.split()
    if len(p) >= 5 and p[0] in r["claims"]:
        f[p[0]] = (p[2] if p[2] != "-" else None, p[-2], p[-1])
live = {
    k: (v.get("choice") or v.get("relation"), v["verdict"], v["action"])
    for k, v in r["claims"].items()
}
out["citation"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("skill-suggest")
order = ["music-video", "screencast-redact", "mastodon"]
picks = [m for m in re.findall(r"^suggest: (\S+)", fx("skill-suggest"), re.M)]
f = {k: (None if p == "nothing" else p) for k, p in zip(order, picks)}
live = {k: v["suggestion"] for k, v in r["tasks"].items()}
out["skill-suggest"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("chief")
f = {
    m[3]: (m[0], m[1])
    for m in re.findall(r"^(\w+)\s+(\w+)\s+([\d.]+)\s+(\S+)$", fx("chief"), re.M)
}
live = {k: (v["destination"], v["choice"]) for k, v in r["jobs"].items()}
out["chief"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("rerank")
f = {m[0]: m[1] for m in re.findall(r"\] (q\d) .*reranked-top=(\S+)", fx("rerank"))}
live = {k: v["ranked_top"] for k, v in r["queries"].items()}
out["rerank"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("date")
f = {}
for line in fx("date").splitlines():
    m = re.match(
        r"^(?:OK|XX) the (?:date (?:of )?)?(?:the )?(.+?)\s{2,}(\S+)\s+(\S+)\s+[\d.]+",
        line,
    )
    if m:
        f[m[1].strip()] = m[3]
live = {k: v["got"] for k, v in r["rows"].items()}


def fkey(k):
    for fk in f:
        if fk.endswith(k) or k.endswith(fk) or k in fk or fk in k:
            return fk
    raise KeyError(k)


out["date"] = (r["call_count"], {k: (f[fkey(k)], live[k]) for k in live})

r = rc("entity")
f = {
    m[0]: m[1]
    for m in re.findall(
        r"^(\S+)\s+score [\d.]+\s+confidence [\d.]+\s+->\s+(.+)$", fx("entity"), re.M
    )
}
live = {k: v["outcome"] for k, v in r["pairs"].items()}
out["entity"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("hierarchy")
f = {
    m[0]: (m[1], m[2])
    for m in re.findall(r"\] (\S+) greedy=(\S+) beam=(\S+)", fx("hierarchy"))
}
live = {k: (v["greedy"], v["beam"]) for k, v in r["docs"].items()}
out["hierarchy"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("autoformat")
m = re.search(r"joins=(\d+) blocks=(\d+)", fx("autoformat"))
out["autoformat"] = (
    r["call_count"],
    {"joins,blocks": ((int(m[1]), int(m[2])), (r["joins_live"], r["blocks_live"]))},
)

r = rc("semantic-find")
fv = re.findall(r"-> (ANSWER|no answer)", fx("semantic-find"))
fp = re.findall(r"points at (L\d+)", fx("semantic-find"))
f = {"answered": (fv[0], fp[0]), "unanswered": (fv[1], None)}
live = {
    "answered": (r["queries"]["answered"]["verdict"], r["queries"]["answered"]["best"]),
    "unanswered": (r["queries"]["unanswered"]["verdict"], None),
}
out["semantic-find"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("preparsed")
t = fx("preparsed")
g = lambda pat: re.search(pat, t).group(1)
f = {
    "receipt": g(r"receipt -> : (\S+)"),
    "sender": g(r"sender  -> : (\S+)"),
    "mobile": g(r"mobile  -> : (\(\d+\) [\d-]+)"),
    "region": g(r"country -> : (\S+)"),
    "e164": g(r"E\.164   -> : (\S+)"),
    "total": (
        g(r"total due : (\S+)"),
        re.search(r"total due : .*\((\w+),", t).group(1),
    ),
    "credit": (
        g(r"credit    : (\S+)"),
        re.search(r"credit    : .*\((\w+),", t).group(1),
    ),
}
e = r["extractions"]
live = {
    "receipt": e["receipt"]["choice"],
    "sender": e["sender"]["choice"],
    "mobile": e["mobile"]["choice"],
    "region": e["region"]["choice"],
    "e164": e["e164"],
    "total": (e["total"]["choice"], e["total"]["kind"]),
    "credit": (e["credit"]["choice"], e["credit"]["kind"]),
}
out["preparsed"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("compact")  # needs ./scripts/bootstrap-compaction.sh first, as the README says
f = {m[0]: m[1] for m in re.findall(r"^(t\d+) \| \w+ \| (\w+) \|", fx("compact"), re.M)}
live = {k: v["verdict"] for k, v in r["actions"].items()}
out["compact"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("parallel")
t = fx("parallel")
f = {
    m[0]: ("yes" if float(m[1]) > 0.5 else "no")
    for m in re.findall(r"(\w+)\s+\[noul\] noul=([\d.]+)", t)
}
f["instrument"] = re.search(r"instrument\s+\[choice\] choice=(\S+)", t).group(1)
a = r["answers"]
live = {
    k: ("yes" if v["noul"] > 0.5 else "no") for k, v in a.items() if v["type"] == "noul"
}
live["instrument"] = a["instrument"]["choice"]
out["parallel"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

r = rc("cascade")
f = {
    m[0]: m[1].lower()
    for m in re.findall(
        r"^\s+(\w+)\s+p_wrong=[\d.]+ (pass|ESCALATE)", fx("cascade"), re.M
    )
}
live = {
    k: ("escalate" if v > r["threshold"] else "pass") for k, v in r["heads"].items()
}
out["cascade"] = (r["call_count"], {k: (f[k], live[k]) for k in live})

for d in ("consistency", "consistency-noul"):
    r = rc(d)
    src = (ROOT / f"demos/{d}/demo.mjs").read_text()
    st = re.search(r"state: (\{[^}]*\})", src).group(1)
    out[d] = (r["call_count"], None, st)

lines = [
    "| demo | calls | verdict | items that differ (fixture -> live) |",
    "|---|---:|---|---|",
]
tally = {"differs": 0, "same": 0, "not compared": 0}
counts = []
for d, v in out.items():
    calls, items = v[0], v[1]
    counts.append(calls)
    if items is None:
        tally["not compared"] += 1
        lines.append(
            f"| {d} | {calls} | not compared | live state is `{v[2].split(',')[0]} }}` only: the post or claim text the fixture judged is never sent |"
        )
        continue
    diff = {k: p for k, p in items.items() if p[0] != p[1]}
    n = len(items)
    if diff:
        tally["differs"] += 1
        verdict = f"differs, {n - len(diff)} of {n} same"
    else:
        tally["same"] += 1
        verdict = f"same, {n} of {n}"
    note = "; ".join(f"{k}: {p[0]} -> {p[1]}" for k, p in diff.items()).replace(
        "|", "/"
    )
    lines.append(f"| {d} | {calls} | {verdict} | {note or '-'} |")
lines.append("")
lines.append(
    f"Recomputed here: {len(out)} demos, {tally['differs']} differ, {tally['same']} same, {tally['not compared']} not compared; call counts range {min(counts)} to {max(counts)} calls."
)
text = "\n".join(lines) + "\n"
print(text, end="")
if "--write" in sys.argv:
    Path(sys.argv[sys.argv.index("--write") + 1]).write_text(text)
