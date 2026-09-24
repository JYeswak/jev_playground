"""OpenRouter as a system-one-adapter incumbent (bead jev-14qk).

OpenRouter speaks the OpenAI Chat Completions API, so it enters the adapter as its own
`AsyncOpenAIProvider` with a different base URL: no adapter code is edited or forked. The provider
instance is passed as `model=` to `AsyncSystemOneAdapterClient.system_one`, which the adapter
documents as a caller-owned provider (`_client.py`, "model name or caller-owned provider instance").

The key comes from OPENROUTER_API_KEY (lane Infisical project) and is never printed or written.
Free models only in this lane: every id in FREE_STRUCTURED ends in ':free'.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)

from system_one_adapter.providers.openai import AsyncOpenAIProvider  # noqa: E402

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


def openrouter_provider(model, api_key=None):
    """An adapter provider for one OpenRouter model. Refuses a paid model and a missing key."""
    if not model.endswith(":free"):
        raise ValueError(
            f"not a free model: {model!r} (this lane sends public rows to :free only)"
        )
    key = api_key if api_key is not None else os.environ.get(KEY_ENV)
    if not key:
        raise RuntimeError(f"unconfigured: {KEY_ENV} is not set, no call made")
    return AsyncOpenAIProvider(
        model, base_url=BASE_URL, api_key=key, api="chat_completions"
    )
