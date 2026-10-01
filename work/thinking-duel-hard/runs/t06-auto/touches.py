def touched_ranks(value, hits):
    ranks = set()
    for i, hit in enumerate(hits):
        if not hit or not value:
            continue
        if value == hit or value.endswith("/" + hit) or hit in value:
            ranks.add(i + 1)
    return sorted(ranks)
