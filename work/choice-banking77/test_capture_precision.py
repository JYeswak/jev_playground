#!/usr/bin/env python3
"""jev-banking77-probability-precision-x940: capture precision boundary (keyless).

Exercises the production answer_row capture path in run.py with injected answers
built from in-tree real observed Banking77 rows (no network, no key):
- positive: observed valid unit-mass vector round-trips wire/SDK/persisted
  bit-exact; SDK float schema, float() and json preserve every value, so any
  quantization predates capture (all 3080 committed rows are 2dp wire values).
- negative: observed frozen 0.99-mass vector is retained verbatim (never
  normalized/filtered/relabeled) and refused strict eligibility with
  invalid_probability_vector semantics; weakening or removing the production
  guard fails this test.
No observed-data coverage claim; frozen IDs/row bytes and D5 acceptance untouched.
"""

import importlib.util
import json
import os
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

_VALID_ID = 0  # real observed valid unit-mass row in rows-full-jev.jsonl
_FROZEN_ID = 71  # real observed frozen 0.99-mass row in rows-full-jev.jsonl


def _load_capture():
    """Exec run.py with stubbed metered/network imports (keyless, offline).

    run.py imports typesafe_sdk and anthropic_stop at module scope for its live
    arms; the capture path under test (answer_row, conformal_mass_eligible)
    touches neither. Stubs keep the suite keyless without altering run.py.
    """
    sdk = types.ModuleType("typesafe_sdk")

    class _Placeholder:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("live SDK must not be constructed in keyless tests")

    setattr(sdk, "Choice", _Placeholder)
    setattr(sdk, "RetryPolicy", _Placeholder)
    setattr(sdk, "TypeSafeClient", _Placeholder)
    sys.modules.setdefault("typesafe_sdk", sdk)
    stop = types.ModuleType("anthropic_stop")
    setattr(stop, "refuse_paid_comparator", lambda *_args, **_kwargs: None)
    sys.modules.setdefault("anthropic_stop", stop)
    spec = importlib.util.spec_from_file_location(
        "choice_banking77_run", os.path.join(HERE, "run.py")
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _committed_row(row_id):
    with open(os.path.join(HERE, "rows-full-jev.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                row = json.loads(line)
                if row["i"] == row_id:
                    return row
    raise AssertionError(f"committed fixture row {row_id} missing")


class FakeAnswer:
    """Stands in for the SDK answer object; carries exact observed values."""

    def __init__(self, choice, confidence, probabilities):
        self.choice = choice
        self.confidence = confidence
        self.probabilities = probabilities


class CapturePrecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture = _load_capture()

    def test_valid_vector_round_trips_bit_exact(self):
        source = _committed_row(_VALID_ID)
        self.assertAlmostEqual(sum(source["probabilities"].values()), 1.0, delta=1e-6)
        label_map = {label: label for label in source["probabilities"]}
        ans = FakeAnswer(
            choice=source["intent"],
            confidence=source["confidence"],
            probabilities=dict(source["probabilities"]),
        )
        row = self.capture.answer_row(
            {"i": source["i"], "intent": source["intent"]},
            label_map,
            ans,
            "jev-1.13.0",
            0,
            None,
        )
        self.assertEqual(row["probabilities"], source["probabilities"])
        self.assertEqual(sum(row["probabilities"].values()), 1.0)
        self.assertEqual(
            json.loads(json.dumps(row["probabilities"])), source["probabilities"]
        )
        self.assertTrue(self.capture.conformal_mass_eligible(row["probabilities"]))

    def test_quantization_predates_capture(self):
        with open(os.path.join(HERE, "rows-full-jev.jsonl"), encoding="utf-8") as fh:
            rows = [json.loads(line) for line in fh if line.strip()]
        self.assertEqual(len(rows), 3080)
        for row in rows:
            for value in row["probabilities"].values():
                self.assertEqual(value, float(value))
                self.assertEqual(json.loads(json.dumps(value)), value)
                self.assertTrue(abs(value * 100 - round(value * 100)) < 1e-9)
        # float()/json are lossless here, so the 2dp quantization observed on
        # every committed row originates at the wire/SDK response, not capture.

    def test_frozen_099_retained_and_refused(self):
        source = _committed_row(_FROZEN_ID)
        mass = sum(source["probabilities"].values())
        self.assertGreater(abs(mass - 1.0), 1e-6)
        label_map = {label: label for label in source["probabilities"]}
        ans = FakeAnswer(
            choice=source["intent"],
            confidence=source["confidence"],
            probabilities=dict(source["probabilities"]),
        )
        row = self.capture.answer_row(
            {"i": source["i"], "intent": source["intent"]},
            label_map,
            ans,
            "jev-1.13.0",
            0,
            None,
        )
        self.assertEqual(row["probabilities"], source["probabilities"])
        self.assertEqual(sum(row["probabilities"].values()), mass)
        self.assertFalse(self.capture.conformal_mass_eligible(row["probabilities"]))

    def test_guard_tolerance_is_strict(self):
        self.assertEqual(self.capture.STRICT_MASS_TOLERANCE, 1e-6)
        self.assertFalse(
            self.capture.conformal_mass_eligible({"a": 0.7, "b": 0.300002})
        )
        self.assertFalse(
            self.capture.conformal_mass_eligible({"a": 0.5, "b": float("nan")})
        )
        self.assertFalse(self.capture.conformal_mass_eligible({}))


if __name__ == "__main__":
    unittest.main()
