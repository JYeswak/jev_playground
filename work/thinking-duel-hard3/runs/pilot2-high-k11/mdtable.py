import re

_DELIM = re.compile(r"^:?-+:?$")


def _has_pipe(line):
    i = 0
    n = len(line)
    while i < n:
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == "|":
            return True
        i += 1
    return False


def _split(line):
    cells = []
    cur = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == "\\" and i + 1 < n and line[i + 1] in ("|", "\\"):
            cur.append(line[i + 1])
            i += 2
        elif ch == "|":
            cells.append("".join(cur))
            cur = []
            i += 1
        else:
            cur.append(ch)
            i += 1
    cells.append("".join(cur))
    cells = [c.strip() for c in cells]
    s = line.strip()
    if s.startswith("|") and cells and cells[0] == "":
        cells.pop(0)
    if s.endswith("|") and cells and cells[-1] == "":
        k = 0
        j = len(s) - 2
        while j >= 0 and s[j] == "\\":
            k += 1
            j -= 1
        if k % 2 == 0:
            cells.pop()
    return cells


def parse(text):
    lines = text.split("\n")
    for i in range(len(lines) - 1):
        if not _has_pipe(lines[i]):
            continue
        header = _split(lines[i])
        if not header:
            continue
        delim = _split(lines[i + 1])
        if len(delim) != len(header):
            continue
        if not all(_DELIM.match(d) for d in delim):
            continue
        rows = []
        for dl in lines[i + 2 :]:
            if not dl.strip():
                break
            if not _has_pipe(dl):
                break
            cells = _split(dl)
            if len(cells) < len(header):
                cells += [None] * (len(header) - len(cells))
            else:
                cells = cells[: len(header)]
            rows.append(dict(zip(header, cells)))
        return rows
    return []
