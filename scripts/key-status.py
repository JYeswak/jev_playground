#!/usr/bin/env python3
"""Report whether TYPESAFE_API_KEY matches a committed revoked fingerprint."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVOKED_FILE = ROOT / "scripts" / "key-revoked.tsv"


def fingerprint(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def revoked_entry(path: Path, wanted: str) -> tuple[str, str] | None:
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip() or line.startswith("fingerprint\t"):
            continue
        fields = line.split("\t", 2)
        if len(fields) != 3:
            raise ValueError(
                f"{path} line {line_number}: expected fingerprint, date, reason"
            )
        if fields[0] == wanted:
            return fields[1], fields[2]
    return None


def main() -> int:
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not key:
        print("KEY: NOT_RUN (no TYPESAFE_API_KEY in env)")
        return 2
    path = Path(os.environ.get("KEY_STATUS_REVOKED_FILE", DEFAULT_REVOKED_FILE))
    try:
        match = revoked_entry(path, fingerprint(key))
    except (OSError, ValueError) as exc:
        print(f"KEY: NOT_RUN ({type(exc).__name__}: {exc})")
        return 2
    if match is None:
        print("KEY: OK (not on the revoked list)")
        return 0
    date, reason = match
    print(f"KEY: REVOKED (leaked {date}; {reason})")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
