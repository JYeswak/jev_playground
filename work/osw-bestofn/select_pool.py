"""Select the fixed N=8 15-step OSWorld pool using result.txt only."""

from __future__ import annotations

import json
import re
from pathlib import Path

from range_zip import archive_score, archive_url, list_root_archives, open_remote_zip

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pool.json"
N = 8


def eligible_filename(path: str) -> bool:
    lower = path.lower()
    return (
        lower.endswith(".zip")
        and ("15step" in lower or "15steps" in lower)
        and "results_only" not in lower
    )


def main() -> None:
    candidates = sorted(
        str(row["path"])
        for row in list_root_archives()
        if eligible_filename(str(row["path"]))
    )
    records: list[dict[str, object]] = []
    excluded: list[dict[str, str]] = []
    for filename in candidates:
        url = archive_url(filename)
        archive, remote = open_remote_zip(url)
        try:
            rows, score = archive_score(archive, remote)
            if len(rows) != 361 or len(set(rows)) != 361:
                excluded.append(
                    {
                        "archive": filename,
                        "reason": f"result rows={len(rows)}, expected 361",
                    }
                )
                continue
            records.append(
                {
                    "archive": filename,
                    "url": url,
                    "tasks": len(rows),
                    "score": score,
                    "fetched_bytes": remote.fetched_bytes,
                }
            )
        except Exception as exc:
            excluded.append({"archive": filename, "reason": repr(exc)})
        finally:
            archive.close()
    records.sort(key=lambda row: (-int(row["score"]), str(row["archive"])))
    if len(records) < N:
        raise SystemExit(f"eligible archives={len(records)} < N={N}")
    selected = records[:N]
    receipt = {
        "rule": "root .zip names containing 15step/15steps, excluding results_only; result.txt has exactly 361 rows; sort score descending then filename; take first N=8",
        "n": N,
        "candidates_considered": candidates,
        "excluded": excluded,
        "eligible_sorted": records,
        "selected": selected,
    }
    OUT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"selected": selected, "excluded": len(excluded)}, indent=2))


if __name__ == "__main__":
    main()
