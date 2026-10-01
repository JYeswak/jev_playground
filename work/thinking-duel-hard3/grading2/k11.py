import sys

sys.path.insert(0, SYS_PATH)
from mdtable import parse

doc = "intro\n| a | b |\n|---|---|\n| 1 | x\\|y |\n| 2 |\n| 3 | z | w |\nend\n"
rows = parse(doc)
assert rows == [
    {"a": "1", "b": "x|y"},
    {"a": "2", "b": None},
    {"a": "3", "b": "z"},
], rows
assert parse("no table here") == []
assert parse("| h |\n| :- |\n| v |") == [{"h": "v"}]
print("k11 PASS")
