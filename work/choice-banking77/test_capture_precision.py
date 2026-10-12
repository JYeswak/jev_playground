#!/usr/bin/env python3
"""jev-banking77-probability-precision-x940: capture-to-validator smoke (keyless).

Captures real observed Banking77 rows through the production answer_row path in
run.py (injected answers, no network, no key), then feeds the captured vectors
to the EXISTING D5 split-conformal validator (kit/.../measurement-conformal.mjs)
via node: an observed valid unit-mass row must come back OK, and the observed
frozen 0.99-mass row must come back REFUSE invalid_probability_vector.

Provenance boundary (code-traced, models.py ChoiceAnswer): the SDK schema keeps
only parsed probabilities (no raw wire text retained). Whether the observed 2dp
quantization happened at the wire, the SDK, or earlier is UNKNOWN: the raw wire
response bodies were never retained (exact missing source). This suite makes no
claim about where quantization happened and no observed-data coverage claim.
Frozen IDs/row bytes and D5 acceptance untouched.
"""

import importlib.util
import json
import os
import subprocess
import sys
import unittest
import types
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
_NODE_SMOKE = """\
import { readFileSync } from "node:fs";
import { splitConformalLac } from %s;
const payload = JSON.parse(readFileSync(0, "utf8"));
const result = splitConformalLac(payload);
process.stdout.write(JSON.stringify({ status: result.status, reason: result.reason ?? null }));
"""
VALIDATOR = os.path.join(ROOT, "kit", "src", "measurement-conformal.mjs")

_VALID_ID = 0  # real observed valid unit-mass row in rows-full-jev.jsonl
_VALID_ID_2 = 1  # second real observed valid unit-mass row
_FROZEN_ID = 71  # real observed frozen 0.99-mass row in rows-full-jev.jsonl


_CAPTURE = None


def _load_capture(testcase):
    """Exec run.py with stubbed metered/network imports, scoped to exec_module.

    unittest.mock.patch.dict swaps the stubs in for exactly the exec_module
    call and restores pre-existing modules on exit, so stubs never leak into
    the node subprocess window or later tests. Unused parameter kept for callers.
    """
    del testcase
    sdk = types.ModuleType("typesafe_sdk")

    class _Placeholder:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("live SDK must not be constructed in keyless tests")

    setattr(sdk, "Choice", _Placeholder)
    setattr(sdk, "RetryPolicy", _Placeholder)
    setattr(sdk, "TypeSafeClient", _Placeholder)
    stop = types.ModuleType("anthropic_stop")
    setattr(stop, "refuse_paid_comparator", lambda *_args, **_kwargs: None)
    spec = importlib.util.spec_from_file_location(
        "choice_banking77_run", os.path.join(HERE, "run.py")
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(
        sys.modules, {"typesafe_sdk": sdk, "anthropic_stop": stop}
    ):
        spec.loader.exec_module(module)
    return module


def _capture_module(testcase):
    global _CAPTURE
    if _CAPTURE is None:
        _CAPTURE = _load_capture(testcase)
    return _CAPTURE


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


def _capture(capture, source):
    label_map = {label: label for label in source["probabilities"]}
    ans = FakeAnswer(
        choice=source["intent"],
        confidence=source["confidence"],
        probabilities=dict(source["probabilities"]),
    )
    return capture.answer_row(
        {"i": source["i"], "intent": source["intent"]},
        label_map,
        ans,
        "jev-1.13.0",
        0,
        None,
    )


def _validator_call(frame_name, labels, calibration, test):
    frame = {
        "name": frame_name,
        "source": "x940 capture smoke",
        "targetPopulation": "Banking77 full corpus",
        "calibrationGroup": {
            "name": "DEV",
            "targetPopulation": "Banking77 full corpus",
        },
        "testGroup": {"name": "SAMPLE", "targetPopulation": "Banking77 full corpus"},
    }

    def grow(row, split):
        return {
            "id": row["i"],
            "trueLabel": row["intent"],
            "probabilities": row["probabilities"],
            "group": split,
            "samplingFrame": frame_name,
        }

    payload = {
        "labels": labels,
        "calibration": [grow(r, "DEV") for r in calibration],
        "test": [grow(r, "SAMPLE") for r in test],
        "alpha": 0.1,
        "probabilityFloor": 0.005,
        "samplingFrame": frame,
    }
    script = _NODE_SMOKE % json.dumps(VALIDATOR)
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", script, "-"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    return json.loads(proc.stdout)


class CaptureValidatorSmokeTests(unittest.TestCase):
    def test_valid_captured_row_passes_d5_validator(self):
        capture = _capture_module(self)
        good = _capture(capture, _committed_row(_VALID_ID))
        good2 = _capture(capture, _committed_row(_VALID_ID_2))
        labels = sorted(good["probabilities"])
        result = _validator_call("x940-smoke-frame", labels, [good], [good2])
        self.assertEqual(result["status"], "OK")

    def test_frozen_099_retained_and_refused(self):
        capture = _capture_module(self)
        source = _committed_row(_FROZEN_ID)
        row = _capture(capture, source)
        self.assertEqual(row["probabilities"], source["probabilities"])
        self.assertGreater(abs(sum(row["probabilities"].values()) - 1.0), 1e-6)
        good = _capture(capture, _committed_row(_VALID_ID))
        labels = sorted(row["probabilities"])
        result = _validator_call("x940-smoke-frame", labels, [good], [row])
        self.assertEqual(result["status"], "REFUSE")
        self.assertEqual(result["reason"], "invalid_probability_vector")


if __name__ == "__main__":
    unittest.main()
