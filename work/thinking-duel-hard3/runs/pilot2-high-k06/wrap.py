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
    return bool(word) and all(_char_width(c) == 2 for c in word)


def _chunk_wide(word, width):
    per = max(1, width // 2)
    return [word[i : i + per] for i in range(0, len(word), per)]


def wrap(text, width):
    lines, cur, cur_w = [], "", 0
    for word in text.split(" "):
        if not word:
            continue
        if _is_all_wide(word) and _dwidth(word) > width:
            for chunk in _chunk_wide(word, width):
                cw = _dwidth(chunk)
                if cur and cur_w + 1 + cw > width:
                    lines.append(cur)
                    cur, cur_w = "", 0
                if cur:
                    cur = cur + " " + chunk
                    cur_w += 1 + cw
                else:
                    cur, cur_w = chunk, cw
            continue
        w = _dwidth(word)
        if cur and cur_w + 1 + w > width:
            lines.append(cur)
            cur, cur_w = "", 0
        if cur:
            cur = cur + " " + word
            cur_w += 1 + w
        else:
            cur, cur_w = word, w
    if cur:
        lines.append(cur)
    return lines
