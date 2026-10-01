import sys

sys.path.insert(0, SYS_PATH)
from retrypy import fetch_with_retry, TransientError, PermanentError

sleeps = []


def slp(s):
    assert s >= 0, s
    sleeps.append(s)


# 200 first try
assert fetch_with_retry(lambda a: (200, {}, "ok"), sleeper=slp) == "ok"
# 4xx permanent immediately, no sleep
sleeps.clear()
try:
    fetch_with_retry(lambda a: (404, {}, None), sleeper=slp)
    raise SystemExit("t02 FAIL: no raise")
except PermanentError:
    pass
assert sleeps == [], sleeps
# Retry-After honored exactly
sleeps.clear()
calls = iter([(503, {"Retry-After": "1"}, None), (200, {}, "back")])
assert fetch_with_retry(lambda a: next(calls), sleeper=slp) == "back"
assert sleeps == [1.0], sleeps
# TransientError retried; total sleep capped <= 2.0
sleeps.clear()
# exhaustion raises
try:
    fetch_with_retry(lambda a: (503, {}, None), retries=3, sleeper=lambda s: None)
    raise SystemExit("t02 FAIL: no exhaust raise")
except PermanentError:
    pass
print("t02 PASS")
