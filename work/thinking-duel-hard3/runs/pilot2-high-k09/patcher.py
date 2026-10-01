import re

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def apply_patch(original, diff):
    orig_lines = [] if original == "" else original.split("\n")
    result = list(orig_lines)
    diff_lines = diff.splitlines()
    hunks = []
    current = None
    for dl in diff_lines:
        m = _HUNK_RE.match(dl)
        if m:
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) is not None else 1
            c = int(m.group(3))
            d = int(m.group(4)) if m.group(4) is not None else 1
            current = {"a": a, "b": b, "c": c, "d": d, "body": []}
            hunks.append(current)
        elif dl.startswith("@@"):
            raise ValueError("invalid hunk header: %r" % dl)
        elif current is None:
            continue
        else:
            current["body"].append(dl)
    offset = 0
    prev_end = 0
    for h in hunks:
        a, b, d = h["a"], h["b"], h["d"]
        if b == 0:
            start = a + offset
        else:
            if a < 1:
                raise ValueError("invalid hunk start: -%d,%d" % (a, b))
            start = (a - 1) + offset
        if start < 0 or start > len(result):
            raise ValueError("hunk start out of range: -%d,%d" % (a, b))
        if start < prev_end:
            raise ValueError("overlapping/out-of-order hunks")
        pos = start
        orig_count = 0
        new_count = 0
        for bl in h["body"]:
            if bl.startswith("\\"):
                continue
            if bl.startswith(" ") or bl == "":
                content = bl[1:] if bl.startswith(" ") else ""
                if pos >= len(result) or result[pos] != content:
                    raise ValueError("context mismatch: %r" % content)
                pos += 1
                orig_count += 1
                new_count += 1
            elif bl.startswith("-") and not bl.startswith("---"):
                content = bl[1:]
                if pos >= len(result) or result[pos] != content:
                    raise ValueError("context mismatch: %r" % content)
                del result[pos]
                offset -= 1
                orig_count += 1
            elif bl.startswith("+") and not bl.startswith("+++"):
                content = bl[1:]
                result.insert(pos, content)
                pos += 1
                offset += 1
                new_count += 1
            elif bl.startswith("---") or bl.startswith("+++"):
                raise ValueError("unexpected header inside hunk: %r" % bl)
            else:
                raise ValueError("invalid diff line: %r" % bl)
        if orig_count != b:
            raise ValueError(
                "hunk orig count mismatch: header %d vs body %d" % (b, orig_count)
            )
        if new_count != d:
            raise ValueError(
                "hunk new count mismatch: header %d vs body %d" % (d, new_count)
            )
        prev_end = pos
    return "\n".join(result)
