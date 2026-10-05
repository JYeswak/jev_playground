import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILTER = ROOT / "work" / "jev-6pjh" / "stale_filter.jq"
START = "2026-10-02T16:44:40Z"
END = "2026-10-03T16:44:40Z"


class StaleFilterTests(unittest.TestCase):
    def count(self, rows, start=START, end=END):
        input_text = "".join(json.dumps(row) + "\n" for row in rows)
        result = subprocess.run(
            [
                "jq",
                "-s",
                "-f",
                str(FILTER),
                "--arg",
                "start",
                start,
                "--arg",
                "end",
                end,
            ],
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return int(result.stdout.strip())

    def test_observed_log_shapes_count_stale_markers_not_scored_rows(self):
        rows = [
            {
                "ts": START,
                "status": "NOT_RUN",
                "error": "reason=permission-required",
            },
            {
                "schema": "jev-injection-shadow.v1",
                "ts": START,
                "toolName": "bash",
                "status": "not-run",
                "reason": "recipient-and-data-class-approval-required",
                "error": None,
            },
            {"ts": START, "status": "scored", "reason": None, "error": None},
        ]

        self.assertEqual(self.count(rows), 2)

    def test_window_includes_start_and_excludes_end(self):
        rows = [
            {"ts": START, "status": "NOT_RUN", "error": "reason=permission-required"},
            {
                "ts": END,
                "status": "not-run",
                "reason": "recipient-and-data-class-approval-required",
            },
            {
                "ts": "2026-10-02T16:44:39Z",
                "status": "not-run",
                "error": "reason=permission-required",
            },
        ]

        self.assertEqual(self.count(rows), 1)


if __name__ == "__main__":
    unittest.main()
