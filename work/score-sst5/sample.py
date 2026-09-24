#!/usr/bin/env python3
"""Sampler for bead jev-zui: SST-5 test split, fixed seed, no replacement.

Source: Hugging Face dataset SetFit/sst5, file test.jsonl at revision
e51bdcd8cd3a30da231967c1a249ba59361279a3 (2210 rows, sha256 below). The file is fetched from the
pinned revision URL and refused if its sha256 differs, so the sample cannot drift.

Run: python3 work/score-sst5/sample.py 500 20260924
Writes work/score-sst5/sample.jsonl, one row per line: i (sample position), src (0-based line in
test.jsonl), text, label (0 very negative .. 4 very positive), label_text. Byte-identical on rerun.
"""

import hashlib
import json
import os
import random
import sys
import urllib.request

REVISION = "e51bdcd8cd3a30da231967c1a249ba59361279a3"
URL = f"https://huggingface.co/datasets/SetFit/sst5/resolve/{REVISION}/test.jsonl"
SHA256 = "1384216112a34f3d70b6fa210762f3399bb080410c0456ac6e54a5cb413f04b2"
ROWS = 2210
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample.jsonl")


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
    got = hashlib.sha256(body).hexdigest()
    if got != SHA256:
        raise SystemExit(f"sha256 mismatch: got {got}, want {SHA256}")
    rows = [
        json.loads(line) for line in body.decode("utf-8").splitlines() if line.strip()
    ]
    if len(rows) != ROWS:
        raise SystemExit(f"row count {len(rows)}, want {ROWS}")
    return rows


def main(n, seed):
    rows = fetch()
    picks = random.Random(seed).sample(range(len(rows)), n)
    with open(OUT, "w") as f:
        for i, src in enumerate(picks):
            r = rows[src]
            f.write(
                json.dumps(
                    {
                        "i": i,
                        "src": src,
                        "text": r["text"],
                        "label": int(r["label"]),
                        "label_text": r["label_text"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"wrote {n} rows (seed {seed}) from {ROWS} to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
