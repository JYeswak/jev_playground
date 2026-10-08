from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "shadow_report", Path(__file__).with_name("shadow-report.py")
)
assert _spec and _spec.loader
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
build_report = _module.build_report
write_outputs = _module.write_outputs
webscreen_report = _module.webscreen_report


class ShadowReportTests(unittest.TestCase):
    def write(self, root: Path, name: str, rows: list[dict]) -> Path:
        path = root / name
        path.write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        return path

    def test_gate_matrix_spend_latency_and_hash_only_disagreement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shadow = self.write(
                root,
                "shadow.jsonl",
                [
                    {
                        "status": "scored",
                        "cmdSha": "a" * 64,
                        "jevFlag": True,
                        "latencyMs": 100,
                        "tokens": {"input_tokens": 10, "output_tokens": 2},
                    },
                    {
                        "status": "scored",
                        "cmdSha": "b" * 64,
                        "jevFlag": False,
                        "latencyMs": 300,
                        "tokens": {"input_tokens": 20, "output_tokens": 3},
                    },
                ],
            )
            existing = self.write(
                root,
                "existing.jsonl",
                [
                    {"status": "scored", "cmdSha": "a" * 64, "flag": False},
                    {"status": "scored", "cmdSha": "b" * 64, "flag": False},
                ],
            )
            report = build_report(
                shadow,
                existing,
                root / "missing.jsonl",
                root / "missing-injection.jsonl",
                sample_size=2,
            )
            gate = report["gate"]
            self.assertEqual(gate["matrix_2x2"]["jev_true_existing_false"], 1)
            self.assertEqual(gate["spend"]["input_tokens"], 30)
            self.assertEqual(gate["latency_ms"]["p50"], 300)
            self.assertEqual(
                gate["disagreements"],
                [{"cmdSha": "a" * 64, "existingFlag": False, "jevFlag": True}],
            )

    def test_web_report_counts_answer_and_rank_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            web = self.write(
                root,
                "web.jsonl",
                [
                    {
                        "status": "answered",
                        "pickIndex": 0,
                        "providerRank1Index": 0,
                        "openedPick": True,
                        "openedRank1": True,
                        "latencyMs": 100,
                    },
                    {
                        "status": "answered",
                        "pickIndex": 1,
                        "providerRank1Index": 0,
                        "openedPick": False,
                        "openedRank1": True,
                        "latencyMs": 200,
                    },
                ],
            )
            report = build_report(
                root / "missing.jsonl",
                root / "missing2.jsonl",
                web,
                root / "missing-injection.jsonl",
            )
            self.assertEqual(report["web_search_rerank"]["answered"], 2)
            self.assertEqual(report["web_search_rerank"]["pick_equals_rank1"], 1)
            self.assertEqual(report["web_search_rerank"]["opened_pick"], 1)

    def test_fake_clock_cap_rows_are_excluded_and_counted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            injection = self.write(
                root,
                "injection.jsonl",
                [
                    {"ts": "2026-09-27T00:00:00.000Z", "status": "cap"},
                    {"ts": "2026-09-27T00:00:00.000Z", "status": "cap"},
                    {
                        "ts": "2026-09-27T10:00:00.000Z",
                        "status": "scored",
                        "flag": False,
                        "latencyMs": 10,
                        "tokens": {"input_tokens": 2},
                    },
                ],
            )
            report = build_report(root / "a", root / "b", root / "c", injection)
            shadow = report["injection_shadow"]
            self.assertEqual(shadow["excluded_test_rows"], 2)
            self.assertEqual(shadow["status_counts"], {"scored": 1})


    def test_approval_markers_are_counted_across_reason_and_error_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate_observe = self.write(
                root,
                "gate-observe.jsonl",
                [
                    {
                        "ts": "2026-10-02T16:51:28.967Z",
                        "status": "not-run",
                        "error": "NOT_RUN reason=permission-required",
                    },
                    {"ts": "2026-10-04T00:00:00Z", "status": "scored"},
                ],
            )
            injection = self.write(
                root,
                "injection-shadow.jsonl",
                [
                    {
                        "ts": "2026-10-02T16:51:15.840Z",
                        "status": "cap",
                        "reason": "recipient-and-data-class-approval-required",
                    },
                    {"ts": "2026-10-04T00:00:00Z", "status": "scored"},
                ],
            )
            report = build_report(
                root / "missing-shadow.jsonl",
                gate_observe,
                root / "missing-web.jsonl",
                injection,
            )
            self.assertEqual(report["gate"]["existing_approval_marker_rows"], 1)
            self.assertEqual(report["injection_shadow"]["approval_marker_rows"], 1)

    def test_output_names_are_latest_or_explicit_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = build_report(
                root / "missing-a",
                root / "missing-b",
                root / "missing-c",
                root / "missing-injection.jsonl",
            )
            latest, latest_disagreements = write_outputs(report, root, "latest")
            snapshot, snapshot_disagreements = write_outputs(
                report, root, "report-20990101"
            )
            self.assertEqual(latest.name, "latest.json")
            self.assertEqual(latest_disagreements.name, "disagreements-latest.jsonl")
            self.assertEqual(snapshot.name, "report-20990101.json")
            self.assertEqual(
                snapshot_disagreements.name, "disagreements-20990101.jsonl"
            )

    def test_missing_logs_are_empty_not_raw_or_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = build_report(
                root / "missing-a",
                root / "missing-b",
                root / "missing-c",
                root / "missing-injection.jsonl",
            )
            self.assertEqual(report["gate"]["scored_rows"], 0)
            self.assertEqual(report["web_search_rerank"]["answered"], 0)

    def test_webscreen_report_excludes_pre_fix_rows_and_reports_window(self) -> None:
        # Captured records from ~/.local/state/jev/webscreen-shadow.jsonl; payload text is absent.
        rows = [
            {
                "ts": "2026-09-27T00:35:52.237Z",
                "toolName": "web_extract",
                "rawSha256": "2345a12b2fe72060afdce9e486fcb0f5e625db6fd4293b27077562f1f910372f",
                "units": 1,
                "flagged": 0,
                "topScore": 0.03,
                "latencyMs": 751,
                "input_tokens": 352,
                "output_tokens": 22,
                "status": "ok",
                "model": "jev-1.13.0",
                "cap": 100,
            },
            {
                "ts": "2026-09-27T06:41:24.159Z",
                "toolName": "web_search",
                "rawSha256": "1df75d8c4ac822f7b51125ef84aa54e3a701cb14167720a4e3c463b6b78225d3",
                "units": 1,
                "flagged": 0,
                "topScore": 0.03,
                "latencyMs": 142,
                "input_tokens": 741,
                "output_tokens": 22,
                "status": "ok",
                "model": "jev-1.13.0",
                "cap": 100,
            },
            {
                "ts": "2026-09-28T04:25:37.142Z",
                "toolName": "web_search",
                "rawSha256": "adb38b38baba8a71f82ab327f7176e7a1195d931278c360ada0bd119c7e89f02",
                "units": 1,
                "flagged": 0,
                "topScore": None,
                "latencyMs": 0,
                "input_tokens": None,
                "output_tokens": None,
                "status": "fail_open",
                "model": "jev-1.13.0",
                "cap": 100,
            },
        ]
        report = webscreen_report(rows, as_of="2026-09-28T06:41:24.159Z")
        self.assertEqual(report["rows"], 2)
        self.assertEqual(report["excluded_pre_fix_rows"], 1)
        self.assertEqual(report["status_counts"], {"fail_open": 1, "ok": 1})
        self.assertEqual(report["input_tokens"], 741)
        self.assertAlmostEqual(report["input_cost_usd_known"], 741 * 0.042 / 1_000_000)
        self.assertEqual(report["usage_missing_rows"], 1)
        self.assertFalse(report["spend_complete"])
        self.assertFalse(report["window_complete_24h"])
        self.assertAlmostEqual(report["report_age_hours"], 24.0)
        self.assertLess(report["window_elapsed_hours"], 24.0)
        self.assertNotIn("rawSha256", json.dumps(report))

    def test_webscreen_report_uses_answered_unit_denominator(self) -> None:
        # Arithmetic-only fixture; these values are not a Jev/model observation.
        rows = [
            {
                "ts": "2026-09-27T06:41:24.159Z",
                "units": 2,
                "flagged": 1,
                "status": "ok",
                "latencyMs": 100,
                "input_tokens": 100,
                "output_tokens": 10,
                "model": "jev-1.13.0",
            },
            {
                "ts": "2026-09-27T07:41:24.159Z",
                "units": 1,
                "flagged": 0,
                "status": "ok",
                "latencyMs": 200,
                "input_tokens": 200,
                "output_tokens": 20,
                "model": "jev-1.13.0",
            },
            {
                "ts": "2026-09-27T08:41:24.159Z",
                "units": 3,
                "flagged": 0,
                "status": "fail_open",
                "latencyMs": None,
                "input_tokens": None,
                "output_tokens": None,
                "model": "jev-1.13.0",
            },
        ]
        report = webscreen_report(rows, as_of="2026-09-28T06:41:24.159Z")
        self.assertEqual(report["flagged_rows"], 1)
        self.assertEqual(report["answered_rows"], 2)
        self.assertEqual(report["flagged_units"], 1)
        self.assertEqual(report["answered_units"], 3)
        self.assertAlmostEqual(report["flag_rate_per_unit"], 1 / 3)
        self.assertEqual(report["status_counts"], {"fail_open": 1, "ok": 2})
        # Timestamp-only plumbing control verifies the exact 24 h boundary.
        window_rows = [
            {"ts": "2026-09-29T12:00:00Z", "status": "ok", "units": 1, "flagged": 0},
            {"ts": "2026-09-30T12:00:00Z", "status": "ok", "units": 1, "flagged": 0},
        ]
        complete = webscreen_report(window_rows, as_of="2026-09-30T12:00:00Z")
        self.assertEqual(complete["window_elapsed_hours"], 24.0)
        self.assertTrue(complete["window_complete_24h"])


    def test_cli_web_shadow_argument_reports_answered_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            web = self.write(
                root,
                "web.jsonl",
                [{
                    "status": "answered",
                    "pickIndex": 0,
                    "providerRank1Index": 0,
                    "openedPick": True,
                    "openedRank1": True,
                    "latencyMs": 100,
                }],
            )
            empty = self.write(root, "empty.jsonl", [])
            output_dir = root / "report"
            command = [
                sys.executable,
                str(Path(__file__).with_name("shadow-report.py")),
                "--gate-shadow", str(empty),
                "--gate-observe", str(empty),
                "--web-shadow", str(web),
                "--injection-shadow", str(empty),
                "--webscreen-shadow", str(empty),
                "--out-dir", str(output_dir),
            ]
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            report = json.loads(Path(payload["report"]).read_text(encoding="utf-8"))
            self.assertEqual(report["web_search_rerank"]["answered"], 1)
if __name__ == "__main__":
    unittest.main()
