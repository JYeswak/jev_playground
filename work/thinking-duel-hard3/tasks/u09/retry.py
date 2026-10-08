import time


RETRYABLE = {408, 425, 429, 500, 501, 502, 503, 504}


class RetryExhausted(Exception):
    pass


def _parse_retry_after(headers):
    if "Retry-After" in headers:
        return float(headers["Retry-After"])
    return None


def do_request(call, max_attempts=4, now=None, sleeper=None):
    now = now or time.time
    slp = sleeper or time.sleep
    for attempt in range(max_attempts + 1):
        try:
            status, headers, body = call(attempt)
        except Exception as e:
            raise RetryExhausted(e)
        if 200 <= status < 300:
            return body
        if status in RETRYABLE:
            wait = _parse_retry_after(headers) or 0.2 * 2**attempt
            slp(wait)
            continue
        raise RetryExhausted(status)
    raise RetryExhausted("exhausted")
