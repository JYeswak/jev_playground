import re

_PAT = re.compile(
    r"P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)D)?"
    r"(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$"
)


def parse_duration(s):
    m = _PAT.match(s)
    if not m:
        raise ValueError(f"bad duration: {s!r}")
    y, mo, d, h, mi, sec = (int(v) if v else 0 for v in m.groups())
    return y * 365 * 86400 + mo * 30 * 86400 + d * 86400 + h * 3600 + mi * 60 + sec
