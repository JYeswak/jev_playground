from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAP3_REFERENCE_SCHEMA = "jev-jzgm-cap3-reference-v1"
CAP3_REFERENCE_SHA256 = (
    "f4479a5d940ca0df44fe51b155b37ddbe8c14b90c742824da06293d3f1fffb59"
)
_ROW_FIELDS = {"turn_sha256", "received", "cut", "items"}
_HEX = frozenset("0123456789abcdef")


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in _HEX for char in value)
    )


def canonical_rows_bytes(rows: list[dict[str, Any]]) -> bytes:
    text = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
        for row in sorted(rows, key=lambda row: row["turn_sha256"])
    )
    return text.encode("utf-8")


def load_cap3_reference(
    manifest_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema") != CAP3_REFERENCE_SCHEMA
    ):
        raise ValueError("cap3 reference manifest has an unsupported schema")
    rows_name = manifest.get("rows_file")
    if rows_name != "cap3-reference.jsonl":
        raise ValueError("cap3 reference manifest names an unexpected rows file")
    expected_hash = manifest.get("rows_sha256")
    if expected_hash != CAP3_REFERENCE_SHA256:
        raise ValueError(
            "cap3 reference manifest SHA-256 differs from the preregistered bar"
        )
    rows_bytes = (manifest_path.parent / rows_name).read_bytes()
    actual_hash = hashlib.sha256(rows_bytes).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError("cap3 reference rows SHA-256 mismatch")

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(
        rows_bytes.decode("utf-8").splitlines(), start=1
    ):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"cap3 reference row {line_number} is invalid JSON"
            ) from exc
        if not isinstance(row, dict) or set(row) != _ROW_FIELDS:
            raise ValueError(f"cap3 reference row {line_number} has an invalid shape")
        turn_hash = row["turn_sha256"]
        if not _is_sha256(turn_hash) or turn_hash in seen:
            raise ValueError(
                f"cap3 reference row {line_number} has an invalid or duplicate turn hash"
            )
        seen.add(turn_hash)
        if any(
            isinstance(row[field], bool)
            or not isinstance(row[field], int)
            or row[field] < 0
            for field in ("received", "cut", "items")
        ):
            raise ValueError(f"cap3 reference row {line_number} has invalid totals")
        rows.append(row)

    expected_totals = {
        "turn_rows": len(rows),
        "sidecar_items": sum(row["items"] for row in rows),
        "received_tokens": sum(row["received"] for row in rows),
        "cut_tokens": sum(row["cut"] for row in rows),
    }
    for name, actual in expected_totals.items():
        expected = manifest.get(name)
        if isinstance(expected, bool) or expected != actual:
            raise ValueError(f"cap3 reference manifest {name} does not match its rows")
    if rows != sorted(rows, key=lambda row: row["turn_sha256"]):
        raise ValueError("cap3 reference rows are not in canonical turn-hash order")
    return manifest, rows


def compare_cap3_rows(
    expected: list[dict[str, Any]], observed: list[dict[str, Any]]
) -> dict[str, int | bool]:
    expected_by_turn = {row["turn_sha256"]: row for row in expected}
    observed_by_turn = {row["turn_sha256"]: row for row in observed}
    if len(expected_by_turn) != len(expected) or len(observed_by_turn) != len(observed):
        raise ValueError("cap3 per-turn comparison contains duplicate turn hashes")
    shared = expected_by_turn.keys() & observed_by_turn.keys()
    result = {
        "missing_turns": len(expected_by_turn.keys() - observed_by_turn.keys()),
        "extra_turns": len(observed_by_turn.keys() - expected_by_turn.keys()),
        "changed_turns": sum(
            expected_by_turn[turn] != observed_by_turn[turn] for turn in shared
        ),
    }
    result["matches_exactly"] = not any(result.values())
    return result


def cap3_turn_rows(
    turns: dict[tuple[Any, ...], dict[str, int]],
) -> list[dict[str, Any]]:
    rows = []
    for key, totals in turns.items():
        turn_key = "\n".join("" if value is None else str(value) for value in key)
        rows.append(
            {
                "turn_sha256": hashlib.sha256(turn_key.encode("utf-8")).hexdigest(),
                **totals,
            }
        )
    return sorted(rows, key=lambda row: row["turn_sha256"])


def _parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo is not None else None


def cap3_reference_report(
    manifest_path: Path,
    legacy_path: Path,
    observed_rows: list[dict[str, Any]],
    start: datetime,
    end: datetime,
) -> dict[str, dict[str, Any]]:
    manifest, expected_rows = load_cap3_reference(manifest_path)
    reference_window = manifest.get("window_utc")
    if not isinstance(reference_window, dict):
        raise TypeError("cap3 reference manifest UTC window must be an object")
    ref_start = _parse_utc(reference_window.get("from_inclusive"))
    ref_end = _parse_utc(reference_window.get("to_exclusive"))
    if ref_start is None or ref_end is None:
        raise ValueError("cap3 reference window bounds are invalid")
    window_matches = start == ref_start and end == ref_end

    observed = {
        "turns": len(observed_rows),
        "received_tokens": sum(row["received"] for row in observed_rows),
        "cut_tokens": sum(row["cut"] for row in observed_rows),
    }
    expected = {
        "turns": manifest["turn_rows"],
        "received_tokens": manifest["received_tokens"],
        "cut_tokens": manifest["cut_tokens"],
    }
    deltas = {key: observed[key] - expected[key] for key in expected}
    row_comparison = compare_cap3_rows(expected_rows, observed_rows)
    observed_hash = hashlib.sha256(canonical_rows_bytes(observed_rows)).hexdigest()
    frozen_match = (
        window_matches
        and row_comparison["matches_exactly"]
        and observed_hash == CAP3_REFERENCE_SHA256
        and all(delta == 0 for delta in deltas.values())
    )
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    if not isinstance(legacy, dict):
        raise TypeError("legacy aggregate cap3 reference must be an object")
    bounds = (
        legacy.get("window", "").split("..")
        if isinstance(legacy.get("window"), str)
        else []
    )
    legacy_start = _parse_utc(bounds[0]) if len(bounds) == 2 else None
    legacy_end = _parse_utc(bounds[1]) if len(bounds) == 2 else None
    legacy_window_matches = (
        legacy_start == start and legacy_end == end
        if legacy_start is not None and legacy_end is not None
        else False
    )
    legacy_values = {
        "turns": legacy.get("turns"),
        "received_tokens": legacy.get("received"),
        "cut_tokens": legacy.get("cut"),
    }
    legacy_deltas = {
        key: observed[key] - value if isinstance(value, int) else None
        for key, value in legacy_values.items()
    }
    legacy_match = legacy_window_matches and all(
        delta == 0 for delta in legacy_deltas.values()
    )
    return {
        "frozen_reference": {
            "window": reference_window,
            "rows_sha256": manifest["rows_sha256"],
            "source_log_sha256": manifest["source_logs"],
            "observed_rows_sha256": observed_hash,
            "observed_minus_reference": deltas,
            "window_matches": window_matches,
            "per_turn_comparison": row_comparison,
            "matches_exactly": frozen_match,
        },
        "legacy_aggregate_reference": {
            "window": legacy.get("window"),
            **legacy_values,
            "observed_minus_reference": legacy_deltas,
            "window_matches": legacy_window_matches,
            "matches_exactly": legacy_match,
        },
    }
