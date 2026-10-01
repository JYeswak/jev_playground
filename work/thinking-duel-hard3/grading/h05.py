import sys, time

sys.path.insert(0, SYS_PATH)
from runbox import run

code, merged = run(["echo", "hi"], 5)
assert code == 0 and merged.strip() == "hi", (code, merged)
t = time.time()
code, merged = run(
    [
        "python3",
        "-c",
        'import subprocess,time;subprocess.Popen(["sleep","30"]);time.sleep(30)',
    ],
    1,
)
dt = time.time() - t
assert code == 124 and dt < 10, (code, dt)
import subprocess as sp

left = sp.run(
    ["pgrep", "-f", "sleep 30"], capture_output=True, text=True
).stdout.strip()
assert left == "", left
t = time.time()
code, merged = run(
    ["python3", "-c", 'import sys; sys.stderr.write("e"*200000); print("o"*200000)'], 10
)
assert code == 0 and merged.count("e") == 200000 and merged.count("o") == 200000, (
    code,
    len(merged),
)
print("h05 PASS")
