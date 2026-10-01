import sys, time

sys.path.insert(0, SYS_PATH)
from runbox import run

code, out, err = run(["echo", "hi"], 5)
assert (code, out.strip()) == (0, "hi"), (code, out)
t = time.time()
code, out, err = run(["sleep", "30"], 1)
assert code == 124 and time.time() - t < 10, (code, time.time() - t)
t = time.time()
code, out, err = run(
    ["python3", "-c", 'import sys; sys.stderr.write("x"*300000); print("y"*300000)'], 10
)
assert code == 0 and out == "y" * 300000 + "\n" and err == "x" * 300000, (
    code,
    len(out),
    len(err),
)
import subprocess as sp

left = sp.run(
    ["pgrep", "-f", "sleep 30"], capture_output=True, text=True
).stdout.strip()
assert left == "", left
print("t05 PASS")
