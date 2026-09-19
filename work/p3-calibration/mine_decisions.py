"""Mine dcg bridge decisions + outcomes from omp sessions (OFFLINE, read-only).

Decision row: {"type":"custom","customType":"com.zeststream.omp-dcg-bridge.decision.v1",
  "data":{"kind":"dcg_allow"|"dcg_block","toolCallId":...}} — unspaced keys only
  (the spaced form `"kind" :` matches zero decision rows; other spaced `"kind":`
  hits are non-decision custom rows, verified 2026-09-19).
Join key is the SESSION DIR (calls, results and decisions for one tool often
live in different files of the same session).

OUTCOME PREDICATE (stated verbatim, mechanical, no taste):
  BAD iff the matching toolResult has isError true, OR any of the next 3 user
  messages after the decision matches /(revert|undo that|you broke|not what I
  asked|wrong command|stop doing|that broke|start over|didn't work|did not
  work)/i -- causal phrasing only; bare "failed|wrong|stop" proved ambient
  (59k of 62k BAD under the lax version).
REVERT = re.compile(r"revert|undo that|you broke|not what I asked|wrong command|stop doing|that broke|start over|didn't work|did not work",
                    re.IGNORECASE)
Blocked commands never execute: counted, never scored.
Usage: python mine_decisions.py  (writes decisions_full.jsonl locally + stats)
"""

import glob
import json
import os
import re
from collections import Counter, defaultdict

HOME = os.path.expanduser("~")
REVERT = re.compile(
    r"revert|undo|wrong|stop|don't|do not|not that|broken|didn't work|failed",
    re.IGNORECASE,
)


def iter_rows():
    for f in sorted(
        glob.glob(HOME + "/.omp/profiles/*/agent/sessions/*/*/*.jsonl")
        + glob.glob(HOME + "/.omp/profiles/*/agent/sessions/*/*/*.log")
        + glob.glob(HOME + "/.omp/profiles/*/agent/sessions/*/*.jsonl")
        + glob.glob(HOME + "/.omp/profiles/*/agent/sessions/*/*.log")
    ):
        with open(f, errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                yield f, os.path.dirname(f), r


def main():
    calls, users, decisions = {}, defaultdict(list), []
    n_files = set()
    for f, sdir, r in iter_rows():
        n_files.add(f)
        if r.get("customType") == "com.zeststream.omp-dcg-bridge.decision.v1":
            d = r.get("data", {})
            decisions.append(
                {
                    "sdir": sdir,
                    "ts": r.get("timestamp", ""),
                    "kind": d.get("kind"),
                    "tid": d.get("toolCallId"),
                }
            )
            continue
        m = r.get("message")
        if not isinstance(m, dict):
            continue
        if m.get("role") == "assistant":
            for p in m.get("content") or []:
                if isinstance(p, dict) and p.get("type") == "toolCall" and p.get("id"):
                    calls[(sdir, p["id"])] = {
                        "tool": p.get("name", "?"),
                        "args": json.dumps(p.get("arguments", {}))[:400],
                    }
        elif m.get("role") == "toolResult" and m.get("toolCallId"):
            key = (sdir, m["toolCallId"])
            calls.setdefault(key, {})["isError"] = bool(m.get("isError"))
        elif m.get("role") == "user":
            txt = "\n".join(
                p.get("text", "")
                for p in m.get("content") or []
                if isinstance(p, dict) and p.get("type") == "text"
            )
            users[sdir].append((r.get("timestamp", ""), txt))

    def find_call(sdir, tid):
        if (sdir, tid) in calls:
            return calls[(sdir, tid)]
        if tid:
            for part in str(tid).split("|"):
                if (sdir, part) in calls:
                    return calls[(sdir, part)]
        return None

    rows = []
    for d in decisions:
        c = find_call(d["sdir"], d["tid"])
        row = {
            "ts": d["ts"],
            "kind": d["kind"],
            "tid": d["tid"],
            "sdir": d["sdir"].split("sessions/")[-1][:120],
            "sess": d["sdir"].split("sessions/")[-1][:70],
            "tool": (c or {}).get("tool"),
            "isError": (c or {}).get("isError"),
            "args": (c or {}).get("args", "")[:200],
        }
        if d["kind"] != "dcg_allow":
            row["outcome"] = "BLOCKED"
        elif c is None or "isError" not in c:
            row["outcome"] = "NO_RESULT"
        else:
            nxt = [txt for t, txt in users[d["sdir"]] if t > d["ts"]][:3]
            row["outcome"] = (
                "BAD"
                if c["isError"] or any(REVERT.search(u or "") for u in nxt)
                else "GOOD"
            )
        rows.append(row)
    with open("decisions_full.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(
        "files:",
        len(n_files),
        "decisions:",
        len(rows),
        Counter(r["outcome"] for r in rows),
    )
    print("kinds:", Counter(r["kind"] for r in rows))


if __name__ == "__main__":
    main()
