from __future__ import annotations

import json
import tempfile
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MINER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MINER_DIR))

import miner

try:
    TASK = json.loads((MINER_DIR / "task.json").read_text(encoding="utf-8"))
    FIXTURE = MINER_DIR / TASK["fixture"]
    AS_OF = TASK["as_of"]
except (OSError, json.JSONDecodeError) as error:
    raise RuntimeError("invalid fleet-miner task or fixture path") from error


def fixture_rows():
    rows = []
    for line_number, line in enumerate(FIXTURE.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise AssertionError(f"invalid fixture JSON at line {line_number}") from error
    return rows


class MinerLabelsTest(unittest.TestCase):
    def test_result_readback_join_is_scoped_to_session_and_hash_only(self):
        rows = miner.extract_result_labels(fixture_rows(), AS_OF)

        self.assertEqual([row["label"] for row in rows], ["read_back", "not_read_back"])
        for row in rows:
            self.assertIsInstance(row["session_id_sha256"], str)
            self.assertEqual(len(row["session_id_sha256"]), 64)
            self.assertIsInstance(row["call_index"], int)
            self.assertEqual(
                set(row),
                {"session_id_sha256", "call_index", "artifact_sha256", "event_sha256", "label"},
            )

    def test_label_emitters_exclude_events_before_the_fourteen_day_window(self):
        rows = []
        for row in fixture_rows():
            older = dict(row)
            older["timestamp"] = "2026-09-19T00:40:00Z"
            rows.append(older)

        self.assertEqual(miner.extract_result_labels(rows, AS_OF), [])
        self.assertEqual(miner.extract_reread_events(rows, AS_OF), [])

    def test_as_of_drops_every_later_tool_call(self):
        calls = miner.tool_calls(fixture_rows(), AS_OF)

        self.assertFalse(any(call.path == "/fixture/after-cutoff.py" for call in calls))

    def test_reread_emits_raw_refetch_metadata_without_harm_or_label(self):
        rows = miner.extract_reread_events(fixture_rows(), AS_OF)

        self.assertEqual(len(rows), 3)
        self.assertEqual([row["calls_since_prior_read"] for row in rows], [1, 0, 1])
        for row in rows:
            self.assertEqual(
                set(row),
                {
                    "session_id_sha256",
                    "call_index",
                    "path_sha256",
                    "line_range",
                    "fetch_tool",
                    "calls_since_prior_read",
                },
            )

    def test_sed_in_place_write_invalidates_repeat_read_candidate(self):
        repeats = miner.classify_repeat_reads(fixture_rows(), AS_OF)

        self.assertEqual([row["is_redundant"] for row in repeats], [False, True, True])

    def test_missing_joined_outcome_is_not_counted(self):
        self.assertEqual(miner.label_status({"positives": 1}), "NOT_COUNTED")
        self.assertEqual(miner.label_status({"label": "positive"}), "COUNTED")

    def test_ca37_rows_reproduce_observed_label_counts(self):
        counts = miner.ca37_candidate_counts(ROOT / "work" / "jev-census" / "candidates.json")

        self.assertEqual(
            counts,
            {
                "vendor_paste": (0, 39),
                "skill_veto": (53, 200),
                "gate_cascade": (4, 102),
                "memory_filter": (75, 100),
            },
        )

    def test_decision_log_scalar_counts_accumulate_as_integer_values(self):
        stamp = "2026-10-05T14:56:20.781Z"
        metrics = miner.Metrics(miner._timestamp(stamp), miner._timestamp(stamp))

        metrics.process(
            {"ts": stamp, "status": "scored", "flag": False, "latencyMs": 858, "model": "nimble:latest"},
            "/fixture/.local/state/jev/gate-observe.jsonl",
        )

        self.assertEqual(miner._source_count("dl:gate-observe.jsonl:status=scored", metrics), 1)

    def test_rank_labels_count_touched_hit_rows_not_hit_entries(self):
        stamp = "2026-09-27T03:32:28.259Z"
        metrics = miner.Metrics(miner._timestamp("2026-09-20T00:48:27Z"), miner._timestamp(AS_OF))
        observed_hit_sha256 = "780bc12cbd4e805bf40a03d309f29f31d86a5eb0d8c58ceeb715636d40360ba8"

        metrics.process(
            {
                "ts": stamp,
                "nextToolCalls": [
                    {"ordinal": 5, "tool": "read", "touched": [observed_hit_sha256]},
                    {"ordinal": 6, "tool": "read", "touched": [observed_hit_sha256]},
                ],
            },
            "/fixture/.local/state/jev/find-rank.jsonl",
        )

        source = "k:421:find-rank.jsonl rows whose next calls touched a returned hit"
        self.assertEqual(miner._source_count(source, metrics), 1)

    def test_missing_golden_provenance_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            family = Path(directory) / "result"
            family.mkdir()
            (family / "labels.jsonl").write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "PROVENANCE.md"):
                miner.validate_golden_provenance(family)

    def test_golden_writer_records_and_checks_hash_only_rows(self):
        row = miner.extract_result_labels(fixture_rows(), AS_OF)[0]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result"
            with patch.dict("os.environ", {"UPDATE_GOLDENS": "1"}):
                miner._write_labels([row], "result", AS_OF, target)

            miner.validate_golden_provenance(target)
            saved = json.loads((target / "labels.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(saved, row)
            self.assertEqual(
                set(saved),
                {"session_id_sha256", "call_index", "artifact_sha256", "event_sha256", "label"},
            )
            (target / "labels.jsonl").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "sha256"):
                miner.validate_golden_provenance(target)



class MinerSafetyTest(unittest.TestCase):
    def test_empty_scan_set_fails_closed(self):
        result = miner.scan_files(
            [],
            AS_OF,
            load_average=lambda: 0.0,
            clock=lambda: 0.0,
        )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.complete_counts, {})
        self.assertEqual(result.counts, {"empty_input": 1})

    def test_load_above_80_defers_without_reading(self):
        result = miner.scan_files(
            [FIXTURE],
            AS_OF,
            load_average=lambda: 81.0,
            clock=lambda: 0.0,
            budget_seconds=3000.0,
        )

        self.assertEqual(result.verdict, "DEFERRED")
        self.assertEqual(result.files_read, ())
        self.assertEqual(result.files_not_read, (str(FIXTURE),))
        self.assertEqual(result.complete_counts, {})

    def test_load_crossing_limit_mid_file_stops_with_partial_verdict(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.jsonl"
            row = '{"timestamp":"2026-10-04T00:40:00Z","type":"observed"}\n'
            path.write_text(row * 16384, encoding="utf-8")
            loads = iter((0.0, 81.0))
            result = miner.scan_files(
                [path],
                AS_OF,
                load_average=lambda: next(loads),
                clock=lambda: 0.0,
            )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.files_read, ())
        self.assertEqual(result.files_not_read, (str(path),))
        self.assertNotIn("complete", result.counts)

    def test_budget_overrun_is_partial_and_names_unread_files(self):
        times = iter((0.0, 0.0, 1.1))
        result = miner.scan_files(
            [FIXTURE, FIXTURE],
            AS_OF,
            load_average=lambda: 0.0,
            clock=lambda: next(times),
            budget_seconds=1.0,
        )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.files_read, (str(FIXTURE),))
        self.assertEqual(result.files_not_read, (str(FIXTURE),))
        self.assertNotIn("complete", result.counts)

    def test_budget_above_cap_is_rejected_by_scanner_and_cli(self):
        with self.assertRaisesRegex(ValueError, "budget must be"):
            miner.scan_files(
                [FIXTURE],
                AS_OF,
                load_average=lambda: 0.0,
                clock=lambda: 0.0,
                budget_seconds=3000.1,
            )

        with self.assertRaises(SystemExit) as caught:
            miner._main([
                "--labels", "result",
                "--as-of", AS_OF,
                "--input", str(FIXTURE),
                "--budget-seconds", "3001",
            ])
        self.assertEqual(caught.exception.code, 2)

    def test_unreadable_file_makes_scan_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.jsonl"
            result = miner.scan_files(
                [FIXTURE, missing],
                AS_OF,
                load_average=lambda: 0.0,
                clock=lambda: 0.0,
            )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.files_read, (str(FIXTURE),))
        self.assertEqual(result.files_not_read, (str(missing),))
        self.assertNotIn("complete", result.counts)

    def test_invalid_json_never_yields_complete_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "malformed.jsonl"
            observed_session_row = FIXTURE.read_text(encoding="utf-8").splitlines()[0]
            path.write_text(observed_session_row + "\n{malformed\n", encoding="utf-8")
            result = miner.scan_files(
                [path],
                AS_OF,
                load_average=lambda: 0.0,
                clock=lambda: 0.0,
            )

        self.assertEqual(result.verdict, "PARTIAL")
        self.assertEqual(result.files_read, ())
        self.assertEqual(result.files_not_read, (str(path),))
        self.assertEqual(result.counts.get("invalid_json"), 1)

    def test_rank_reopens_at_thirty_positive_labels(self):
        report = miner.rank_report(
            {"outcome": {"occurrences": 10, "labels": 30, "positives": 30}},
            {"outcome": {"occurrences": 10, "labels": 29, "positives": 29}},
            AS_OF,
        )

        self.assertIn("| outcome | 10 | 10 | +0 | 30 | 29 | +1 | REOPEN |", report)
        self.assertIn(f"as_of: {AS_OF}", report)
        self.assertIn(f"command: nice -n 10 python3 work/fleet-schema/miner.py --rank --as-of {AS_OF} --json", report)

    def test_rank_report_is_written_as_utf8(self):
        report = miner.rank_report(
            {"outcome": {"occurrences": 10, "labels": 30}},
            {"outcome": {"occurrences": 10, "labels": 29}},
            AS_OF,
        )
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "RANK.md"

            miner.write_rank_report(report, destination)

            self.assertEqual(destination.read_text(encoding="utf-8"), report)


if __name__ == "__main__":
    unittest.main()
