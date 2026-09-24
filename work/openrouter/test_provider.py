"""Offline test of the OpenRouter provider construction (bead jev-14qk). No key, no network.

Run: upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python -m unittest work/openrouter/test_provider.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import provider  # noqa: E402


class ProviderConstruction(unittest.TestCase):
    def test_free_model_targets_openrouter_chat_completions(self):
        p = provider.openrouter_provider(
            "nex-agi/nex-n2.5-pro:free", api_key="test-not-a-key"
        )
        self.assertEqual(p.model_name, "nex-agi/nex-n2.5-pro:free")
        self.assertEqual(p.api, "chat_completions")
        self.assertEqual(str(p._client.base_url).rstrip("/"), provider.BASE_URL)
        self.assertEqual(p._client.api_key, "test-not-a-key")
        self.assertEqual(
            p._client.max_retries, 0
        )  # retries belong to the adapter's RetryPolicy

    def test_paid_model_is_refused_before_any_client_exists(self):
        with self.assertRaises(ValueError):
            provider.openrouter_provider(
                "anthropic/claude-haiku-4.5", api_key="test-not-a-key"
            )

    def test_missing_key_is_refused_not_sent_empty(self):
        saved = os.environ.pop(provider.KEY_ENV, None)
        try:
            with self.assertRaises(RuntimeError):
                provider.openrouter_provider("qwen/qwen3.8-27b:free")
        finally:
            if saved is not None:
                os.environ[provider.KEY_ENV] = saved

    def test_every_listed_model_is_free(self):
        self.assertEqual(len(provider.FREE_STRUCTURED), 6)
        self.assertTrue(all(m.endswith(":free") for m in provider.FREE_STRUCTURED))


if __name__ == "__main__":
    unittest.main()
