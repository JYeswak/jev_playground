import sys

sys.path.insert(0, SYS_PATH)
from where import build

sql, params = build(("name", "=", "ann"))
assert sql == "name = $1" and params == ["ann"], (sql, params)
sql, params = build(
    ("and", [("a", ">", 1), ("or", [("b", "LIKE", "%x%"), ("c", "!=", None)])])
)
assert params == [1, "%x%", None], params
assert sql.count("$") == 3 and "$1" in sql and "$3" in sql, sql
assert "AND" in sql and "OR" in sql, sql
evil = "x' OR '1'='1"
sql, params = build(("name", "=", evil))
assert evil not in sql and params == [evil], (sql, params)
sql, params = build(("not", ("a", "=", 1)))
assert "NOT" in sql and params == [1], (sql, params)
print("k08 PASS")
