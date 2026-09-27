from __future__ import annotations

import json
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


if __name__ == "__main__":
    unittest.main()
