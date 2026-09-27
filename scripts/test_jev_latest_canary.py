"""Policy tests for scripts/jev-latest-canary.py; fixtures are captured response bodies."""

import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "canary", Path(__file__).with_name("jev-latest-canary.py")
)
assert spec is not None and spec.loader is not None
canary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canary)

# Captured 2026-09-27 00:11Z from POST /v1/systemone with model=jev-latest (request req_01a0e033a8f87ef0).
CAPTURED = {
    "model": "jev-1.13.0",
    "answers": {"q": {"type": "noul", "noul": 0.78}},
    "usage": {"input_tokens": 282, "output_tokens": 20},
}


class CanaryPolicyTests(unittest.TestCase):
    def test_captured_response_is_unchanged(self):
        self.assertEqual(canary.verdict(CAPTURED, "jev-1.13.0")[0], 0)

    def test_moved_alias_fails_loudly(self):
        moved = dict(CAPTURED, model="jev-1.14.0")
        code, message = canary.verdict(moved, "jev-1.13.0")
        self.assertEqual(code, 1)
        self.assertIn("jev-1.14.0", message)

    def test_missing_model_field_is_an_error_not_a_pass(self):
        broken = {k: v for k, v in CAPTURED.items() if k != "model"}
        self.assertEqual(canary.verdict(broken, "jev-1.13.0")[0], 3)


if __name__ == "__main__":
    unittest.main()
