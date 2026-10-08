#!/usr/bin/env python3
"""Freeze and sample the X7 event frame without committing command text."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import random
import re
import stat
import subprocess
import sys
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = Path.home() / ".local" / "state" / "jev"
PRIOR_MANIFEST = ROOT / "work" / "jev-1lim" / "manifest.jsonl"
PREREG = ROOT / "work" / "x7-gate-rules" / "unflagged-PREREG.md"
PREPARE = ROOT / "work" / "x7-gate-rules" / "prepare.py"
RUNNER = ROOT / "work" / "x7-gate-rules" / "run.mjs"
FILTER_SOURCE = ROOT / "work" / "bicameral-gate" / "real-sample.py"
HOOK_SOURCE = ROOT / ".omp" / "hooks" / "post" / "jev-gate-observe.ts"
FRAME_PATH = ROOT / "work" / "x7-gate-rules" / "frame.jsonl"
FRAME_MANIFEST_PATH = ROOT / "work" / "x7-gate-rules" / "frame-manifest.json"
SAMPLE_PATH = ROOT / "work" / "x7-gate-rules" / "sample.jsonl"
SAMPLE_MANIFEST_PATH = ROOT / "work" / "x7-gate-rules" / "sample-manifest.json"
DCG_ARGS = ["dcg", "test", "--stdin", "--format", "json", "--robot", "--dialect", "posix", "--agent", "omp"]
LABEL_SEED = 20261005
PER_STRATUM = 200
MAX_COMMAND_CHARS = 1_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_jsonl(rows: Iterable[dict[str, Any]]) -> str:
    lines = [json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for row in rows]
    return "" if not lines else "\n".join(lines) + "\n"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON at {path.name}:{number}") from error
            if not isinstance(row, dict):
                raise ValueError(f"non-object JSON at {path.name}:{number}")
            rows.append(row)
    return rows


def parse_dcg_result(stdout: str, returncode: int) -> str:
    if returncode != 0:
        return "error"
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError:
        return "error"
    if not isinstance(result, dict):
        return "error"
    decision = result.get("decision")
    return decision if isinstance(decision, str) and decision in {"allow", "deny", "warn"} else "error"


def _literal_regex(node: ast.AST) -> tuple[str, int]:
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "compile" or not node.args:
        raise ValueError("privacy filter source shape changed")
    pattern = ast.literal_eval(node.args[0])
    flags = 0
    for keyword in node.keywords:
        if keyword.arg == "flags":
            value = keyword.value
            if isinstance(value, ast.Attribute) and value.attr == "I":
                flags |= re.IGNORECASE
            else:
                flags |= int(ast.literal_eval(value))
    if not isinstance(pattern, str):
        raise ValueError("privacy filter pattern is not text")
    return pattern, flags


def load_privacy_filters(source: Path = FILTER_SOURCE) -> tuple[re.Pattern[str], re.Pattern[str]]:
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=source.name)
    patterns: dict[str, re.Pattern[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = {target.id for target in node.targets if isinstance(target, ast.Name)}
        for name in ("PRIVATE", "SECRET"):
            if name in names:
                pattern, flags = _literal_regex(node.value)
                patterns[name] = re.compile(pattern, flags)
    if set(patterns) != {"PRIVATE", "SECRET"}:
        raise ValueError("both committed privacy filters are required")
    return patterns["PRIVATE"], patterns["SECRET"]


def privacy_exclusion(command: str, filters: tuple[re.Pattern[str], re.Pattern[str]]) -> str | None:
    if len(command) > MAX_COMMAND_CHARS:
        return "too-large"
    private, secret = filters
    if private.search(command):
        return "private"
    if secret.search(command):
        return "secret"
    return None


def _event_id(row: dict[str, Any], occurrence: int) -> str:
    identity = [row["ts"], row["session"], row["cmd_sha"], occurrence]
    return sha256(json.dumps(identity, separators=(",", ":"), ensure_ascii=True).encode())


def assign_event_ids(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    occurrences: Counter[tuple[str, str, str]] = Counter()
    result = []
    for row in rows:
        key = (row["ts"], row["session"], row["cmd_sha"])
        occurrence = occurrences[key]
        occurrences[key] += 1
        result.append({**row, "event_id": _event_id(row, occurrence)})
    return result


def _prior_keys(prior_rows: Iterable[dict[str, Any]]) -> tuple[set[str], set[str]]:
    event_ids: set[str] = set()
    command_hashes: set[str] = set()
    for row in prior_rows:
        event_id = row.get("event_id", row.get("id"))
        command_hash = row.get("cmd_sha", row.get("cmdSha"))
        if isinstance(event_id, str):
            event_ids.add(event_id)
        if isinstance(command_hash, str):
            command_hashes.add(command_hash)
    return event_ids, command_hashes


def exclude_prior_rows(rows: Iterable[dict[str, Any]], prior_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    prior_ids, prior_hashes = _prior_keys(prior_rows)
    return [
        row for row in rows
        if row.get("event_id") not in prior_ids and row.get("cmd_sha", row.get("cmdSha")) not in prior_hashes
    ]


def draw_sample(rows: list[dict[str, Any]], seed: int = LABEL_SEED, per_stratum: int = PER_STRATUM) -> list[dict[str, Any]]:
    if per_stratum < 0:
        raise ValueError("per_stratum must be non-negative")
    if len({row.get("event_id") for row in rows}) != len(rows):
        raise ValueError("frame event IDs must be unique")
    rng = random.Random(seed)
    selected = []
    for stratum in ("deny", "allow"):
        population = [row for row in rows if row.get("dcg_decision") == stratum]
        sample_n = min(per_stratum, len(population))
        for row in rng.sample(population, sample_n):
            selected.append({
                **row,
                "stratum": stratum,
                "population_n": len(population),
                "sample_n": sample_n,
                "inclusion_probability": sample_n / len(population),
            })
    return sorted(selected, key=lambda row: (row["stratum"], row["event_id"]))


def match_command_occurrences(events: Iterable[dict[str, Any]], transcript_calls: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    available: dict[tuple[str, str], deque[str]] = defaultdict(deque)
    for call in transcript_calls:
        session, command = call.get("session"), call.get("command")
        if isinstance(session, str) and isinstance(command, str):
            available[(session, sha256(command.encode("utf-8")))].append(command)
    matched = []
    for event in events:
        session = event.get("session")
        command_hash = event.get("cmd_sha", event.get("cmdSha"))
        commands = available[(session, command_hash)]
        if commands:
            matched.append({**event, "source_match": "matched", "_command": commands.popleft()})
        else:
            matched.append({**event, "source_match": "unreadable"})
    return matched


def _parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError("cutoff must be an ISO-8601 UTC timestamp ending in Z")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("cutoff must be UTC")
    return parsed


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def _require_committed_clean(paths: Iterable[Path]) -> str:
    relpaths = [str(path.resolve().relative_to(ROOT)) for path in paths]
    tracked = _git("ls-files", "--error-unmatch", "--", *relpaths)
    if tracked.returncode != 0:
        raise RuntimeError("required X7 inputs must be tracked and committed")
    clean = _git("diff", "--quiet", "HEAD", "--", *relpaths)
    if clean.returncode != 0:
        raise RuntimeError("required X7 inputs have uncommitted changes")
    commit = _git("rev-parse", "HEAD")
    if commit.returncode != 0:
        raise RuntimeError("cannot resolve the committed X7 inputs")
    return commit.stdout.strip()


def _prereg_commit() -> str:
    result = _git("log", "-1", "--format=%H", "--", str(PREREG.relative_to(ROOT)))
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("preregistration must be committed before frame preparation")
    return result.stdout.strip()


def _source_logs(state_dir: Path) -> list[Path]:
    paths = []
    current = state_dir / "gate-observe.jsonl"
    if current.is_file():
        paths.append(current)
    if state_dir.is_dir():
        paths.extend(path for path in sorted(state_dir.glob("gate-observe.jsonl.*.archive")) if path.is_file())
    if not paths:
        raise RuntimeError("no gate-observe event logs found")
    return paths


def _read_observe_rows(state_dir: Path, cutoff: datetime) -> tuple[list[dict[str, Any]], list[Path], Counter[str]]:
    paths = _source_logs(state_dir)
    rows = []
    counts: Counter[str] = Counter()
    for path in paths:
        with path.open(encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"invalid event JSON at {path.name}:{number}") from error
                if not isinstance(row, dict):
                    raise ValueError(f"non-object event row at {path.name}:{number}")
                timestamp, session, command_hash, status = (row.get("ts"), row.get("session"), row.get("cmdSha"), row.get("status"))
                if not all(isinstance(value, str) for value in (timestamp, session, command_hash, status)):
                    raise ValueError(f"event identity fields missing at {path.name}:{number}")
                if _parse_utc(timestamp) > cutoff:
                    counts["after_cutoff"] += 1
                    continue
                counts["through_cutoff"] += 1
                rows.append({
                    "ts": timestamp,
                    "session": session,
                    "cmd_sha": command_hash,
                    "status": status,
                    "skipped": row.get("skipped"),
                    "_source_file": path.name,
                    "_line": number,
                })
    rows.sort(key=lambda row: (row["ts"], row["_source_file"], row["_line"]))
    return assign_event_ids(rows), paths, counts


def _session_id(path: Path) -> str:
    stem = path.name[:-6] if path.name.endswith(".jsonl") else path.name
    return stem.rsplit("_", 1)[-1]


def _transcript_paths(session_ids: set[str]) -> tuple[dict[str, Path], set[str]]:
    roots = [
        Path.home() / ".omp" / "agent" / "sessions" / "-Developer-jev",
        *sorted((Path.home() / ".omp" / "profiles").glob("*/agent/sessions/-Developer-jev")),
    ]
    found: dict[str, list[Path]] = defaultdict(list)
    for root in roots:
        if root.is_dir():
            for path in root.rglob("*.jsonl"):
                session_id = _session_id(path)
                if session_id in session_ids:
                    found[session_id].append(path)
    ambiguous = {session_id for session_id, paths in found.items() if len(paths) != 1}
    if ambiguous:
        raise RuntimeError(f"ambiguous transcript files for {len(ambiguous)} sessions")
    return {session_id: paths[0] for session_id, paths in found.items()}, session_ids - set(found)


def _transcript_calls(paths: dict[str, Path], cutoff: datetime) -> tuple[list[dict[str, Any]], str]:
    calls = []
    receipts = []
    for session_id, path in sorted(paths.items()):
        pending: dict[str, str] = {}
        file_hash = hashlib.sha256()
        with path.open("rb") as stream:
            for raw_line in stream:
                file_hash.update(raw_line)
                try:
                    row = json.loads(raw_line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                message = row.get("message")
                if not isinstance(message, dict):
                    continue
                timestamp = row.get("timestamp")
                if not isinstance(timestamp, str) or _parse_utc(timestamp) > cutoff:
                    continue
                if message.get("role") == "assistant":
                    for block in message.get("content") or []:
                        if not isinstance(block, dict) or block.get("type") != "toolCall" or block.get("name") != "bash":
                            continue
                        arguments = block.get("arguments")
                        call_id = block.get("id")
                        command = arguments.get("command") if isinstance(arguments, dict) else None
                        if isinstance(call_id, str) and isinstance(command, str):
                            pending[call_id] = command
                elif message.get("role") == "toolResult":
                    call_id = message.get("toolCallId")
                    command = pending.pop(call_id, None) if isinstance(call_id, str) else None
                    if command is not None:
                        calls.append({"session": session_id, "command": command})
        receipts.append(file_hash.digest())
    aggregate = hashlib.sha256(b"".join(sorted(receipts))).hexdigest()
    return calls, aggregate


def _dcg_decision(command: str, timeout_seconds: float) -> str:
    try:
        result = subprocess.run(DCG_ARGS, input=command, text=True, capture_output=True, timeout=timeout_seconds, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return "error"
    return parse_dcg_result(result.stdout, result.returncode)


def _joined_commands(events: list[dict[str, Any]], cutoff: datetime) -> tuple[dict[str, dict[str, Any]], int, str, set[str]]:
    session_ids = {row["session"] for row in events if row["session"] and row["session"] != "unknown"}
    transcript_map, missing_sessions = _transcript_paths(session_ids)
    fleet_events = [row for row in events if row["session"] in transcript_map]
    calls, transcript_sha = _transcript_calls(transcript_map, cutoff)
    joined = match_command_occurrences(fleet_events, calls)
    return (
        {row["event_id"]: row for row in joined},
        len(missing_sessions),
        transcript_sha,
        {row["event_id"] for row in fleet_events},
    )


def _source_paths() -> list[Path]:
    return [PREREG, PREPARE, RUNNER, FILTER_SOURCE, HOOK_SOURCE]


def _build_frame(cutoff_text: str, state_dir: Path, prior_path: Path, dcg_timeout: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cutoff = _parse_utc(cutoff_text)
    source_rows, log_paths, counts = _read_observe_rows(state_dir, cutoff)
    prior_rows = read_jsonl(prior_path)
    prior_ids, prior_hashes = _prior_keys(prior_rows)
    event_id_excluded = [row for row in source_rows if row["event_id"] in prior_ids]
    command_hash_excluded = [row for row in source_rows if row["cmd_sha"] in prior_hashes]
    excluded_ids = prior_ids | {row["event_id"] for row in command_hash_excluded}
    fresh_rows = [row for row in source_rows if row["event_id"] not in excluded_ids and row["cmd_sha"] not in prior_hashes]
    joined, missing_sessions, transcript_sha, fleet_event_ids = _joined_commands(fresh_rows, cutoff)
    non_fleet_rows = len(fresh_rows) - len(fleet_event_ids)
    frame_events = fresh_rows
    filters = load_privacy_filters()
    frame_rows = []
    filter_counts: Counter[str] = Counter()
    for event in frame_events:
        call = joined.get(event["event_id"])
        command = call.get("_command") if call else None
        if not isinstance(command, str) or not command.strip() or event["status"] == "skipped":
            decision = "unreadable"
        else:
            excluded = privacy_exclusion(command, filters)
            if excluded:
                filter_counts[excluded] += 1
                decision = "unreadable"
            elif sha256(command.encode("utf-8")) != event["cmd_sha"]:
                decision = "unreadable"
            else:
                decision = _dcg_decision(command, dcg_timeout)
        frame_rows.append({"event_id": event["event_id"], "cmd_sha": event["cmd_sha"], "dcg_decision": decision})
    decision_counts = Counter(row["dcg_decision"] for row in frame_rows)
    log_hashes = sorted(sha256(path.read_bytes()) for path in log_paths)
    source_event_identity = [
        {"ts": row["ts"], "session": row["session"], "cmd_sha": row["cmd_sha"], "event_id": row["event_id"]}
        for row in source_rows
    ]
    manifest = {
        "schema_version": 1,
        "cutoff_utc": cutoff_text,
        "prereg_commit": _prereg_commit(),
        "prereg_sha256": sha256(PREREG.read_bytes()),
        "filter_source_sha256": sha256(FILTER_SOURCE.read_bytes()),
        "gate_source_sha256": sha256(HOOK_SOURCE.read_bytes()),
        "prior_manifest_sha256": sha256(prior_path.read_bytes()),
        "source_log_sha256": sha256("".join(log_hashes).encode()),
        "transcript_set_sha256": transcript_sha,
        "missing_transcript_sessions": missing_sessions,
        "prior_event_id_matches": len(event_id_excluded),
        "prior_command_hash_matches": len(command_hash_excluded),
        "prior_excluded": len(source_rows) - len(fresh_rows),
        "non_fleet_rows": non_fleet_rows,
        "frame_rows": len(frame_rows),
        "dcg_decision_counts": dict(sorted(decision_counts.items())),
        "event_source_sha256": sha256(canonical_jsonl(source_event_identity).encode()),
        "frame_sha256": sha256(canonical_jsonl(frame_rows).encode()),
    }
    return frame_rows, manifest


def _write_new(path: Path, text: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)


def _frame_command(args: argparse.Namespace) -> int:
    prior_path = Path(args.prior_manifest)
    _require_committed_clean([*(_source_paths()), prior_path])
    cutoff = _parse_utc(args.cutoff)
    commit_time = _git("show", "-s", "--format=%cI", _prereg_commit())
    if commit_time.returncode != 0 or cutoff <= _parse_utc(commit_time.stdout.strip().replace("+00:00", "Z")):
        raise ValueError("cutoff must be after the committed preregistration")
    if FRAME_PATH.exists() or FRAME_MANIFEST_PATH.exists():
        raise FileExistsError("frozen frame output already exists")
    rows, manifest = _build_frame(args.cutoff, Path(args.state_dir), prior_path, args.dcg_timeout)
    _write_new(FRAME_PATH, canonical_jsonl(rows))
    _write_new(FRAME_MANIFEST_PATH, json.dumps(manifest, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "frame_rows": manifest["frame_rows"],
        "frame_sha256": manifest["frame_sha256"],
        "dcg_decision_counts": manifest["dcg_decision_counts"],
        "prior_excluded": manifest["prior_excluded"],
        "non_fleet_rows": manifest["non_fleet_rows"],
        "missing_transcript_sessions": manifest["missing_transcript_sessions"],
        "cutoff_utc": manifest["cutoff_utc"],
    }, sort_keys=True))
    return 0
def _sample_command(args: argparse.Namespace) -> int:
    frame_path, manifest_path = Path(args.frame), Path(args.frame_manifest)
    commit = _require_committed_clean([*(_source_paths()), frame_path, manifest_path])
    frame_text = frame_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256(frame_text.encode("utf-8")) != manifest.get("frame_sha256"):
        raise ValueError("frame SHA-256 does not match its manifest")
    if manifest.get("prereg_sha256") != sha256(PREREG.read_bytes()):
        raise ValueError("preregistration changed after frame freeze")
    if manifest.get("prereg_commit") != _prereg_commit():
        raise ValueError("preregistration commit does not match the frozen frame")
    rows = read_jsonl(frame_path)
    selected = draw_sample(rows)
    sample_text = canonical_jsonl(selected)
    sample_manifest = {
        "schema_version": 1,
        "cutoff_utc": manifest["cutoff_utc"],
        "frame_commit": commit,
        "sample_selection_commit": commit,
        "prereg_commit": manifest["prereg_commit"],
        "frame_sha256": manifest["frame_sha256"],
        "prereg_sha256": manifest["prereg_sha256"],
        "seed": LABEL_SEED,
        "per_stratum_cap": PER_STRATUM,
        "sample_rows": len(selected),
        "strata": {
            stratum: {
                "population_n": sum(row.get("dcg_decision") == stratum for row in rows),
                "sample_n": sum(row.get("stratum") == stratum for row in selected),
                "inclusion_probability": next((row["inclusion_probability"] for row in selected if row["stratum"] == stratum), 0.0),
            }
            for stratum in ("deny", "allow")
        },
        "sample_sha256": sha256(sample_text.encode("utf-8")),
    }
    if SAMPLE_PATH.exists() or SAMPLE_MANIFEST_PATH.exists():
        raise FileExistsError("frozen sample output already exists")
    _write_new(SAMPLE_PATH, sample_text)
    _write_new(SAMPLE_MANIFEST_PATH, json.dumps(sample_manifest, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"sample_rows": len(selected), "sample_sha256": sample_manifest["sample_sha256"], "strata": sample_manifest["strata"], "frame_commit": commit}, sort_keys=True))
    return 0


def _private_pack_path(path: Path) -> Path:
    resolved = path.resolve()
    scratch_root = (ROOT / "var" / "agent-tmp").resolve()
    if scratch_root not in resolved.parents:
        raise ValueError("private command pack must be under var/agent-tmp")
    if not resolved.parent.is_dir() or not (resolved.parent / ".owner").is_file():
        raise ValueError("private command pack directory needs its .owner file")
    if stat.S_IMODE(resolved.parent.stat().st_mode) & 0o077:
        raise PermissionError("private command pack directory must not be group/world accessible")
    return resolved


def _pack_command(args: argparse.Namespace) -> int:
    prior_path = Path(args.prior_manifest)
    _require_committed_clean([*(_source_paths()), FRAME_PATH, FRAME_MANIFEST_PATH, SAMPLE_PATH, SAMPLE_MANIFEST_PATH, prior_path])
    output = _private_pack_path(Path(args.output))
    if output.exists():
        raise FileExistsError("private command pack already exists")
    sample_rows = read_jsonl(SAMPLE_PATH)
    sample_manifest = json.loads(SAMPLE_MANIFEST_PATH.read_text(encoding="utf-8"))
    if sha256(canonical_jsonl(sample_rows).encode("utf-8")) != sample_manifest.get("sample_sha256"):
        raise ValueError("sample SHA-256 does not match its manifest")
    frame_text = FRAME_PATH.read_text(encoding="utf-8")
    frame_rows = read_jsonl(FRAME_PATH)
    frame_manifest = json.loads(FRAME_MANIFEST_PATH.read_text(encoding="utf-8"))
    if sha256(frame_text.encode("utf-8")) != frame_manifest.get("frame_sha256"):
        raise ValueError("frame SHA-256 does not match its manifest")
    if frame_manifest.get("frame_sha256") != sample_manifest.get("frame_sha256"):
        raise ValueError("sample refers to a different frozen frame")
    if sha256(prior_path.read_bytes()) != frame_manifest.get("prior_manifest_sha256"):
        raise ValueError("prior manifest changed since frame freeze")
    cutoff = _parse_utc(sample_manifest["cutoff_utc"])
    event_rows, _, _ = _read_observe_rows(Path(args.state_dir), cutoff)
    prior_rows = read_jsonl(prior_path)
    fresh_rows = exclude_prior_rows(event_rows, prior_rows)
    joined, _, _, fleet_event_ids = _joined_commands(fresh_rows, cutoff)
    filters = load_privacy_filters()
    expected_ids = {row["event_id"] for row in sample_rows}
    frame_ids = {row["event_id"] for row in frame_rows if row.get("dcg_decision") in {"deny", "allow"}}
    if not expected_ids <= frame_ids or not expected_ids <= fleet_event_ids:
        raise ValueError("sample contains an ID outside the eligible fleet frame")
    frame_by_id = {row["event_id"]: row for row in frame_rows}
    commands = []
    for sample in sample_rows:
        frame = frame_by_id[sample["event_id"]]
        if frame.get("cmd_sha") != sample.get("cmd_sha") or frame.get("dcg_decision") != sample.get("dcg_decision"):
            raise ValueError("sample row differs from its frozen frame")
        match = joined.get(sample["event_id"])
        command = match.get("_command") if match else None
        if not isinstance(command, str) or sha256(command.encode("utf-8")) != sample.get("cmd_sha"):
            raise ValueError("a sampled event has no exact source command")
        if privacy_exclusion(command, filters):
            raise ValueError("a sampled command fails the committed privacy filters")
        commands.append({"event_id": sample["event_id"], "cmd_sha": sample["cmd_sha"], "command": command})
    payload = canonical_jsonl(commands).encode("utf-8")
    fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(payload)
    print(json.dumps({"command_rows": len(commands), "pack_sha256": sha256(payload), "status": "private-local-only"}, sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    frame = commands.add_parser("frame", help="freeze and classify the complete post-prereg frame")
    frame.add_argument("--cutoff", required=True)
    frame.add_argument("--state-dir", default=str(STATE_DIR))
    frame.add_argument("--prior-manifest", default=str(PRIOR_MANIFEST))
    frame.add_argument("--dcg-timeout", type=float, default=10.0)
    frame.set_defaults(handler=_frame_command)
    sample = commands.add_parser("sample", help="draw the committed DCG-stratified sample")
    sample.add_argument("--frame", default=str(FRAME_PATH))
    sample.add_argument("--frame-manifest", default=str(FRAME_MANIFEST_PATH))
    sample.set_defaults(handler=_sample_command)
    pack = commands.add_parser("pack", help="reconstruct sample commands into a private scratch file")
    pack.add_argument("--output", required=True)
    pack.add_argument("--state-dir", default=str(STATE_DIR))
    pack.add_argument("--prior-manifest", default=str(PRIOR_MANIFEST))
    pack.set_defaults(handler=_pack_command)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except Exception as error:
        print(f"ERROR {type(error).__name__}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
