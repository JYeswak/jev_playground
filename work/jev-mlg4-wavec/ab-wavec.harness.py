#!/usr/bin/env python3
"""Wave-c harness: locate tasks, ON (native judge) vs OFF (judge:off overlay).
Order per task: ON-r1, OFF-r1, ON-r2, OFF-r2. OFF pins thinking to ON-r1 level.
"""

import json, os, subprocess, sys, glob
from datetime import datetime, timezone

ROOT = "/Users/josh/Developer/jev"
SCR = os.path.join(ROOT, "var/agent-tmp/ab-wavec.main")
JUDGEOFF = os.path.join(ROOT, "var/agent-tmp/nojudge2.yml")
MANIFEST = os.path.join(SCR, "manifest2.jsonl")
os.makedirs(SCR, exist_ok=True)
TASKS = json.load(open(os.path.join(ROOT, "var/agent-tmp/wavec.tasks.json")))
TPL = (
    "TASK-ID findwave-{tid}-{arm}. In this repo (/Users/josh/Developer/jev), locate the file described below. "
    "Reply with ONLY the exact relative path (e.g. scripts/foo.py) and one line on how you found it. "
    "Then stop. Do not edit, commit, or modify anything.\nTARGET: {target}"
)


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def think_of(sessdir):
    files = sorted(glob.glob(os.path.join(sessdir, "*.jsonl")), key=os.path.getmtime)
    if not files:
        return None
    for line in open(files[-1], encoding="utf-8", errors="replace"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("type") == "thinking_level_change":
            return r.get("thinkingLevel")
    return None


def run(tid, target, arm, rep, think=None):
    d = os.path.join(SCR, "%s-%s" % (tid, arm))
    os.makedirs(d, exist_ok=True)
    pf = os.path.join(SCR, "prompt-%s-%s-%s.txt" % (tid, arm, rep))
    open(pf, "w").write(TPL.format(tid=tid + "-" + rep, arm=arm, target=target))
    t0 = utcnow()
    cmd = ["python3", "var/agent-tmp/rpc_run.py", d, pf]
    if arm == "ON":
        pass
    else:
        cmd += ["--config", JUDGEOFF]
        if think:
            cmd += ["--thinking", think]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=590, cwd=ROOT)
    t1 = utcnow()
    out = p.stdout + p.stderr
    sd = None
    for line in out.split("\n"):
        if line.startswith("sessdir="):
            sd = line.split("=", 1)[1].strip()
    lvl = think_of(sd) if sd else None
    rec = {
        "task": tid,
        "arm": arm,
        "rep": rep,
        "t0": t0,
        "t1": t1,
        "think": lvl,
        "sessdir": sd,
        "rc": p.returncode,
        "tail": out[-200:],
    }
    open(MANIFEST, "a").write(json.dumps(rec) + "\n")
    print("%s %s %s rc=%d think=%s" % (tid, arm, rep, p.returncode, lvl), flush=True)
    return rec, lvl


def main():
    only = sys.argv[1:] or [t["id"] for t in TASKS]
    byid = {t["id"]: t["target"] for t in TASKS}
    for tid in only:
        _, lvl = run(tid, byid[tid], "ON", "r1")
        run(tid, byid[tid], "OFF", "r1", think=lvl)
        run(tid, byid[tid], "ON", "r2")
        run(tid, byid[tid], "OFF", "r2", think=lvl)
    print("WAVEC DONE", flush=True)


if __name__ == "__main__":
    main()
