#!/usr/bin/env python3
"""Build keyless, private Jev decision units and candidate-check inputs."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import glob
import hashlib
import json
import math
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

# PTC safety: first execution is read-only. Flip only after dry-run review.
DRY_RUN = True
ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
PRIVATE_OUT = ROOT / "var" / "jev-bank"
PUBLIC_OUT = ROOT / "work" / "jev-bank"
CALIBRATION = ROOT / "work" / "jev-state-size" / "calibration-osworld-r3.tsv"
MAX_FULL_TOKENS = 32_768
MAX_LOCAL_TOKENS = 1_500
LONG_RESULT_CHARS = 10_000
CENSOR_RECENT_HOURS = 48
MIN_VERBATIM_REFERENCE_CHARS = 20
D_LABEL_SOURCE = "observed-outcome:later-exact-reference-v1"
D_LABEL_DEFINITION = (
    "relevant iff a later source-order assistant message in the same session has a text "
    "block or the text representation of a toolCall.arguments key or scalar value containing "
    "either (a) an exact, case-sensitive contiguous span of at least 20 Unicode code points "
    "from the full tool result, or (b) an exact path token or code identifier extracted from "
    "that result. Paths are slash-delimited tokens with optional leading /, ~/ or ./; "
    "terminal periods are stripped as sentence punctuation. Code identifiers are "
    "backtick-delimited tokens, qualified ASCII identifiers, or "
    "ASCII identifiers containing an underscore, digit, or internal uppercase letter. "
    "User, thinking, and toolResult content does not count. Censored rows remain unlabeled."
)
PATH_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_./~])(?:~?/|\.{1,2}/|/)?"
    r"(?:[A-Za-z0-9_.@+-]+/)+[A-Za-z0-9_.@+-]+"
    r"(?![A-Za-z0-9_./-])"
)
BACKTICK_TOKEN_RE = re.compile(r"`([^`\s]+)`")
QUALIFIED_IDENTIFIER_RE = re.compile(
    r"(?<![A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*(?:(?:\.|::)"
    r"[A-Za-z_][A-Za-z0-9_]*)+(?![A-Za-z0-9_])"
)
IDENTIFIER_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*(?![A-Za-z0-9_])")

SECRET_PATTERNS = [
    re.compile("s" "k-[A-Za-z0-9_-]{20,}"),
    re.compile(r"xai-[A-Za-z0-9]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE),
    re.compile(
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
        re.DOTALL,
    ),
    re.compile(r"apikey_[A-Za-z0-9_.-]{20,}"),
    re.compile(
        r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|passwd|authorization)\s*[:=]\s*[^\s,;]{8,}",
        re.IGNORECASE,
    ),
]
PRIVATE_PROJECTS = re.compile(
    r"clutter|cfsios|cfs-|hubspot|phoenix|accountcenter|grokbot|zesttube|alps|"
    r"control-plane|omp-orchestrator|franken-harvest|josh-claude-config",
    re.IGNORECASE,
)
HOME_PATH = re.compile(r"/Users/[^/\s]+")
_JSON_QUOTE = r'\\?"'
ANSWER_FIELD = re.compile(
    _JSON_QUOTE
    + r"(?:noul|choice|probabilities|raw_score|score)"
    + _JSON_QUOTE
    + r"\s*:",
    re.IGNORECASE,
)
ANSWER_MARKER = re.compile(
    _JSON_QUOTE + r"(?:noul|raw_score)" + _JSON_QUOTE + r"\s*:", re.IGNORECASE
)
JEV_MODEL = re.compile(
    _JSON_QUOTE
    + r"(?:model|model_id|provider|engine)"
    + _JSON_QUOTE
    + r"\s*:\s*"
    + _JSON_QUOTE
    + r'[^"]*(?:jev|typesafe)',
    re.IGNORECASE,
)
ANSWER_CONTAINER = re.compile(
    _JSON_QUOTE + r"answers" + _JSON_QUOTE + r"\s*:\s*\{", re.IGNORECASE
)
ANSWER_PROVIDER = re.compile(
    _JSON_QUOTE + r"(?:jev|typesafe)" + _JSON_QUOTE + r"\s*:\s*\{", re.IGNORECASE
)


def contains_jev_answer_shape(value: str) -> bool:
    if not ANSWER_FIELD.search(value):
        return False
    if ANSWER_MARKER.search(value):
        return True
    for marker in JEV_MODEL.finditer(value):
        start = max(0, marker.start() - 4096)
        end = min(len(value), marker.end() + 4096)
        if ANSWER_FIELD.search(value, start, end):
            return True
    for wrapper in (ANSWER_CONTAINER, ANSWER_PROVIDER):
        for marker in wrapper.finditer(value):
            end = min(len(value), marker.end() + 4096)
            if ANSWER_FIELD.search(value, marker.end(), end):
                return True
    return False


def scrub(value: str) -> str:
    value = HOME_PATH.sub("~", value)
    value = PRIVATE_PROJECTS.sub("[PRIVATE_PROJECT]", value)
    for pattern in SECRET_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    return value


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()


def source_manifest_digest(source_hashes: Iterable[tuple[str, str]]) -> str:
    manifest = hashlib.sha256()
    for source_id, file_sha in sorted(source_hashes):
        manifest.update(source_id.encode("ascii"))
        manifest.update(b"\0")
        manifest.update(file_sha.encode("ascii"))
        manifest.update(b"\n")
    return manifest.hexdigest()


def text_of(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
            elif isinstance(part, str):
                parts.append(part)
        return "\n".join(parts)
    return ""


def parse_ts(value: Any) -> dt.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return (
            parsed.replace(tzinfo=dt.timezone.utc)
            if parsed.tzinfo is None
            else parsed.astimezone(dt.timezone.utc)
        )
    except ValueError:
        return None


def calibration_min_bytes_per_token(path: Path = CALIBRATION) -> float:
    ratios = []
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row.get("outcome") == "answered" and row.get("input_tokens"):
                total = int(row["state_bytes"]) + int(row["question_bytes"])
                ratios.append(total / int(row["input_tokens"]))
    if not ratios:
        raise ValueError(f"no answered token calibration rows in {path}")
    return min(ratios)


def token_upper_bound(state: dict[str, Any], min_bytes_per_token: float) -> int:
    compact = json.dumps(state, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    return math.ceil(len(compact) / min_bytes_per_token)


def session_files() -> list[Path]:
    roots = [HOME / ".omp" / "agent" / "sessions"]
    roots.extend(
        Path(p)
        for p in glob.glob(str(HOME / ".omp" / "profiles" / "*" / "agent" / "sessions"))
    )
    found = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.jsonl"):
            if path.name.startswith(".") or ".lock" in path.name:
                continue
            found.add(path)
    return sorted(found)


def iter_jsonl(
    path: Path, source_digest: Any | None = None
) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("rb") as fh:
        for index, raw_line in enumerate(fh):
            if source_digest is not None:
                source_digest.update(raw_line)
            try:
                row = json.loads(raw_line.decode("utf-8", errors="replace"))
            except (json.JSONDecodeError, UnicodeError):
                continue
            if isinstance(row, dict):
                yield index, row


def reference_tokens(text: str) -> set[str]:
    tokens = {token.rstrip(".") for token in PATH_TOKEN_RE.findall(text)}
    tokens.update(BACKTICK_TOKEN_RE.findall(text))
    tokens.update(QUALIFIED_IDENTIFIER_RE.findall(text))
    for match in IDENTIFIER_RE.finditer(text):
        token = match.group()
        if (
            "_" in token
            or any(char.isdigit() for char in token)
            or any(char.isupper() for char in token[1:])
        ):
            tokens.add(token)
    return tokens


def argument_texts(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from argument_texts(child)
    elif isinstance(value, list):
        for child in value:
            yield from argument_texts(child)
    elif isinstance(value, (str, int, float, bool)):
        yield str(value)


def assistant_reference_texts(message: dict[str, Any]) -> Iterable[str]:
    if message.get("role") != "assistant":
        return
    content = message.get("content")
    if isinstance(content, str):
        yield content
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text" and isinstance(block.get("text"), str):
                yield block["text"]
            elif block.get("type") == "toolCall":
                yield from argument_texts(block.get("arguments"))


def has_later_exact_reference(
    source: str, source_line: int, events: Iterable[tuple[int, dict[str, Any]]]
) -> bool:
    span_hashes = {
        hash(source[offset : offset + MIN_VERBATIM_REFERENCE_CHARS])
        for offset in range(len(source) - MIN_VERBATIM_REFERENCE_CHARS + 1)
    }
    source_tokens = reference_tokens(source)
    for index, event in events:
        if index <= source_line:
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        for text in assistant_reference_texts(message):
            if source_tokens.intersection(reference_tokens(text)):
                return True
            for offset in range(len(text) - MIN_VERBATIM_REFERENCE_CHARS + 1):
                span = text[offset : offset + MIN_VERBATIM_REFERENCE_CHARS]
                if hash(span) in span_hashes and span in source:
                    return True
    return False


def longres_candidates(
    path: Path,
    group: str,
    cutoff: dt.datetime,
    now: dt.datetime,
    min_bpt: float,
    counters: collections.Counter[str],
    source_digest: Any | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    last_user = ""
    for index, row in iter_jsonl(path, source_digest):
        message = row.get("message")
        if not isinstance(message, dict):
            continue
        if message.get("role") == "user":
            last_user = text_of(message)[:500]
            continue
        if message.get("role") != "toolResult":
            continue
        raw = text_of(message)
        if len(raw) < LONG_RESULT_CHARS:
            continue
        counters["long_results"] += 1
        stamp = parse_ts(row.get("timestamp"))
        if stamp is None:
            counters["missing_timestamp"] += 1
            continue
        if stamp < cutoff:
            continue
        state_full = {
            "tool": scrub(str(message.get("toolName", ""))),
            "task": scrub(last_user),
            "result_head": scrub(raw[:350]),
            "result_tail": scrub(raw[-350:]),
            "result_chars": len(raw),
        }
        tokens = token_upper_bound(state_full, min_bpt)
        if tokens > MAX_FULL_TOKENS:
            counters["over_32k_dropped"] += 1
            continue
        if token_upper_bound(state_full, min_bpt) > MAX_LOCAL_TOKENS:
            local = {
                "tool": state_full["tool"],
                "task": state_full["task"][:160],
                "result_head": state_full["result_head"][:160],
                "result_tail": state_full["result_tail"][-160:],
                "result_chars": state_full["result_chars"],
            }
        else:
            local = state_full
        local_tokens = token_upper_bound(local, min_bpt)
        source_ref = f"omp-session:{group}:{index}"
        candidates.append(
            {
                "unit_id": sha(source_ref),
                "source": {"corpus": "omp-sessions", "ref": f"{group}:{index}"},
                "group_key": group,
                "ts": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "state_full": state_full,
                "state_local": local,
                "tokens_full": tokens,
                "tokens_local": local_tokens,
                "label": None,
                "label_source": "observed-outcome:later-exact-reference-v1",
                "censored": path.stat().st_mtime
                >= now.timestamp() - CENSOR_RECENT_HOURS * 3600,
                "baseline": {"tool": state_full["tool"], "result_chars": len(raw)},
                "_source_text": raw,
                "_line": index,
            }
        )
    return candidates


def _index_later_reference_candidates(
    rows: list[dict[str, Any]], counters: collections.Counter[str]
) -> tuple[int, dict[str, list[int]], dict[int, list[int]]]:
    token_index: dict[str, list[int]] = collections.defaultdict(list)
    span_index: dict[int, list[int]] = collections.defaultdict(list)
    eligible_count = 0
    for candidate_id, row in enumerate(rows):
        if row["censored"]:
            row["label"] = None
            counters["censored"] += 1
            continue
        eligible_count += 1
        source = row["_source_text"]
        for token in reference_tokens(source):
            token_index[token].append(candidate_id)
        spans = {
            hash(source[offset : offset + MIN_VERBATIM_REFERENCE_CHARS])
            for offset in range(len(source) - MIN_VERBATIM_REFERENCE_CHARS + 1)
        }
        for span_hash in spans:
            span_index[span_hash].append(candidate_id)
    return eligible_count, token_index, span_index


def _mark_later_references(
    text: str,
    line_no: int,
    rows: list[dict[str, Any]],
    token_index: dict[str, list[int]],
    span_index: dict[int, list[int]],
    matched: set[int],
) -> None:
    for token in reference_tokens(text):
        for candidate_id in token_index.get(token, ()):
            if rows[candidate_id]["_line"] < line_no:
                matched.add(candidate_id)
    for offset in range(len(text) - MIN_VERBATIM_REFERENCE_CHARS + 1):
        span = text[offset : offset + MIN_VERBATIM_REFERENCE_CHARS]
        for candidate_id in span_index.get(hash(span), ()):
            if (
                rows[candidate_id]["_line"] < line_no
                and span in rows[candidate_id]["_source_text"]
            ):
                matched.add(candidate_id)


def classify_later_references(
    path: Path, rows: list[dict[str, Any]], counters: collections.Counter[str]
) -> None:
    eligible_count, token_index, span_index = _index_later_reference_candidates(
        rows, counters
    )
    matched: set[int] = set()
    for line_no, event in iter_jsonl(path):
        message = event.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        for text in assistant_reference_texts(message):
            _mark_later_references(
                text, line_no, rows, token_index, span_index, matched
            )
        if len(matched) == eligible_count:
            break

    for candidate_id, row in enumerate(rows):
        if not row["censored"]:
            row["label"] = "relevant" if candidate_id in matched else "not-relevant"
            counters["labeled"] += 1
        row.pop("_line", None)
        row.pop("_source_text", None)
        row["hash"] = row["unit_id"]


def _emit_jsonl(path: Path, rows: list[dict[str, Any]], dry_run: bool) -> str:
    encoded = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in rows
    )
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(encoded, encoding="utf-8")
    return digest


def temporal_splits(
    rows: list[dict[str, Any]],
) -> tuple[dict[str, str], dt.datetime | None]:
    group_times: dict[str, list[dt.datetime]] = collections.defaultdict(list)
    for row in rows:
        if row["label"] is None:
            continue
        stamp = parse_ts(row["ts"])
        if stamp:
            group_times[row["group_key"]].append(stamp)
    intervals = sorted(
        (min(times), max(times), group) for group, times in group_times.items() if times
    )
    if len(intervals) < 2:
        return {}, None
    cut_index = min(len(intervals) - 1, max(1, math.floor(len(intervals) * 0.8)))
    cutoff = intervals[cut_index][0]
    split_map = {}
    for first, last, group in intervals:
        if last < cutoff:
            split_map[group] = "dev"
        elif first >= cutoff:
            split_map[group] = "held"
    return split_map, cutoff


def d_candidate(
    rows: list[dict[str, Any]], cutoff: dt.datetime | None
) -> dict[str, Any]:
    split_map, _ = temporal_splits(rows)
    labeled = [
        r for r in rows if r["label"] is not None and r["group_key"] in split_map
    ]
    dev = [r for r in labeled if split_map[r["group_key"]] == "dev"]
    held = [r for r in labeled if split_map[r["group_key"]] == "held"]
    # Existing prereg: DROP iff size >= T and tool is in the fixed content-tool set;
    # fit T on dev using Youden-J, tie-break highest T.
    content_tools = {
        "read",
        "bash",
        "eval",
        "grep",
        "glob",
        "find",
        "web_search",
        "web_extract",
        "fetch",
    }
    thresholds = sorted({int(r["baseline"]["result_chars"]) for r in dev}, reverse=True)
    best_t, best_j = 10**18, -1.0
    positives = sum(r["label"] == "not-relevant" for r in dev)
    negatives = len(dev) - positives
    for threshold in thresholds:
        predicted = [
            r["baseline"]["result_chars"] >= threshold
            and r["baseline"]["tool"] in content_tools
            for r in dev
        ]
        tp = sum(p and r["label"] == "not-relevant" for p, r in zip(predicted, dev))
        fp = sum(p and r["label"] == "relevant" for p, r in zip(predicted, dev))
        tpr = tp / positives if positives else 0.0
        fpr = fp / negatives if negatives else 0.0
        score = tpr - fpr
        if score > best_j or (score == best_j and threshold > best_t):
            best_t, best_j = threshold, score
    preds = {}
    for row in held:
        drop = (
            row["baseline"]["result_chars"] >= best_t
            and row["baseline"]["tool"] in content_tools
        )
        preds[row["hash"]] = "not-relevant" if drop else "relevant"
    timestamps = [
        stamp for row in labeled if (stamp := parse_ts(row["ts"])) is not None
    ]
    latest = max(timestamps) if timestamps else None
    earliest = min(timestamps) if timestamps else None
    days = (
        max(1 / 24, (latest - earliest).total_seconds() / 86400)
        if latest and earliest
        else 0
    )
    return {
        "name": "tool-result-later-reference",
        "label_source": "observed-outcome:later-exact-reference-v1",
        "censoring_rate": sum(r["censored"] for r in rows) / max(1, len(rows)),
        "recomputable": True,
        "class": "savings",
        "primitive": "Choice",
        "options": ["keep", "summarize", "drop"],
        "features": {
            "direction": "predict",
            "future": False,
            "answer_visible": False,
            "primitive": "Choice",
        },
        "min_headroom": 0.05,
        "daily_volume": len(labeled) / max(days, 1 / 24),
        "traffic": {
            "days": days,
            "opportunities": len(labeled),
            "outcomes_labelled": 0,
            "harmful": 0,
        },
        "baseline": {
            "name": f"preregistered-size-tool-threshold:{best_t}",
            "predictions": preds,
        },
        "agreement": {"n": 0, "agree": 0},
        "rows": [
            {
                "hash": r["hash"],
                "label": r["label"],
                "split": split_map[r["group_key"]],
                "group": r["group_key"],
            }
            for r in labeled
        ],
        "temporal_cutoff": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ") if cutoff else None,
    }


def run_d(
    dry_run: bool,
    cutoff: dt.datetime | None,
    as_of: dt.datetime | None = None,
) -> dict[str, Any]:
    now = as_of or dt.datetime.now(dt.timezone.utc)
    min_bpt = calibration_min_bytes_per_token()
    files = session_files()
    counters: collections.Counter[str] = collections.Counter()
    all_rows: list[dict[str, Any]] = []
    source_hashes: list[tuple[str, str]] = []
    for number, path in enumerate(files, 1):
        group = sha(str(path))
        try:
            file_digest = hashlib.sha256()
            sess = longres_candidates(
                path,
                group,
                cutoff or dt.datetime.min.replace(tzinfo=dt.timezone.utc),
                now,
                min_bpt,
                counters,
                file_digest,
            )
            source_hashes.append((group, file_digest.hexdigest()))
            if not sess:
                continue
            classify_later_references(path, sess, counters)
            all_rows.extend(sess)
        except (OSError, UnicodeError) as exc:
            counters["file_errors"] += 1
            if counters["file_errors"] <= 5:
                print(
                    f"skip unreadable session #{number}: {type(exc).__name__}",
                    file=sys.stderr,
                )
    source_manifest = source_manifest_digest(source_hashes)
    all_rows = deduplicate_units(all_rows, counters)
    split_map, split_cutoff = temporal_splits(all_rows)
    for row in all_rows:
        row["split"] = split_map.get(row["group_key"], "temporal-boundary")
    mechanical_label_audit = (
        d_mechanical_label_audit(all_rows)
        if cutoff is None
        else not_run_mechanical_label_audit(
            "filtered run excludes the full audit sample"
        )
    )
    blind_double_label = (
        d_blind_double_label(all_rows)
        if cutoff is None
        else not_run_blind_double_label("filtered run excludes the full blind sample")
    )
    units_path = PRIVATE_OUT / "tool-result" / "units.jsonl"
    digest = _emit_jsonl(units_path, all_rows, dry_run)
    candidate = d_candidate(all_rows, split_cutoff)
    candidate_path = PRIVATE_OUT / "tool-result" / "candidate.json"
    candidate_bytes = (
        json.dumps(candidate, ensure_ascii=False, separators=(",", ":")) + "\n"
    )
    candidate_sha = hashlib.sha256(candidate_bytes.encode()).hexdigest()
    if not dry_run:
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.write_text(candidate_bytes, encoding="utf-8")
    labeled = [
        r for r in all_rows if r["label"] is not None and r["split"] in {"dev", "held"}
    ]
    timestamps = [parse_ts(r["ts"]) for r in labeled]
    timestamps = [stamp for stamp in timestamps if stamp is not None]
    summary = {
        "task": "tool-result",
        "dry_run": dry_run,
        "source_files": len(files),
        "source_hashed_files": len(source_hashes),
        "source_manifest_sha256": source_manifest,
        "censor_as_of_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "units": len(all_rows),
        "labeled": len(labeled),
        "censored": sum(bool(r["censored"]) for r in all_rows),
        "censoring_rate": sum(bool(r["censored"]) for r in all_rows)
        / max(1, len(all_rows)),
        "groups": len({r["group_key"] for r in all_rows}),
        "split_groups": {
            k: len({r["group_key"] for r in labeled if r["split"] == k})
            for k in ("dev", "held")
        },
        "time_span": [
            min(timestamps).strftime("%Y-%m-%dT%H:%M:%SZ"),
            max(timestamps).strftime("%Y-%m-%dT%H:%M:%SZ"),
        ]
        if timestamps
        else [None, None],
        "temporal_cutoff": split_cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        if split_cutoff
        else None,
        "base_rate_relevant": sum(r["label"] == "relevant" for r in labeled)
        / max(1, len(labeled)),
        "dropped_over_32k": counters["over_32k_dropped"],
        "candidate_min_result_chars": LONG_RESULT_CHARS,
        "duplicate_state": counters["duplicate_state"],
        "conflicting_state": counters["conflicting_state"],
        "mechanical_label_audit": mechanical_label_audit,
        "blind_double_label": blind_double_label,
        "unit_sha256": digest,
        "candidate_sha256": candidate_sha,
    }
    if not dry_run:
        task_path = PUBLIC_OUT / "tool-result" / "task.json"
        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(
            json.dumps(
                build_task_metadata("tool-result", summary, digest, candidate_sha),
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return {"summary": summary, "candidate": candidate}


def scrub_obj(value: Any) -> Any:
    if isinstance(value, str):
        return scrub(value)
    if isinstance(value, list):
        return [scrub_obj(item) for item in value]
    if isinstance(value, dict):
        return {str(key): scrub_obj(item) for key, item in value.items()}
    return value


def redact_blind_sheet_value(value: Any) -> Any:
    if isinstance(value, str):
        if contains_jev_answer_shape(value):
            return "[MODEL_ANSWER_REDACTED]"
        return value
    if isinstance(value, list):
        return [redact_blind_sheet_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): redact_blind_sheet_value(item) for key, item in value.items()}
    return value


def localize(state: dict[str, Any], min_bpt: float) -> dict[str, Any]:
    local = json.loads(json.dumps(state, ensure_ascii=False))
    text_fields = [
        key
        for key, value in local.items()
        if isinstance(value, str) and key not in {"domain", "tool"}
    ]
    while token_upper_bound(local, min_bpt) > MAX_LOCAL_TOKENS and text_fields:
        key = max(text_fields, key=lambda item: len(local[item]))
        value = local[key]
        if len(value) <= 32:
            text_fields.remove(key)
            continue
        keep = max(32, int(len(value) * 0.8))
        local[key] = value[: keep // 2] + "\n[…]\n" + value[-(keep - keep // 2) :]
    return local


def make_teacher_unit(
    domain: str,
    source_ref: str,
    group: str,
    ts: str,
    state: dict[str, Any],
    label: str,
    min_bpt: float,
    counters: collections.Counter[str],
) -> dict[str, Any] | None:
    state_full = scrub_obj(state)
    tokens_full = token_upper_bound(state_full, min_bpt)
    if tokens_full > MAX_FULL_TOKENS:
        counters["over_32k_dropped"] += 1
        return None
    state_local = localize(state_full, min_bpt)
    tokens_local = token_upper_bound(state_local, min_bpt)
    if tokens_local > MAX_LOCAL_TOKENS:
        counters["local_over_1500_dropped"] += 1
        return None
    reference = f"{domain}:{source_ref}"
    unit_id = sha(reference)
    return {
        "unit_id": unit_id,
        "source": {"corpus": domain, "ref": sha(source_ref)},
        "group_key": group,
        "ts": ts,
        "state_full": state_full,
        "state_local": state_local,
        "tokens_full": tokens_full,
        "tokens_local": tokens_local,
        "label": label,
        "label_source": "paid-jev-1.13.0-decision",
        "censored": False,
        "hash": unit_id,
    }


def unit_state_key(row: dict[str, Any]) -> str:
    return sha(
        json.dumps(
            row["state_full"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
    )


def deduplicate_units(
    rows: list[dict[str, Any]], counters: collections.Counter[str]
) -> list[dict[str, Any]]:
    kept: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = unit_state_key(row)
        previous = kept.get(key)
        if previous is None:
            kept[key] = row
        elif previous["label"] == row["label"]:
            counters["duplicate_state"] += 1
        else:
            previous["label"] = None
            previous["censored"] = True
            previous["split"] = "label-conflict"
            counters["conflicting_state"] += 1
    return list(kept.values())


def read_rows(path: Path, source_digest: Any | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        if source_digest is not None:
            source_digest.update(b"<missing>")
        return []
    return [row for _, row in iter_jsonl(path, source_digest)]


def read_source_rows(
    path: Path, source_hashes: list[tuple[str, str]]
) -> list[dict[str, Any]]:
    digest = hashlib.sha256()
    rows = read_rows(path, digest)
    source_hashes.append((sha(str(path)), digest.hexdigest()))
    return rows


def model_is_1130(row: dict[str, Any]) -> bool:
    return isinstance(row.get("model"), str) and "1.13.0" in row["model"]


def best_join(
    rows: list[dict[str, Any]], stamp: dt.datetime | None
) -> dict[str, Any] | None:
    if not rows:
        return None
    if stamp is None:
        return rows[0]

    def distance(row: dict[str, Any]) -> float:
        other = parse_ts(row.get("ts"))
        return abs((other - stamp).total_seconds()) if other else float("inf")

    return min(rows, key=distance)


def build_gate_units(
    min_bpt: float,
    counters: collections.Counter[str],
    source_hashes: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    base = HOME / ".local" / "state" / "jev"
    full_rows = read_source_rows(base / "gate-observe-full.jsonl", source_hashes)
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in full_rows:
        by_key[(str(row.get("session", "")), str(row.get("cmdSha", "")))].append(row)
    units = []
    for row in read_source_rows(base / "gate-observe.jsonl", source_hashes):
        if row.get("status") != "scored" or row.get("jevSkipped") is True:
            counters["gate_not_paid_scored"] += 1
            continue
        if not model_is_1130(row):
            counters["gate_wrong_model"] += 1
            continue
        if not isinstance(row.get("flag"), bool):
            counters["gate_invalid_label"] += 1
            continue
        key = (str(row.get("session", "")), str(row.get("cmdSha", "")))
        side = best_join(by_key.get(key, []), parse_ts(row.get("ts")))
        if not side or not isinstance(side.get("cmd"), str):
            counters["gate_missing_state"] += 1
            continue
        stamp = parse_ts(row.get("ts"))
        if stamp is None:
            counters["gate_missing_timestamp"] += 1
            continue
        group = sha("gate-session:" + key[0])
        unit = make_teacher_unit(
            "gate",
            f"{key[0]}:{key[1]}:{row['ts']}",
            group,
            stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            {"domain": "command-gate", "command": side["cmd"]},
            "pos" if row["flag"] else "neg",
            min_bpt,
            counters,
        )
        if unit:
            units.append(unit)
            counters["gate_joined"] += 1
    return units


def memory_join_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("instance", "")),
        str(row.get("promptHash", "")),
        str(row.get("memoryHash", "")),
    )


def build_memory_units(
    min_bpt: float,
    counters: collections.Counter[str],
    source_hashes: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    base = HOME / ".local" / "state" / "jev"
    full_rows = read_source_rows(base / "memory-filter-full.jsonl", source_hashes)
    by_key: dict[tuple[str, str, str], list[dict[str, Any]]] = collections.defaultdict(
        list
    )
    for row in full_rows:
        key = memory_join_key(row)
    units = []
    for row in read_source_rows(base / "memory-filter.jsonl", source_hashes):
        if row.get("status") != "scored" or not model_is_1130(row):
            counters["memory_not_paid_scored"] += 1
            continue
        decision = row.get("decision")
        if decision not in {"drop", "keep"}:
            counters["memory_invalid_label"] += 1
            continue
        key = memory_join_key(row)
        side = best_join(by_key.get(key, []), parse_ts(row.get("ts")))
        if (
            not side
            or not isinstance(side.get("prompt"), str)
            or not isinstance(side.get("memory"), str)
        ):
            counters["memory_missing_state"] += 1
            continue
        stamp = parse_ts(row.get("ts"))
        if stamp is None:
            counters["memory_missing_timestamp"] += 1
            continue
        group = sha("memory-instance:" + key[0])
        unit = make_teacher_unit(
            "memory",
            f"{key[0]}:{key[1]}:{key[2]}:{row['ts']}",
            group,
            stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            {
                "domain": "memory-filter",
                "prompt": side["prompt"],
                "memory": side["memory"],
            },
            "pos" if decision == "drop" else "neg",
            min_bpt,
            counters,
        )
        if unit:
            units.append(unit)
            counters["memory_joined"] += 1
    return units


def build_injection_units(
    min_bpt: float,
    counters: collections.Counter[str],
    source_hashes: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    base = HOME / ".local" / "state" / "jev"
    scored = [
        row
        for row in read_source_rows(base / "injection-shadow.jsonl", source_hashes)
        if row.get("status") == "scored"
        and model_is_1130(row)
        and isinstance(row.get("flag"), bool)
    ]
    targets: dict[str, list[int]] = collections.defaultdict(list)
    for index, row in enumerate(scored):
        if isinstance(row.get("outputSha256"), str):
            targets[row["outputSha256"]].append(index)
    sources: dict[int, tuple[dt.datetime, str, str, int, str]] = {}
    if targets:
        for path in session_files():
            session_group = sha(str(path))
            file_digest = hashlib.sha256()
            for line_no, event in iter_jsonl(path, file_digest):
                message = event.get("message")
                if not isinstance(message, dict) or message.get("role") != "toolResult":
                    continue
                tool = str(message.get("toolName", ""))
                raw = text_of(message)
                digest = sha(raw)
                if digest not in targets:
                    continue
                stamp = parse_ts(event.get("timestamp"))
                if stamp is None:
                    continue
                for target_index in targets[digest]:
                    target = scored[target_index]
                    if target.get("toolName") == tool:
                        sources[target_index] = (
                            stamp,
                            session_group,
                            str(path),
                            line_no,
                            raw,
                        )
            source_hashes.append((session_group, file_digest.hexdigest()))
        counters["injection_sources_joined"] = len(sources)
        counters["injection_sources_missing"] = len(scored) - len(sources)
    units = []
    for index, row in enumerate(scored):
        source = sources.get(index)
        if source is None:
            continue
        stamp, group, path, line_no, raw = source
        target_ts = parse_ts(row.get("ts"))
        if target_ts and abs((target_ts - stamp).total_seconds()) > 300:
            counters["injection_timestamp_mismatch"] += 1
            continue
        unit = make_teacher_unit(
            "injection",
            f"{sha(path)}:{line_no}:{row['outputSha256']}:{row['ts']}",
            group,
            (target_ts or stamp).strftime("%Y-%m-%dT%H:%M:%SZ"),
            {
                "domain": "tool-result-injection",
                "tool": row.get("toolName", ""),
                "result": raw,
            },
            "pos" if row["flag"] else "neg",
            min_bpt,
            counters,
        )
        if unit:
            units.append(unit)
            counters["injection_joined"] += 1
    return units


def teacher_candidate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    split_map, cutoff = temporal_splits(rows)
    selected = [
        row
        for row in rows
        if row["label"] is not None and row["group_key"] in split_map
    ]
    dev = [row for row in selected if split_map[row["group_key"]] == "dev"]
    held = [row for row in selected if split_map[row["group_key"]] == "held"]
    rate = sum(row["label"] == "pos" for row in dev) / max(1, len(dev))
    guess = "pos" if rate >= 0.5 else "neg"
    return {
        "name": "local-student-agreement-with-paid-decisions",
        "label_source": "teacher-decision",
        "censoring_rate": 0.0,
        "recomputable": True,
        "class": "savings",
        "primitive": "Choice",
        "options": ["act", "pass"],
        "features": {
            "direction": "predict",
            "future": False,
            "answer_visible": False,
            "primitive": "Choice",
        },
        "min_headroom": 0.05,
        "daily_volume": len(selected),
        "action_value": 0.001,
        "traffic": {
            "days": 1,
            "opportunities": len(selected),
            "outcomes_labelled": 0,
            "harmful": 0,
        },
        "baseline": {
            "name": "dev-majority-paid-action-rate",
            "predictions": {row["hash"]: guess for row in held},
        },
        "agreement": {"n": 0, "agree": 0},
        "rows": [
            {
                "hash": row["hash"],
                "label": row["label"],
                "split": split_map[row["group_key"]],
                "group": row["group_key"],
            }
            for row in selected
        ],
        "temporal_cutoff": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ") if cutoff else None,
    }


def g_blind_double_label(
    rows: list[dict[str, Any]], evidence_root: Path = PUBLIC_OUT
) -> dict[str, Any]:
    manifest_path = evidence_root / "blind-sample-manifest.json"
    rubric_path = evidence_root / "blind-rubrics.json"
    label_paths = {
        "WildCarp": evidence_root / "vvkr-labels-wildcarp.json",
        "HazySpring": evidence_root / "vvkr-labels-hazyspring.json",
    }
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    sample = manifest["tasks"]["G"]
    ids = sample["ids"]
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError("G blind sample must contain 50 unique IDs")
    candidate_ids = {row.get("unit_id") for row in rows}
    if not set(ids).issubset(candidate_ids):
        raise ValueError("G blind sample contains IDs not in candidate rows")

    labels: dict[str, dict[str, str]] = {}
    packets: set[str] = set()
    label_hashes: dict[str, str] = {}
    for labeler, path in label_paths.items():
        raw = path.read_bytes()
        record = json.loads(raw)
        entries = record["G"]
        if (
            record.get("labeler") != labeler
            or record.get("rubric_only") is not True
            or len(entries) != len(ids)
        ):
            raise ValueError(f"invalid G blind labels from {labeler}")
        pairs = dict(entries)
        if len(pairs) != len(entries) or set(pairs) != set(ids):
            raise ValueError(f"G blind label IDs do not match sample for {labeler}")
        if not set(pairs.values()).issubset({"act", "pass"}):
            raise ValueError(f"invalid G blind label value from {labeler}")
        labels[labeler] = pairs
        packets.add(record["packet"])
        label_hashes[path.name] = hashlib.sha256(raw).hexdigest()
    if len(packets) != 1:
        raise ValueError("G blind label packet IDs disagree")

    left, right = labels.values()
    agree = sum(left[item] == right[item] for item in ids)
    observed = agree / len(ids)
    left_counts = collections.Counter(left.values())
    right_counts = collections.Counter(right.values())
    expected = sum(
        left_counts[value] * right_counts[value] for value in ("act", "pass")
    ) / (len(ids) ** 2)
    kappa = (observed - expected) / (1 - expected) if expected < 1 else None
    rubric_bytes = rubric_path.read_bytes()
    return {
        "n": len(ids),
        "agree": agree,
        "agreement": observed,
        "cohen_kappa": kappa,
        "status": "COMPLETE",
        "labelers": list(labels),
        "packet": next(iter(packets)),
        "seed": sample["seed"],
        "rubric_sha256": sample["rubric_sha256"],
        "sample_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "rubric_file_sha256": hashlib.sha256(rubric_bytes).hexdigest(),
        "label_files_sha256": label_hashes,
    }


def not_run_blind_double_label(reason: str) -> dict[str, Any]:
    return {"n": 0, "agree": 0, "status": "NOT_RUN", "reason": reason}


def d_blind_double_label(
    rows: list[dict[str, Any]], evidence_root: Path = PUBLIC_OUT
) -> dict[str, Any]:
    manifest_path = evidence_root / "blind-sample-manifest.json"
    rubric_path = evidence_root / "blind-rubrics.json"
    labels_path = evidence_root / "vvkr-D-blind-labels.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    sample = manifest["tasks"]["D"]
    ids = sample["ids"]
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError("D blind sample must contain 50 unique IDs")
    candidate_ids = {row.get("unit_id") for row in rows}
    if not set(ids).issubset(candidate_ids):
        raise ValueError("D blind sample contains IDs not in candidate rows")

    if not labels_path.is_file():
        return {
            **not_run_blind_double_label("D blind-label artifact is missing"),
            "expected_rubric_sha256": sample["rubric_sha256"],
            "sample_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        }

    labels_bytes = labels_path.read_bytes()
    record = json.loads(labels_bytes)
    sample_ids_sha = hashlib.sha256(
        json.dumps(ids, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if (
        record.get("schema_version") != "jev.decision-bank.blind-labels.v1"
        or record.get("task") != "D"
        or record.get("seed") != sample["seed"]
        or record.get("sample_ids_sha256") != sample_ids_sha
    ):
        raise ValueError("D blind-label metadata does not match the frozen sample")

    rubric_bytes = rubric_path.read_bytes()
    rubrics = json.loads(rubric_bytes)
    rubric_sha = hashlib.sha256(
        json.dumps(
            rubrics["D"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    if rubric_sha != sample["rubric_sha256"]:
        raise ValueError("D blind rubric does not match the frozen sample")
    if record.get("rubric_sha256") != sample["rubric_sha256"]:
        observed_rubric_sha = record.get("rubric_sha256")
        return {
            **not_run_blind_double_label(
                "D blind labels use a different rubric; agreement is not claimed"
            ),
            "expected_rubric_sha256": sample["rubric_sha256"],
            "observed_rubric_sha256": observed_rubric_sha,
            "sample_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "label_artifact_sha256": hashlib.sha256(labels_bytes).hexdigest(),
        }

    labelers: dict[str, dict[str, str]] = {}
    source_hashes: dict[str, str] = {}
    label_records = record.get("labelers")
    if not isinstance(label_records, dict) or set(label_records) != {
        "WildCarp",
        "HazySpring",
    }:
        raise ValueError("D blind-label artifact must contain exactly two labelers")
    for labeler in ("WildCarp", "HazySpring"):
        label_record = label_records[labeler]
        if not isinstance(label_record, dict):
            raise TypeError(f"invalid D blind-label record for {labeler}")
        if label_record.get("blind") is not True:
            raise ValueError(f"D blind labels were not marked blind for {labeler}")
        entries = label_record["labels"]
        if not isinstance(entries, list) or len(entries) != len(ids):
            raise ValueError(f"invalid D blind labels from {labeler}")
        pairs = dict(entries)
        if len(pairs) != len(entries) or set(pairs) != set(ids):
            raise ValueError(f"D blind label IDs do not match sample for {labeler}")
        if not set(pairs.values()).issubset({"relevant", "not-relevant"}):
            raise ValueError(f"invalid D blind label value from {labeler}")
        source_sha = label_record["source_artifact_sha256"]
        if (
            not isinstance(source_sha, str)
            or len(source_sha) != 64
            or any(char not in "0123456789abcdef" for char in source_sha.lower())
        ):
            raise ValueError(f"invalid D label source hash for {labeler}")
        labelers[labeler] = pairs
        source_hashes[labeler] = source_sha

    left, right = (labelers[name] for name in ("WildCarp", "HazySpring"))
    agree = sum(left[item] == right[item] for item in ids)
    observed = agree / len(ids)
    left_counts = collections.Counter(left.values())
    right_counts = collections.Counter(right.values())
    expected = sum(
        left_counts[value] * right_counts[value]
        for value in ("relevant", "not-relevant")
    ) / (len(ids) ** 2)
    kappa = (observed - expected) / (1 - expected) if expected < 1 else None
    return {
        "n": len(ids),
        "agree": agree,
        "agreement": observed,
        "cohen_kappa": kappa,
        "status": "COMPLETE",
        "labelers": ["WildCarp", "HazySpring"],
        "seed": sample["seed"],
        "rubric_sha256": sample["rubric_sha256"],
        "sample_ids_sha256": sample_ids_sha,
        "sample_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "rubric_file_sha256": hashlib.sha256(rubric_bytes).hexdigest(),
        "label_artifact_sha256": hashlib.sha256(labels_bytes).hexdigest(),
        "label_files_sha256": source_hashes,
    }


def d_mechanical_label_audit(
    rows: list[dict[str, Any]], evidence_root: Path = PUBLIC_OUT
) -> dict[str, Any]:
    manifest_path = evidence_root / "blind-sample-manifest.json"
    labels_path = evidence_root / "vvkr-D-mechanical-labels-wildcarp.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    ids = manifest["tasks"]["D"]["ids"]
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError("D mechanical audit sample must contain 50 unique IDs")
    labels_bytes = labels_path.read_bytes()
    labels = json.loads(labels_bytes)
    if set(labels) != set(ids) or len(labels) != len(ids):
        raise ValueError("D mechanical labels do not match the frozen sample")
    candidate_labels = {
        row["unit_id"]: row["label"]
        for row in rows
        if isinstance(row.get("unit_id"), str)
    }
    if not set(ids).issubset(candidate_labels):
        raise ValueError("D mechanical audit contains IDs not in candidate rows")
    if any(candidate_labels[item] != labels[item] for item in ids):
        raise ValueError("D mechanical labels disagree with builder outcomes")
    return {
        "n": len(ids),
        "matched": len(ids),
        "counts": dict(sorted(collections.Counter(labels.values()).items())),
        "status": "MATCHED_TO_BUILDER",
        "sample_seed": manifest["tasks"]["D"]["seed"],
        "sample_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "label_artifact_sha256": hashlib.sha256(labels_bytes).hexdigest(),
        "label_definition_sha256": sha(D_LABEL_DEFINITION),
    }


def not_run_mechanical_label_audit(reason: str) -> dict[str, Any]:
    return {"n": 0, "matched": 0, "status": "NOT_RUN", "reason": reason}


def build_task_metadata(
    task: str, summary: dict[str, Any], units_sha: str, candidate_sha: str
) -> dict[str, Any]:
    if task == "tool-result":
        return {
            "schema_version": "jev.decision-bank.task.v1",
            "decision": "whether a long tool result is referenced later in the same session",
            "consumer": "long-result keep/summarize/drop routing experiment",
            "class": "savings",
            "primitive": "Choice",
            "options": ["keep", "summarize", "drop"],
            "label_source": D_LABEL_SOURCE,
            "label_definition": D_LABEL_DEFINITION,
            "label_definition_sha256": sha(D_LABEL_DEFINITION),
            "positive_label": "relevant",
            "base_rate": summary.get("base_rate_relevant"),
            "censoring_rate": summary.get("censoring_rate"),
            "N": summary.get("labeled"),
            "N_units_including_censored": summary.get("units"),
            "N_groups": summary.get("groups"),
            "N_groups_by_split": summary.get("split_groups"),
            "source_files": summary.get("source_files"),
            "source_hashed_files": summary.get("source_hashed_files"),
            "source_manifest_sha256": summary.get("source_manifest_sha256"),
            "censor_as_of_utc": summary.get("censor_as_of_utc"),
            "dropped_over_32k": summary.get("dropped_over_32k"),
            "duplicate_state": summary.get("duplicate_state"),
            "conflicting_state": summary.get("conflicting_state"),
            "candidate_min_result_chars": summary.get("candidate_min_result_chars"),
            "time_span_utc": summary.get("time_span"),
            "temporal_cutoff_utc": summary.get("temporal_cutoff"),
            "mechanical_label_audit": summary.get("mechanical_label_audit"),
            "blind_double_label": summary.get(
                "blind_double_label", {"n": 0, "agree": 0, "status": "NOT_RUN"}
            ),
            "unit_path": "var/jev-bank/tool-result/units.jsonl",
            "units_sha256": units_sha,
            "candidate_path": "var/jev-bank/tool-result/candidate.json",
            "candidate_sha256": candidate_sha,
        }
    return {
        "schema_version": "jev.decision-bank.task.v1",
        "decision": "whether local models agree with paid Jev 1.13.0 action on state_local",
        "consumer": "local nimble/tev1 route before paid Jev; teacher labels are action proxies only",
        "class": "savings",
        "primitive": "Choice",
        "options": ["act", "pass"],
        "label_source": "paid-jev-1.13.0-decision; not truth",
        "positive_label": "pos = paid Jev took action",
        "base_rate": summary.get("base_rate_action"),
        "censoring_rate": 0.0,
        "N": summary.get("units"),
        "N_groups": summary.get("groups"),
        "N_groups_by_split": summary.get("split_groups"),
        "time_span_utc": summary.get("time_span"),
        "temporal_cutoff_utc": summary.get("temporal_cutoff"),
        "blind_double_label": summary.get("blind_double_label"),
        "unit_path": "var/jev-bank/teacher-student/units.jsonl",
        "units_sha256": units_sha,
        "candidate_path": "var/jev-bank/teacher-student/candidate.json",
        "candidate_sha256": candidate_sha,
        "source_files": summary.get("source_files"),
        "source_hashed_files": summary.get("source_hashed_files"),
        "source_manifest_sha256": summary.get("source_manifest_sha256"),
        "source_counts": summary.get("source_counts"),
        "dropped": summary.get("dropped"),
    }


def run_teacher(dry_run: bool, cutoff: dt.datetime | None) -> dict[str, Any]:
    min_bpt = calibration_min_bytes_per_token()
    counters: collections.Counter[str] = collections.Counter()
    source_hashes: list[tuple[str, str]] = []
    rows = (
        build_gate_units(min_bpt, counters, source_hashes)
        + build_injection_units(min_bpt, counters, source_hashes)
        + build_memory_units(min_bpt, counters, source_hashes)
    )
    if cutoff:
        rows = [
            row for row in rows if parse_ts(row["ts"]) and parse_ts(row["ts"]) >= cutoff
        ]
    rows = deduplicate_units(rows, counters)
    split_map, split_cutoff = temporal_splits(rows)
    for row in rows:
        row["split"] = split_map.get(row["group_key"], "temporal-boundary")
    blind_double_label = (
        g_blind_double_label(rows)
        if cutoff is None
        else not_run_blind_double_label("filtered run excludes the full blind sample")
    )
    units_sha = _emit_jsonl(
        PRIVATE_OUT / "teacher-student" / "units.jsonl", rows, dry_run
    )
    candidate = teacher_candidate(rows)
    candidate_bytes = (
        json.dumps(candidate, ensure_ascii=False, separators=(",", ":")) + "\n"
    )
    candidate_sha = hashlib.sha256(candidate_bytes.encode()).hexdigest()
    if not dry_run:
        path = PRIVATE_OUT / "teacher-student" / "candidate.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(candidate_bytes, encoding="utf-8")
    selected = [
        row
        for row in rows
        if row["label"] is not None and row["split"] in {"dev", "held"}
    ]
    timestamps = [parse_ts(row["ts"]) for row in selected]
    timestamps = [stamp for stamp in timestamps if stamp is not None]
    summary = {
        "task": "teacher-student",
        "dry_run": dry_run,
        "units": len(rows),
        "selected": len(selected),
        "groups": len({row["group_key"] for row in rows}),
        "split_groups": {
            key: len({row["group_key"] for row in selected if row["split"] == key})
            for key in ("dev", "held")
        },
        "time_span": [
            min(timestamps).strftime("%Y-%m-%dT%H:%M:%SZ"),
            max(timestamps).strftime("%Y-%m-%dT%H:%M:%SZ"),
        ]
        if timestamps
        else [None, None],
        "temporal_cutoff": split_cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        if split_cutoff
        else None,
        "base_rate_action": sum(row["label"] == "pos" for row in selected)
        / max(1, len(selected)),
        "blind_double_label": blind_double_label,
        "source_files": len(source_hashes),
        "source_hashed_files": len(source_hashes),
        "source_manifest_sha256": source_manifest_digest(source_hashes),
        "unit_sha256": units_sha,
        "candidate_sha256": candidate_sha,
        "source_counts": {
            key: counters[key]
            for key in sorted(counters)
            if key.endswith(("_joined", "_missing"))
        },
        "dropped": {
            key: counters[key]
            for key in (
                "over_32k_dropped",
                "local_over_1500_dropped",
                "duplicate_state",
                "conflicting_state",
            )
        },
    }
    if not dry_run:
        task_path = PUBLIC_OUT / "teacher-student" / "task.json"
        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(
            json.dumps(
                build_task_metadata(
                    "teacher-student", summary, units_sha, candidate_sha
                ),
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return {"summary": summary, "candidate": candidate}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=("tool-result", "teacher-student"))
    parser.add_argument(
        "--write",
        action="store_true",
        help="write private rows/candidate after reviewing a dry run",
    )
    parser.add_argument(
        "--since", help="include source events since this ISO-8601 UTC time"
    )
    parser.add_argument(
        "--as-of", help="freeze the tool-result 48-hour censor boundary"
    )
    args = parser.parse_args()
    dry_run = DRY_RUN and not args.write
    cutoff = parse_ts(args.since) if args.since else None
    if args.since and cutoff is None:
        parser.error("--since must be an ISO-8601 timestamp")
    as_of = parse_ts(args.as_of) if args.as_of else None
    if args.as_of and as_of is None:
        parser.error("--as-of must be an ISO-8601 timestamp")
    if args.as_of and args.task != "tool-result":
        parser.error("--as-of applies only to tool-result")
    result = (
        run_d(dry_run, cutoff, as_of)
        if args.task == "tool-result"
        else run_teacher(dry_run, cutoff)
    )
    print(json.dumps(result["summary"], sort_keys=True))
    if dry_run:
        print("DRY RUN: no rows written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
