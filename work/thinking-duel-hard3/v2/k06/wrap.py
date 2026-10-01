def wrap(text, width):
    lines, cur = [], ""
    for word in text.split(" "):
        if len(cur) + 1 + len(word) > width and cur:
            lines.append(cur)
            cur = ""
        cur = (cur + " " + word).strip() if cur else word
    if cur:
        lines.append(cur)
    return lines
