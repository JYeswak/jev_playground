"""Offline test of the OpenRouter provider construction (bead jev-14qk). No key, no network.

Run: upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python -m unittest work/openrouter/test_provider.py
"""

import asyncio
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

    def test_run2_list_is_eight_free_ids(self):
        self.assertEqual(len(provider.FREE_STRUCTURED_RUN2), 8)
        self.assertEqual(len(set(provider.FREE_STRUCTURED_RUN2)), 8)
        self.assertTrue(all(m.endswith(":free") for m in provider.FREE_STRUCTURED_RUN2))


class FakeInner:
    def __init__(self, model_name, delay=0.0):
        self.model_name, self.delay, self.calls = model_name, delay, 0

    async def request(self, messages, *, schema, structured):
        self.calls += 1
        await asyncio.sleep(self.delay)
        return "ok"

    async def aclose(self):
        pass


class FakeClock:
    """Time only moves when the pacer sleeps."""

    def __init__(self):
        self.now, self.slept = 0.0, []

    def __call__(self):
        return self.now

    async def sleep(self, s):
        self.slept.append(s)
        self.now += s


class PacedProviderGuards(unittest.TestCase):
    def call(self, prov):
        return asyncio.run(prov.request([], schema={}, structured=True))

    def test_paid_id_is_refused_before_pacing_or_any_request(self):
        inner, pacer = FakeInner("anthropic/claude-haiku-4.5"), provider.Pacer()
        with self.assertRaises(ValueError):
            self.call(provider.PacedProvider(inner, pacer))
        self.assertEqual((inner.calls, pacer.requests), (0, 0))

    def test_sixteenth_start_in_a_minute_waits_for_the_first_to_age_out(self):
        clock = FakeClock()
        pacer = provider.Pacer(15, 599, clock=clock, sleep=clock.sleep)
        prov = provider.PacedProvider(FakeInner("x/y:free"), pacer)
        for _ in range(15):
            self.call(prov)
        self.assertEqual(clock.slept, [])
        self.call(prov)
        self.assertEqual(clock.slept, [60.0])
        self.assertEqual(pacer.waited_s(), 60.0)

    def test_request_cap_refuses_without_sending(self):
        inner = FakeInner("x/y:free")
        prov = provider.PacedProvider(inner, provider.Pacer(15, 2))
        self.call(prov)
        self.call(prov)
        with self.assertRaises(provider.RequestCapReached):
            self.call(prov)
        self.assertEqual(inner.calls, 2)

    def test_slow_attempt_becomes_the_sdk_timeout_error(self):
        from typesafe_sdk import TypeSafeAPITimeoutError

        prov = provider.PacedProvider(
            FakeInner("x/y:free", delay=1.0), provider.Pacer(), attempt_timeout_s=0.05
        )
        with self.assertRaises(TypeSafeAPITimeoutError):
            self.call(prov)


if __name__ == "__main__":
    unittest.main()
