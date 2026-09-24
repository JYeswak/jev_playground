#!/usr/bin/env python3
"""Sampler for bead jev-wx5: FEVER claim/evidence pairs, fixed seed, one pair per claim.

Source: copenlu/fever_gold_evidence `valid.jsonl` on Hugging Face at revision a6b8d891 (refused
unless its sha256 matches). That file is FEVER's labelled paper_dev split with evidence text
attached: gold Wikipedia sentences for SUPPORTS and REFUTES, and for NOT ENOUGH INFO the sentences
the Papelo retrieval system returned (FEVER ships no evidence for NEI). The sampler also downloads
FEVER's own paper_dev.jsonl from fever.ai (sha256-pinned) and refuses to run unless every row's
claim and label match FEVER's for the same id.

Pool: one pair per FEVER claim id, the first row for that id in file order whose evidence has
non-empty text (the file repeats a claim once per evidence set; some NEI rows carry an empty
sentence, which is dropped, and a row left with no text is skipped). Truth: SUPPORTS is true;
REFUTES and NOT ENOUGH INFO are false.

State text, frozen with the bar: title = the evidence pages in order of first appearance,
underscores as spaces, joined by "; ". abstract = the evidence sentences joined by spaces; when the
evidence spans more than one page, each sentence is prefixed "<page>: ". FEVER's bracket tokens
(-LRB- -RRB- -LSB- -RSB- -LCB- -RCB-) are restored in both; all other tokenization is left as is.

Run: python3 work/noul-fever/sample.py 400 20260924
Writes work/noul-fever/sample.jsonl: i, fever_id, claim, title, abstract, pages, gold
(SUPPORTS | REFUTES | NEI), truth (bool). Byte-identical on rerun.
"""

import hashlib
import json
import os
import random
import sys
import urllib.request

COPENLU = (
    "https://huggingface.co/datasets/copenlu/fever_gold_evidence/resolve/"
    "a6b8d891d393e97a4efac791afffb2d7de5e57c6/valid.jsonl"
)
COPENLU_SHA256 = "5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9"
FEVER = "https://fever.ai/download/fever/paper_dev.jsonl"
FEVER_SHA256 = "41158707810008747946bf23471e82df53e77a513524b9e3ec1c2e674ef5ef8c"
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample.jsonl")
BRACKETS = {
    "-LRB-": "(",
    "-RRB-": ")",
    "-LSB-": "[",
    "-RSB-": "]",
    "-LCB-": "{",
    "-RCB-": "}",
}
GOLD = {"SUPPORTS": "SUPPORTS", "REFUTES": "REFUTES", "NOT ENOUGH INFO": "NEI"}


def fetch(url, sha):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        body = r.read()
    got = hashlib.sha256(body).hexdigest()
    if got != sha:
        raise SystemExit(f"sha256 mismatch for {url}: got {got}, want {sha}")
    return [
        json.loads(line) for line in body.decode("utf-8").splitlines() if line.strip()
    ]


def detok(text):
    for tok, ch in BRACKETS.items():
        text = text.replace(tok, ch)
    return text


def pool(rows, fever):
    truth_by_id = {r["id"]: (r["claim"], r["label"]) for r in fever}
    seen, pairs, empty = set(), [], 0
    for r in rows:
        if truth_by_id.get(r["original_id"]) != (r["claim"], r["label"]):
            raise SystemExit(
                f"claim/label disagree with FEVER paper_dev for id {r['original_id']}"
            )
        evidence = [(p, s.strip()) for p, _, s in r["evidence"] if s.strip()]
        if not evidence:
            empty += 1
            continue
        if r["original_id"] in seen:
            continue
        seen.add(r["original_id"])
        pages = []
        for page, _ in evidence:
            if page not in pages:
                pages.append(page)
        names = [detok(p.replace("_", " ")) for p in pages]
        if len(pages) == 1:
            abstract = " ".join(detok(s) for _, s in evidence)
        else:
            abstract = " ".join(
                f"{names[pages.index(p)]}: {detok(s)}" for p, s in evidence
            )
        pairs.append(
            {
                "fever_id": r["original_id"],
                "claim": r["claim"],
                "title": "; ".join(names),
                "abstract": abstract,
                "pages": len(pages),
                "gold": GOLD[r["label"]],
                "truth": r["label"] == "SUPPORTS",
            }
        )
    print(
        f"pool: {len(pairs)} claims; {empty} rows skipped for empty evidence text",
        file=sys.stderr,
    )
    return pairs


def main(n, seed):
    pairs = pool(fetch(COPENLU, COPENLU_SHA256), fetch(FEVER, FEVER_SHA256))
    picks = random.Random(seed).sample(range(len(pairs)), n)
    with open(OUT, "w") as f:
        for i, k in enumerate(picks):
            f.write(json.dumps({"i": i, **pairs[k]}, ensure_ascii=False) + "\n")
    print(f"wrote {n} of {len(pairs)} claims (seed {seed}) to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
