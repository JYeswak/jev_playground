from datetime import datetime, timedelta


def _match(field, lo, hi):
    if field == "*":
        return set(range(lo, hi + 1))
    vals = set()
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/")
            step = int(step)
            r = range(lo, hi + 1) if base == "*" else [int(base)]
            vals.update(r[::step])
        elif "-" in part:
            a, b = part.split("-")
            vals.update(range(int(a), int(b) + 1))
        else:
            vals.add(int(part))
    return vals


def next_fire(expr, after):
    mins = _match(expr.split()[0], 0, 59)
    hours = _match(expr.split()[1], 0, 23)
    t = after
    while True:
        if t.minute in mins and t.hour in hours:
            return t
        t += timedelta(minutes=1)
