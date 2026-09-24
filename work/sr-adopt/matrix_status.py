"""Status validator for a matrix-row ledger.

Keeps skillranker's four-string enum (validate_contract_matrix.py:38),
found by header name. skillranker also checks that a non-planned row names
resolvable unit tests (validate_contract_matrix.py:361-364). This file does
not. In jev that evidence check is lane-status.sh's trace join.

An unknown status or an empty ledger exits 1. A missing file or a missing
column exits 2. Exit 1 is never a traceback.
"""

import sys

DEFAULT_ENUM = ("planned", "executed", "passed", "failed")


def validate(rows, enum):
    allowed = set(enum)
    bad = []
    for i, row in enumerate(rows, start=1):
        status = row.get("status")
        if status not in allowed:
            bad.append(f"{i}:{status}")
    return bad


def load_tsv(path, column):
    lines = [
        line.rstrip("\n")
        for line in open(path, encoding="utf-8")
        if line.strip() and not line.startswith("#")
    ]
    if not lines:
        return []
    header = lines[0].split("\t")
    if column not in header:
        raise ValueError(f"no column {column}")
    index = header.index(column)
    rows = []
    for line in lines[1:]:
        cols = line.split("\t")
        status = cols[index] if index < len(cols) else ""
        rows.append({"status": status})
    return rows


def main(argv):
    column = "status"
    enum = list(DEFAULT_ENUM)
    args = argv[1:]
    while args and args[0].startswith("--"):
        flag = args.pop(0)
        if flag == "--column" and args:
            column = args.pop(0)
        elif flag == "--enum" and args:
            enum = [item for item in args.pop(0).split(",") if item]
        else:
            print(
                "usage: matrix_status.py [--column name] [--enum a,b] <ledger.tsv>",
                file=sys.stderr,
            )
            return 2
    if len(args) != 1:
        print(
            "usage: matrix_status.py [--column name] [--enum a,b] <ledger.tsv>",
            file=sys.stderr,
        )
        return 2
    try:
        rows = load_tsv(args[0], column)
    except FileNotFoundError:
        print(f"missing ledger: {args[0]}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not rows:
        print("empty ledger")
        return 1
    bad = validate(rows, enum)
    if bad:
        print("invalid status: " + " ".join(bad))
        return 1
    print(f"ok {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
