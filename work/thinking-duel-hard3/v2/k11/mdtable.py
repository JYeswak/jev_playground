def parse(text):
    for i, line in enumerate(text.split("\n")):
        if "|" in line:
            header = [c.strip() for c in line.strip("|").split("|")]
            rows = []
            for dl in text.split("\n")[i + 2 :]:
                if "|" not in dl:
                    break
                rows.append(
                    dict(zip(header, [c.strip() for c in dl.strip("|").split("|")]))
                )
            return rows
    return []
