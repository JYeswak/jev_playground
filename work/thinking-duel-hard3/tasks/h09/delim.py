def write_delim(path, rows, delim="|", none_as=""):
    with open(path, "w") as fh:
        for row in rows:
            fh.write(delim.join("" if v is None else v for v in row) + "\n")


def read_delim(path, delim="|", none_as=""):
    rows = []
    for line in open(path):
        rows.append(line.rstrip("\n").split(delim))
    return rows
