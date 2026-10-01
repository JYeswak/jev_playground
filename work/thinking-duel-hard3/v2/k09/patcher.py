def apply_patch(original, diff):
    lines = original.split("\n")
    for dl in diff.split("\n"):
        if dl.startswith("+") and not dl.startswith("+++"):
            lines.append(dl[1:])
    return "\n".join(lines)
