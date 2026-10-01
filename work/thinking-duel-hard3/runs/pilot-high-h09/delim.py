def _encode_field(v, delim, none_as):
    if v is None:
        if none_as == "":
            return '""'
        return none_as
    if v == "":
        return ""
    if (
        (delim != "" and delim in v)
        or '"' in v
        or "\n" in v
        or "\r" in v
        or (none_as != "" and v == none_as)
    ):
        return '"' + v.replace('"', '""') + '"'
    return v


def _decode_field(content, quoted, none_as):
    if quoted and content == "":
        return None if none_as == "" else ""
    if not quoted and none_as != "" and content == none_as:
        return None
    return content


def _split_rows(text, delim):
    if text == "":
        return []
    if delim == "":
        raise ValueError("delim must be nonempty")
    rows = []
    row = []
    buf = []
    in_quotes = False
    quoted = False
    field_start = True
    i = 0
    n = len(text)
    dl = len(delim)
    while i < n:
        if in_quotes:
            if text[i] == '"':
                if i + 1 < n and text[i + 1] == '"':
                    buf.append('"')
                    i += 2
                else:
                    in_quotes = False
                    i += 1
            else:
                buf.append(text[i])
                i += 1
        elif field_start and text[i] == '"':
            in_quotes = True
            quoted = True
            field_start = False
            i += 1
        elif text[i] == "\r" or text[i] == "\n":
            row.append(("".join(buf), quoted))
            buf = []
            quoted = False
            field_start = True
            rows.append(row)
            row = []
            if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
            else:
                i += 1
        elif text.startswith(delim, i):
            row.append(("".join(buf), quoted))
            buf = []
            quoted = False
            field_start = True
            i += dl
        else:
            buf.append(text[i])
            field_start = False
            i += 1
    if row or buf or quoted or not field_start:
        row.append(("".join(buf), quoted))
        rows.append(row)
    return rows


def write_delim(path, rows, delim="|", none_as=""):
    with open(path, "w", newline="") as fh:
        for row in rows:
            fh.write(delim.join(_encode_field(v, delim, none_as) for v in row) + "\n")


def read_delim(path, delim="|", none_as=""):
    with open(path, "r", newline="") as fh:
        text = fh.read()
    return [
        [_decode_field(content, quoted, none_as) for content, quoted in row]
        for row in _split_rows(text, delim)
    ]
