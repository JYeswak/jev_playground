import re

_HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def apply_patch(original, diff):
    if original == "":
        result = []
    else:
        result = original.split("\n")

    diff_lines = diff.split("\n")
    # Drop single trailing empty element from final newline.
    if diff_lines and diff_lines[-1] == "":
        diff_lines.pop()

    offset = 0
    prev_old_end = 0  # exclusive, in original coordinates (0 means before line 1)
    i = 0
    n = len(diff_lines)
    while i < n:
        line = diff_lines[i]
        if line.startswith("@@"):
            m = _HUNK_RE.match(line)
            if not m:
                raise ValueError("bad hunk header: %r" % line)
            old_start = int(m.group(1))
            old_count = int(m.group(2)) if m.group(2) is not None else 1
            # new_start/new_count parsed for count validation only;
            # positioning uses the ORIGINAL (-a) side plus offset.
            new_count = int(m.group(4)) if m.group(4) is not None else 1
            if old_count < 0 or new_count < 0:
                raise ValueError("negative hunk count")
            if old_count > 0 and old_start < 1:
                raise ValueError("bad old start: %r" % line)
            if old_count == 0 and old_start < 0:
                raise ValueError("bad old start: %r" % line)
            if old_start < prev_old_end:
                raise ValueError("hunks out of order or overlapping")
            i += 1
            body = []
            old_seen = 0
            new_seen = 0
            while i < n and (old_seen < old_count or new_seen < new_count):
                bl = diff_lines[i]
                if bl.startswith("\\"):
                    # "\ No newline at end of file" marker: ignore.
                    i += 1
                    continue
                if bl.startswith("@@"):
                    break
                if bl == "" and old_seen < old_count and new_seen < new_count:
                    # Tolerate a bare empty line as empty context line.
                    body.append(" ")
                    old_seen += 1
                    new_seen += 1
                    i += 1
                    continue
                if not bl or bl[0] not in (" ", "-", "+"):
                    raise ValueError("bad hunk line: %r" % bl)
                if bl[0] == " ":
                    old_seen += 1
                    new_seen += 1
                elif bl[0] == "-":
                    old_seen += 1
                else:
                    new_seen += 1
                body.append(bl)
                i += 1
            if old_seen != old_count or new_seen != new_count:
                raise ValueError(
                    "hunk body counts %d/%d do not match header %d/%d"
                    % (old_seen, new_seen, old_count, new_count)
                )
            if old_count == 0:
                cur = old_start + offset
            else:
                cur = (old_start - 1) + offset
            if cur < 0 or cur + old_count > len(result):
                raise ValueError("hunk out of range")
            # Validate context/removals against current content.
            j = 0
            for bl in body:
                if bl[0] in (" ", "-"):
                    want = bl[1:]
                    if result[cur + j] != want:
                        raise ValueError(
                            "context mismatch at line %d: %r != %r"
                            % (cur + j + 1, result[cur + j], want)
                        )
                    j += 1
                # '+' lines consume no old slot.
            # Re-walk to build replacement preserving order.
            new_lines = []
            k = cur
            for bl in body:
                if bl[0] == " ":
                    new_lines.append(bl[1:])
                    k += 1
                elif bl[0] == "-":
                    k += 1
                else:
                    new_lines.append(bl[1:])
            result[cur : cur + old_count] = new_lines
            offset += len(new_lines) - old_count
            prev_old_end = old_start + old_count
        elif line.startswith("---") or line.startswith("+++"):
            i += 1
            continue
        elif line.startswith("\\"):
            i += 1
            continue
        elif line.strip() == "":
            # Blank separators between file sections (e.g. multiple
            # diffs concatenated); ignore outside hunks.
            i += 1
            continue
        elif line.startswith("diff ") or line.startswith("index "):
            i += 1
            continue
        else:
            raise ValueError("unexpected line outside hunk: %r" % line)
    return "\n".join(result)
