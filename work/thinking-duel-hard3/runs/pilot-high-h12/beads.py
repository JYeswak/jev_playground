import re

_MARKS = {"x": "closed", " ": "open", "~": "in_progress", "-": "deferred"}
_WORDS = {
    "closed": "closed",
    "open": "open",
    "in_progress": "in_progress",
    "in-progress": "in_progress",
    "deferred": "deferred",
}
_ID_RE = re.compile(r"[A-Za-z0-9_-]+\Z")
_MARK_RE = re.compile(r"^\s*-\s*\[([ x~\-])\]\s+(\S+)\s*\|\s*(.*)\s*$")
_WORD_RE = re.compile(
    r"^\s*-\s*(closed|open|in_progress|in-progress|deferred)\s+(\S+?)\s*:\s*(.*)\s*$"
)


def parse_rows(text):
    rows = []
    for line in text.splitlines():
        m = _MARK_RE.match(line)
        if m:
            mark, bid, title = m.groups()
            status = _MARKS.get(mark)
            title = title.strip()
            if status is None or not _ID_RE.match(bid) or not title:
                continue
            rows.append({"id": bid, "title": title, "status": status})
            continue
        m = _WORD_RE.match(line)
        if not m:
            continue
        word, bid, title = m.groups()
        bid = bid.strip()
        title = title.strip()
        if not _ID_RE.match(bid) or not title:
            continue
        rows.append({"id": bid, "title": title, "status": _WORDS[word]})
    return rows
