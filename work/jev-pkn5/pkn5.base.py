import json, re

RX = re.compile(
    r"git\+|github\.com|\.git\b|\*|latest|http://|postinstall|preinstall", re.I
)
for split in ["dev", "held"]:
    rows = json.load(open("var/agent-tmp/pkn5.%s.json" % split))
    tp = sum(
        1 for e in rows if RX.search(e["ver"] + " " + e["name"]) and e["removed_later"]
    )
    fp = sum(
        1
        for e in rows
        if RX.search(e["ver"] + " " + e["name"]) and not e["removed_later"]
    )
    fn = sum(
        1
        for e in rows
        if not RX.search(e["ver"] + " " + e["name"]) and e["removed_later"]
    )
    tn = sum(
        1
        for e in rows
        if not RX.search(e["ver"] + " " + e["name"]) and not e["removed_later"]
    )
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    acc = (tp + tn) / len(rows)
    print(
        "%s: tp=%d fp=%d fn=%d tn=%d prec=%.4f rec=%.4f acc=%.4f"
        % (split, tp, fp, fn, tn, prec, rec, acc)
    )
