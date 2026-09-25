"""Offline tests for the frozen leaf evaluator arms."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


def require_prerequisites() -> None:
    missing = []
    if sys.version_info < (3, 12):
        missing.append("Python >= 3.12")
    root = Path(__file__).resolve().parents[4]
    if not (root / "pokechamp" / "pokechamp").is_dir():
        missing.append("pokechamp clone")
    if missing:
        print(f"SKIP (missing prerequisite: {', '.join(missing)})")
        raise SystemExit(8)


require_prerequisites()

sys.path.insert(0, str(Path(__file__).parent))
import run as battle_run  # noqa: E402


class _FakeAsker:
    def __init__(self, result=None, error=None):
        self.calls = []
        self.result = result
        self.error = error

    def __call__(self, state):
        self.calls.append(state)
        if self.error is not None:
            raise self.error
        return self.result


class _HttpError(RuntimeError):
    def __init__(self, status_code):
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


def _model_file(directory: Path) -> tuple[Path, str]:
    payload = {
        "format": "leaf-model-v1",
        "features": ["hp", "pressure"],
        "noul_features": ["ko", "danger", "switch"],
        "intercept": 0.0,
        "code_weights": [1.0, 0.5],
        "means": [0.0, 0.0],
        "scales": [1.0, 1.0],
        "noul_intercept": 0.0,
        "noul_code_weights": [1.0, 0.5],
        "noul_weights": [0.2, -0.1, 0.3],
        "noul_means": [0.0, 0.0, 0.0, 0.0, 0.0],
        "noul_scales": [1.0, 1.0, 1.0, 1.0, 1.0],
    }
    path = directory / "leaf-model.json"
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, digest


class FrozenLeafArmTests(unittest.TestCase):
    def test_code_arm_never_calls_jev_in_leaf(self):
        with tempfile.TemporaryDirectory() as temp:
            model_path, digest = _model_file(Path(temp))
            asker = _FakeAsker(result={"ko": 0.9, "danger": 0.1, "switch": 0.2})
            model = battle_run.FrozenLeafModel.from_json(
                model_path, expected_sha256=digest
            )
            arm = battle_run.LeafArm(mode="code", model=model, asker=asker)

            decision = arm.choose(
                {"hp": 0.8, "pressure": 0.4},
                [
                    {"id": "hold", "features": {"hp": 0.8, "pressure": 0.4}},
                    {"id": "switch", "features": {"hp": 0.2, "pressure": 0.1}},
                ],
            )

            self.assertEqual(decision.choice, "hold")
            self.assertEqual(asker.calls, [])

    def test_noul_arm_calls_once_per_leaf(self):
        with tempfile.TemporaryDirectory() as temp:
            model_path, digest = _model_file(Path(temp))
            asker = _FakeAsker(result={"ko": 0.9, "danger": 0.1, "switch": 0.2})
            model = battle_run.FrozenLeafModel.from_json(
                model_path, expected_sha256=digest
            )
            arm = battle_run.LeafArm(mode="code+noul", model=model, asker=asker)

            decision = arm.choose(
                {"hp": 0.8, "pressure": 0.4},
                [
                    {"id": "hold", "features": {"hp": 0.8, "pressure": 0.4}},
                    {"id": "switch", "features": {"hp": 0.2, "pressure": 0.1}},
                ],
            )

            self.assertIn(decision.choice, {"hold", "switch"})
            self.assertEqual(len(asker.calls), 1)

    def test_unauthorized_or_billing_error_stops_noul_arm(self):
        for status_code in (401, 402):
            with (
                self.subTest(status_code=status_code),
                tempfile.TemporaryDirectory() as temp,
            ):
                model_path, digest = _model_file(Path(temp))
                asker = _FakeAsker(error=_HttpError(status_code))
                model = battle_run.FrozenLeafModel.from_json(
                    model_path, expected_sha256=digest
                )
                arm = battle_run.LeafArm(mode="code+noul", model=model, asker=asker)

                with self.assertRaises(battle_run.LeafArmStopped):
                    arm.choose(
                        {"hp": 0.8, "pressure": 0.4},
                        [{"id": "hold", "features": {"hp": 0.8, "pressure": 0.4}}],
                    )
                self.assertTrue(arm.stopped)
                self.assertEqual(len(asker.calls), 1)

    def test_frozen_weights_hash_mismatch_refuses_to_start(self):
        with tempfile.TemporaryDirectory() as temp:
            model_path, _digest = _model_file(Path(temp))
            with self.assertRaisesRegex(ValueError, "sha256"):
                battle_run.FrozenLeafModel.from_json(
                    model_path,
                    expected_sha256="0" * 64,
                )


if __name__ == "__main__":
    unittest.main()
