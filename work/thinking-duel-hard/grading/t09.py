import sys, csv, io, json, subprocess

sys.path.insert(0, SYS_PATH)
from csvexp import write_csv
import tempfile, os

rows = [["a", "b,c", 'd"e', "f\ng"], ["plain", "", "x"]]
fd, p = tempfile.mkstemp(suffix=".csv")
os.close(fd)
write_csv(p, rows)
back = list(csv.reader(open(p)))
assert back == rows, back
os.unlink(p)
proc = subprocess.run(
    [sys.executable, "cli.py"],
    input=json.dumps(rows),
    capture_output=True,
    text=True,
    cwd=SYSCWD,
)
assert proc.returncode == 0, proc.stderr
assert list(csv.reader(io.StringIO(proc.stdout))) == rows
print("t09 PASS")
