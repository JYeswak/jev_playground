import sys, re

sys.path.insert(0, SYS_PATH)
from prefix import redact

pats = [re.compile(r"sk-[a-z]{20,}"), re.compile(r"Bearer [A-Za-z0-9]{16,}")]
assert redact("ls", "/h", pats) == "ls"
got = redact(
    "export A=sk-abcdefghijklmnopqrst B=Bearer ABCDEFGH12345678 end", "/h", pats
)
assert got == "export A=[REDACTED] B=[REDACTED] end", got
cmd = "x" * 185 + " sk-abcdefghijklmnopqrstuvwxyz tail here"
got = redact(cmd, "/h", pats)
assert len(got) <= 200 and "sk-" not in got, got
assert "[REDACT" not in got.replace("[REDACTED]", ""), got
cmd2 = "x" * 195 + "sk-abcdefghijklmnopqrstuvwxyz"
got2 = redact(cmd2, "/h", pats)
assert "sk-" not in got2 and len(got2) <= 200, got2
assert "[REDACT" not in got2.replace("[REDACTED]", ""), got2
print("h08 PASS")
