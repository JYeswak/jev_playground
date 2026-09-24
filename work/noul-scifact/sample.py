#!/usr/bin/env python3
"""Sampler for bead jev-9er: SciFact claim/abstract pairs, fixed seed, no replacement.

Source: AllenAI's SciFact release tarball (the URL the Hugging Face loader allenai/scifact @
1fe54665 downloads), refused unless its sha256 matches. Pool: every (claim, cited abstract) pair in
claims_train.jsonl and claims_dev.jsonl (the test split ships without labels). Truth: the pair is
true when SciFact's rationale label for that abstract is SUPPORT; CONTRADICT and no rationale
(NOT ENOUGH INFO) are false.

Run: python3 work/noul-scifact/sample.py 400 20260924
Writes work/noul-scifact/sample.jsonl: i, split, claim_id, doc_id, claim, title, abstract,
gold (SUPPORT | CONTRADICT | NEI), truth (bool). Byte-identical on rerun.
"""

import hashlib
import io
import json
import os
import random
import sys
import tarfile
import urllib.request

URL = "https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz"
SHA256 = "11c621288d41ac144d29b13b0f8503b3820b7d6e8b1f6ff24dff335c196d76be"
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample.jsonl")


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
    got = hashlib.sha256(body).hexdigest()
    if got != SHA256:
        raise SystemExit(f"sha256 mismatch: got {got}, want {SHA256}")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tar:
        for name in ("claims_train.jsonl", "claims_dev.jsonl", "corpus.jsonl"):
            data = tar.extractfile(f"data/{name}").read().decode("utf-8")
            files[name] = [
                json.loads(line) for line in data.splitlines() if line.strip()
            ]
    return files


def pool(files):
    corpus = {d["doc_id"]: d for d in files["corpus.jsonl"]}
    pairs = []
    for split in ("train", "dev"):
        for c in files[f"claims_{split}.jsonl"]:
            for doc_id in c["cited_doc_ids"]:
                ev = c["evidence"].get(str(doc_id))
                if ev:
                    labels = {e["label"] for e in ev}
                    if len(labels) != 1:
                        raise SystemExit(
                            f"mixed labels for claim {c['id']} doc {doc_id}"
                        )
                    gold = labels.pop()
                else:
                    gold = "NEI"
                doc = corpus[doc_id]
                pairs.append(
                    {
                        "split": split,
                        "claim_id": c["id"],
                        "doc_id": doc_id,
                        "claim": c["claim"],
                        "title": doc["title"],
                        "abstract": " ".join(s.strip() for s in doc["abstract"]),
                        "gold": gold,
                        "truth": gold == "SUPPORT",
                    }
                )
    return pairs


def main(n, seed):
    pairs = pool(fetch())
    picks = random.Random(seed).sample(range(len(pairs)), n)
    with open(OUT, "w") as f:
        for i, k in enumerate(picks):
            f.write(json.dumps({"i": i, **pairs[k]}, ensure_ascii=False) + "\n")
    print(f"wrote {n} of {len(pairs)} pairs (seed {seed}) to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
