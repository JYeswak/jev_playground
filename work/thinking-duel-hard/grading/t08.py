import sys, re

sys.path.insert(0, SYS_PATH)
from prefix import redact

sec = re.compile(r"sk-[a-z]{20,}")
assert redact("ls /tmp", "/home/u", sec) == "ls /tmp"
assert (
    redact("export K=sk-abcdefghijklmnopqrst dir", "/home/u", sec)
    == "export K=[REDACTED] dir"
)
home = "/Users/josh"
cmd = "x" * 190 + " sk-abcdefghijklmnopqrstuvwxyz tail"
got = redact(cmd, home, sec)
assert len(got) <= 200, len(got)
assert "sk-" not in got, got
assert "[REDACTED" in got, got
cmd2 = "cd " + home + "/proj && echo hi"
assert redact(cmd2, home, sec) == "cd ~/proj && echo hi", redact(cmd2, home, sec)
print("t08 PASS")
