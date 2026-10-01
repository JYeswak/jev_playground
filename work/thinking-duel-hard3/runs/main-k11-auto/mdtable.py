def _split_row(line):
    cells = []
    cur = []
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == "\\" and i + 1 < n and line[i + 1] in ("|", "\\"):
            cur.append(line[i + 1])
            i += 2
        elif c == "|":
            cells.append("".join(cur))
            cur = []
            i += 1
        else:
            cur.append(c)
            i += 1
    cells.append("".join(cur))
    s = line.strip()
    if s.startswith("|") and cells and cells[0].strip() == "":
        cells.pop(0)
    if s.endswith("|") and cells and cells[-1].strip() == "":
        # trailing '|' was a delimiter (an escaped '\|' would not
        # have split, so last cell would not be empty here)
        cells.pop()
    return [c.strip() for c in cells]


def _is_delim_cell(cell):
    t = cell.strip()
    if len(t) < 3:
        return False
    if t.startswith(":"):
        t = t[1:]
    if t.endswith(":"):
        t = t[:-1]
    return len(t) >= 1 and all(c == "-" for c in t)


def parse(text):
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        if "|" not in lines[i]:
            continue
        if lines[i].strip() == "":
            continue
        header = _split_row(lines[i])
        if not header or all(h == "" for h in header):
            continue
        if "|" not in lines[i + 1]:
            continue
        delim = _split_row(lines[i + 1])
        if len(delim) != len(header):
            continue
        if not delim or not all(_is_delim_cell(c) for c in delim):
            continue
        rows = []
        for dl in lines[i + 2 :]:
            if dl.strip() == "":
                break
            if "|" not in dl:
                break
            cells = _split_row(dl)
            if len(cells) < len(header):
                cells = cells + [None] * (len(header) - len(cells))
            else:
                cells = cells[: len(header)]
            rows.append(dict(zip(header, cells)))
        return rows
    return []
