#!/usr/bin/env python3
"""Sampler for bead jev-76o: Yelp review stars (yelp_review_full test split), fixed seed.

Source: Hugging Face dataset Yelp/yelp_review_full, file
yelp_review_full/test-00000-of-00001.parquet at revision c1f9ee939b7d05667af864ee1cb066393154bf85
(50,000 rows, sha256 below). The file is fetched from the pinned revision URL and refused if its
sha256 differs, so the sample cannot drift.

The review text is under the Yelp dataset licence, and this repository is public, so no review
text is committed. Two files are written:
  sample.jsonl  (committed)  i, src (0-based row in the parquet), label (0 = 1 star .. 4 = 5 stars),
                             chars, text_sha256
  texts.jsonl   (gitignored) i, text: what the live runner sends. It is checked against
                             text_sha256 before any call.

Run (needs pyarrow; uv provides it without touching any project):
  uv run --no-project --python 3.12 --with pyarrow==21.0.0 python work/score-yelp/sample.py 500 20260924
  uv run --no-project --python 3.12 --with pyarrow==21.0.0 python work/score-yelp/sample.py 500 20260924 --check
--check rebuilds in memory and exits 1 unless sample.jsonl is byte-identical.
"""

import hashlib
import io
import json
import os
import random
import sys
import urllib.request

REVISION = "c1f9ee939b7d05667af864ee1cb066393154bf85"
URL = (
    "https://huggingface.co/datasets/Yelp/yelp_review_full/resolve/"
    f"{REVISION}/yelp_review_full/test-00000-of-00001.parquet"
)
SHA256 = "bf06d5969bff93ecd4a6d4b330643761ce108b42e9b8a894cf82c9df02a08540"
ROWS = 50000
HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample.jsonl")
TEXTS = os.path.join(HERE, "texts.jsonl")


def fetch():
    import pyarrow.parquet as pq

    with urllib.request.urlopen(URL, timeout=120) as r:
        body = r.read()
    got = hashlib.sha256(body).hexdigest()
    if got != SHA256:
        raise SystemExit(f"sha256 mismatch: got {got}, want {SHA256}")
    table = pq.read_table(io.BytesIO(body)).to_pydict()
    if len(table["label"]) != ROWS:
        raise SystemExit(f"row count {len(table['label'])}, want {ROWS}")
    return table["label"], table["text"]


def build(n, seed):
    labels, texts = fetch()
    picks = random.Random(seed).sample(range(ROWS), n)
    sample, text_rows = [], []
    for i, src in enumerate(picks):
        text = texts[src]
        sample.append(
            json.dumps(
                {
                    "i": i,
                    "src": src,
                    "label": int(labels[src]),
                    "chars": len(text),
                    "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                }
            )
            + "\n"
        )
        text_rows.append(json.dumps({"i": i, "text": text}, ensure_ascii=False) + "\n")
    return "".join(sample), "".join(text_rows)


def main(n, seed, check):
    sample, texts = build(n, seed)
    if check:
        same = os.path.exists(SAMPLE) and open(SAMPLE).read() == sample
        print("check: identical" if same else "check: DIFFERS", file=sys.stderr)
        return 0 if same else 1
    with open(SAMPLE, "w") as f:
        f.write(sample)
    with open(TEXTS, "w") as f:
        f.write(texts)
    print(
        f"wrote {n} rows (seed {seed}) from {ROWS} to {SAMPLE} and {TEXTS}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4) or (len(sys.argv) == 4 and sys.argv[3] != "--check"):
        raise SystemExit("usage: sample.py N SEED [--check]")
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), len(sys.argv) == 4))
