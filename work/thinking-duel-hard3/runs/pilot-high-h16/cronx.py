from datetime import datetime, timedelta


def _span(a, b, lo, hi):
    if a <= b:
        return list(range(a, b + 1))
    return list(range(a, hi + 1)) + list(range(lo, b + 1))


def _match(field, lo, hi):
    if field == "*":
        return set(range(lo, hi + 1))
    vals = set()
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/")
            step = int(step)
            if base == "*":
                vals.update(range(lo, hi + 1, step))
            elif "-" in base:
                a, b = base.split("-")
                vals.update(_span(int(a), int(b), lo, hi)[::step])
            else:
                vals.update(range(int(base), hi + 1, step))
        elif "-" in part:
            a, b = part.split("-")
            vals.update(_span(int(a), int(b), lo, hi))
        else:
            vals.add(int(part))
    return vals


def next_fire(expr, after):
    mins = _match(expr.split()[0], 0, 59)
    hours = _match(expr.split()[1], 0, 23)
    t = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    while True:
        if t.minute in mins and t.hour in hours:
            return t
        t += timedelta(minutes=1)
