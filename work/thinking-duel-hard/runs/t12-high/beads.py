import re

_STATUS = {"x": "closed", " ": "open", "~": "in_progress", "-": "deferred"}

_ROW = re.compile(r"^\s*-\s+\[([ x~\-])\]\s+(jev-\d+)\s+\|\s+(.*\S)\s*$")


def parse_rows(text):
    rows = []
    for line in text.splitlines():
        m = _ROW.match(line)
        if not m:
            continue
        mark, bid, title = m.groups()
        rows.append({"id": bid, "title": title, "status": _STATUS[mark]})
    return rows
