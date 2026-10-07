#!/usr/bin/env python3
"""Collect the frozen 48-hour long-result cohort without storing full results."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import random
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
WINDOW_START = dt.datetime.fromisoformat("2026-10-02T22:00:00+00:00")
WINDOW_END = dt.datetime.fromisoformat("2026-10-04T22:00:00+00:00")
SEED = 20261008
DEV_COUNT = 100
HELD_COUNT = 100
MIN_RESULT_CHARS = 10_000
MIN_LONG_WORDS = 6
CONTENT_WORD_CHARS = 40
PROBE_CHARS = 60
PRIOR_CORPORA = (
    ROOT / "work/longres/corpus.json",
    BASE / "corpus.json",
    ROOT / "work/longres/corpus2.json",
)
PROTECTED_CORPUS = (BASE / "corpus.json").resolve()
DEFAULT_OUTPUT = BASE / "timewindow-corpus.json"
SESSION_ROOTS = (
    Path.home() / ".omp/agent/sessions",
)


def text_of(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and isinstance(block.get("text"), str)
        )
    return content if isinstance(content, str) else ""


def timestamp_of(value: object) -> dt.datetime | None:
    try:
        timestamp = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=dt.timezone.utc)
    return timestamp.astimezone(dt.timezone.utc)


def reference_probes(text: str) -> tuple[str, str, str] | None:
    """Match the original extractor's frozen three-probe selection exactly."""
    words = [word for word in text.split() if len(word) >= CONTENT_WORD_CHARS]
    if len(words) < MIN_LONG_WORDS:
        return None
    third = len(words) // 3
    return (words[third][:PROBE_CHARS], words[2 * third][:PROBE_CHARS], words[-2][:PROBE_CHARS])


def canonical_path_hash(path: Path) -> str:
    return hashlib.sha256(path.resolve().as_posix().encode("utf-8")).hexdigest()


def prior_exclusions() -> tuple[set[str], set[str]]:
    source_hashes: set[str] = set()
    result_hash_prefixes: set[str] = set()
    for corpus_path in PRIOR_CORPORA:
        try:
            corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid prior corpus: {corpus_path}") from error
        for row in corpus["dev"] + corpus["held"]:
            source_hashes.add(canonical_path_hash(Path(row["file"])))
            digest = row.get("win_sha")
            if isinstance(digest, str) and digest:
                result_hash_prefixes.add(digest.lower())
    return source_hashes, result_hash_prefixes


def session_files() -> list[Path]:
    roots = [*SESSION_ROOTS]
    roots.extend(sorted(Path.home().glob(".omp/profiles/*/agent/sessions")))
    files: list[Path] = []
    for root in roots:
        try:
            slugs = sorted(root.iterdir())
        except OSError:
            continue
        for slug in slugs:
            if not slug.is_dir():
                continue
            try:
                files.extend(
                    item.resolve()
                    for item in sorted(slug.iterdir())
                    if not item.name.startswith(".")
                    and item.name.endswith(".jsonl")
                    and item.is_file()
                )
            except OSError:
                continue
    return sorted(set(files))


