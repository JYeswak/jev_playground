"""Select the fixed N=8 15-step OSWorld pool using result.txt only."""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from range_zip import archive_score, archive_url, list_root_archives, open_remote_zip

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pool.json"
N = 8

POOL_FILES = [
    "autoglm_15steps.zip",
    "claude-3-7-sonnet-20250219-15steps.zip",
    "claude-4-sonnet-20250514-15steps.zip",
    "claude-sonnet-4-5-20250929_15steps.zip",
    "doubao-1-5-thinking-vision-pro-250428-15step.zip",
    "jedi-7b-4o-15steps.zip",
    "jedi-7b-o3-15steps.zip",
    "kimi-vl-a3b-15step.zip",
]


def eligible_filename(path: str) -> bool:
    lower = path.lower()
    return (
        lower.endswith(".zip")
        and ("15step" in lower or "15steps" in lower)
        and "results_only" not in lower
    )


def main() -> None:
    candidates = POOL_FILES.copy()

    def inspect(filename: str) -> tuple[str, dict[str, object]]:
        url = archive_url(filename)
        archive, remote = open_remote_zip(url)
        try:
            rows, score = archive_score(archive, remote)
            if len(rows) != 361 or len(set(rows)) != 361:
                return "excluded", {
                    "archive": filename,
                    "reason": f"result rows={len(rows)}, expected 361",
                }
            return "record", {
                "archive": filename,
                "url": url,
                "tasks": len(rows),
                "score": score,
                "fetched_bytes": remote.fetched_bytes,
            }
        except Exception as exc:
            return "excluded", {"archive": filename, "reason": repr(exc)}
        finally:
            archive.close()

    records: list[dict[str, object]] = []
    excluded: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for kind, value in executor.map(inspect, candidates):
            (records if kind == "record" else excluded).append(value)
    if len(records) != N:
        raise SystemExit(
            f"eligible archives={len(records)} < N={N}; excluded={excluded}"
        )
    selected = records
    receipt = {
        "rule": "fixed POOL_FILES allowlist; each result.txt has exactly 361 rows; no score or trajectory selection",
        "n": N,
        "candidates_considered": candidates,
        "excluded": excluded,
        "eligible_in_preregistered_order": records,
        "selected": selected,
    }
    OUT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"selected": selected, "excluded": len(excluded)}, indent=2))


if __name__ == "__main__":
    main()
