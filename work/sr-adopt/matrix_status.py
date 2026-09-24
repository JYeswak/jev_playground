"""Status validator for a matrix-row ledger.

Adopted from skillranker@a6f1ff0 scripts/validate_contract_matrix.py:38
VALID_STATUSES and tests/contract_matrix.toml:10 (status is a declaration,
not a receipt). An unknown status exits 1. Score 0 and a missing file exit 2.
"""

import sys

VALID_STATUSES = {"planned", "executed", "passed", "failed"}


def validate(rows):
    bad = []
    for i, row in enumerate(rows, start=1):
        status = row.get("status")
        if status not in VALID_STATUSES:
            bad.append(f"{i}:{status}")
    return bad


def load_tsv(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("id\t"):
            continue
        cols = line.split("\t")
        if len(cols) < 2:
            rows.append({"id": cols[0], "status": ""})
            continue
        rows.append({"id": cols[0], "status": cols[1]})
    return rows


def main(argv):
    if len(argv) != 2:
        print("usage: matrix_status.py <ledger.tsv>", file=sys.stderr)
        return 2
    bad = validate(load_tsv(argv[1]))
    if bad:
        print("invalid status: " + " ".join(bad))
        return 1
    print(f"ok {len(load_tsv(argv[1]))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
