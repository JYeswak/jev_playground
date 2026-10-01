import unicodedata


def _char_width(ch):
    if unicodedata.combining(ch):
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


def _split_wide_word(word, width):
    chunks, cur, cur_w = [], "", 0
    for ch in word:
        w = _char_width(ch)
        if cur and cur_w + w > width:
            chunks.append(cur)
            cur, cur_w = "", 0
        cur += ch
        cur_w += w
    if cur:
        chunks.append(cur)
    return chunks


def wrap(text, width):
    lines, cur, cur_w = [], "", 0
    for word in text.split(" "):
        if word == "":
            continue
        units = (
            _split_wide_word(word, width)
            if _is_all_wide(word) and _dwidth(word) > width
            else [word]
        )
        for u in units:
            uw = _dwidth(u)
            if not cur:
                cur, cur_w = u, uw
            elif cur_w + 1 + uw <= width:
                cur += " " + u
                cur_w += 1 + uw
            else:
                lines.append(cur)
                cur, cur_w = u, uw
    if cur:
        lines.append(cur)
    return lines
