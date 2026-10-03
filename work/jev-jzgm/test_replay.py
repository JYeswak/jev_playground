from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
cap3 = importlib.import_module("cap3_reference")
replay = importlib.import_module("replay")


def test_committed_cap3_reference_rows_match_preregistered_hash_and_totals() -> None:
    manifest, rows = cap3.load_cap3_reference(HERE / "cap3-reference.json")

    assert manifest["rows_sha256"] == cap3.CAP3_REFERENCE_SHA256
    assert len(rows) == manifest["turn_rows"] == 179
    assert len({row["turn_sha256"] for row in rows}) == len(rows)
    assert sum(row["received"] for row in rows) == manifest["received_tokens"] == 166095
    assert sum(row["cut"] for row in rows) == manifest["cut_tokens"] == 846
    assert sum(row["items"] for row in rows) == manifest["sidecar_items"] == 3238


def test_cap3_reference_loader_rejects_changed_source_rows(tmp_path: Path) -> None:
    manifest = json.loads((HERE / "cap3-reference.json").read_text(encoding="utf-8"))
    source_rows = (HERE / manifest["rows_file"]).read_text(encoding="utf-8")
    changed = source_rows.replace('"received":1063', '"received":1064', 1)
    assert changed != source_rows
    (tmp_path / "cap3-reference.jsonl").write_text(changed, encoding="utf-8")
    manifest["rows_file"] = "cap3-reference.jsonl"
    (tmp_path / "cap3-reference.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="SHA-256"):
        cap3.load_cap3_reference(tmp_path / "cap3-reference.json")


def test_cap3_row_comparison_requires_identical_turns_and_values() -> None:
    _, expected = cap3.load_cap3_reference(HERE / "cap3-reference.json")
    assert cap3.compare_cap3_rows(expected, list(reversed(expected)))["matches_exactly"]

    changed = [dict(row) for row in expected]
    changed[0]["received"] += 1
    result = cap3.compare_cap3_rows(expected, changed)
    assert result == {
        "matches_exactly": False,
        "missing_turns": 0,
        "extra_turns": 0,
        "changed_turns": 1,
    }

    missing = cap3.compare_cap3_rows(expected, expected[:-1])
    assert missing["matches_exactly"] is False
    assert missing["missing_turns"] == 1
    assert missing["extra_turns"] == 0


def test_memory_report_counts_javascript_utf16_units(monkeypatch) -> None:
    rows = [
        {
            "instance": "emoji",
            "promptHash": "p1",
            "memoryHash": "m1",
            "memory": "😀" * 4,
        },
        {
            "instance": "surrogate",
            "promptHash": "p2",
            "memoryHash": "m2",
            "memory": "\ud800" * 4,
        },
    ]
    monkeypatch.setattr(
        replay,
        "read_main_memory",
        lambda *args: {
            "statuses": {},
            "observed_latency_ms_sum": 0,
            "observed_latency_rows": 0,
            "coverage": {},
            "rows": [],
            "malformed": 0,
        },
    )
    monkeypatch.setattr(
        replay, "sidecar_memory", lambda *args: ([], rows, 0, "synthetic")
    )

    report = replay.memory_report(
        HERE / "main.jsonl",
        HERE / "sidecar.jsonl",
        HERE.parent / "jev-i20b" / "n60-rows.json",
        HERE / "cap3-reference.json",
        HERE.parent / "jev-i20b" / "cap3-before.json",
        datetime(2026, 10, 1, 19, 45, tzinfo=timezone.utc),
        datetime(2026, 10, 2, 19, 45, tzinfo=timezone.utc),
        False,
    )
    assert report["cap3"]["observed"]["received_tokens"] == 3


def test_noop_memory_replays_policy_off_rows_and_computes_identity_deltas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    start = datetime(2026, 10, 1, 19, 45, tzinfo=timezone.utc)
    end = datetime(2026, 10, 2, 19, 45, tzinfo=timezone.utc)
    # Rehashed identifiers; payload is redacted while preserving the observed 47-char length.
    instance = "0fcad15ff97b8b844156e8d43b3d9ce1dbe438096f054f5dc652e4520b0d9adc"
    prompt_hash = "cc78b46cc8e512b63cf2858778eec891e4ed1f18d21bd4d0bc1ed2f9f637c467"
    memory_hash = "6db3743ba354b70e51d61ef5a8b2ee91a13d38100015c0087a61329db4977463"
    main_row = {
        "ts": "2026-10-02T19:41:57.620Z",
        "instance": instance,
        "promptHash": prompt_hash,
        "memoryHash": memory_hash,
        "status": "cap3-pruned",
        "latencyMs": None,
    }
    sidecar_row = {
        "ts": "2026-10-02T19:41:57.621Z",
        "instance": instance,
        "promptHash": prompt_hash,
        "memoryHash": memory_hash,
        "status": "cap3-pruned",
        "decision": "prune",
        "memory": "x" * 47,
    }
    monkeypatch.setattr(
        replay,
        "read_main_memory",
        lambda *args: {
            "statuses": {(instance, prompt_hash, memory_hash): "cap3-pruned"},
            "observed_latency_ms_sum": 0,
            "observed_latency_rows": 0,
            "coverage": {"first": main_row["ts"], "last": main_row["ts"], "rows": 1},
            "rows": [main_row],
            "malformed": 0,
        },
    )
    monkeypatch.setattr(
        replay,
        "sidecar_memory",
        lambda *args: ([], [sidecar_row], 0, "recorded-source"),
    )

    memory = replay.memory_report(
        HERE / "main.jsonl",
        HERE / "sidecar.jsonl",
        HERE.parent / "jev-i20b" / "n60-rows.json",
        HERE / "cap3-reference.json",
        HERE.parent / "jev-i20b" / "cap3-before.json",
        start,
        end,
        True,
    )["cap3"]

    assert memory["observed"]["cut_tokens"] == 11
    policy_off = memory["policy_off"]
    assert policy_off["baseline"] == {
        "turns": 1,
        "sidecar_items": 1,
        "received_tokens": 0,
        "cut_tokens": 11,
        "misses": None,
        "labeled_miss_rows": 0,
        "latency_ms": 0,
    }
    assert policy_off["replayed"] == policy_off["baseline"]
    assert (
        policy_off["misses_status"]
        == "unobserved: source logs have no blind harm labels"
    )
    assert memory["noop_delta"] == {
        "received_tokens": 0,
        "cut_tokens": 0,
        "misses": 0,
        "latency_ms": 0,
    }


def test_noop_gate_replays_policy_off_rows_and_computes_identity_deltas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    start = datetime(2026, 10, 3, 2, tzinfo=timezone.utc)
    end = datetime(2026, 10, 3, 3, tzinfo=timezone.utc)
    rows = [
        {
            "ts": "2026-10-03T02:00:21.967Z",
            "jevSkipped": True,
            "latencyMs": 1253,
            "status": "scored",
        },
        {
            "ts": "2026-10-03T02:37:30.149Z",
            "jevSkipped": False,
            "latencyMs": 144,
            "status": "scored",
        },
    ]
    monkeypatch.setattr(replay, "load_jsonl", lambda path: (rows, 0, "recorded-source"))

    gate = replay.gate_report(HERE / "gate-observe.jsonl", start, end, True)

    assert gate["eligible_screens"] == 2
    assert gate["free_screen_share"] == 0.5
    policy_off = gate["policy_off"]
    assert policy_off["baseline"] == {
        "eligible_screens": 2,
        "free_screens": 1,
        "free_screen_share": 0.5,
        "would_reach_paid_jev": 1,
        "misses": None,
        "labeled_miss_rows": 0,
        "latency_ms": 1397,
    }
    assert policy_off["replayed"] == policy_off["baseline"]
    assert gate["noop_delta"] == {
        "free_screen_share": 0,
        "would_reach_paid_jev": 0,
        "latency_ms": 0,
        "misses": 0,
    }
