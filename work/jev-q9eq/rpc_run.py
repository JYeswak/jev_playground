#!/usr/bin/env python3
"""RPC driver: run one prompt in a fresh interactive omp session, wait for settle.
Usage: rpc_run.py <workdir> <promptfile> [--no-extensions] [--thinking LEVEL]
Prints sessionFile on completion. Exit 0 settled, 1 timeout/error.
"""

import json, subprocess, sys, threading, time

TIMEOUT = 560


def main():
    workdir = sys.argv[1]
    prompt = open(sys.argv[2]).read()
    extra = sys.argv[3:]
    # extra omp flags follow the prompt file: rpc_run.py <dir> <prompt> [--flags...]
    cmd = ["omp", "--mode", "rpc", "--cwd", workdir] + extra
    p = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        cwd="/Users/josh/Developer/jev",
    )
    settled = threading.Event()
    result = {}
    session_file = [None]

    def reader():
        try:
            for line in p.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    f = json.loads(line)
                except Exception:
                    continue
                t = f.get("type")
                if t == "prompt_result":
                    result.update(f)
                elif t == "session_settled":
                    settled.set()
                elif t == "get_state":
                    pass
                if t == "response" and f.get("command") == "get_state":
                    d = f.get("data") or {}
                    if d.get("sessionFile"):
                        session_file[0] = d["sessionFile"]
        except Exception:
            pass

    th = threading.Thread(target=reader, daemon=True)
    th.start()
    try:
        p.stdin.write(
            json.dumps({"id": "p1", "type": "prompt", "message": prompt}) + "\n"
        )
        p.stdin.flush()
    except BrokenPipeError:
        print("FAIL: stdin closed early")
        return 1
    ok = settled.wait(TIMEOUT)
    try:
        p.stdin.write(json.dumps({"id": "g1", "type": "get_state"}) + "\n")
        p.stdin.flush()
    except Exception:
        pass
    time.sleep(3)
    try:
        p.stdin.close()
    except Exception:
        pass
    try:
        p.wait(timeout=30)
    except Exception:
        p.kill()
    # session file: query via sessions dir newest
    import glob, os

    cands = glob.glob(os.path.expanduser("~/.omp/agent/sessions/-Developer-jev*"))
    best, bestmt = None, 0
    for c in cands:
        try:
            mt = os.path.getmtime(c)
        except Exception:
            continue
        if mt > bestmt:
            best, bestmt = c, mt
    print(
        "settled=%s status=%s sessionSettled=%s"
        % (ok, result.get("status"), result.get("sessionSettled"))
    )
    print("sessdir=%s" % (best or ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
