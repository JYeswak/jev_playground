"""HTTP-boundary tests using the captured response and derived refusal cases."""

import importlib.util
import io
import json
import os
import urllib.error
from contextlib import redirect_stdout
import unittest
from pathlib import Path
from unittest.mock import patch

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


class CanaryHTTPTests(unittest.TestCase):
    def setUp(self):
        transport = patch.object(canary.urllib.request, "urlopen")
        self.transport = transport.start()
        self.addCleanup(transport.stop)
        self.transport.side_effect = AssertionError("Unconfigured HTTP attempt")

    def invoke(self, body=None, *, error=None, key="not-a-real-credential"):
        if error is None:
            self.transport.side_effect = None
            self.transport.return_value = io.BytesIO(
                json.dumps(CAPTURED).encode() if body is None else body
            )
        else:
            self.transport.side_effect = error
        output = io.StringIO()
        with (
            patch.dict(os.environ, {"TYPESAFE_API_KEY": key}),
            patch.object(canary.sys, "argv", ["jev-latest-canary.py"]),
            redirect_stdout(output),
        ):
            code = canary.main()
        return code, output.getvalue()

    def test_captured_http_response_is_unchanged(self):
        code, message = self.invoke()
        self.assertEqual(code, 0)
        self.assertIn("OK: jev-latest resolves to jev-1.13.0", message)

    def test_moved_http_alias_fails_loudly(self):
        moved = dict(CAPTURED, model="jev-1.14.0")
        code, message = self.invoke(json.dumps(moved).encode())
        self.assertEqual(code, 1)
        self.assertIn("MOVED: jev-latest resolves to jev-1.14.0", message)

    def test_missing_model_is_error_not_moved_or_ok(self):
        broken = {k: v for k, v in CAPTURED.items() if k != "model"}
        code, message = self.invoke(json.dumps(broken).encode())
        self.assertEqual(code, 3)
        self.assertTrue(message.startswith("ERROR:"))

    def test_truncated_http_json_is_error_not_moved(self):
        code, message = self.invoke(json.dumps(CAPTURED).encode()[:1])
        self.assertEqual(code, 3)
        self.assertIn("ERROR: JSONDecodeError:", message)

    def test_nonobject_http_json_is_error_not_traceback(self):
        code, message = self.invoke(json.dumps([CAPTURED]).encode())
        self.assertEqual(code, 3)
        self.assertIn("ERROR: response is not a JSON object", message)

    def test_http_failure_is_error_not_alias_movement(self):
        code, message = self.invoke(
            error=urllib.error.HTTPError(canary.URL, 502, "Bad Gateway", None, None)
        )
        self.assertEqual(code, 3)
        self.assertIn("ERROR: HTTPError:", message)

    def test_missing_key_never_opens_http_transport(self):
        code, message = self.invoke(key="")
        self.assertEqual(code, 2)
        self.assertTrue(message.startswith("NOT_RUN:"))
        self.transport.assert_not_called()


if __name__ == "__main__":
    unittest.main()
