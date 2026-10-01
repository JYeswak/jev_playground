import sys

sys.path.insert(0, SYS_PATH)
from beads import parse_rows

text = (
    "- [x] jev-1234 | Fix the thing\n"
    "- [ ] jev-99 | Title with | pipe and [brackets]\n"
    "- [~] jev-100 | In flight\n"
    "- [-] jev-101 | Parked\n"
    "not a row\n"
    "- [x] broken-noid\n"
)
rows = parse_rows(text)
assert rows == [
    {"id": "jev-1234", "title": "Fix the thing", "status": "closed"},
    {"id": "jev-99", "title": "Title with | pipe and [brackets]", "status": "open"},
    {"id": "jev-100", "title": "In flight", "status": "in_progress"},
    {"id": "jev-101", "title": "Parked", "status": "deferred"},
], rows
print("t12 PASS")
