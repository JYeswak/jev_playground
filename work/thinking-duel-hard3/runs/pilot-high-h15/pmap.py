from concurrent.futures import ThreadPoolExecutor, as_completed, wait


def pmap(fn, items, limit):
    items = list(items)
    if not items:
        return []
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit must be a positive int")
    with ThreadPoolExecutor(max_workers=limit) as ex:
        futs = [ex.submit(fn, x) for x in items]
        try:
            for f in as_completed(futs):
                f.result()
        except BaseException:
            for f in futs:
                f.cancel()
            wait(futs)
            raise
        return [f.result() for f in futs]
