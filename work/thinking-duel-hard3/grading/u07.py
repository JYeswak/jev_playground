import sys

sys.path.insert(0, SYS_PATH)
from urlmerge import merge_url as m

# 1. repeated keys accumulate in order, blank values survive
assert m("https://h/p?a=1&a=2", {"a": "3"}) == "https://h/p?a=1&a=2&a=3"
assert m("https://h/p?x=", {"y": ""}) == "https://h/p?x=&y="
assert m("https://h/p?a=&a=", {"a": ["", ""]}) == "https://h/p?a=&a=&a=&a="

# 2. lists expand in order, existing order preserved, extras appended
got = m("https://h/p?b=1&a=2", {"c": ["x", "y"], "a": "3"})
assert got == "https://h/p?b=1&a=2&c=x&c=y&a=3", got

# 3. fragment stays last, params before it, no-query and empty-query bases
got = m("https://h/p?a=1#frag", {"b": "2"})
assert got == "https://h/p?a=1&b=2#frag", got
assert m("https://h/p", {"a": "1"}) == "https://h/p?a=1"
assert m("https://h/p?a=1", {}) == "https://h/p?a=1"
assert m("https://h/p#frag", {"a": "1"}) == "https://h/p?a=1#frag"

# 4. reserved characters and non-string leaves encoded, plus surviving blanks
got = m("https://h/p", {"q": "a b&c=d", "k y": "v/z"})
assert got == "https://h/p?q=a+b%26c%3Dd&k+y=v%2Fz", got
got = m("https://h/p?keep=0", {"n": "a&b"})
assert "keep=0" in got and "n=a%26b" in got, got
print("u07 PASS")
