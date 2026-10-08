import os
import sys
import tempfile

sys.path.insert(0, SYS_PATH)
from csvload import load_table

d = tempfile.mkdtemp()


def w(name, data):
    p = os.path.join(d, name)
    with open(p, "wb") as f:
        f.write(data)
    return p


# 1. utf-8-sig BOM must not pollute the first header
p = w("bom.csv", "name,age\nAda,36\n".encode("utf-8-sig"))
assert load_table(p) == [{"name": "Ada", "age": "36"}]

# 2. lone-\r row separators
p = w("cr.csv", b"a,b\r1,2\r3,4\r")
assert load_table(p) == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]

# 3. quoted commas, doubled quotes, newline inside quotes
p = w("q.csv", b'a,b\n"Doe, Jane","she said ""hi"""\n"x","line1\nline2"\n')
assert load_table(p) == [{"a": "Doe, Jane", "b": 'she said "hi"'},
                          {"a": "x", "b": "line1\nline2"}]

# 4. latin-1 bytes that are invalid UTF-8
p = w("lat.csv", "name,city\nCafé,naïve\n".encode("latin-1"))
assert load_table(p) == [{"name": "Café", "city": "naïve"}]

# 5. empty and header-only files
assert load_table(w("empty.csv", b"")) == []
assert load_table(w("hdr.csv", b"a,b\n")) == []
print("u03 PASS")
