import csv


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(
            fh, quoting=csv.QUOTE_MINIMAL, doublequote=True, lineterminator="\r\n"
        )
        w.writerows(rows)
