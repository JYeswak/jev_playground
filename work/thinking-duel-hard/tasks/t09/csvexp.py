def write_csv(path, rows):
    with open(path, "w") as fh:
        for row in rows:
            fh.write(",".join(row) + "\n")
