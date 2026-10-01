import re

_STATUS = {"x": "closed", " ": "open", "~": "in_progress", "-": "deferred"}
_ROW_RE = re.compile(r"\s*-\s+\[(.)\]\s+([A-Za-z0-9_-]+)\s+\|\s+(.*)")


def parse_rows(text):
    rows = []
    if not text:
        return rows
    for line in text.splitlines():
        m = _ROW_RE.match(line)
        if not m:
            continue
        mark, bid, title = m.groups()
        if mark not in _STATUS:
            continue
        title = title.strip()
        if not title:
            continue
        rows.append({"id": bid, "title": title, "status": _STATUS[mark]})
    return rows
