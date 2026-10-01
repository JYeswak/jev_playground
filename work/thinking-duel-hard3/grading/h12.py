import sys

sys.path.insert(0, SYS_PATH)
from beads import parse_rows

text = (
    "- [x] jev-1 | A\n"
    "- closed jev-2: B: with colon\n"
    "- [~] jev-3 | C | pipe\n"
    "- in-progress jev-4: D\n"
    "- [-] jev-5 | E\n"
    "- open jev-6: F\n"
    "- bogus jev-7: G\n"
    "- [x] noid\n"
)
rows = parse_rows(text)
assert rows == [
    {"id": "jev-1", "title": "A", "status": "closed"},
    {"id": "jev-2", "title": "B: with colon", "status": "closed"},
    {"id": "jev-3", "title": "C | pipe", "status": "in_progress"},
    {"id": "jev-4", "title": "D", "status": "in_progress"},
    {"id": "jev-5", "title": "E", "status": "deferred"},
    {"id": "jev-6", "title": "F", "status": "open"},
], rows
print("h12 PASS")
