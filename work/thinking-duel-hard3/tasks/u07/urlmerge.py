from urllib.parse import urlparse, parse_qs, urlencode


def merge_url(base, extra):
    parts = urlparse(base)
    q = parse_qs(parts.query)
    for k, v in extra.items():
        q[k] = list(v) if isinstance(v, list) else [v]
    query = urlencode(q, doseq=True)
    return f"{parts.scheme}://{parts.netloc}{parts.path}?{query}"
