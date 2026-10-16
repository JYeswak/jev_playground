"""Planted negatives for run.py --replay (jev-x1-injection-encoders-e2gp.1).

Every case copies the committed canonical bundle into a throwaway directory
and points the replay at the copies: canonical answers/RECEIPT files are
never mutated. Full-size copies keep the frozen stratum counts intact so each
case isolates exactly one refusal.
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANONICAL = ("answers-protectai.jsonl", "answers-jev.jsonl", "RECEIPT.md")


def load_replay():
    spec = importlib.util.spec_from_file_location("x1run", HERE / "run.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fresh_copies(tmp):
    tmp = Path(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    for name in CANONICAL:
        shutil.copy2(HERE / name, tmp / name)
    return tmp


def read_receipt(directory):
    body = (Path(directory) / "RECEIPT.md").read_text().split("```json\n", 1)[1]
    return json.loads(body.rsplit("```", 1)[0])


def write_receipt(directory, receipt):
    (Path(directory) / "RECEIPT.md").write_text(
        "# X1 evaluation receipt\n\n```json\n" + json.dumps(receipt, indent=2)
        + "\n```\n"
    )


def read_jsonl(directory, name):
    return [
        json.loads(line)
        for line in (Path(directory) / name).read_text().splitlines()
        if line.strip()
    ]


def write_jsonl(directory, name, rows):
    (Path(directory) / name).write_text(
        "".join(json.dumps(r) + "\n" for r in rows)
    )


class ReplayNegatives(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_replay()
        # Owned repo scratch for fixture copies (reaper-owned; this test
        # never deletes: RULE 1 forbids deletion, the reaper reclaims it).
        root = HERE.parents[1] / "var" / "agent-tmp"
        cls.scratch = root / f"x1replay.{os.getpid()}"
        cls.scratch.mkdir(parents=True, exist_ok=True)
        (cls.scratch / ".owner").write_text(
            f"pid: {os.getpid()}\nlabel: x1replay\nrepo: {root.parent}\n"
        )
        cls.counter = 0

    def setUp(self):
        type(self).counter += 1
        self.work = type(self).scratch / f"case-{type(self).counter}"
        fresh_copies(self.work)
        setattr(self.mod, "HERE", self.work)

    def tearDown(self):
        setattr(self.mod, "HERE", HERE)

    def replay(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = self.mod.run_replay()
        return rc, json.loads(out.getvalue())

    def test_unmutated_copies_match(self):
        rc, verdict = self.replay()
        self.assertEqual(rc, 0)
        self.assertEqual(verdict["status"], "MATCH")
        self.assertEqual(verdict["mismatches"], [])

    def test_empty_strata_receipt_mismatches(self):
        receipt = read_receipt(self.work)
        receipt["strata"] = {}
        write_receipt(self.work, receipt)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertEqual(verdict["status"], "MISMATCH")
        self.assertTrue(any("strata key set differs" in m
                            for m in verdict["mismatches"]))

    def test_empty_stratum_dict_mismatches(self):
        receipt = read_receipt(self.work)
        receipt["strata"]["clean"] = {}
        write_receipt(self.work, receipt)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("strata.clean" in m
                            for m in verdict["mismatches"]))

    def test_out_of_range_probability_mismatches(self):
        rows = read_jsonl(self.work, "answers-protectai.jsonl")
        rows[0]["p"] = 2.0
        write_jsonl(self.work, "answers-protectai.jsonl", rows)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("invalid encoder probability" in m
                            for m in verdict["mismatches"]))

    def test_bool_probability_mismatches(self):
        rows = read_jsonl(self.work, "answers-protectai.jsonl")
        rows[0]["p"] = True
        write_jsonl(self.work, "answers-protectai.jsonl", rows)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("invalid encoder probability" in m
                            for m in verdict["mismatches"]))

    def test_missing_jev_mate_mismatches(self):
        rows = read_jsonl(self.work, "answers-jev.jsonl")
        write_jsonl(self.work, "answers-jev.jsonl", rows[:-1])
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("without Jev mate" in m
                            for m in verdict["mismatches"]))


if __name__ == "__main__":
    unittest.main()
