# /// script
# requires-python = ">=3.12"
# dependencies = ["bm25s==0.3.11", "PyStemmer==3.1.0", "numpy==2.5.3"]
# ///
"""BM25 shortlists for bead jev-nssg (BEIR SciFact rerank). No model call, no key.

  uv run --script work/rerank-scifact/build.py            # writes candidates.jsonl
  uv run --script work/rerank-scifact/build.py --check    # rebuild and compare bytes

BM25 is bm25s (the fast-search library docs-mirror/typesafe/cookbooks/rerank_typesafe.md uses) with
Anserini's BEIR "flat" settings: method lucene, k1 0.9, b 0.4, English stopwords, English Snowball
stemmer, document = title + " " + text. Every one of the 5,183 abstracts is scored for every test
query; ties break by corpus-file order, so the ranking is total and deterministic.

Feasibility, fixed before this script first ran: full-corpus BM25 nDCG@10 must land within 0.03 of
Anserini's published BM25 (flat) 0.6789 (castorini/anserini
docs/fatjar-regressions/fatjar-regressions-v1.6.0.md:419). Outside that band the floor is not a
credible BM25 and the build exits 3.

Output rows carry ids, BM25 scores and qrels ids only. Query and abstract text are not written.
The zip has no license file. AllenAI LICENSE.md (fetched 2026-09-24) licenses claims CC BY 4.0 and
abstracts ODC-By 1.0; the HuggingFace card also says CC BY-NC 2.0. Text stays in the pinned zip.
"""

import hashlib
import json
import math
import os
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP_URL = (
    "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
)
ZIP_SHA256 = "536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165"
ZIP_PATH = os.environ.get("BEIR_SCIFACT_ZIP", "/tmp/beir-scifact/scifact.zip")
DEPTH = 20
K1, B = 0.9, 0.4
ANSERINI_FLAT_NDCG10 = 0.6789
TOLERANCE = 0.03
OUT = os.path.join(HERE, "candidates.jsonl")


def fetch_zip(path=ZIP_PATH):
    """Download once, then refuse any byte that is not the pinned archive."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(
            ZIP_URL,
            headers={"User-Agent": "OpenAI File Downloader, XaiImageApiFetch/1.0"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp, open(path, "wb") as fh:
            fh.write(resp.read())
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if digest != ZIP_SHA256:
        raise SystemExit(
            f"scifact.zip sha256 mismatch: got {digest}, want {ZIP_SHA256}"
        )
    return path


def load(path=ZIP_PATH):
    """corpus (ordered list of dicts), queries {qid: text}, test qrels {qid: {docid}}."""
    with zipfile.ZipFile(fetch_zip(path)) as zf:
        corpus = [
            json.loads(line)
            for line in zf.read("scifact/corpus.jsonl").decode("utf-8").splitlines()
            if line.strip()
        ]
        queries = {
            q["_id"]: q["text"]
            for q in (
                json.loads(line)
                for line in zf.read("scifact/queries.jsonl")
                .decode("utf-8")
                .splitlines()
                if line.strip()
            )
        }
        qrels = {}
        lines = zf.read("scifact/qrels/test.tsv").decode("utf-8").splitlines()
        if lines[0].split("\t") != ["query-id", "corpus-id", "score"]:
            raise SystemExit(f"unexpected qrels header: {lines[0]!r}")
        for line in lines[1:]:
            if not line.strip():
                continue
            qid, did, score = line.split("\t")
            if int(score) > 0:
                qrels.setdefault(qid, set()).add(did)
    return corpus, queries, qrels


def ndcg10(ranked, rel):
    dcg = sum(1 / math.log2(i + 2) for i, d in enumerate(ranked[:10]) if d in rel)
    idcg = sum(1 / math.log2(i + 2) for i in range(min(10, len(rel))))
    return dcg / idcg


def build():
    import bm25s
    import numpy as np
    import Stemmer

    corpus, queries, qrels = load()
    stemmer = Stemmer.Stemmer("english")
    ids = [d["_id"] for d in corpus]
    docs = [(d.get("title") or "") + " " + (d.get("text") or "") for d in corpus]
    retriever = bm25s.BM25(method="lucene", k1=K1, b=B)
    retriever.index(
        bm25s.tokenize(docs, stopwords="en", stemmer=stemmer, show_progress=False)
    )
    qids = sorted(qrels, key=int)
    q_tokens = bm25s.tokenize(
        [queries[q] for q in qids],
        stopwords="en",
        stemmer=stemmer,
        return_ids=False,
        show_progress=False,
    )
    order = np.arange(len(ids))
    rows, full = [], []
    for qid, toks in zip(qids, q_tokens):
        scores = retriever.get_scores(toks)
        rank = np.lexsort((order, -scores))  # score desc, then corpus order
        ranked = [ids[i] for i in rank]
        full.append(ndcg10(ranked, qrels[qid]))
        top = rank[:DEPTH]
        rows.append(
            {
                "qid": qid,
                "cands": [[ids[i], round(float(scores[i]), 6)] for i in top],
                "rel": sorted(qrels[qid], key=int),
            }
        )
    text = "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows)
    return text, sum(full) / len(full), rows


def main(argv):
    text, full_ndcg, rows = build()
    digest = hashlib.sha256(text.encode()).hexdigest()
    in_top = sum(sum(1 for d, _ in r["cands"] if d in set(r["rel"])) for r in rows)
    n_rel = sum(len(r["rel"]) for r in rows)
    print(f"queries={len(rows)} relevant={n_rel} relevant_in_top{DEPTH}={in_top}")
    print(
        f"full-corpus BM25 nDCG@10={full_ndcg:.4f} (Anserini flat {ANSERINI_FLAT_NDCG10})"
    )
    print(f"candidates sha256={digest}")
    if abs(full_ndcg - ANSERINI_FLAT_NDCG10) > TOLERANCE:
        print("FEASIBILITY FAIL: BM25 outside the published band", file=sys.stderr)
        return 3
    if "--check" in argv:
        have = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if have != text:
            print(
                "CHECK FAIL: rebuilt candidates differ from the committed file",
                file=sys.stderr,
            )
            return 1
        print("CHECK PASS: rebuilt candidates are byte-identical")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
