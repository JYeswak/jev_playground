import fnmatch


def touched_ranks(value, hits):
    if not value:
        return []
    ranks = set()
    for i, hit in enumerate(hits):
        if not hit:
            continue
        if value == hit or value.endswith("/" + hit) or hit in value:
            ranks.add(i + 1)
            continue
        if ("*" in hit or "?" in hit or "[" in hit) and (
            fnmatch.fnmatchcase(value, hit) or fnmatch.fnmatchcase(value, "*/" + hit)
        ):
            ranks.add(i + 1)
    return sorted(ranks)
