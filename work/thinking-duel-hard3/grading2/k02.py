import sys

sys.path.insert(0, SYS_PATH)
from qs import parse

assert parse("a=&b=1&a=2") == [("a", ""), ("b", "1"), ("a", "2")]
assert parse("q=a+b") == [("q", "a b")]
assert parse("q=a%2Bb") == [("q", "a+b")]
assert parse("?x=%41%5a") == [("x", "AZ")]
assert parse("flag") == [("flag", None)]
assert parse("") == []
assert parse("a=%E2%82%AC") == [("a", "\u20ac")]
assert parse("k=a=b") == [("k", "a=b")]
print("k02 PASS")
