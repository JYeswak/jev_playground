"""Planted negative: status `done` is not in the enum and must exit 1."""

import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "work/sr-adopt/matrix_status.py"


def run(text):
    with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as handle:
        handle.write(text)
        path = handle.name
    return subprocess.run(
        ["python3", str(SCRIPT), path],
        capture_output=True,
        text=True,
    )


class MatrixStatusTest(unittest.TestCase):
    def test_legal_statuses_pass(self):
        result = run("id\tstatus\nrow\tplanned\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_done_is_rejected(self):
        result = run("id\tstatus\nrow\tdone\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("done", result.stdout)


if __name__ == "__main__":
    unittest.main()
