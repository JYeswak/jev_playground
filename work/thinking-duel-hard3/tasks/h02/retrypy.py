import time


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


TRANSIENT = {429, 502, 503, 504}


def fetch_with_retry(call, retries=5, now=None, sleeper=None):
    slp = sleeper or time.sleep
    total = 0.0
    for attempt in range(retries):
        try:
            status, headers, body = call(attempt)
        except TransientError:
            status, headers, body = 503, {}, None
        if status == 200:
            return body
        if status in TRANSIENT:
            wait = 0.1 * (2**attempt)
            slp(wait)
            total += wait
            continue
        raise PermanentError(status)
    raise PermanentError("exhausted")
