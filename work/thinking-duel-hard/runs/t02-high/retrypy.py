import time, random


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


TRANSIENT = {429, 502, 503, 504}


def _retry_after(headers):
    if not headers:
        return None
    for k, v in headers.items():
        if isinstance(k, str) and k.lower() == "retry-after":
            try:
                secs = float(v)
            except (TypeError, ValueError):
                return None
            if secs < 0:
                return None
            return secs
    return None


def _backoff(attempt):
    base = 0.1 * (2**attempt)
    return base * random.uniform(0.5, 1.0)


def fetch_with_retry(call, retries=5, sleeper=None):
    slp = sleeper or time.sleep
    total = 0.0
    cap = 2.0
    for attempt in range(retries):
        try:
            status, headers, body = call(attempt)
        except TransientError:
            status, headers, body = 503, {}, None
        if status == 200:
            return body
        if status in TRANSIENT:
            if attempt == retries - 1:
                break
            ra = _retry_after(headers)
            wait = ra if ra is not None else _backoff(attempt)
            remaining = cap - total
            if remaining <= 0:
                break
            if wait > remaining:
                wait = remaining
            if wait > 0:
                slp(wait)
                total += wait
            continue
        raise PermanentError(status)
    raise PermanentError("exhausted")
