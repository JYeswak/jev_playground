from datetime import timedelta


def _parse_field(field, lo, hi):
    if field == "*":
        return set(range(lo, hi + 1))
    vals = set()
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/")
            step = int(step)
            if base == "*":
                vals.update(range(lo, hi + 1, step))
            else:
                a, b = base.split("-")
                vals.update(range(int(a), int(b), int(step)))
        elif "-" in part:
            a, b = part.split("-")
            vals.update(range(int(a), int(b) + 1))
        else:
            vals.add(int(part))
    return vals


def next_fire(expr, after):
    mi, hr, dom, mon, dow = (
        _parse_field(f, lo, hi)
        for f, (lo, hi) in zip(
            expr.split(), [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
        )
    )
    cand = after.replace(second=0, microsecond=0)
    for _ in range(366 * 24 * 60):
        if (
            cand.minute in mi
            and cand.hour in hr
            and cand.month in mon
            and cand.day in dom
            and (cand.weekday() + 1) % 7 in dow
        ):
            return cand
        cand += timedelta(minutes=1)
    raise ValueError("no fire time")
