"""An all-zero Choice distribution comes back as a well-formed answer for the first option.

Standalone: no key, no network call to a model. Run against the released package:
  uv run --no-project --with system-one-adapter==0.2.1 python stranger_repro.py
"""

import json

from typesafe_sdk import Choice

from system_one_adapter import SystemOneAdapterClient
from system_one_adapter.providers import ProviderResult

LABELS = ["refund", "shipping", "billing"]


class CannedProvider:
    """A custom provider returning one fixed model output."""

    model_name = "canned"

    def __init__(self, distribution):
        self.text = json.dumps({"answers": {"topic": distribution}})
        self.calls = 0

    def request(self, messages, *, schema, structured):
        self.calls += 1
        return ProviderResult(text=self.text, input_tokens=0, output_tokens=0)

    def translate_error(self, error):
        return error


question = {
    "topic": Choice(instructions="Ticket topic", criteria=dict.fromkeys(LABELS))
}

for label, distribution, normalize in [
    ("model returned all zeros", dict.fromkeys(LABELS, 0.0), True),
    ("model returned all zeros", dict.fromkeys(LABELS, 0.0), False),
    ("model returned 1/3 each", dict.fromkeys(LABELS, 1 / 3), True),
]:
    provider = CannedProvider(distribution)
    with SystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=normalize,
        n_retry_malformed_structure=2,
    ) as client:
        response = client.system_one({"ticket": "x"}, question, model=provider)
    answer = response.answers["topic"]
    print(
        f"{label:26} normalize={normalize!s:5} calls={provider.calls} "
        f"choice={answer.choice!r} confidence={answer.confidence} "
        f"probabilities={ {k: round(v, 3) for k, v in answer.probabilities.items()} } "
        f"probability_errors={response.debug['probability_errors']}"
    )
