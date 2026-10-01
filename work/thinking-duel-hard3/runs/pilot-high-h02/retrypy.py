import time
from email.utils import parsedate_to_datetime


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


TRANSIENT = {429, 502, 503, 504}


def _retry_after_wait(headers, now_fn):
    hdrs = headers or {}
    raw = None
    for k, v in hdrs.items():
        if k.lower() == "retry-after":
            raw = v
            break
    if raw is None:
        return None
    s = str(raw).strip()
    try:
        secs = int(s)
        return max(0.0, float(secs))
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(s)
    except Exception:
        return None
    try:
        ts = dt.timestamp()
    except Exception:
        return None
    return max(0.0, ts - now_fn())


def fetch_with_retry(call, retries=5, now=None, sleeper=None):
    slp = sleeper or time.sleep
    now_fn = now or time.time
    total = 0.0
    for attempt in range(retries):
        try:
            status, headers, body = call(attempt)
        except TransientError:
            status, headers, body = 503, {}, None
        if status == 200:
            return body
        if status not in TRANSIENT:
            raise PermanentError(status)
        if attempt == retries - 1:
            break
        wait = _retry_after_wait(headers, now_fn)
        if wait is None:
            wait = 0.1 * (2**attempt)
            remaining = 2.0 - total
            if remaining <= 0:
                break
            if wait > remaining:
                wait = remaining
            if wait <= 0:
                continue
            slp(wait)
            total += wait
        elif wait > 0:
            slp(wait)
    raise PermanentError("exhausted")
