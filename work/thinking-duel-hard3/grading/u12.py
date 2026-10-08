import sys
sys.path.insert(0, SYS_PATH)
from slugify import slugify

# 1. non-ASCII letters survive per-category (accents stripped, scripts kept)
assert slugify("Café Münchner Kindl 123") == "cafe-munchner-kindl-123", slugify("Café Münchner Kindl 123")
assert slugify("Καλημέρα Αθήνα") == "καλημερα-αθηνα", slugify("Καλημέρα Αθήνα")
assert slugify("北京烤鸭!") == "北京烤鸭", slugify("北京烤鸭!")

# 2. separators collapse; punctuation-only yields ""
assert slugify("  Héllo---Wörld  ") == "hello-world"
assert slugify("release 2.0 🚀 notes") == "release-2-0-notes"
assert slugify("!!! … ???") == ""

# 3. length cap backs off to a word boundary instead of splitting a run
assert slugify("lorem ipsum dolor sit amet", max_len=14) == "lorem-ipsum"
assert slugify("ab cd ef", max_len=5) == "ab-cd"
assert slugify("abcdefghij", max_len=5) == "abcde"
assert slugify("ab--cd", max_len=4) == "ab"

# 4. bad cap raises; short slugs untouched
try:
    slugify("hi", max_len=0)
    raise AssertionError("max_len=0 should raise")
except ValueError:
    pass
assert slugify("already-fine") == "already-fine"

print("u12 PASS")
