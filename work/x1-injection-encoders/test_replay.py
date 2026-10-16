"""Planted negatives for the X1 recorded replay (jev-x1-injection-encoders-e2gp.1).

ReplayNegatives copies the committed canonical bundle into a throwaway
directory and points the replay module at the copies: canonical
answers/RECEIPT files are never mutated. Full-size copies keep the frozen
stratum counts intact so each case isolates exactly one refusal.
TestJsonEntrypoint drives the canonical run.py --json command itself and
asserts it never writes canonical files, on both the MATCH and the
guard-refusal paths.
"""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANONICAL = ("answers-protectai.jsonl", "answers-jev.jsonl", "RECEIPT.md")


def load_replay():
    spec = importlib.util.spec_from_file_location("x1replay", HERE / "replay.py")
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
        self.assertEqual(verdict["status"], "MISMATCH")
        self.assertTrue(any(m.startswith("strata: recomputed")
                            for m in verdict["mismatches"]))

    def test_empty_stratum_dict_mismatches(self):
        receipt = read_receipt(self.work)
        receipt["strata"]["clean"] = {}
        write_receipt(self.work, receipt)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertEqual(verdict["status"], "MISMATCH")
        self.assertTrue(any(m.startswith("strata: recomputed")
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

    def test_invalid_trigger_probability_mismatches(self):
        rows = read_jsonl(self.work, "answers-protectai.jsonl")
        trigger = next(r for r in rows if r["set"] == "trigger-negative")
        trigger["p"] = -1.0
        write_jsonl(self.work, "answers-protectai.jsonl", rows)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("invalid trigger probability" in m
                            for m in verdict["mismatches"]))

    def test_wrong_call_count_mismatches(self):
        receipt = read_receipt(self.work)
        receipt["jev_public_calls"] = 448
        write_receipt(self.work, receipt)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("jev_public_calls" in m
                            for m in verdict["mismatches"]))

    def test_tampered_spend_mismatches(self):
        receipt = read_receipt(self.work)
        receipt["jev_public_input_tokens"] += 1
        write_receipt(self.work, receipt)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("jev_public_input_tokens" in m
                            for m in verdict["mismatches"]))

    def test_missing_dev_row_mismatches(self):
        rows = read_jsonl(self.work, "answers-protectai.jsonl")
        write_jsonl(self.work, "answers-protectai.jsonl", rows[1:])
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertEqual(verdict["status"], "MISMATCH")

    def test_match_emits_full_recomputed_report(self):
        rc, verdict = self.replay()
        self.assertEqual(rc, 0)
        recomputed = verdict["recomputed"]
        self.assertEqual(set(recomputed["strata"]),
                         {"clean", "marked", "markerless", "public-english"})
        self.assertEqual(recomputed["cut"], 0.9999990463256836)
        self.assertEqual(recomputed["jev_public_calls"], 447)
        self.assertEqual(verdict["not_recomputed"],
                         ["encoder_runtime", "guard", "model_loads",
                          "started_at_utc"])

    def test_missing_jev_mate_mismatches(self):
        rows = read_jsonl(self.work, "answers-jev.jsonl")
        write_jsonl(self.work, "answers-jev.jsonl", rows[:-1])
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("without Jev mate" in m
                            for m in verdict["mismatches"]))


WATCHED = (
    HERE / "answers-protectai.jsonl",
    HERE / "answers-jev.jsonl",
    HERE / "RECEIPT.md",
    HERE / "PREREG.md",
    HERE / "../../kit/fixtures/screen/answers-protectai.jsonl",
    HERE / "../../kit/fixtures/screen/answers-jev.jsonl",
)


class TestJsonEntrypoint(unittest.TestCase):
    """The canonical run.py --json command never writes canonical files."""

    @classmethod
    def setUpClass(cls):
        root = HERE.parents[1] / "var" / "agent-tmp"
        cls.scratch = root / f"x1json.{os.getpid()}"
        cls.scratch.mkdir(parents=True, exist_ok=True)
        (cls.scratch / ".owner").write_text(
            f"pid: {os.getpid()}\nlabel: x1json\nrepo: {root.parent}\n"
        )
        stub = cls.scratch / "localbench-stub.sh"
        stub.write_text('#!/bin/sh\necho \'{"parked": []}\'\n')
        stub.chmod(0o755)
        cls.stub = stub

    def snapshot(self):
        return {str(p): p.read_bytes() for p in WATCHED}

    def run_json(self, extra_env):
        env = dict(os.environ)
        env["LOCALBENCH_BIN"] = str(type(self).stub)
        env.update(extra_env)
        before = self.snapshot()
        proc = subprocess.run(
            [sys.executable, str(HERE / "run.py"), "--json"],
            capture_output=True, text=True, timeout=300, env=env,
            cwd=str(HERE.parents[1]),
        )
        after = self.snapshot()
        self.assertEqual(before, after)
        return proc

    def test_json_match_writes_nothing(self):
        proc = self.run_json({})
        self.assertEqual(proc.returncode, 0)
        verdict = json.loads(proc.stdout)
        self.assertEqual(verdict["status"], "MATCH")
        self.assertEqual(verdict["mismatches"], [])

    def test_json_guard_refusal_writes_nothing(self):
        hold = type(self).scratch / "gpu-hold"
        hold.write_text(str(int(time.time()) + 3600))
        proc = self.run_json({"JEV_GPU_HOLD_FILE": str(hold)})
        self.assertEqual(proc.returncode, 0)
        verdict = json.loads(proc.stdout)
        self.assertEqual(verdict["status"], "NOT_RUN")
        self.assertEqual(verdict["jev_calls"], 0)


class ReplayConsistency(unittest.TestCase):
    """Per-record status/flag/backend consistency (fixture copies)."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_replay()
        root = HERE.parents[1] / "var" / "agent-tmp"
        cls.scratch = root / f"x1cons.{os.getpid()}"
        cls.scratch.mkdir(parents=True, exist_ok=True)
        (cls.scratch / ".owner").write_text(
            f"pid: {os.getpid()}\nlabel: x1cons\nrepo: {root.parent}\n"
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

    def test_jev_error_status_mismatches(self):
        rows = read_jsonl(self.work, "answers-jev.jsonl")
        rows[5]["status"] = "ERROR_INVALID_CONTROL"
        write_jsonl(self.work, "answers-jev.jsonl", rows)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("unexpected Jev status" in m
                            for m in verdict["mismatches"]))

    def test_flipped_jev_flag_mismatches(self):
        rows = read_jsonl(self.work, "answers-jev.jsonl")
        rows[5]["flag"] = not rows[5]["flag"]
        write_jsonl(self.work, "answers-jev.jsonl", rows)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("Jev flag inconsistent" in m
                            for m in verdict["mismatches"]))

    def test_wrong_nonfirst_backend_mismatches(self):
        rows = read_jsonl(self.work, "answers-protectai.jsonl")
        rows[7]["backend"] = "wrong-backend-control"
        write_jsonl(self.work, "answers-protectai.jsonl", rows)
        rc, verdict = self.replay()
        self.assertEqual(rc, 1)
        self.assertTrue(any("unexpected encoder backend" in m
                            for m in verdict["mismatches"]))

if __name__ == "__main__":
    unittest.main()
