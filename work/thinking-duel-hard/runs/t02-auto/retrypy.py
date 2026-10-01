import time, random


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


TRANSIENT = {429, 502, 503, 504}


def fetch_with_retry(call, retries=5, sleeper=None):
    slp = sleeper if sleeper is not None else time.sleep
    total = 0.0
    cap = 2.0
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
        headers = headers or {}
        ra = None
        for k, v in headers.items():
            if str(k).lower() == "retry-after":
                ra = v
                break
        if ra is not None:
            try:
                wait = float(ra)
            except (TypeError, ValueError):
                ra = None
        if ra is None:
            wait = 0.1 * (2**attempt) * (0.5 + random.random())
        if wait < 0:
            wait = 0.0
        remaining = cap - total
        if remaining <= 0:
            continue
        if wait > remaining:
            wait = remaining
        if wait > 0:
            slp(wait)
            total += wait
    raise PermanentError("exhausted")
