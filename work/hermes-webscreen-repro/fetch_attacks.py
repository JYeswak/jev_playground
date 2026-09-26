#!/usr/bin/env python3
"""Arm B attacks: every label=1 row of deepset/prompt-injections, fetched from the HF datasets-server.

Neither Hermes nor this lane wrote these rows. The text goes to --raw (outside the tree); the
committed manifest (--manifest) holds split, row index, character count and a sha256 per row, plus
the Hub revision the rows were read at, so a re-fetch can be checked row by row.

    python3 work/hermes-webscreen-repro/fetch_attacks.py \
        --raw var/agent-tmp/hermes-webscreen-repro/attacks-b.jsonl \
        --manifest work/hermes-webscreen-repro/attacks-b-manifest.json
"""

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

DATASET = "deepset/prompt-injections"
UA = "OpenAI File Downloader, XaiImageApiFetch/1.0"
PAGE = 100


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    hub = get(f"https://huggingface.co/api/datasets/{DATASET}")
    splits = [
        s["split"]
        for s in get(
            f"https://datasets-server.huggingface.co/splits?dataset={DATASET}"
        )["splits"]
    ]
    rows = []
    for split in sorted(splits, key=lambda s: (s != "train", s)):
        offset = 0
        while True:
            page = get(
                f"https://datasets-server.huggingface.co/rows?dataset={DATASET}&config=default"
                f"&split={split}&offset={offset}&length={PAGE}"
            )
            got = page.get("rows") or []
            for item in got:
                rows.append({"split": split, "row_idx": item["row_idx"], **item["row"]})
            offset += len(got)
            if not got or offset >= page.get("num_rows_total", 0):
                break
    attacks, seen = [], set()
    for row in rows:
        if row.get("label") != 1 or row["text"] in seen:
            continue
        seen.add(row["text"])
        attacks.append(
            {
                "id": f"B{len(attacks):03d}",
                "split": row["split"],
                "row_idx": row["row_idx"],
                "text": row["text"],
            }
        )
    raw = Path(args.raw)
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(
        "".join(json.dumps(a, ensure_ascii=False) + "\n" for a in attacks),
        encoding="utf-8",
    )
    manifest = {
        "dataset": DATASET,
        "hub_sha": hub.get("sha"),
        "hub_last_modified": hub.get("lastModified"),
        "license": (hub.get("cardData") or {}).get("license"),
        "user_agent": UA,
        "rows_total": len(rows),
        "label1_rows": sum(1 for r in rows if r.get("label") == 1),
        "label1_unique_texts": len(attacks),
        "attacks": [
            {
                "id": a["id"],
                "split": a["split"],
                "row_idx": a["row_idx"],
                "chars": len(a["text"]),
                "sha256": hashlib.sha256(a["text"].encode("utf-8")).hexdigest(),
            }
            for a in attacks
        ],
    }
    Path(args.manifest).write_text(
        json.dumps(manifest, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in manifest.items() if k != "attacks"}))


if __name__ == "__main__":
    main()
