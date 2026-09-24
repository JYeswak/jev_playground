#!/usr/bin/env python3
"""Spend probe for bead jev-3e2i: GET https://openrouter.ai/api/v1/key, print only usage fields.

Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
       python3 work/openrouter/usage_daily.py
Prints a UTC timestamp and the numeric/boolean usage fields; never the key or its label. Stdlib only.
"""

import datetime
import json
import os
import sys
import urllib.request

KEY_ENV = "OPENROUTER_API_KEY"
DROP = {"label", "name", "key", "hash", "creator_user_id"}

key = os.environ.get(KEY_ENV)
if not key:
    raise SystemExit(f"unconfigured: {KEY_ENV} is not set, no call made")
req = urllib.request.Request(
    "https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {key}"}
)
with urllib.request.urlopen(req, timeout=30) as r:
    data = json.load(r)["data"]
out = {k: v for k, v in data.items() if k not in DROP and not isinstance(v, str)}
out["at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
json.dump(out, sys.stdout, sort_keys=True)
print()
