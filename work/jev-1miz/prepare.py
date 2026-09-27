#!/usr/bin/env python3
"""Build the jev-1miz blind-label manifest without persisting command text.

The gate log and the projected command files under var/agent-tmp remain local. The
committed manifest contains only row ids, command hashes, flag status, and sampling
provenance. Selection is fixed before either labeller sees a command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GATE_LOG = Path.home() / ".local/state/jev/gate-observe.jsonl"
DEFAULT_RAW_ROOT = ROOT / "var/agent-tmp/jev-1miz"
DEFAULT_OUT = ROOT / "work/jev-1miz"
SEED = 20260925
SAMPLE_SIZE = 200


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        row = json.loads(raw)
        if isinstance(row, dict):
            row["source_line"] = line_number
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-log", type=Path, default=DEFAULT_GATE_LOG)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = [
        row
        for row in read_rows(args.gate_log)
        if row.get("status") == "scored"
        and isinstance(row.get("cmd"), str)
        and isinstance(row.get("flag"), bool)
        and isinstance(row.get("cmdSha"), str)
    ]
    flagged = [row for row in rows if row["flag"] is True]
    unflagged = [row for row in rows if row["flag"] is False]
    if len(unflagged) < SAMPLE_SIZE:
        raise SystemExit(
            f"REFUSED: only {len(unflagged)} unflagged rows; need {SAMPLE_SIZE}"
        )

    rng = random.Random(SEED)
    sampled_unflagged = set(rng.sample(range(len(unflagged)), SAMPLE_SIZE))
    selected: list[tuple[dict[str, object], str]] = []
    unflagged_i = 0
    for row in rows:
        if row["flag"] is True:
            selected.append((row, "flagged"))
        else:
            if unflagged_i in sampled_unflagged:
                selected.append((row, "random-unflagged"))
            unflagged_i += 1

    args.raw_root.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    projected = []
    manifest = []
    for position, (row, source) in enumerate(selected):
        cmd_sha = str(row["cmdSha"])
        row_id = hashlib.sha256(f"{position}:{cmd_sha}".encode()).hexdigest()
        projected.append({"id": row_id, "command": row["cmd"]})
        manifest.append(
            {
                "id": row_id,
                "cmdSha": cmd_sha,
                "flag": bool(row["flag"]),
                "sample_source": source,
            }
        )

    raw_text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in projected
    )
    for name in ("commands-A.jsonl", "commands-B.jsonl"):
        (args.raw_root / name).write_text(raw_text, encoding="utf-8")
    manifest_text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in manifest)
    (args.out / "manifest.jsonl").write_text(manifest_text, encoding="utf-8")
    metadata = {
        "unit": "jev-1miz",
        "source_gate_log": str(args.gate_log),
        "source_gate_log_sha256": sha256_bytes(args.gate_log.read_bytes()),
        "source_scored_rows": len(rows),
        "flagged_rows": len(flagged),
        "unflagged_rows": len(unflagged),
        "random_seed": SEED,
        "random_unflagged_sample_size": SAMPLE_SIZE,
        "selected_rows": len(selected),
        "selected_flagged": sum(source == "flagged" for _, source in selected),
        "selected_random_unflagged": sum(
            source == "random-unflagged" for _, source in selected
        ),
        "manifest_sha256": sha256_bytes(manifest_text.encode()),
        "raw_projection_sha256": sha256_bytes(raw_text.encode()),
        "raw_projection_path": str(args.raw_root),
        "raw_projection_committed": False,
    }
    (args.out / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                k: metadata[k]
                for k in (
                    "source_scored_rows",
                    "flagged_rows",
                    "unflagged_rows",
                    "random_seed",
                    "random_unflagged_sample_size",
                    "selected_rows",
                    "manifest_sha256",
                )
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
