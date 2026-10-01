import csv
import io


def load_table(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    # Accept \n, \r\n, and lone-\r row separators. Normalize to \n
    # (embedded \r\n inside quoted fields normalizes to \n as well).
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        return []
    reader = csv.reader(io.StringIO(text))
    records = [
        r for r in reader if not (len(r) == 0 or (len(r) == 1 and r[0].strip() == ""))
    ]
    if not records:
        return []
    header = records[0]
    if len(records) == 1:
        return []
    rows = []
    for r in records[1:]:
        d = {h: (r[i] if i < len(r) else None) for i, h in enumerate(header)}
        if len(r) > len(header):
            d[None] = r[len(header) :]
        rows.append(d)
    return rows
