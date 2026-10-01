import sys, tempfile, os

sys.path.insert(0, SYS_PATH)
from census import summarize

lines = [
    '{"message": {"role": "assistant", "content": [{"type": "toolCall", "name": "read"}, {"type": "thinking", "thinking": "abc"}]}}',
    "junk{",
    "[1,2]",
    '{"message": {"role": "user", "content": [{"type": "toolCall", "name": "read"}, {"type": "thinking", "thinking": "zz"}]}}',
    '{"message": {"role": "assistant", "content": [{"type": "toolCall"}, {"type": "thinking", "thinking": 5}]}}',
    "has\x00nul",
    '{"message": {"role": "assistant", "content": "plain"}}',
]
fd, p = tempfile.mkstemp(suffix=".jsonl")
with os.fdopen(fd, "w") as fh:
    fh.write("\n".join(lines) + "\n")
got = summarize(p)
assert got == {"calls": {"read": 1}, "think_chars": 3}, got
os.unlink(p)
print("h03 PASS")
