import re

_DELIM_RE = re.compile(r"^:?-+:?$")


def _split_cells(inner):
    """Split on unescaped '|' ('\\|' -> literal '|'), strip each cell."""
    cells = []
    buf = []
    i = 0
    n = len(inner)
    while i < n:
        if inner[i] == "\\" and i + 1 < n and inner[i + 1] == "|":
            buf.append("|")
            i += 2
        elif inner[i] == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
        else:
            buf.append(inner[i])
            i += 1
    cells.append("".join(buf).strip())
    return cells


def _parse_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and s:
        j = len(s) - 2
        bs = 0
        while j >= 0 and s[j] == "\\":
            bs += 1
            j -= 1
        if bs % 2 == 0:
            s = s[:-1]
    return _split_cells(s)


def _is_delim(cells):
    return bool(cells) and all(bool(_DELIM_RE.match(c)) for c in cells)


def parse(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "|" not in line:
            continue
        header = _parse_row(line)
        if i + 1 >= len(lines):
            continue
        delim = _parse_row(lines[i + 1])
        if len(delim) != len(header) or not _is_delim(delim):
            continue
        n = len(header)
        rows = []
        for dl in lines[i + 2 :]:
            if dl.strip() == "" or "|" not in dl:
                break
            vals = _parse_row(dl)
            if len(vals) < n:
                vals = vals + [None] * (n - len(vals))
            else:
                vals = vals[:n]
            rows.append(dict(zip(header, vals)))
        return rows
    return []
