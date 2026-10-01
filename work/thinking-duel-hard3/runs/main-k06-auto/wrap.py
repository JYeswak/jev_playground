import unicodedata


def _char_width(ch):
    if unicodedata.combining(ch):
        return 0
    if unicodedata.category(ch) in ("Mn", "Me"):
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def _dwidth(s):
    return sum(_char_width(c) for c in s)


def _is_all_wide(word):
    return len(word) > 0 and all(
        unicodedata.east_asian_width(c) in ("W", "F") for c in word
    )


def _chunk_wide(word, width):
    chunks, cur, cur_w = [], "", 0
    for ch in word:
        w = _char_width(ch)
        if w == 0:
            if not cur:
                cur, cur_w = ch, 0
            else:
                cur += ch
            continue
        if cur and cur_w + w > width:
            chunks.append(cur)
            cur, cur_w = "", 0
        cur += ch
        cur_w += w
    if cur:
        chunks.append(cur)
    return chunks or [word]


def wrap(text, width):
    lines, cur, cur_w = [], "", 0
    for word in text.split(" "):
        if word == "":
            continue
        ww = _dwidth(word)
        if ww > width:
            if cur:
                lines.append(cur)
                cur, cur_w = "", 0
            if _is_all_wide(word):
                lines.extend(_chunk_wide(word, width))
            else:
                lines.append(word)
            continue
        if not cur:
            cur, cur_w = word, ww
        elif cur_w + 1 + ww <= width:
            cur, cur_w = cur + " " + word, cur_w + 1 + ww
        else:
            lines.append(cur)
            cur, cur_w = word, ww
    if cur:
        lines.append(cur)
    return lines
