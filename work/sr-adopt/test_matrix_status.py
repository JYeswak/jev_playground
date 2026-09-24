"""Planted negatives: illegal status, empty ledger, missing file, wrong column."""

import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "work/sr-adopt/matrix_status.py"
TRACE = ROOT / "docs/demos/upstream-repro/status-score-trace-20260924.tsv"


def run(text=None, path=None, extra=None):
    if path is None:
        handle = tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False)
        handle.write(text)
        handle.close()
        path = handle.name
    cmd = ["python3", str(SCRIPT), *(extra or []), path]
    return subprocess.run(cmd, capture_output=True, text=True)


class MatrixStatusTest(unittest.TestCase):
    def test_legal_statuses_pass(self):
        result = run("id\tstatus\nrow\tplanned\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_done_is_rejected(self):
        result = run("id\tstatus\nrow\tdone\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("done", result.stdout)

    def test_empty_ledger_is_an_error(self):
        result = run("id\tstatus\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("empty ledger", result.stdout)

    def test_missing_file_exits_2(self):
        result = run(path="/tmp/jev-matrix-status-missing.tsv")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("missing ledger", result.stderr)

    def test_status_column_is_found_by_header(self):
        text = "id\tpriority\tstatus\nrow\tP1\tpassed\n"
        result = run(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        bad = run("id\tpriority\tstatus\nrow\tP1\tdone\n")
        self.assertEqual(bad.returncode, 1)
        self.assertIn("done", bad.stdout)
        self.assertNotIn("P1", bad.stdout)

    def test_trace_class_column_is_the_ledger(self):
        result = run(
            path=str(TRACE),
            extra=[
                "--column",
                "class",
                "--enum",
                "CITED,OTHER_RECEIPT,DERIVED,NOT_FOUND",
            ],
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ok ", result.stdout)


if __name__ == "__main__":
    unittest.main()
