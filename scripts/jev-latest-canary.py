#!/usr/bin/env python3
"""One live call to `jev-latest`; exit 1 when it no longer resolves to the pinned version.

omp's judge role (find, auto-thinking; ~1,700 calls/day) can only use the `jev-latest` alias,
and omp logs only the alias. TypeSafe's response body carries the resolved model id, so one
cheap call tells us whether the alias has moved (jev-v87h). Costs ~282 input tokens.

Run:  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
        python3 scripts/jev-latest-canary.py
Exit: 0 unchanged, 1 moved, 2 NOT_RUN (no key), 3 request or response error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
PINNED = "jev-1.13.0"
BODY = {
    "model": "jev-latest",
    "state": {"text": "The sky is blue."},
    "questions": {
        "q": {"type": "noul", "instructions": "The text says the sky is blue."}
    },
}


def verdict(response: dict, expected: str) -> tuple[int, str]:
    """Pure policy: classify one decoded response."""
    resolved = response.get("model")
    if not isinstance(resolved, str) or not resolved:
        return 3, f"ERROR: response has no model field: {sorted(response)}"
    if resolved != expected:
        return 1, f"MOVED: jev-latest resolves to {resolved}, expected {expected}"
    return 0, f"OK: jev-latest resolves to {resolved}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that jev-latest still resolves to the pinned Jev version."
    )
    parser.add_argument("--expected", default=PINNED)
    args = parser.parse_args()
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("NOT_RUN: TYPESAFE_API_KEY is not set")
        return 2
    request = urllib.request.Request(
        URL,
        data=json.dumps(BODY).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as reply:
            response = json.load(reply)
    except Exception as error:  # the key is never part of the message
        print(f"ERROR: {type(error).__name__}: {error}")
        return 3
    code, message = verdict(response, args.expected)
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
