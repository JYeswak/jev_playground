#!/usr/bin/env python3
"""Fetch the pinned STS-B English dev file and write ids plus gold scores only.

Sentence text is not written. The source licenses do not let this repo commit it
(see docs/demos/upstream-repro/score-stsb-20260924.md). No model call.
"""

import csv
import hashlib
import io
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
URL = (
    "https://raw.githubusercontent.com/PhilipMay/stsb-multi-mt/"
    "30de0dec4ee199b7f42351d3f1a0b19592955385/data/stsb-en-dev.csv"
)
SHA256 = "d29586e96558c4eb52cf5ea5d14e9c24d3bf0e44f111b017caba43a5adc33226"
N = 1500
OUT = os.path.join(HERE, "labels.jsonl")


def fetch():
    req = urllib.request.Request(
        URL, headers={"User-Agent": "OpenAI File Downloader, XaiImageApiFetch/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256:
        raise SystemExit(f"sha256 mismatch: {digest}")
    return data


def main():
    rows = list(csv.reader(io.StringIO(fetch().decode("utf-8"))))
    if len(rows) != N:
        raise SystemExit(f"expected {N} rows, got {len(rows)}")
    with open(OUT, "w", encoding="utf-8") as fh:
        for i, row in enumerate(rows):
            if len(row) != 3:
                raise SystemExit(f"row {i} has {len(row)} fields")
            label = float(row[2])
            if not 0.0 <= label <= 5.0:
                raise SystemExit(f"row {i} label out of range")
            fh.write(json.dumps({"i": i, "label": label}) + "\n")
    print(f"wrote {N} labels to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
