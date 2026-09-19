"""Scan omp sessions for supervision windows with future-derived labels (OFFLINE).

Window = K consecutive tool calls. Features per window, all from row data:
  elapsed_s: last.ts - first.ts (ISO message timestamps / startedAt)
  max_repeat: longest run of identical toolName+canonical-args
  write_fired: any call whose tool is in WRITE_TOOLS
  testfail: failure regex in any window output (feasibility label)
Labels from the transcript's own future (stated predicate, no judgment):
  STUCK iff max_repeat>=3 AND not write_fired AND elapsed_s>300 AND
    INTERVENTION matches the next user message after the window
  HEALTHY iff write_fired AND no INTERVENTION match in the next 5 user messages
    AND at least one future user message exists
  else AMBIGUOUS
Usage: python scan_windows.py  (writes real_windows.jsonl)
"""

import glob
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

HOME = os.path.expanduser("~")
ROOTS = sorted(glob.glob(HOME + "/.omp/profiles/*/agent/sessions/*/*"))
WRITE_TOOLS = {"edit", "write", "create", "apply_patch", "write_file", "save"}
INTERVENTION = re.compile(
    r"\bstop\b|\bstuck\b|wrong|don't|do not|not that|hold on|\bwait\b"
    r"|actually|redirect|interrupt|going the wrong way|that's not|start over|revert",
    re.IGNORECASE,
)
FAIL = re.compile(r"fail|error|assert|traceback|exit [1-9]|FAILED", re.IGNORECASE)
K = 8


def epoch(ts):
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def canon_args(a):
    try:
        return json.dumps(a, sort_keys=True)[:300]
    except Exception:
        return str(a)[:300]


def main():
    events = []  # (ts, sid, kind, payload)
    for sdir in ROOTS:
        for f in sorted(glob.glob(sdir + "/*.jsonl") + glob.glob(sdir + "/*.log")):
            with open(f, errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line.startswith("{"):
                        continue
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    t = r.get("timestamp", "")
                    if r.get("customType") == "tool_execution_start":
                        events.append(
                            (
                                t,
                                sdir,
                                "call",
                                {
                                    "tool": r.get("toolName", "?"),
                                    "args": {},
                                    "ts": r.get("startedAt", t),
                                },
                            )
                        )
                        continue
                    m = r.get("message")
                    if not isinstance(m, dict):
                        continue
                    role = m.get("role")
                    if role == "assistant":
                        for p in m.get("content") or []:
                            if isinstance(p, dict) and p.get("type") == "toolCall":
                                events.append(
                                    (
                                        t,
                                        sdir,
                                        "call",
                                        {
                                            "tool": p.get("name", "?"),
                                            "args": p.get("arguments", {}),
                                            "ts": t,
                                        },
                                    )
                                )
                    elif role == "user":
                        txt = "\n".join(
                            p.get("text", "")
                            for p in m.get("content") or []
                            if isinstance(p, dict) and p.get("type") == "text"
                        )
                        events.append((t, sdir, "user", {"text": txt}))
                    elif role == "toolResult":
                        txt = "\n".join(
                            p.get("text", "")
                            for p in m.get("content") or []
                            if isinstance(p, dict) and p.get("type") == "text"
                        )
                        if events and events[-1][2] == "call" and events[-1][1] == sdir:
                            events[-1][3]["output"] = txt[:2000]
    by_sess = defaultdict(list)
    users = defaultdict(list)
    for t, sid, kind, p in events:
        (by_sess if kind == "call" else users)[sid].append((t, p))
    wins = []
    for sid, calls in by_sess.items():
        if len(calls) < K:
            continue
        for i in range(len(calls) - K + 1):
            w = calls[i : i + K]
            t0 = epoch(w[0][1].get("ts", ""))
            t1 = epoch(w[-1][1].get("ts", ""))
            el = max(0.0, t1 - t0) if t0 and t1 else 0.0
            keys = [(c["tool"], canon_args(c.get("args", {}))) for _, c in w]
            run = mx = 1
            for x, y in zip(keys, keys[1:]):
                run = run + 1 if x == y else 1
                mx = max(mx, run)
            wf = any(c["tool"] in WRITE_TOOLS for _, c in w)
            wend = w[-1][0]
            future_users = [
                (p.get("text", "") if isinstance(p, dict) else "")
                for t, p in users[sid]
                if t > wend
            ][:6]
            intervened = bool(future_users) and bool(
                INTERVENTION.search(future_users[0] or "")
            )
            clean5 = not any(INTERVENTION.search(u or "") for u in future_users[:5])
            if mx >= 3 and not wf and el > 300 and intervened:
                lab = "stuck"
            elif wf and clean5 and len(future_users) > 0:
                lab = "healthy"
            else:
                lab = "ambiguous"
            tf = any(FAIL.search(c.get("output", "")) for _, c in w)
            wins.append(
                {
                    "session": sid,
                    "start": w[0][0],
                    "label": lab,
                    "elapsed_s": round(el, 1),
                    "max_repeat": mx,
                    "write_fired": wf,
                    "testfail": tf,
                    "tools": [c["tool"] for _, c in w],
                    "outputs": [c.get("output", "")[:800] for _, c in w],
                }
            )
    print("windows:", len(wins), Counter(w["label"] for w in wins))
    with open("real_windows.jsonl", "w") as fh:
        for w in wins:
            fh.write(json.dumps(w) + "\n")


if __name__ == "__main__":
    main()
