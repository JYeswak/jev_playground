def load_table(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    header = lines[0].split(",")
    rows = []
    for line in lines[1:]:
        if line.strip():
            rows.append(dict(zip(header, line.split(","))))
    return rows
