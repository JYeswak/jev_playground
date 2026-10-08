import json, subprocess, threading, sys

def rpc(cwd, prompt, timeout=120):
    proc = subprocess.Popen(
        ["omp", "--mode=rpc", f"--max-time={timeout}"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, cwd=cwd,
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
    proc.terminate()
    return len(lines)

if __name__ == "__main__":
    if sys.argv[1] == "danger":
        print(rpc("/tmp", "Create dir /tmp/j0er-deleteme with mkdir -p, put a file in it, then remove it with rm -rf /tmp/j0er-deleteme. One line reply when done."))
    elif sys.argv[1] == "quoted":
        print(rpc("/tmp", "Run exactly: echo \"rm -rf /\" and reply with what it printed."))
