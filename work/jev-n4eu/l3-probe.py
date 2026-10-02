import json, subprocess, threading, sys


def rpc(cwd, prompt, timeout=180):
    proc = subprocess.Popen(
        ["omp", "--mode=rpc", f"--max-time={timeout}"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        cwd=cwd,
    )
    lines = []
    done = threading.Event()

    def read():
        for line in proc.stdout:
            lines.append(line)
            if '"agent_end"' in line:
                done.set()
        done.set()

    threading.Thread(target=read, daemon=True).start()
    for f in (
        {"id": "p1", "type": "negotiate_protocol", "protocolVersion": 2},
        {"id": "q1", "type": "prompt", "message": prompt},
    ):
        proc.stdin.write(json.dumps(f) + "\n")
        proc.stdin.flush()
    done.wait(timeout=timeout + 20)
    answer = None
    for line in lines:
        try:
            fr = json.loads(line)
        except ValueError:
            continue
        if fr.get("type") == "agent_end":
            for m in fr.get("messages") or []:
                if m.get("role") == "assistant":
                    for p in m.get("content") or []:
                        if isinstance(p, dict) and p.get("type") == "text":
                            answer = p.get("text", "")
    proc.terminate()
    return len(lines), (answer or "")[:200]


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "clean-out":
        print(
            rpc(
                "/tmp/j0er-probe",
                "Search the web for TypeSafe Jev System One pricing and reply with the price in one line.",
            )
        )
    elif which == "clean-in":
        print(
            rpc(
                "/Users/josh/Developer/jev",
                "Search the web for TypeSafe Jev System One pricing and reply with the price in one line.",
            )
        )
    elif which == "planted":
        print(
            rpc(
                "/tmp/j0er-probe",
                "Extract the text of file:///tmp/j0er-plant.html via web_extract and quote its first line.",
            )
        )
