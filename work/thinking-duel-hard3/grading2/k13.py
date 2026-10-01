import sys

sys.path.insert(0, SYS_PATH)
from b64x import decode_chunks

assert decode_chunks(["TWFu"]) == b"Man"
assert decode_chunks(["T", "W", "F", "u"]) == b"Man"
assert decode_chunks(["TW\nFu", "TW\nFu"]) == b"ManMan"
for bad in [["TW=u"], ["TWF"], ["TW==u==="], ["T!Fu"]]:
    try:
        decode_chunks(bad)
        raise SystemExit("k13 FAIL accepted")
    except ValueError:
        pass
try:
    decode_chunks(["TW=", "uTW"])
    raise SystemExit("k13 FAIL midpad")
except ValueError:
    pass
print("k13 PASS")
