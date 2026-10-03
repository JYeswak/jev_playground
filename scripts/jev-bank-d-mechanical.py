#!/usr/bin/env python3
"""Label a frozen D packet from exact later-session reuse, without semantic judgments."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "jev-bank-build.py"
SPEC = importlib.util.spec_from_file_location("jev_bank_build", BUILDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load builder from {BUILDER_PATH}")
BUILDER: Any = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def locate_sources(
    packet_ids: set[str], home: Path
) -> dict[str, tuple[Path, int, str]]:
    BUILDER.HOME = home
    found: dict[str, tuple[Path, int, str]] = {}
    for path in BUILDER.session_files():
        group = BUILDER.sha(str(path))
        for index, event in BUILDER.iter_jsonl(path):
            message = event.get("message")
            if not isinstance(message, dict) or message.get("role") != "toolResult":
                continue
            unit_id = BUILDER.sha(f"omp-session:{group}:{index}")
            if unit_id not in packet_ids:
                continue
            found[unit_id] = (path, index, BUILDER.text_of(message))
        if len(found) == len(packet_ids):
            break
    missing = packet_ids - found.keys()
    if missing:
        raise RuntimeError(f"Could not resolve {len(missing)} D sample source IDs")
    return found


def build_labels(packet_path: Path, home: Path) -> dict[str, Any]:
    packet_bytes = packet_path.read_bytes()
    try:
        packet = json.loads(packet_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid D packet JSON: {packet_path}") from exc
    if not isinstance(packet, dict):
        raise TypeError("D packet must be a JSON object")
    items = packet.get("items")
    if not isinstance(items, list):
        raise TypeError("D packet items must be a list")
    if len(items) != 50:
        raise ValueError("D mechanical labeling requires the frozen 50-row packet")
    if any(not isinstance(item, dict) for item in items):
        raise TypeError("D packet items must be objects")
    ids = [item.get("id") for item in items]
    if any(not isinstance(item_id, str) for item_id in ids):
        raise TypeError("D packet IDs must be strings")
    if len(set(ids)) != 50:
        raise ValueError("D packet IDs must be distinct")

    sources = locate_sources(set(ids), home)
    labels = {}
    for item_id in ids:
        path, source_line, source_text = sources[item_id]
        events = BUILDER.iter_jsonl(path)
        relevant = BUILDER.has_later_exact_reference(source_text, source_line, events)
        labels[item_id] = "relevant" if relevant else "not-relevant"

    return {
        "schema": "jev.d-mechanical-labels.v1",
        "label_source": BUILDER.D_LABEL_SOURCE,
        "label_definition": BUILDER.D_LABEL_DEFINITION,
        "packet_sha256": hashlib.sha256(packet_bytes).hexdigest(),
        "labels": labels,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--home", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.packet.is_file() or not args.home.is_dir():
        parser.error("--packet must be a file and --home must be a directory")
    if not args.output.parent.is_dir():
        parser.error("--output parent must already exist")

    result = build_labels(args.packet, args.home)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
    counts = {
        label: sum(value == label for value in result["labels"].values())
        for label in ("relevant", "not-relevant")
    }
    print(
        json.dumps(
            {
                "rows": len(result["labels"]),
                "counts": counts,
                "packet_sha256": result["packet_sha256"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
