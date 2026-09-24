#!/usr/bin/env python3
"""Bead jev-mly, keyless arm: what system-one-adapter-python returns when the model's
Choice distribution sums to zero. No key, no network: a caller-owned fake provider
(the adapter's own documented injection seam, `model=<provider instance>`) returns a
fixed raw payload, and the adapter's real decode/normalize/confidence code runs on it.

Run:
  upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/adapter-uniform/repro_keyless.py
Prints one JSON line per case; exits 1 if any expectation below does not hold.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "upstream/typesafe-ai/typesafe-sdk-python/src"))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)

from typesafe_sdk import Choice  # noqa: E402

from system_one_adapter import SystemOneAdapterClient  # noqa: E402
from system_one_adapter.providers.base import ProviderResult  # noqa: E402

LABELS = ["alpha", "beta", "gamma", "delta"]


class FixedProvider:
    """Returns one fixed raw payload; mirrors the SyncProvider protocol."""

    model_name = "fixed-payload"

    def __init__(self, text):
        self.text = text

    def request(self, messages, *, schema, structured):
        return ProviderResult(text=self.text, input_tokens=0, output_tokens=0)

    def translate_error(self, error):
        raise error


def run(values, normalize):
    payload = json.dumps({"answers": {"q": dict(zip(LABELS, values))}})
    q = {
        "q": Choice(
            instructions="Which label?", criteria={label: None for label in LABELS}
        )
    }
    with SystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=normalize,
    ) as client:
        resp = client.system_one({"text": "x"}, q, model=FixedProvider(payload))
    ans = resp.answers["q"]
    debug = {
        k: resp.debug[k]
        for k in ("max_error", "invalid_probs", "probability_errors")
        if k in resp.debug
    }
    if "original_probabilities" in resp.debug:
        debug["original_probabilities"] = resp.debug["original_probabilities"]
    return {
        "model_payload": payload,
        "normalize_probabilities": normalize,
        "choice": ans.choice,
        "confidence": ans.confidence,
        "probabilities": ans.probabilities,
        "debug": debug,
    }


def main():
    zeros = [0.0] * len(LABELS)
    cases = [
        # (name, values, normalize, expected choice, expected probs, expected confidence)
        ("all-zero, normalize=True", zeros, True, "alpha", [0.25] * 4, 0.0),
        ("all-zero, normalize=False", zeros, False, "alpha", [0.0] * 4, 0.0),
        # Control: a genuine uniform the model actually asserted is indistinguishable in answers.
        (
            "model-asserted uniform, normalize=True",
            [0.25] * 4,
            True,
            "alpha",
            [0.25] * 4,
            0.0,
        ),
        # Control: a non-degenerate distribution resolves normally.
        (
            "peaked, normalize=True",
            [0.0, 0.0, 1.0, 0.0],
            True,
            "gamma",
            [0.0, 0.0, 1.0, 0.0],
            1.0,
        ),
    ]
    ok = True
    for name, values, normalize, want_choice, want_probs, want_conf in cases:
        out = run(values, normalize)
        got_probs = [out["probabilities"][label] for label in LABELS]
        holds = (
            out["choice"] == want_choice
            and all(abs(a - b) < 1e-9 for a, b in zip(got_probs, want_probs))
            and abs(out["confidence"] - want_conf) < 1e-9
        )
        ok &= holds
        print(json.dumps({"case": name, "expectation_holds": holds, **out}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
