import json, subprocess, threading

proc = subprocess.Popen(
    ["omp", "--mode=rpc", "--max-time=180"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    text=True, cwd="/tmp/j0er-probe",
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
        "message": "What did we decide about the memory relevance filter removal path? And search the web for TypeSafe Jev pricing. Two lines total.",
    },
):
    proc.stdin.write(json.dumps(f) + "\n")
    proc.stdin.flush()
done.wait(timeout=200)
print("frames:", len(lines))
proc.terminate()
