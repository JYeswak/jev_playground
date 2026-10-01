import re

_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def apply_patch(original, diff):
    if original == "":
        orig_lines = []
    else:
        orig_lines = original.split("\n")
    out = []
    orig_idx = 0
    lines = diff.split("\n")
    n = len(lines)
    i = 0
    while i < n:
        raw = lines[i]
        m = _HUNK.match(raw)
        if not m:
            i += 1
            continue
        a = int(m.group(1))
        ab = int(m.group(2)) if m.group(2) is not None else 1
        # new-file start/count parsed for count validation only;
        # positioning always uses the ORIGINAL coordinates + offset accumulator
        cd = int(m.group(4)) if m.group(4) is not None else 1
        if ab == 0:
            start0 = a
        else:
            start0 = a - 1
        if start0 < 0 or start0 > len(orig_lines) or start0 < orig_idx:
            raise ValueError(f"bad hunk position: {raw!r}")
        out.extend(orig_lines[orig_idx:start0])
        orig_idx = start0
        need_orig = ab
        need_new = cd
        cons_orig = 0
        prod_new = 0
        i += 1
        while i < n and (cons_orig < need_orig or prod_new < need_new):
            dl = lines[i]
            if dl.startswith("\\"):
                i += 1
                continue
            if dl == "":
                # blank context line encoded bare (content ""); the
                # trailing "" from a final newline never reaches here
                # because a satisfied hunk already exited the loop.
                if orig_idx >= len(orig_lines) or orig_lines[orig_idx] != "":
                    raise ValueError("context mismatch on blank line")
                out.append("")
                orig_idx += 1
                cons_orig += 1
                prod_new += 1
                i += 1
                continue
            prefix = dl[0]
            content = dl[1:]
            if prefix == " ":
                if cons_orig >= need_orig or prod_new >= need_new:
                    raise ValueError(f"hunk overfull: {raw!r}")
                if orig_idx >= len(orig_lines) or orig_lines[orig_idx] != content:
                    raise ValueError(
                        f"context mismatch: expected {orig_lines[orig_idx]!r} "
                        f"got {content!r}"
                    )
                out.append(content)
                orig_idx += 1
                cons_orig += 1
                prod_new += 1
            elif prefix == "-":
                if cons_orig >= need_orig:
                    raise ValueError(f"hunk overfull: {raw!r}")
                if orig_idx >= len(orig_lines) or orig_lines[orig_idx] != content:
                    raise ValueError(
                        f"removal mismatch: expected {orig_lines[orig_idx]!r} "
                        f"got {content!r}"
                    )
                orig_idx += 1
                cons_orig += 1
            elif prefix == "+":
                if prod_new >= need_new:
                    raise ValueError(f"hunk overfull: {raw!r}")
                out.append(content)
                prod_new += 1
            else:
                raise ValueError(f"bad diff line: {dl!r}")
            i += 1
        if cons_orig != need_orig or prod_new != need_new:
            raise ValueError(f"hunk length mismatch: {raw!r}")
    out.extend(orig_lines[orig_idx:])
    return "\n".join(out)
