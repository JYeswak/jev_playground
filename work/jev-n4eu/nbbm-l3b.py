import json, subprocess, threading

proc = subprocess.Popen(
    ["omp", "--mode=rpc", "--max-time=90"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    text=True, cwd="/tmp",
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
    {
        "id": "q1",
        "type": "prompt",
        "message": "Run exactly: echo \"rm -rf /\" and reply with what it printed.",
    },
):
    proc.stdin.write(json.dumps(f) + "\n")
    proc.stdin.flush()
done.wait(timeout=110)
print("frames:", len(lines))
rc = proc.wait(timeout=60)
print("natural exit:", rc)
