#!/usr/bin/env python3
"""Rebuild the committed Civil Comments sample from the pinned validation parquet.

No model call. Refuses a parquet sha256 mismatch or a sample that is not
byte-identical to work/noul-toxicity/sample.jsonl.
"""

import hashlib
import json
import os
import random
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
URL = (
    "https://huggingface.co/datasets/google/civil_comments/resolve/"
    "f2970eb3a55777454c94069077cc8d9b5866312d/data/validation-00000-of-00001.parquet"
)
PARQUET_SHA = "2e0eb65474e7e1290df8689fc93eea783160c898c09ae15382c0a9662367bd03"
SAMPLE_SHA = "99b860a9f7ce9c81f4177aae29bf05d2a63756515edcb48b986294a3266e0493"
N_SPLIT = 97320
N = 2000
SEED = 20260924
CUT = 0.5


def fetch(dest):
    req = urllib.request.Request(
        URL, headers={"User-Agent": "OpenAI File Downloader, XaiImageApiFetch/1.0"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as fh:
        fh.write(resp.read())
    digest = hashlib.sha256(open(dest, "rb").read()).hexdigest()
    if digest != PARQUET_SHA:
        raise SystemExit(f"parquet sha256 mismatch: {digest}")


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else "/tmp/civil-comments-val.parquet"
    if (
        not os.path.exists(dest)
        or hashlib.sha256(open(dest, "rb").read()).hexdigest() != PARQUET_SHA
    ):
        fetch(dest)
    out = "/tmp/civil-val-rebuild.jsonl"
    subprocess.check_call(
        [
            "duckdb",
            "-c",
            f"COPY (SELECT row_number() OVER () - 1 AS src, text, toxicity "
            f"FROM '{dest}') TO '{out}' (FORMAT JSON);",
        ]
    )
    rows = [json.loads(line) for line in open(out) if line.strip()]
    if len(rows) != N_SPLIT:
        raise SystemExit(f"expected {N_SPLIT} rows, got {len(rows)}")
    rng = random.Random(SEED)
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    pick = sorted(idx[:N])
    body = []
    for i, src in enumerate(pick):
        row = rows[src]
        body.append(
            json.dumps(
                {
                    "i": i,
                    "src": int(row["src"]),
                    "label": 1 if row["toxicity"] >= CUT else 0,
                    "toxicity": row["toxicity"],
                    "text": row["text"],
                },
                ensure_ascii=False,
            )
        )
    text = "\n".join(body) + "\n"
    digest = hashlib.sha256(text.encode()).hexdigest()
    if digest != SAMPLE_SHA:
        raise SystemExit(f"sample sha256 mismatch: {digest}")
    print(f"sample matches {SAMPLE_SHA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
