#!/usr/bin/env python3
"""Run the preregistered free OpenRouter incumbent through the shared checkpoint runner."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import hmac
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODEL = "dots-studio/dots-3-note-preview:free"
CANDIDATES = HERE / "candidates-nfcorpus.jsonl"
CANDIDATES_SHA256 = "1ef3835708d8522ed39f2f2bd4018ea07390e403bcfd8e00119580e69860e3ec"
PREREG = HERE / "PREREG-jev-97bq.md"
ZIP_SHA256 = "efe5be03f8c5b86a5870102d0599d227c8c6e2484328e68c6522560385671b0b"
ZIP_PATH = Path(os.environ.get("BEIR_NFCORPUS_ZIP", "/tmp/beir-nfcorpus/nfcorpus.zip"))

sys.path.insert(0, str(ROOT / "upstream/typesafe-ai/typesafe-sdk-python/src"))
sys.path.insert(0, str(ROOT / "upstream/typesafe-ai/system-one-adapter-python/src"))
sys.path.insert(0, str(ROOT))

from kit.experiment.run import run as checkpoint_run  # noqa: E402
from system_one_adapter import AsyncSystemOneAdapterClient  # noqa: E402
from system_one_adapter.providers.openai import AsyncOpenAIProvider  # noqa: E402
from typesafe_sdk import Choice, RetryPolicy  # noqa: E402


def load_base() -> Any:
    os.environ["BEIR_DATASET"] = "nfcorpus"
    os.environ["BEIR_CANDIDATES"] = str(CANDIDATES)
    os.environ["BEIR_ZIP_PATH"] = str(ZIP_PATH)
    os.environ["BEIR_ZIP_SHA256"] = ZIP_SHA256
    path = HERE / "run.py"
    spec = importlib.util.spec_from_file_location("rerank_base_jev97bq", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load rerank helpers from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_corpus() -> list[dict[str, Any]]:
    digest = hashlib.sha256(CANDIDATES.read_bytes()).hexdigest()
    if not hmac.compare_digest(digest, CANDIDATES_SHA256):
        raise RuntimeError(f"candidate SHA mismatch: {digest}")
    rows = [
        json.loads(line) for line in CANDIDATES.read_text().splitlines() if line.strip()
    ]
    if len(rows) != 234 or len({row["qid"] for row in rows}) != 234:
        raise RuntimeError("candidate file must contain 234 unique NFCorpus queries")
    if any(len(row["cands"]) != 20 or not row["rel"] for row in rows):
        raise RuntimeError("every candidate row must have 20 candidates and qrels")
    return rows


def question(doc_ids: list[str]) -> Choice:
    return Choice(
        instructions=(
            "Select the candidate passage most relevant to the query. "
            "Choose the passage that best answers or provides evidence for the query; "
            "choose among the IDs."
        ),
        criteria={doc_id: f"Candidate passage with ID {doc_id}." for doc_id in doc_ids},
    )


async def run_arm(
    output: Path, reach: Path, items: Path, prereg: Path, resume: bool
) -> int:
    rows = validate_corpus()
    base = load_base()
    corpus, queries = base.load_text()
    provider = AsyncOpenAIProvider(
        MODEL,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        api="chat_completions",
    )
    client = AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(),
    )
    invalid = 0
    errors = 0

    async def answer(item: dict[str, Any]) -> dict[str, Any]:
        nonlocal invalid, errors
        qid = item["qid"]
        docs = base.candidate_docs(qid)
        started = time.perf_counter()
        try:
            response = await client.system_one(
                base.state_for(corpus, queries, qid, qid),
                {base.QNAME: question(docs)},
                model=provider,
            )
            answer_obj = response.answers.get(base.QNAME)
            choice = getattr(answer_obj, "choice", None)
            usage = response.usage
            row: dict[str, Any] = {
                "qid": qid,
                "model": MODEL,
                "latencyMs": int((time.perf_counter() - started) * 1000),
                "usage": {
                    "input_tokens": int(usage.input_tokens_total),
                    "output_tokens": int(usage.output_tokens_total),
                },
            }
            if not isinstance(choice, str) or choice not in docs:
                invalid += 1
                row.update(
                    {
                        "status": "invalid",
                        "invalid_reason": "missing or out-of-set choice",
                        "raw_choice_type": type(choice).__name__,
                    }
                )
                return row
            row.update({"status": "ok", "choice": choice})
            return row
        except Exception as exc:  # noqa: BLE001 - checkpoint the failure and continue boundedly
            errors += 1
            return {
                "qid": qid,
                "model": MODEL,
                "status": "error",
                "error": f"{type(exc).__name__}: {str(exc)[:500]}",
                "latencyMs": int((time.perf_counter() - started) * 1000),
            }

    items_for_run = [{"qid": row["qid"]} for row in rows]
    if not resume and output.exists():
        raise RuntimeError(f"output exists; pass --resume to continue: {output}")
    async with client:
        await checkpoint_run(
            items_for_run,
            answer,
            output,
            id_key="qid",
            live=True,
            reach=reach,
            items_path=items,
            prereg_path=prereg,
        )
    await provider.aclose()
    print(
        json.dumps(
            {
                "status": "complete",
                "invalid": invalid,
                "errors": errors,
                "rows": len(rows),
            }
        )
    )
    return 0 if invalid == 0 and errors == 0 else 3


def selftest() -> int:
    validate_corpus()
    if not PREREG.exists():
        raise RuntimeError(f"missing preregistration: {PREREG}")
    print("SELFTEST PASS: 234 unique candidates, 20 candidates/query, pinned SHA")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=HERE / "rows-jev-97bq-openrouter.jsonl"
    )
    parser.add_argument(
        "--reach", type=Path, default=HERE / "reach-receipt-jev-97bq.json"
    )
    parser.add_argument("--items", type=Path, default=CANDIDATES)
    parser.add_argument("--prereg", type=Path, default=PREREG)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("OPENROUTER_API_KEY is not set; no call made")
    return asyncio.run(
        run_arm(args.output, args.reach, args.items, args.prereg, args.resume)
    )


if __name__ == "__main__":
    raise SystemExit(main())
