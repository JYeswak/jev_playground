import sys

sys.path.insert(0, SYS_PATH)
from retrypy import fetch_with_retry, TransientError, PermanentError
import email.utils, calendar

sl = []
now = [1000.0]


def slp(s):
    sl.append(s)


assert (
    fetch_with_retry(lambda a: (200, {}, "ok"), now=lambda: now[0], sleeper=slp) == "ok"
)
sl.clear()
try:
    fetch_with_retry(lambda a: (501, {}, None), now=lambda: now[0], sleeper=slp)
    raise SystemExit("h02 FAIL")
except PermanentError:
    pass
assert sl == [], sl
sl.clear()
dt = email.utils.formatdate(now[0] + 3, usegmt=True)
calls = iter([(503, {"Retry-After": dt}, None), (200, {}, "d")])
assert fetch_with_retry(lambda a: next(calls), now=lambda: now[0], sleeper=slp) == "d"
assert len(sl) == 1 and abs(sl[0] - 3.0) < 0.01, sl
sl.clear()


def flaky(a):
    if a < 4:
        raise TransientError()
    return (200, {}, "late")


assert fetch_with_retry(flaky, now=lambda: now[0], sleeper=slp) == "late"
assert sum(sl) <= 2.0 + 1e-9, sl
try:
    fetch_with_retry(
        lambda a: (500, {}, None), retries=2, now=lambda: now[0], sleeper=lambda s: None
    )
    raise SystemExit("h02 FAIL 500")
except PermanentError:
    pass
print("h02 PASS")
