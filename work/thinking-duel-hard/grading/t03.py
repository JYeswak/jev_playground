import sys

sys.path.insert(0, SYS_PATH)
from census import count_calls
import tempfile, os

body = (
    '{"message": {"role": "assistant", "content": [{"type": "toolCall", "name": "read"}]}}\n'
    "junk\n"
    '{"message": {"role": "assistant", "content": [{"type": "toolCall", "name": "bash"}, {"type": "toolcall", "name": "read"}]}}\n'
    "[1]\n"
    '{"message": {"role": "assistant", "content": "plain"}}\n'
    '{"message": {"role": "assistant", "content": [{"type": "toolCall"}, {"type": "toolCall", "name": null}]}}\n'
)
fd, p = tempfile.mkstemp(suffix=".jsonl")
os.write(fd, body.encode())
os.close(fd)
got = count_calls(p)
assert got == {"read": 1, "bash": 1}, got
os.unlink(p)
print("t03 PASS")