def _rows_for_file(
    path: Path,
    source_hash: str,
    prior_result_hash_prefixes: set[str],
    counts: dict[str, int],
) -> list[dict[str, object]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        counts["unreadable_files"] += 1
        return []

    output: list[dict[str, object]] = []
    last_user = ""
    for index, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if role == "user":
            last_user = text_of(message)[:500]
            continue
        if role != "toolResult":
            continue
        timestamp = timestamp_of(entry.get("timestamp"))
        if timestamp is None or not WINDOW_START <= timestamp < WINDOW_END:
            continue
        result = text_of(message)
        if len(result) < MIN_RESULT_CHARS:
            continue
        counts["eligible_after_source_exclusion"] += 1
        full_hash = hashlib.sha256(result.encode("utf-8")).hexdigest()
        if any(full_hash.startswith(prefix) for prefix in prior_result_hash_prefixes):
            counts["prior_result_hash_prefix_exclusions"] += 1
            continue
        probes = reference_probes(result)
        if probes is None:
            counts["unlabelable_fewer_than_six_long_words"] += 1
            continue
        counts["labelable_after_all_exclusions"] += 1
        later = "\n".join(lines[index + 1 : index + 400])
        output.append(
            {
                "_source_path": path.as_posix(),
                "source_path_sha256": source_hash,
                "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
                "full_result_sha256": full_hash,
                "tool": message.get("toolName", ""),
                "size": len(result),
                "head": result[:350],
                "tail": result[-350:],
                "task": last_user,
                "ref": any(probe in later for probe in probes),
            }
        )
    return output


def _sample(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_file: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_file.setdefault(str(row["_source_path"]), []).append(row)
    paths = sorted(by_file)
    # The frozen seed requires repeatability; cryptographic randomness is undesirable here.
    rng = random.Random(SEED)  # nosec B311
    rng.shuffle(paths)
    midpoint = len(paths) // 2
    dev_paths = set(paths[:midpoint])
    held_paths = set(paths[midpoint:])
    dev = [row for path in paths if path in dev_paths for row in by_file[path]]
    held = [row for path in paths if path in held_paths for row in by_file[path]]
    rng.shuffle(dev)
    rng.shuffle(held)
    dev, held = dev[:DEV_COUNT], held[:HELD_COUNT]
    for index, row in enumerate(dev):
        row["sample_id"] = f"d{index:03d}"
    for index, row in enumerate(held):
        row["sample_id"] = f"h{index:03d}"
    for row in dev + held:
        row.pop("_source_path", None)
    return dev, held


def collect() -> dict[str, object]:
    excluded_paths, prior_hash_prefixes = prior_exclusions()
    counts = {
        "source_files_scanned": 0,
        "source_files_excluded": 0,
        "unreadable_files": 0,
        "eligible_after_source_exclusion": 0,
        "prior_result_hash_prefix_exclusions": 0,
        "unlabelable_fewer_than_six_long_words": 0,
        "labelable_after_all_exclusions": 0,
    }
    rows: list[dict[str, object]] = []
    for path in session_files():
        counts["source_files_scanned"] += 1
        source_hash = canonical_path_hash(path)
        if source_hash in excluded_paths:
            counts["source_files_excluded"] += 1
            continue
        rows.extend(_rows_for_file(path, source_hash, prior_hash_prefixes, counts))

    dev, held = _sample(rows)
    held_referenced = sum(bool(row["ref"]) for row in held)
    held_unreferenced = len(held) - held_referenced
    enough_data = (
        len(rows) >= DEV_COUNT + HELD_COUNT
        and len(dev) == DEV_COUNT
        and len(held) == HELD_COUNT
        and held_referenced >= 20
        and held_unreferenced >= 20
    )
    return {
        "status": "READY" if enough_data else "NOT ENOUGH DATA",
        "window_start": WINDOW_START.isoformat().replace("+00:00", "Z"),
        "window_end_exclusive": WINDOW_END.isoformat().replace("+00:00", "Z"),
        "seed": SEED,
        "counts": counts,
        "weekly_volume_estimate": round(counts["labelable_after_all_exclusions"] * 7 / 2),
        "probe_method": "three 60-character slices from the three evenly spaced long words at indices floor(n/3), floor(2n/3), and -2; each word must be at least 40 characters; rows with fewer than six such words are unlabelable, matching work/longres/extract.py",
        "dev": dev,
        "held": held,
    }


def write_corpus(path: Path, corpus: object) -> None:
    target = path.resolve()
    if target == PROTECTED_CORPUS:
        raise ValueError(f"refusing to write excluded prior corpus: {target}")
    target.write_text(json.dumps(corpus, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.resolve() == PROTECTED_CORPUS:
        raise SystemExit(f"refusing to write excluded prior corpus: {args.output.resolve()}")
    corpus = collect()
    write_corpus(args.output, corpus)
    counts = cast(dict[str, int], corpus["counts"])
    dev = cast(list[dict[str, object]], corpus["dev"])
    held = cast(list[dict[str, object]], corpus["held"])
    summary = {
        "status": corpus["status"],
        "counts": counts,
        "dev": len(dev),
        "held": len(held),
        "held_referenced": sum(bool(row["ref"]) for row in held),
        "held_unreferenced": sum(not bool(row["ref"]) for row in held),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if corpus["status"] == "READY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
