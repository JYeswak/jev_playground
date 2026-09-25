"""scripts/jev-state-size.py (bead jev-9gtw.2 follow-up). Keyless.

The behavioural claim is checked on real outcomes, not invented ones: the committed calibration
table holds, for each of the 337 requests of the 2026-09-25 OSWorld run, the compact bytes sent
and whether the API answered or refused with max_tokens_exceeded. The CLI tests use padded
states only to exercise byte counting, key naming and exit codes.
"""

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parents[1] / "scripts" / "jev-state-size.py"
TABLE = HERE / "calibration-osworld-r3.tsv"

spec = importlib.util.spec_from_file_location("jev_state_size", SCRIPT)
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)


def table_rows():
    with TABLE.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


class OnRealOutcomes(unittest.TestCase):
    def setUp(self):
        self.band = ss.ratio_band(TABLE)
        self.rows = table_rows()

    def verdict(self, row):
        return ss.classify(
            int(row["state_bytes"]) + int(row["question_bytes"]), self.band
        )

    def test_the_table_is_the_run_it_claims(self):
        outcomes = [r["outcome"] for r in self.rows]
        self.assertEqual(len(self.rows), 337)
        self.assertEqual(outcomes.count("max_tokens_exceeded"), 12)
        self.assertEqual(outcomes.count("answered"), 325)

    def test_no_refused_request_is_called_fits(self):
        refused = [
            r["task"] for r in self.rows if r["outcome"] == "max_tokens_exceeded"
        ]
        self.assertEqual(
            [t for t in refused if self.verdict(self.table(t)) == "FITS"], []
        )

    def test_every_request_called_fits_was_answered(self):
        fits = [r for r in self.rows if self.verdict(r) == "FITS"]
        self.assertTrue(fits)
        self.assertEqual({r["outcome"] for r in fits}, {"answered"})

    def test_no_answered_request_is_called_over(self):
        over = [r for r in self.rows if self.verdict(r) == "OVER"]
        self.assertEqual({r["outcome"] for r in over}, {"max_tokens_exceeded"})

    def test_the_old_planning_ratio_would_have_let_refusals_through(self):
        # The Emerald and OSWorld budgets estimated tokens as bytes / 4. With that ratio the
        # check calls refused requests FITS, which is why the band comes from billed tokens.
        through = [
            r
            for r in self.rows
            if r["outcome"] != "answered"
            and ss.classify(
                int(r["state_bytes"]) + int(r["question_bytes"]), (4.0, 4.0)
            )
            == "FITS"
        ]
        self.assertGreater(len(through), 0)

    def table(self, task):
        return next(r for r in self.rows if r["task"] == task)


class Cli(unittest.TestCase):
    def run_cli(self, lines, *extra, calibration=TABLE):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "states.jsonl"
            path.write_text(
                "".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8"
            )
            return subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(path),
                    "--calibration",
                    str(calibration),
                    *extra,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

    def test_small_states_fit_and_exit_zero(self):
        done = self.run_cli(
            [{"task": "a", "text": "x" * 100}, {"task": "b", "text": "y" * 200}]
        )
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("FITS 2, NEAR 0, OVER 0", done.stdout)

    def test_an_oversized_state_is_named_and_exits_one(self):
        done = self.run_cli(
            [{"task": "small", "t": "x"}, {"task": "huge", "t": "x" * 90_000}]
        )
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertRegex(done.stdout, r"(?m)^OVER\thuge\t")
        self.assertNotIn("small", done.stdout.split("\n", 1)[1])

    def test_question_bytes_count_toward_the_limit(self):
        state = [{"task": "edge", "t": "x" * 40_000}]
        self.assertEqual(self.run_cli(state).returncode, 0)
        self.assertEqual(self.run_cli(state, "--question-bytes", "20000").returncode, 1)

    def test_field_reads_a_nested_state_and_missing_field_is_not_run(self):
        done = self.run_cli(
            [{"task": "a", "state": {"t": "x" * 90_000}}], "--field", "state"
        )
        self.assertEqual(done.returncode, 1)
        done = self.run_cli([{"task": "a"}], "--field", "state")
        self.assertEqual(done.returncode, 2)
        self.assertIn("NOT_RUN", done.stdout)

    def test_missing_calibration_is_not_run(self):
        done = self.run_cli([{"t": "x"}], calibration=Path("/nonexistent/table.tsv"))
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stdout.startswith("NOT_RUN"), done.stdout)

    def test_bytes_are_compact_utf8_like_json_stringify(self):
        self.assertEqual(
            ss.compact_bytes({"a": "é", "b": [1, 2]}),
            len('{"a":"é","b":[1,2]}'.encode()),
        )


if __name__ == "__main__":
    unittest.main()
