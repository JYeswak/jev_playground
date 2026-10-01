import re


def parse_rows(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r"- \[(.)\] (\S+) \| (.*)", line)
        if not m:
            continue
        mark, bid, title = m.groups()
        status = {"x": "closed", " ": "open"}.get(mark, "open")
        rows.append({"id": bid, "title": title, "status": status})
    return rows
