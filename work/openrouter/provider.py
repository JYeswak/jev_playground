"""OpenRouter as a system-one-adapter incumbent (bead jev-14qk).

OpenRouter speaks the OpenAI Chat Completions API, so it enters the adapter as its own
`AsyncOpenAIProvider` with a different base URL: no adapter code is edited or forked. The provider
instance is passed as `model=` to `AsyncSystemOneAdapterClient.system_one`, which the adapter
documents as a caller-owned provider (`_client.py`, "model name or caller-owned provider instance").

The key comes from OPENROUTER_API_KEY (lane Infisical project) and is never printed or written.
Free models only in this lane: every id in FREE_STRUCTURED ends in ':free', and any other id is
refused by work/anthropic-stop's require_free_comparator before a client exists (jev-lbgk).
"""

import asyncio
import collections
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)
sys.path.insert(0, os.path.join(ROOT, "work", "anthropic-stop"))

from system_one_adapter.providers.openai import AsyncOpenAIProvider  # noqa: E402
from anthropic_stop import require_free_comparator  # noqa: E402  jev-lbgk
from typesafe_sdk import TypeSafeAPITimeoutError  # noqa: E402

BASE_URL = "https://openrouter.ai/api/v1"
KEY_ENV = "OPENROUTER_API_KEY"

# The six :free models bead jev-14qk names, all listing structured output or response_format on
# https://openrouter.ai/api/v1/models (2026-09-24).
FREE_STRUCTURED = (
    "google/gemma-4-31b-it:free",
    "qwen/qwen3.8-27b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nex-agi/nex-n2.5-pro:free",
    "dots-studio/dots-3-note-preview:free",
    "google/gemma-4-26b-a4b-it:free",
)

# Run 2 (bead jev-3e2i, docs/demos/upstream-repro/openrouter-free-feasibility-2-20260924.md): the 8
# :free ids pane 1 listed with structured output, in the preregistered run order.
FREE_STRUCTURED_RUN2 = (
    "dots-studio/dots-3-note-preview:free",
    "nex-agi/nex-n2.5-pro:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nex-agi/nex-n2.5-mini:free",
    "liquid/lfm-2.5-2.6b:free",
    "qwen/qwen3.8-27b:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
)


def openrouter_provider(model, api_key=None):
    """An adapter provider for one OpenRouter model. Refuses a paid model and a missing key."""
    require_free_comparator(model, "openrouter provider")
    key = api_key if api_key is not None else os.environ.get(KEY_ENV)
    if not key:
        raise RuntimeError(f"unconfigured: {KEY_ENV} is not set, no call made")
    return AsyncOpenAIProvider(
        model, base_url=BASE_URL, api_key=key, api="chat_completions"
    )


class RequestCapReached(RuntimeError):
    """The run's preregistered request cap is spent; no request was sent."""


class Pacer:
    """Process-wide request pacing shared by every model in a run: at most `per_min` request starts
    in any 60 s window, and at most `max_requests` requests in total."""

    def __init__(
        self, per_min=15, max_requests=599, clock=time.monotonic, sleep=asyncio.sleep
    ):
        self.per_min, self.max_requests = per_min, max_requests
        self._clock, self._sleep = clock, sleep
        self._starts = collections.deque()
        self.requests = 0
        self._waited_s = 0.0
        self._sleeping_since = None

    def waited_s(self):
        """Total time spent holding requests back, including a hold still in progress."""
        now = self._clock()
        extra = 0.0 if self._sleeping_since is None else now - self._sleeping_since
        return self._waited_s + extra

    async def acquire(self):
        if self.requests >= self.max_requests:
            raise RequestCapReached(f"request cap {self.max_requests} reached")
        while True:
            now = self._clock()
            while self._starts and self._starts[0] <= now - 60:
                self._starts.popleft()
            if len(self._starts) < self.per_min:
                break
            self._sleeping_since = now
            try:
                await self._sleep(self._starts[0] + 60 - now)
            finally:
                self._waited_s += self._clock() - self._sleeping_since
                self._sleeping_since = None
        self._starts.append(self._clock())
        self.requests += 1


class PacedProvider:
    """An AsyncProvider wrapper: refuses a non-:free id before every request, waits for the shared
    Pacer, and bounds each attempt at `attempt_timeout_s` (raised as the SDK's timeout error so the
    adapter's RetryPolicy classifies it like any other provider timeout)."""

    def __init__(self, inner, pacer, attempt_timeout_s=120.0):
        self.inner, self.pacer, self.attempt_timeout_s = inner, pacer, attempt_timeout_s
        self.model_name = inner.model_name

    async def request(self, messages, *, schema, structured):
        require_free_comparator(self.model_name, "openrouter paced request")
        await self.pacer.acquire()
        try:
            return await asyncio.wait_for(
                self.inner.request(messages, schema=schema, structured=structured),
                timeout=self.attempt_timeout_s,
            )
        except asyncio.TimeoutError:
            raise TypeSafeAPITimeoutError(self.attempt_timeout_s) from None

    async def aclose(self):
        await self.inner.aclose()
