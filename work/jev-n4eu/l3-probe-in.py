import json, subprocess, threading

proc = subprocess.Popen(
    ["omp", "--mode=rpc", "--max-time=180"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    cwd="/Users/josh/Developer/jev",
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
        "message": "You must run web_search for TypeSafe Jev System One pricing; do not answer from memory. Reply with the price in one line.",
    },
):
    proc.stdin.write(json.dumps(f) + "\n")
    proc.stdin.flush()
done.wait(timeout=200)
print("frames:", len(lines))
proc.terminate()
