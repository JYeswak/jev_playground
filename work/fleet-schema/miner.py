#!/usr/bin/env python3
"""Read-only, bounded miner for fleet decision logs.

The corpus is streamed; raw content is never written. Outputs contain counts,
labels, and SHA-256 identifiers only. A fixed --as-of cutoff makes the
14-day window reproducible; incomplete scans are explicitly PARTIAL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shlex
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

ROOT = Path(__file__).resolve().parents[2]
PLAN_POINTS = ROOT / "work" / "plan-20261004" / "fleet-schema" / "decision-points.jsonl"
DEFAULT_BUDGET_SECONDS = 3000.0
WINDOW_DAYS = 14
MAX_LOAD_AVERAGE = 80.0
RANK_REPORT = ROOT / "work" / "fleet-schema" / "RANK.md"
EMITTED_FAMILIES = frozenset({
    "result", "reread", "rank", "route", "nudge", "recover",
    "land", "outcome", "pin", "delegate",
})

# DP line numbers from FAMILY-REBUILD.md section 1. DP-48 is an outcome
# source for `outcome`, not an additional occurrence-bearing decision.
FAMILY_POINTS: Dict[str, Tuple[int, ...]] = {
    "result": (29,), "rank": (27, 28), "reread": (30,),
    "route": (3, 6, 13, 16, 17), "nudge": (7, 8, 9, 10, 11, 33),
    "recover": (31, 32), "land": (51, 54, 56), "outcome": (5,),
    "pin": (41,), "delegate": (42, 43, 44, 45), "review": (50, 53),
    "memory": (35, 36, 37), "gate": (19, 21), "screen": (25, 26),
    "watch": (46, 47, 60, 61, 65), "effort": (1, 4),
}


@dataclass(frozen=True)
class ToolCall:
    session_id: str
    timestamp: str
    call_index: int
    name: str
    arguments: Mapping[str, object]
    epoch: int
    tool_call_id: str

    @property
    def path(self) -> Optional[str]:
        value = self.arguments.get("path")
        return value if isinstance(value, str) else None


@dataclass(frozen=True)
class ScanResult:
    verdict: str
    files_read: Tuple[str, ...]
    files_not_read: Tuple[str, ...]
    counts: Mapping[str, int]

    @property
    def complete_counts(self) -> Mapping[str, int]:
        return self.counts if self.verdict == "COMPLETE" else {}


def _sha(value: Union[str, bytes]) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def _timestamp(value: object) -> Optional[datetime]:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_budget_seconds(value: str) -> float:
    try:
        budget = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("budget must be a number in (0, 3000]") from error
    if not math.isfinite(budget) or not 0 < budget <= DEFAULT_BUDGET_SECONDS:
        raise argparse.ArgumentTypeError("budget must be a number in (0, 3000]")
    return budget


def _event_time(row: Mapping[str, object]) -> Optional[datetime]:
    return _timestamp(row.get("timestamp") or row.get("ts") or row.get("time") or row.get("at"))


def _text(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str)
    )


def _row_kind(row: Mapping[str, object]) -> Tuple[Optional[str], Optional[Mapping[str, object]]]:
    custom_type = row.get("customType")
    data = row.get("data")
    if isinstance(custom_type, str):
        return custom_type, data if isinstance(data, dict) else None
    if isinstance(custom_type, dict):
        kind = custom_type.get("type")
        payload = custom_type.get("data")
        return (kind, payload if isinstance(payload, dict) else None) if isinstance(kind, str) else (None, None)
    return None, None


def _path_class(path: object) -> str:
    if not isinstance(path, str):
        return "none"
    if "://" in path:
        return path.split("://", 1)[0]
    return "http" if path.startswith("http") else "file"


def _artifact_ids(text: str) -> Iterator[str]:
    marker = "artifact://"
    position = 0
    while True:
        start = text.find(marker, position)
        if start < 0:
            return
        end = start + len(marker)
        while end < len(text) and "0" <= text[end] <= "9":
            end += 1
        if end > start + len(marker):
            yield text[start + len(marker):end]
        position = max(end, start + len(marker))


def _basename(path: str) -> str:
    return path.split(":", 1)[0].rstrip("/").rsplit("/", 1)[-1]


def _read_path(call: ToolCall) -> Optional[str]:
    path = call.path
    if not isinstance(path, str) or "://" in path:
        return None
    return path.split(":", 1)[0]


def _read_selector(call: ToolCall) -> str:
    path = call.path or ""
    suffix = path.partition(":")[2] if "://" not in path else ""
    selector = suffix or str(call.arguments.get("range") or call.arguments.get("line_range") or "")
    parts = selector.split(":")
    if all(
        part in {"raw", "img", "conflicts"} or (
            any(char in "0123456789" for char in part)
            and all(char in "0123456789-+," for char in part)
        )
        for part in parts
    ):
        return selector
    return ""


def _write_paths(call: ToolCall) -> Set[str]:
    args = call.arguments
    found: Set[str] = set()
    if call.name == "write":
        path = args.get("path")
        if isinstance(path, str):
            found.add(_basename(path))
    elif call.name == "edit":
        source = args.get("input")
        if isinstance(source, str):
            cursor = 0
            while True:
                start = source.find("[", cursor)
                if start < 0:
                    break
                separator = source.find("#", start + 1)
                close = source.find("]", separator + 1) if separator >= 0 else -1
                if separator >= 0 and close >= 0:
                    found.add(_basename(source[start + 1:separator]))
                    cursor = close + 1
                else:
                    cursor = start + 1
    elif call.name in ("bash", "eval"):
        key = "command" if call.name == "bash" else "code"
        command = args.get(key)
        if isinstance(command, str):
            try:
                tokens = shlex.split(command)
            except ValueError:
                tokens = command.split()
            for token in tokens:
                cleaned = token.strip("'\"(),;:[]{}")
                if "/" in cleaned or "." in cleaned:
                    found.add(_basename(cleaned))
    return found


def tool_calls(rows: Iterable[Mapping[str, object]], as_of: str) -> List[ToolCall]:
    cutoff = _timestamp(as_of)
    if cutoff is None:
        raise ValueError(f"invalid --as-of timestamp: {as_of}")
    session_id = "unknown-session"
    call_index = 0
    epoch = 0
    calls: List[ToolCall] = []
    for row in rows:
        kind = row.get("type")
        if kind == "session":
            session_id = str(row.get("id") or "unknown-session")
            call_index = 0
            epoch = 0
            continue
        stamp = _event_time(row)
        if stamp is None or stamp > cutoff:
            continue
        if kind == "compaction":
            epoch += 1
            continue
        if kind != "message":
            continue
        message = row.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        for block in message.get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "toolCall":
                continue
            call_index += 1
            arguments = block.get("arguments")
            calls.append(ToolCall(
                session_id, stamp.isoformat(), call_index,
                str(block.get("name") or "?"), arguments if isinstance(arguments, dict) else {},
                epoch, str(block.get("id") or ""),
            ))
    return calls


def extract_result_labels(rows: Sequence[Mapping[str, object]], as_of: str) -> List[dict]:
    cutoff = _timestamp(as_of)
    if cutoff is None:
        raise ValueError(f"invalid --as-of timestamp: {as_of}")
    start = cutoff - timedelta(days=WINDOW_DAYS)
    calls = tool_calls(rows, as_of)
    by_call = {(call.session_id, call.tool_call_id): call for call in calls if call.tool_call_id}
    spills: List[Tuple[str, int, str, str]] = []
    seen: Set[Tuple[str, str]] = set()
    readbacks: Set[Tuple[str, str]] = set()
    session_id = "unknown-session"
    for row in rows:
        if row.get("type") == "session":
            session_id = str(row.get("id") or "unknown-session")
            continue
        stamp = _event_time(row)
        if row.get("type") != "message" or stamp is None or not start <= stamp <= cutoff:
            continue
        message = row.get("message")
        if not isinstance(message, dict):
            continue
        if message.get("role") == "toolResult":
            call = by_call.get((session_id, str(message.get("toolCallId") or "")))
            if call is None:
                continue
            for artifact_id in _artifact_ids(_text(message.get("content"))):
                key = (call.session_id, artifact_id)
                if key not in seen:
                    seen.add(key)
                    event_hash = _sha(json.dumps(row, sort_keys=True, separators=(",", ":")))
                    spills.append((call.session_id, call.call_index, artifact_id, event_hash))
        elif message.get("role") == "assistant":
            for block in message.get("content") or []:
                if not isinstance(block, dict) or block.get("type") != "toolCall" or block.get("name") != "read":
                    continue
                call = by_call.get((session_id, str(block.get("id") or "")))
                args = block.get("arguments")
                path = args.get("path") if isinstance(args, dict) else None
                if call is not None and isinstance(path, str):
                    readbacks.update((call.session_id, artifact_id) for artifact_id in _artifact_ids(path))
    return [
        {
            "session_id_sha256": _sha(session_id),
            "call_index": call_index,
            "artifact_sha256": _sha(artifact_id),
            "event_sha256": event_hash,
            "label": "read_back" if (session_id, artifact_id) in readbacks else "not_read_back",
        }
        for session_id, call_index, artifact_id, event_hash in spills
    ]


def extract_reread_events(rows: Sequence[Mapping[str, object]], as_of: str) -> List[dict]:
    cutoff = _timestamp(as_of)
    if cutoff is None:
        raise ValueError(f"invalid --as-of timestamp: {as_of}")
    start = cutoff - timedelta(days=WINDOW_DAYS)
    prior: Dict[Tuple[str, int, str], ToolCall] = {}
    emitted: List[dict] = []
    for call in tool_calls(rows, as_of):
        if call.name != "read":
            continue
        path = _read_path(call)
        if path is None:
            continue
        key = (call.session_id, call.epoch, path)
        previous = prior.get(key)
        call_time = _timestamp(call.timestamp)
        if previous is not None and call_time is not None and call_time >= start:
            emitted.append({
                "session_id_sha256": _sha(call.session_id),
                "call_index": call.call_index,
                "path_sha256": _sha(path),
                "line_range": _read_selector(call),
                "fetch_tool": call.name,
                "calls_since_prior_read": call.call_index - previous.call_index - 1,
            })
        prior[key] = call
    return emitted


def classify_repeat_reads(rows: Sequence[Mapping[str, object]], as_of: str) -> List[dict]:
    cutoff = _timestamp(as_of)
    if cutoff is None:
        raise ValueError(f"invalid --as-of timestamp: {as_of}")
    start = cutoff - timedelta(days=WINDOW_DAYS)
    last_read: Dict[Tuple[str, int, str], int] = {}
    last_write: Dict[Tuple[str, int, str], int] = {}
    decisions: List[dict] = []
    for call in tool_calls(rows, as_of):
        call_time = _timestamp(call.timestamp)
        path = _read_path(call)
        if call.name == "read" and path is not None:
            key = (call.session_id, call.epoch, path)
            if key in last_read and call_time is not None and start <= call_time <= cutoff:
                basename = _basename(path)
                write_index = last_write.get((call.session_id, call.epoch, basename), -1)
                decisions.append({
                    "session_id_sha256": _sha(call.session_id),
                    "call_index": call.call_index,
                    "path_sha256": _sha(path),
                    "is_redundant": write_index <= last_read[key],
                })
            last_read[key] = call.call_index
        else:
            for basename in _write_paths(call):
                last_write[(call.session_id, call.epoch, basename)] = call.call_index
    return decisions


def label_status(row: Mapping[str, object]) -> str:
    return "COUNTED" if row.get("label") is not None else "NOT_COUNTED"


def ca37_candidate_counts(path: Path) -> Dict[str, Tuple[int, int]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid candidate data at {path}") from error
    candidates = payload.get("candidates")
    if not isinstance(candidates, dict):
        raise ValueError("candidate file has no candidates mapping")
    counts: Dict[str, Tuple[int, int]] = {}
    for name in ("vendor_paste", "skill_veto", "gate_cascade", "memory_filter"):
        item = candidates.get(name)
        if not isinstance(item, dict) or item.get("status") != "COUNTED":
            raise ValueError("candidate " + name + " is not counted")
        if item.get("positives_source") not in ("labels", "labels-paid-as-target"):
            raise ValueError("candidate " + name + " lacks a label source")
        counts[name] = (int(item["positives"]), int(item["opportunities"]))
    return counts


def validate_golden_provenance(
    directory: Path,
    *,
    expected_miner_source_sha256: Optional[str] = None,
    expected_command: Optional[str] = None,
) -> None:
    labels = directory / "labels.jsonl"
    if not labels.is_file():
        raise ValueError("labels.jsonl is missing")
    provenance = directory / "PROVENANCE.md"
    if not provenance.is_file():
        raise ValueError("PROVENANCE.md is missing")
    text = provenance.read_text(encoding="utf-8")
    for required in ("miner commit:", "log window:", "command:", "sha256:"):
        if required not in text:
            raise ValueError("PROVENANCE.md missing " + required)
    expected = next(
        (line.removeprefix("sha256: ") for line in text.splitlines() if line.startswith("sha256: ")),
        None,
    )
    if expected != _sha(labels.read_bytes()):
        raise ValueError("labels.jsonl does not match PROVENANCE.md sha256")
    fields = dict(line.split(": ", 1) for line in text.splitlines() if ": " in line)
    if expected_miner_source_sha256 is not None and fields.get("miner source sha256") != expected_miner_source_sha256:
        raise ValueError("golden miner source identity does not match")
    if expected_command is not None and fields.get("command") != expected_command:
        raise ValueError("golden command/input identity does not match")


def _tokens(command: str) -> List[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _bash_families(command: str) -> Set[str]:
    tokens = _tokens(command)
    families: Set[str] = set()
    for index, token in enumerate(tokens):
        candidate = index
        if token == "git" and candidate + 1 < len(tokens) and tokens[candidate + 1] == "-C":
            candidate += 3
        if candidate < len(tokens) and tokens[candidate] == "git" and candidate + 1 < len(tokens):
            subcommand = tokens[candidate + 1]
            mapping = {
                "commit": "git_commit", "push": "git_push", "revert": "git_revert",
                "diff": "git_diff", "status": "git_status_log", "log": "git_status_log",
                "show": "git_status_log",
            }
            if subcommand in mapping:
                families.add(mapping[subcommand])
            if subcommand == "reset" and "--hard" in tokens[candidate + 2:]:
                families.add("git_reset_hard")
            if subcommand == "restore" or (subcommand == "checkout" and "--" in tokens[candidate + 2:]):
                families.add("git_restore_checkout")
        if token == "br" and index + 1 < len(tokens):
            mapping = {"close": "br_close", "create": "br_create", "update": "br_update", "ready": "br_ready_list_show", "list": "br_ready_list_show", "show": "br_ready_list_show"}
            if tokens[index + 1] in mapping:
                families.add(mapping[tokens[index + 1]])
        if token == "cass" and index + 1 < len(tokens) and tokens[index + 1] in {"search", "health", "status", "index", "view", "expand"}:
            families.add("cass")
        if token == "ntm" and index + 1 < len(tokens):
            families.add("ntm")
        if token == "ee" and index + 1 < len(tokens):
            families.add("ee_cli")
        if token in {"bun", "cargo", "pytest", "npm", "go", "swift", "vitest", "jest", "xcodebuild"}:
            next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
            if token in {"pytest", "vitest", "jest", "xcodebuild"} or next_token in {"test", "nextest"} or (token == "npm" and "test" in tokens[index + 1:index + 3]):
                families.add("test_run")
            if token == "cargo" and next_token in {"build", "check", "clippy"}:
                families.add("build_run")
            if token == "swift" and next_token == "build":
                families.add("build_run")
            if token == "xcodebuild":
                families.add("build_run")
        if token == "tsc" or (token == "bun" and index + 2 < len(tokens) and tokens[index + 1: index + 3] == ["run", "build"]) or (token == "npm" and index + 2 < len(tokens) and tokens[index + 1: index + 3] == ["run", "build"]):
            families.add("build_run")
        if token == "gh" and index + 1 < len(tokens) and tokens[index + 1] in {"pr", "issue", "run", "api", "release"}:
            families.add("gh_cli")
        if token == "curl":
            families.add("curl_http")
        if token == "sleep" and index + 1 < len(tokens) and tokens[index + 1][:1].isdigit():
            families.add("sleep_poll")
        if token == "rm" and any("r" in flag and "f" in flag for flag in tokens[index + 1:index + 3] if flag.startswith("-")):
            families.add("rm_destructive")
        if token in {"railway", "vercel", "wrangler", "fly"} and index + 1 < len(tokens):
            if (token == "railway" and tokens[index + 1] == "up") or (token == "vercel" and (tokens[index + 1] == "deploy" or "--prod" in tokens[index + 1:index + 3])) or (token in {"wrangler", "fly"} and tokens[index + 1] == "deploy"):
                families.add("deploy")
    return families


def _correction(text: str) -> bool:
    value = text.lstrip().lower()
    starts = ("no,", "no.", "no!", "no ", "nope", "wrong", "stop", "don't", "dont", "that's not", "thats not", "actually", "why did you", "you didn't", "you didnt", "undo", "revert", "not what i", "wait,", "wait ", "hold on")
    return value.startswith(starts)


def _user_class(text: str) -> str:
    stripped = text.lstrip()
    if stripped.startswith("Complete assignment") or "§ Coop" in text[:200]:
        return "subagent_assignment"
    folded = stripped.lower()
    if stripped.startswith("CONDUCTOR") or "[TASK]" in stripped[:200] or folded.startswith(("pane ", "[pane", "from ", "[from")):
        return "conductor_dispatch"
    if stripped.startswith("<"):
        return "system_wrapped"
    return "human_or_other"


def _edit_targets(value: object) -> Set[str]:
    if not isinstance(value, str):
        return set()
    targets: Set[str] = set()
    cursor = 0
    while True:
        start = value.find("[", cursor)
        if start < 0:
            return targets
        separator = value.find("#", start + 1)
        close = value.find("]", separator + 1) if separator >= 0 else -1
        if separator >= 0 and close >= 0:
            targets.add(_basename(value[start + 1:separator]))
            cursor = close + 1
        else:
            cursor = start + 1


@dataclass
class _Pending:
    kind: str
    remaining: int
    payload: object
    counted: bool
    origin: Optional[ToolCall] = None
    event_hash: str = ""


@dataclass
class Metrics:
    start: datetime
    cutoff: datetime
    c: Counter = field(default_factory=Counter)
    p2: Counter = field(default_factory=Counter)
    p3: Counter = field(default_factory=Counter)
    p4: Counter = field(default_factory=Counter)
    p5: Counter = field(default_factory=Counter)
    dl_rows: Counter = field(default_factory=Counter)
    dl_values: Counter = field(default_factory=Counter)
    find_rank_rows: int = 0
    find_rank_touched: int = 0
    result_labels: List[dict] = field(default_factory=list)
    reread_events: List[dict] = field(default_factory=list)
    organic_rows: Dict[str, List[dict]] = field(default_factory=dict)
    result_reruns: List[dict] = field(default_factory=list)
    rerun_window_calls: Optional[int] = None
    shaken_wait: Dict[str, List[Tuple[ToolCall, int, str]]] = field(default_factory=dict)
    call_rows: Dict[str, List[dict]] = field(default_factory=dict)
    hint_rows: Dict[str, dict] = field(default_factory=dict)
    rule_rows: Dict[str, dict] = field(default_factory=dict)
    final_row: Optional[dict] = None
    _last_find_call: Optional[ToolCall] = None
    _last_find_hash: str = ""
    session_id: str = "unknown-session"
    call_index: int = 0
    epoch: int = 0
    last_assistant_final: bool = False
    calls: Dict[str, ToolCall] = field(default_factory=dict)
    last_read: Dict[Tuple[int, str], int] = field(default_factory=dict)
    last_write: Dict[Tuple[int, str], int] = field(default_factory=dict)
    hinted: Dict[str, bool] = field(default_factory=dict)
    spills: List[Tuple[int, str, str]] = field(default_factory=list)
    spill_ids: Set[str] = field(default_factory=set)
    artifact_reads: Set[str] = field(default_factory=set)
    repeat_seen: Set[str] = field(default_factory=set)
    pending: List[_Pending] = field(default_factory=list)
    outcome_wait: Dict[str, Tuple[str, _Pending, ToolCall]] = field(default_factory=dict)
    ttsr_rules: Counter = field(default_factory=Counter)

    def _in_window(self, row: Mapping[str, object]) -> bool:
        stamp = _event_time(row)
        return stamp is not None and self.start <= stamp <= self.cutoff


    def label_rows(self, family: str) -> List[dict]:
        if family == "result":
            return self.result_labels + self.result_reruns
        if family == "reread":
            return self.reread_events
        if family not in EMITTED_FAMILIES:
            raise ValueError("no organic emitter for " + family)
        return self.organic_rows.get(family, [])

    def _emit(
        self, family: str, source_kind: str, event_hash: str,
        origin: Optional[ToolCall] = None, label: Optional[str] = None,
        **metadata: object,
    ) -> dict:
        emitted = {
            "schema_version": 1, "family": family,
            "session_id_sha256": _sha(origin.session_id if origin else self.session_id),
            "call_index": origin.call_index if origin else None,
            "event_sha256": event_hash, "label": label,
            "status": "COUNTED" if label is not None else "NOT_COUNTED",
            "source_kind": source_kind,
        }
        emitted.update(metadata)
        self.organic_rows.setdefault(family, []).append(emitted)
        return emitted

    @staticmethod
    def _set_label(emitted: dict, label: Optional[str]) -> None:
        emitted["label"] = label
        emitted["status"] = "COUNTED" if label is not None else "NOT_COUNTED"

    def _expect_result(self, family: str, source_kind: str, call: ToolCall, event_hash: str, **metadata: object) -> None:
        emitted = self._emit(family, source_kind, event_hash, call, **metadata)
        if call.tool_call_id:
            self.call_rows.setdefault(call.tool_call_id, []).append(emitted)

    def _pending_row(self, pending: _Pending, label: Optional[str], call: Optional[ToolCall] = None) -> None:
        family = "recover" if pending.kind in {"bash_error", "edit_error"} else "pin" if pending.kind == "compaction" else "nudge"
        if family == "recover" and label is not None and not label.endswith((":ok", ":err")):
            label = None
        self._emit(family, pending.kind, pending.event_hash, pending.origin or call, label)

    def _rerun_row(self, call: ToolCall, observed_index: int, event_hash: str, repeat: Optional[ToolCall]) -> None:
        distance = repeat.call_index - call.call_index if repeat else None
        result_distance = repeat.call_index - observed_index if repeat else None
        label = None
        if self.rerun_window_calls is not None:
            if result_distance is not None and result_distance <= self.rerun_window_calls:
                label = "same_command_rerun"
            elif self.call_index - observed_index >= self.rerun_window_calls:
                label = "no_rerun_within_window"
        emitted = self._emit(
            "result", "shaken_same_command", event_hash, call, label,
            command_sha256=_sha(str(call.arguments.get("command") or "")),
            calls_until_repeat=distance, calls_since_result=result_distance,
            rerun_window_calls=self.rerun_window_calls,
        )
        self.result_reruns.append(emitted)

    def _record_rule(self, rule: str, event_hash: str) -> None:
        emitted = self.rule_rows.get(rule)
        if emitted is None:
            self.rule_rows[rule] = self._emit("nudge", "ttsr_session_rule", event_hash, rule_sha256=_sha(rule))
        else:
            self._set_label(emitted, "refired")
        if rule in {"kit-close-needs-evidence", "claim-without-evidence", "kit-close-reason-no-evidence", "kit-unverified-done"}:
            self._emit("land", "close_evidence_rule", event_hash, rule_sha256=_sha(rule))

    def _flush_session(self) -> None:
        for _rule, count in self.ttsr_rules.items():
            self.p4["ttsr_session_rule_pairs"] += 1
            if count >= 2:
                self.p4["ttsr_session_rule_pairs_refired"] += 1
        for call_index, artifact_id, event_hash in self.spills:
            self.result_labels.append({
                "session_id_sha256": _sha(self.session_id),
                "call_index": call_index,
                "artifact_sha256": _sha(artifact_id),
                "event_sha256": event_hash,
                "label": "read_back" if artifact_id in self.artifact_reads else "not_read_back",
            })
        if self._last_find_call is not None and self._in_window({"timestamp": self._last_find_call.timestamp}):
            self._emit("route", "find_next_call", self._last_find_hash, self._last_find_call)
        for pending in self.pending:
            if pending.counted:
                self._pending_row(pending, None)
        for _follow, pending, call in self.outcome_wait.values():
            if pending.counted:
                self._pending_row(pending, None, call)
        for waiting in self.shaken_wait.values():
            for call, observed_index, event_hash in waiting:
                self._rerun_row(call, observed_index, event_hash, None)
        self.last_assistant_final = False
        self.ttsr_rules.clear()
        self.spills.clear()
        self.spill_ids.clear()
        self.artifact_reads.clear()
        self.last_read.clear()
        self.last_write.clear()
        self.hinted.clear()
        self.repeat_seen.clear()
        self.pending.clear()
        self.outcome_wait.clear()
        self.calls.clear()
        self.call_rows.clear()
        self.hint_rows.clear()
        self.rule_rows.clear()
        self.final_row = None
        self._last_find_call = None
        self.shaken_wait.clear()
        self._last_find = False

    def finish(self) -> None:
        self._flush_session()

    def _new_session(self, session_id: str) -> None:
        self._flush_session()
        self.session_id = session_id
        self.call_index = 0
        self.epoch = 0
        self.repeat_seen.clear()
        self._last_find = False

    def _call(self, block: Mapping[str, object], row: Mapping[str, object], counted: bool) -> None:
        self.call_index += 1
        args = block.get("arguments")
        arguments = args if isinstance(args, dict) else {}
        name = str(block.get("name") or "?")
        call_id = str(block.get("id") or "")
        call = ToolCall(self.session_id, _event_time(row).isoformat(), self.call_index, name, arguments, self.epoch, call_id)
        if call_id:
            self.calls[call_id] = call
        event_hash = _sha(json.dumps(row, sort_keys=True, separators=(",", ":")))
        if self._last_find_call is not None:
            if self._in_window({"timestamp": self._last_find_call.timestamp}):
                next_kind = name if name in {"read", "edit", "find", "grep"} else "other"
                self._emit("route", "find_next_call", self._last_find_hash, self._last_find_call, "next_" + next_kind)
            self._last_find_call = None
        if name == "find":
            self._last_find_call = call
            self._last_find_hash = event_hash
        path = call.path or ""
        if counted:
            if name in {"find", "grep", "glob"}:
                self._emit("route", "locate_" + name, event_hash, call)
            if name == "todo" and arguments.get("op") == "init":
                self._emit("route", "todo_init", event_hash, call)
            if name == "web_search" or (name == "read" and path.startswith(("http://", "https://"))):
                self._emit("route", "web_search" if name == "web_search" else "web_read", event_hash, call)
            if name == "ask":
                self._expect_result("route", "ask_result", call, event_hash)
            if name == "read" and path.startswith("skill://"):
                self._emit("nudge", "skill_read", event_hash, call, skill_sha256=_sha(path[8:].split("/", 1)[0]))
            if name == "task":
                self._emit("delegate", "task_spawn", event_hash, call)
                self._expect_result("delegate", "task_result", call, event_hash)
                tasks = arguments.get("tasks")
                for task in tasks if isinstance(tasks, list) else []:
                    if isinstance(task, dict):
                        self._expect_result("delegate", "task_agent", call, event_hash, agent_sha256=_sha(str(task.get("agent") or "task")))
                        self._emit("delegate", "task_model", event_hash, call, model_sha256=_sha(str(task.get("model") or "")))
            if name == "yield":
                self._emit("delegate", "yield_error", event_hash, call, "error" if arguments.get("error") else None)
        if counted:
            self.c["tool:" + name] += 1
        if name == "read":
            kind = _path_class(path)
            if counted:
                self.c["read:" + kind] += 1
            if kind == "file":
                file_path = path.split(":", 1)[0]
                if file_path in self.repeat_seen and counted:
                    self.c["read_repeat_same_path"] += 1
                self.repeat_seen.add(file_path)
                key = (self.epoch, file_path)
                prior_index = self.last_read.get(key)
                if prior_index is not None:
                    if counted:
                        self.reread_events.append({
                            "session_id_sha256": _sha(self.session_id),
                            "call_index": call.call_index,
                            "path_sha256": _sha(file_path),
                            "line_range": _read_selector(call),
                            "fetch_tool": "read",
                            "calls_since_prior_read": call.call_index - prior_index - 1,
                        })
                    basename = _basename(file_path)
                    redundant = self.last_write.get((self.epoch, basename), -1) <= prior_index
                    if counted:
                        self.p5["repeat_read"] += 1
                        self.p5["repeat_read_redundant" if redundant else "repeat_read_after_write"] += 1
                self.last_read[key] = call.call_index
            if path.startswith("artifact://"):
                for artifact_id in _artifact_ids(path):
                    self.artifact_reads.add(artifact_id)
            if path.startswith("skill://"):
                skill = path[len("skill://"):].split("/", 1)[0]
                if self.hinted.get(skill) and counted:
                    self.c["skill_hint_followed"] += 1
                    self.hinted[skill] = False
                    hinted_row = self.hint_rows.pop(skill, None)
                    if hinted_row is not None:
                        hinted_row["call_index"] = call.call_index
                        self._set_label(hinted_row, "followed")
            if counted and path.startswith("memory://"):
                self.c["read:memory"] += 1
            if counted and path.startswith("http://"):
                self.c["read:http"] += 1
            if counted and path.startswith("https://"):
                self.c["read:https"] += 1
        elif name == "write" and counted:
            self.c["write:" + _path_class(path)] += 1
            if path.startswith("xd://"):
                self.c["xd:" + path[5:].split("/", 1)[0]] += 1
        elif name == "todo" and counted:
            self.c["todo_op:" + str(arguments.get("op"))] += 1
        elif name == "task":
            tasks = arguments.get("tasks")
            task_list = tasks if isinstance(tasks, list) else []
            if counted:
                self.c["task_spawn_calls"] += 1
                self.c["task_spawned_agents"] += len(task_list)
                for task in task_list:
                    if isinstance(task, dict):
                        self.c["task_agent:" + str(task.get("agent", "task"))] += 1
        elif name == "yield":
            if counted:
                kind = "error" if arguments.get("error") else "data" if "data" in arguments else "other"
                self.p2["yield:" + kind + ":" + str(arguments.get("type"))] += 1
        elif name == "hub" and counted:
            action = arguments.get("op") or arguments.get("action") or arguments.get("command") or ",".join(sorted(arguments))[:60]
            self.p2["hub_op:" + str(action)] += 1
        elif name == "ask" and counted:
            self.p2["ask_call"] += 1
        if name == "read" and path.startswith("artifact://"):
            for artifact_id in _artifact_ids(path):
                self.artifact_reads.add(artifact_id)
        if name == "edit":
            for basename in _edit_targets(arguments.get("input")):
                self.last_write[(self.epoch, basename)] = call.call_index
        elif name in ("write", "bash", "eval"):
            for basename in _write_paths(call):
                self.last_write[(self.epoch, basename)] = call.call_index
        command = arguments.get("command") if name == "bash" else None
        if isinstance(command, str):
            families = _bash_families(command)
            if counted:
                if "bash_async" in arguments and arguments.get("async"):
                    self.c["bash_async"] += 1
                for family in families:
                    self.c["bash:" + family] += 1
                if not families:
                    self.c["bash:other"] += 1
            for origin, observed_index, shaken_hash in self.shaken_wait.pop(command, []):
                self._rerun_row(origin, observed_index, shaken_hash, call)
            if counted:
                for family in ("git_commit", "br_close"):
                    if family in families:
                        self._expect_result("land", family + "_result", call, event_hash)
                        self._expect_result("land", family + ("_hook_reject" if family == "git_commit" else "_refused"), call, event_hash)
                if "git_revert" in families:
                    self._emit("land", "git_revert", event_hash, call, "revert_observed")
        edit_targets = _edit_targets(arguments.get("input")) if name == "edit" else set()
        still: List[_Pending] = []
        for pending in self.pending:
            hit: Optional[str] = None
            if pending.kind == "todo_nudge" and name == "todo":
                hit = "followed"
            elif pending.kind == "lsp_late" and name == "edit" and pending.payload and edit_targets.intersection(pending.payload):
                hit = "edited_file"
            elif pending.kind == "kit_guard" and name == "read" and path.endswith("AGENTS.md"):
                hit = "reread_agents"
            elif pending.kind == "compaction" and name == "read" and _basename(path.split(":", 1)[0]) in pending.payload:
                hit = "reread_prior_file"
            elif pending.kind == "edit_error" and pending.payload:
                targets = pending.payload
                if name == "read" and _basename(path.split(":", 1)[0]) in targets:
                    hit = "reread_then"
                elif name == "edit":
                    hit = "edit_again_no_read"
            elif pending.kind == "bash_error" and name == "bash" and isinstance(pending.payload, str):
                hit = "identical_retry" if command == pending.payload else "changed_command"
            if hit:
                if pending.counted:
                    self.p4["follow:" + pending.kind + ":" + hit] += 1
                if pending.kind in ("bash_error", "edit_error") and hit in ("identical_retry", "changed_command", "edit_again_no_read"):
                    if call_id:
                        self.outcome_wait[call_id] = ("outcome:" + pending.kind + ":" + hit, pending, call)
                    elif pending.counted:
                        self._pending_row(pending, None, call)
                elif pending.counted:
                    self._pending_row(pending, hit, call)
                continue
            pending.remaining -= 1
            if pending.remaining <= 0:
                if pending.counted:
                    self.p4["follow:" + pending.kind + ":none_within_window"] += 1
                    self._pending_row(pending, "none_within_window", call)
            else:
                still.append(pending)
        self.pending = still
        self._last_find = name == "find"
    def process(self, row: Mapping[str, object], source_path: str) -> None:
        event_hash = _sha(json.dumps(row, sort_keys=True, separators=(",", ":")))
        kind = row.get("type")
        stamp = _event_time(row)
        if stamp is None or stamp > self.cutoff:
            return
        counted = self.start <= stamp
        if kind == "session":
            self._new_session(str(row.get("id") or "unknown-session"))
            if counted:
                self.c["rowtype:session"] += 1
            return
        if source_path.endswith(".jsonl") and "/.local/state/jev/" in source_path:
            filename = Path(source_path).name
            if counted:
                self.dl_rows[filename] += 1
                for field_name, value in row.items():
                    if isinstance(value, (str, bool, int)) and not (isinstance(value, int) and not isinstance(value, bool) and abs(value) > 100):
                        self.dl_values[filename + ":" + field_name + "=" + str(value)[:40]] += 1
                rank_label = None
                if filename == "find-rank.jsonl":
                    self.find_rank_rows += 1
                    hits = row.get("hits")
                    shown = {hit for hit in hits if isinstance(hit, str)} if isinstance(hits, list) else set()
                    next_calls = row.get("nextToolCalls")
                    touched = isinstance(next_calls, list) and any(
                        isinstance(item, dict) and isinstance(item.get("touched"), list)
                        and any(isinstance(hit, str) and hit in shown for hit in item["touched"])
                        for item in next_calls
                    )
                    if touched:
                        self.find_rank_touched += 1
                        rank_label = "touched_shown_hit"
                    elif shown and row.get("complete") is True:
                        rank_label = "no_shown_hit_touched"
                log_families = {
                    "find-rank.jsonl": ("rank", "find_rank"),
                    "websearch-rerank.jsonl": ("rank", "web_rerank"),
                    "skill-hint-calls.jsonl": ("nudge", "skill_hint_log"),
                    "skill-veto-shadow.jsonl": ("nudge", "skill_veto"),
                }
                if filename in log_families:
                    family, source_kind = log_families[filename]
                    # A recorded rank outcome does not invent a transcript origin.
                    emitted = self._emit(family, source_kind, event_hash, label=rank_label)
                    source_session = row.get("session") or row.get("sessionId") or row.get("session_id")
                    source_session_hash = row.get("sessionHash")
                    if (
                        isinstance(source_session_hash, str) and len(source_session_hash) == 64
                        and all(char in "0123456789abcdef" for char in source_session_hash)
                    ):
                        emitted["session_id_sha256"] = source_session_hash
                    else:
                        emitted["session_id_sha256"] = _sha(source_session if isinstance(source_session, str) else "unknown-session")
            return
        if counted:
            self.c["rowtype:" + str(kind)] += 1
        if kind == "compaction":
            if counted:
                details = row.get("details")
                read_files = details.get("readFiles") if isinstance(details, dict) else None
                if isinstance(read_files, list) and read_files:
                    self.p4["compaction_with_readFiles"] += 1
                    self.pending.append(_Pending("compaction", 30, {_basename(f) for f in read_files if isinstance(f, str)}, counted, event_hash=event_hash))
            self.epoch += 1
            self.last_read.clear()
            self.last_write.clear()
            return
        if kind == "ttsr_injection":
            rules = row.get("injectedRules")
            if isinstance(rules, list) and counted:
                for rule in rules:
                    self.ttsr_rules[str(rule)] += 1
                    self.c["ttsr_rule:" + str(rule)] += 1
                    self._record_rule(str(rule), event_hash)
            return
        if kind in ("custom", "custom_message"):
            custom_type, data = _row_kind(row)
            prefix = "custom:" if kind == "custom" else "cmsg:"
            if custom_type is None and kind == "custom_message":
                custom_type = str(row.get("customType") or "None")
            if counted:
                self.c[prefix + str(custom_type)] += 1
            details = row.get("details")
            if kind == "custom_message" and custom_type == "jev-skill-hint" and isinstance(details, dict):
                skill = details.get("skill")
                if isinstance(skill, str):
                    self.hinted[skill] = True
                    if counted:
                        self.c["skill_hint_emitted"] += 1
                        previous = self.hint_rows.get(skill)
                        if previous is not None:
                            self._set_label(previous, None)
                        self.hint_rows[skill] = self._emit("nudge", "skill_hint", event_hash, skill_sha256=_sha(skill))
            if kind == "custom_message" and custom_type == "ttsr-injection" and isinstance(details, dict):
                rules = details.get("rules")
                if isinstance(rules, list) and counted:
                    for rule in rules:
                        self.ttsr_rules[str(rule)] += 1
                        self.c["ttsr_rule:" + str(rule)] += 1
                        self._record_rule(str(rule), event_hash)
            if isinstance(data, dict) and "kind" in data and counted:
                self.c["kind:" + str(custom_type) + ":" + str(data.get("kind"))] += 1
            if kind == "custom_message" and counted:
                if custom_type == "mid-run-todo-nudge":
                    self.p4["trig:todo_nudge"] += 1
                    self.pending.append(_Pending("todo_nudge", 3, None, True, event_hash=event_hash))
                elif custom_type == "lsp-late-diagnostic":
                    files = set()
                    if isinstance(details, dict) and isinstance(details.get("files"), list):
                        files = {_basename(item.get("path", "")) for item in details["files"] if isinstance(item, dict) and isinstance(item.get("path"), str)}
                    self.p4["trig:lsp_late"] += 1
                    self.pending.append(_Pending("lsp_late", 3, files, True, event_hash=event_hash))
                elif custom_type == "kit-guard":
                    self.p4["trig:kit_guard"] += 1
                    self.pending.append(_Pending("kit_guard", 5, None, True, event_hash=event_hash))
                elif custom_type == "interrupted-thinking":
                    self._emit("outcome", "interrupted_thinking", event_hash)
            return
        if kind == "model_usage" and counted:
            self.c["model_usage:" + str(row.get("purpose")) + ":" + str(row.get("role"))] += 1
            if row.get("purpose") == "find":
                self._emit("rank", "find_model_usage", event_hash)
            return
        if kind == "thinking_level_change" and counted:
            self.c["thinking_level:" + str(row.get("thinkingLevel")) + ":" + str(row.get("configured"))] += 1
            return
        if kind == "model_change" and counted:
            self.c["model_change"] += 1
            return
        if kind != "message":
            return
        message = row.get("message")
        if not isinstance(message, dict):
            return
        role = message.get("role")
        if counted:
            self.c["role:" + str(role)] += 1
        if role == "assistant":
            has_tool = False
            blocks = [block for block in message.get("content") or [] if isinstance(block, dict) and block.get("type") == "toolCall"]
            if blocks and hasattr(self, "_last_find") and self._last_find:
                first_name = str(blocks[0].get("name") or "?")
                key = first_name if first_name in {"read", "edit", "find", "grep"} else "other"
                if counted:
                    self.p3["after_find:" + key] += 1
            self._last_find = bool(blocks and blocks[-1].get("name") == "find")
            if counted:
                self.c["stop:" + str(message.get("stopReason"))] += 1
                if message.get("stopReason") == "aborted":
                    self._emit("outcome", "assistant_aborted", event_hash)
            for block in blocks:
                has_tool = True
                self._call(block, row, counted)
            self.last_assistant_final = not has_tool and message.get("stopReason") == "stop"
            if self.last_assistant_final and counted:
                self.final_row = self._emit("outcome", "correction_after_final", event_hash)
            elif has_tool:
                self.final_row = None
            return
        if role == "toolResult":
            name = str(message.get("toolName") or "?")
            text = _text(message.get("content"))
            error = bool(message.get("isError"))
            call_id = str(message.get("toolCallId") or "")
            call = self.calls.get(call_id)
            observed_error = message.get("isError")
            if counted and text.startswith("[shaken"):
                command = call.arguments.get("command") if call is not None and call.name == "bash" else None
                if isinstance(command, str) and call is not None:
                    self.shaken_wait.setdefault(command, []).append((call, self.call_index, event_hash))
                else:
                    emitted = self._emit(
                        "result", "shaken_same_command", event_hash, call,
                        command_sha256=None, calls_until_repeat=None,
                        calls_since_result=None, rerun_window_calls=self.rerun_window_calls,
                    )
                    self.result_reruns.append(emitted)
            if counted and isinstance(observed_error, bool):
                for emitted in self.call_rows.pop(call_id, []):
                    source_kind = emitted["source_kind"]
                    lower = text[:2000].lower()
                    if source_kind in {"ask_result", "task_agent", "task_result"}:
                        proxy = "error" if observed_error else "ok"
                    elif source_kind.endswith("_result"):
                        proxy = "error" if observed_error else "ok"
                    elif source_kind == "git_commit_hook_reject":
                        proxy = "hook_reject" if "hook" in lower and ("fail" in lower or "reject" in lower) else "no_hook_reject_observed"
                    else:
                        proxy = "refused_or_error" if any(word in lower for word in ("refus", "cannot close", "blocked", "error")) else "no_refusal_observed"
                    self._set_label(emitted, proxy)
            if counted:
                if text.startswith("[shaken"):
                    self.c["result_shaken"] += 1
                elif "artifact://" in text:
                    self.c["result_spilled"] += 1
                if error:
                    self.c["toolerr:" + name] += 1
                if call is not None and error:
                    command = call.arguments.get("command")
                    for family in _bash_families(command) if isinstance(command, str) else set():
                        self.c["bashfail:" + family] += 1
                lower = text[:2000].lower()
                if call is not None and "br_close" in _bash_families(str(call.arguments.get("command") or "")) and any(word in lower for word in ("refus", "cannot close", "blocked", "error")):
                    self.c["br_close_refused_or_error"] += 1
                if call is not None and "git_commit" in _bash_families(str(call.arguments.get("command") or "")) and "hook" in lower and ("fail" in lower or "reject" in lower):
                    self.c["git_commit_hook_reject"] += 1
                if call is not None and "git_push" in _bash_families(str(call.arguments.get("command") or "")) and ("rejected" in lower or "non-fast-forward" in lower):
                    self.c["git_push_rejected"] += 1
                if call is not None and "test_run" in _bash_families(str(call.arguments.get("command") or "")) and (error or " failed" in lower or " failures" in lower):
                    self.c["test_run_failed"] += 1
                if name == "task" and isinstance(observed_error, bool):
                    self.p2["task_result:" + ("error" if error else "ok")] += 1
                if name == "ask" and isinstance(observed_error, bool):
                    self.p2["ask_result:" + ("error" if error else "ok")] += 1
            if counted:
                for artifact_id in _artifact_ids(text[:600]):
                    if artifact_id not in self.spill_ids:
                        self.spill_ids.add(artifact_id)
                        if call is not None:
                            self.spills.append((call.call_index, artifact_id, _sha(json.dumps(row, sort_keys=True, separators=(",", ":")))))
            follow = self.outcome_wait.pop(call_id, None)
            if follow:
                follow_key, pending, follow_call = follow
                if counted and isinstance(observed_error, bool):
                    self.p4[follow_key + (":err" if error else ":ok")] += 1
                    self._pending_row(pending, follow_key.removeprefix("outcome:").split(":", 1)[1] + (":err" if error else ":ok"), follow_call)
                elif pending.counted:
                    self._pending_row(pending, None, follow_call)
            if call is not None and name == "read":
                for artifact_id in _artifact_ids(call.path or ""):
                    self.artifact_reads.add(artifact_id)
            if error and name in ("bash", "edit") and call is not None and counted:
                if name == "bash":
                    self.p4["trig:bash_error"] += 1
                    self.pending.append(_Pending("bash_error", 1, call.arguments.get("command"), True, call, event_hash))
                else:
                    targets = _edit_targets(call.arguments.get("input"))
                    self.p4["trig:edit_error"] += 1
                    self.pending.append(_Pending("edit_error", 2, targets, True, call, event_hash))
            return
        if role == "user":
            text = _text(message.get("content"))
            user_type = _user_class(text)
            if counted:
                self.c["user:" + user_type] += 1
                if user_type in {"human_or_other", "conductor_dispatch"}:
                    self._emit("route", "prompt_" + user_type, event_hash)
                if user_type == "human_or_other" and self.last_assistant_final and self.final_row is not None:
                    self._set_label(self.final_row, "correction" if _correction(text) else "no_correction_observed")
                # A neutral next turn is only a negative regex proxy, never acceptance.
                if user_type == "human_or_other":
                    if self.last_assistant_final:
                        self.c["user_after_final_answer"] += 1
                        if _correction(text):
                            self.c["user_correction_after_final"] += 1
                    if _correction(text):
                        self.c["user_correction_any"] += 1
            self.last_assistant_final = False
            self.final_row = None


def _source_count(spec: str, metrics: Metrics) -> int:
    if spec.startswith("c:"):
        return int(metrics.c.get(spec[2:], 0))
    if spec.startswith("p2:"):
        return int(metrics.p2.get(spec[3:], 0))
    if spec.startswith("p3:"):
        return int(metrics.p3.get(spec[3:], 0))
    if spec.startswith("p4:"):
        return int(metrics.p4.get(spec[3:], 0))
    if spec.startswith("p5:"):
        return int(metrics.p5.get(spec[3:], 0))
    if spec.startswith("dl:"):
        remainder = spec[3:]
        filename, selector = remainder.split(":", 1)
        if selector == "rows":
            return int(metrics.dl_rows.get(filename, 0))
        field_name, value = selector.split("=", 1)
        return int(metrics.dl_values.get(filename + ":" + field_name + "=" + value, 0))
    if spec.startswith("k:"):
        number, _, explanation = spec[2:].partition(":")
        if "find-rank.jsonl" in explanation:
            return metrics.find_rank_touched
        return int(number)
    raise ValueError("unknown count source: " + spec)


def _family_metrics(metrics: Metrics, point_rows: Sequence[Mapping[str, object]]) -> Dict[str, Dict[str, int]]:
    point_counts: Dict[int, Tuple[int, int]] = {}
    for index, row in enumerate(point_rows, 1):
        source = row.get("count_source")
        if not isinstance(source, dict):
            continue
        occurrence_specs = source.get("occurrences") if isinstance(source.get("occurrences"), list) else []
        label_specs = source.get("labels") if isinstance(source.get("labels"), list) else []
        occurrence_count = sum(_source_count(str(spec), metrics) for spec in occurrence_specs)
        label_count = sum(_source_count(str(spec), metrics) for spec in label_specs)
        point_counts[index] = (occurrence_count, label_count)
    family_counts: Dict[str, Dict[str, int]] = {}
    positives = {
        "pin": metrics.p4["follow:compaction:reread_prior_file"],
        "delegate": metrics.p2["task_result:error"] + metrics.p2["yield:error:None"],
        "outcome": metrics.c["user_correction_after_final"],
    }
    for family, points in FAMILY_POINTS.items():
        family_counts[family] = {
            "occurrences": sum(point_counts.get(point, (0, 0))[0] for point in points),
            "labels": sum(point_counts.get(point, (0, 0))[1] for point in points),
        }
        if family in positives:
            family_counts[family]["positives"] = int(positives[family])
    return family_counts


def _baseline_metrics(point_rows: Sequence[Mapping[str, object]]) -> Dict[str, Dict[str, int]]:
    result: Dict[str, Dict[str, int]] = {}
    positive_points = {"pin": (41,), "delegate": (43, 45), "outcome": (5,)}
    for family, points in FAMILY_POINTS.items():
        result[family] = {
            "occurrences": sum(int(point_rows[point - 1].get("occurrences_14d", 0)) for point in points if point <= len(point_rows)),
            "labels": sum(int(point_rows[point - 1].get("label_count", 0)) for point in points if point <= len(point_rows)),
        }
        if family in positive_points:
            result[family]["positives"] = sum(
                int(point_rows[point - 1].get("label_count", 0))
                for point in positive_points[family] if point <= len(point_rows)
            )
    return result


def rank_reopen_reasons(
    current: Mapping[str, Mapping[str, int]],
    baseline: Mapping[str, Mapping[str, int]],
) -> Dict[str, List[str]]:
    reasons: Dict[str, List[str]] = {}
    for family in FAMILY_POINTS:
        now, old = current.get(family, {}), baseline.get(family, {})
        changed: List[str] = []
        if (now.get("labels", 0) > 0) != (old.get("labels", 0) > 0):
            changed.append("label_availability")
        if family in {"pin", "delegate", "outcome"} and (now or old):
            positive, prior_positive = now.get("positives"), old.get("positives")
            if positive is None or prior_positive is None:
                changed.append("positive_count_unknown")
            elif (positive >= 30) != (prior_positive >= 30):
                changed.append("positive_threshold")
        if changed:
            reasons[family] = changed
    return reasons


def rank_report(current: Mapping[str, Mapping[str, int]], baseline: Mapping[str, Mapping[str, int]], as_of: str) -> str:
    lines = [
        "# Fleet family re-rank", "",
        f"as_of: {as_of}",
        "scan verdict: COMPLETE",
        f"command: nice -n 10 python3 work/fleet-schema/miner.py --rank --as-of {as_of} --json",
        "Current counts are recomputed from the streamed miner output; plan counts are from the committed decision-point registry.",
        "A partial or deferred scan is not a ranking and MUST NOT be treated as complete.", "",
        "## Emitted evidence", "",
        "`--labels FAMILY --json` emits hash-only source-defined proxies; missing outcomes are `NOT_COUNTED`, not negative labels.",
        "`reread` emits raw re-fetch metadata, including recorded path selectors, without harm or label fields.",
        "Rank outcomes refer only to shown hits; an unavailable transcript call index stays null.",
        "`result` also reports shaken-command repeat distances. K remains unknown unless `--rerun-window-calls` is supplied; no default scientific threshold is invented.",
        "For pin, delegate and outcome, the 30-positive cut uses observed re-fetch/error/correction proxies separately from total label counts.",
        "JSON rank output includes baseline counts and explicit `reopen` reasons. These proxies do not establish classifier quality.", "",
        "| Family | Current occurrences | Plan occurrences | Δ occurrences | Current labels | Plan labels | Δ labels | Re-rank |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    reopen = rank_reopen_reasons(current, baseline)
    for family in FAMILY_POINTS:
        now = current.get(family, {})
        old = baseline.get(family, {})
        occurrences = int(now.get("occurrences", 0))
        old_occurrences = int(old.get("occurrences", 0))
        labels = int(now.get("labels", 0))
        old_labels = int(old.get("labels", 0))
        status = "REOPEN" if family in reopen else "—"
        lines.append(f"| {family} | {occurrences} | {old_occurrences} | {occurrences - old_occurrences:+d} | {labels} | {old_labels} | {labels - old_labels:+d} | {status} |")
    lines.extend([
        "", "The `outcome` occurrence count excludes DP-48 aborts; DP-48 is a label source, not a separate decision.",
        "Any REOPEN requires a comment on jev-b35c.5 before family bake-off scores are used.", "",
    ])
    return "\n".join(lines)

def write_rank_report(report: str, path: Path = RANK_REPORT) -> None:
    path.write_text(report, encoding="utf-8")



def scan_files(
    paths: Iterable[Union[Path, str]],
    as_of: str,
    *,
    load_average: Callable[[], float],
    clock: Callable[[], float],
    budget_seconds: float = DEFAULT_BUDGET_SECONDS,
    on_row: Optional[Callable[[Mapping[str, object], str], None]] = None,
) -> ScanResult:
    cutoff = _timestamp(as_of)
    if cutoff is None:
        raise ValueError("invalid --as-of timestamp: " + as_of)
    if not math.isfinite(budget_seconds) or not 0 < budget_seconds <= DEFAULT_BUDGET_SECONDS:
        raise ValueError("budget must be a number in (0, 3000]")
    files = tuple(str(Path(path)) for path in paths)
    if not files:
        return ScanResult("PARTIAL", (), (), {"empty_input": 1})
    started = clock()
    counts: Counter = Counter()
    read: List[str] = []
    for index, path in enumerate(files):
        if load_average() > MAX_LOAD_AVERAGE:
            verdict = "DEFERRED" if not read else "PARTIAL"
            return ScanResult(verdict, tuple(read), files[index:], dict(counts))
        if clock() - started >= budget_seconds:
            return ScanResult("PARTIAL", tuple(read), files[index:], dict(counts))
        try:
            with open(path, "rb") as stream:
                for line_number, raw in enumerate(stream, 1):
                    try:
                        row = json.loads(raw)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        counts["invalid_json"] += 1
                        return ScanResult("PARTIAL", tuple(read), files[index:], dict(counts))
                    if not isinstance(row, dict):
                        counts["invalid_row"] += 1
                        return ScanResult("PARTIAL", tuple(read), files[index:], dict(counts))
                    stamp = _event_time(row)
                    if stamp is None or stamp > cutoff:
                        continue
                    if on_row is not None:
                        on_row(row, path)
                    if stamp >= cutoff - timedelta(days=WINDOW_DAYS):
                        counts["rows"] += 1
                        counts["rowtype:" + str(row.get("type"))] += 1
                        if row.get("type") == "message":
                            message = row.get("message")
                            if isinstance(message, dict) and message.get("role") == "assistant":
                                for block in message.get("content") or []:
                                    if isinstance(block, dict) and block.get("type") == "toolCall":
                                        counts["tool:" + str(block.get("name") or "?")] += 1
                    if line_number % 16384 == 0:
                        if load_average() > MAX_LOAD_AVERAGE:
                            return ScanResult("PARTIAL", tuple(read), files[index:], dict(counts))
                        if clock() - started >= budget_seconds:
                            return ScanResult("PARTIAL", tuple(read), files[index:], dict(counts))
        except OSError:
            counts["unreadable"] += 1
            return ScanResult("PARTIAL", tuple(read), files[index:], dict(counts))
        read.append(path)
    counts["complete"] = 1
    return ScanResult("COMPLETE", tuple(read), (), dict(counts))


def _load_average() -> float:
    try:
        return os.getloadavg()[0]
    except (AttributeError, OSError):
        return 0.0


def _ensure_nice() -> None:
    current = os.getpriority(os.PRIO_PROCESS, 0)
    if current < 10:
        os.nice(10 - current)
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError("miner could not reach nice 10")


def _session_roots(home: Path) -> List[Path]:
    profiles = home / ".omp" / "profiles"
    roots = [home / ".omp" / "agent" / "sessions"]
    if profiles.is_dir():
        roots.extend(path / "agent" / "sessions" for path in profiles.iterdir() if path.is_dir())
    return roots


def _default_paths(home: Path, cutoff: datetime) -> List[Path]:
    since = cutoff - timedelta(days=WINDOW_DAYS)
    found: Set[Path] = set()
    for root in _session_roots(home):
        if root.is_dir():
            for path in root.rglob("*.jsonl"):
                try:
                    if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) >= since:
                        found.add(path)
                except OSError:
                    continue
    decision_dir = home / ".local" / "state" / "jev"
    if decision_dir.is_dir():
        for path in decision_dir.glob("*.jsonl"):
            try:
                if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) >= since:
                    found.add(path)
            except OSError:
                continue
    return sorted(found)


def _miner_commit() -> str:
    source_path = Path(__file__).resolve().relative_to(ROOT).as_posix()
    commit = subprocess.run(
        ["git", "log", "-1", "--format=%H", "origin/main", "--", source_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    ).stdout.strip()
    if not commit:
        raise ValueError("miner source must be committed on origin/main before writing goldens")
    committed = subprocess.run(
        ["git", "show", f"{commit}:{source_path}"], cwd=ROOT,
        capture_output=True, check=True, timeout=5,
    ).stdout
    if committed != Path(__file__).read_bytes():
        raise ValueError("running miner source differs from recorded origin/main commit")
    return commit


def _write_labels(
    rows: Sequence[Mapping[str, object]],
    family: str,
    as_of: str,
    target: Optional[Path] = None,
    *,
    command: Optional[str] = None,
) -> None:
    if os.environ.get("UPDATE_GOLDENS") != "1":
        return
    if family not in EMITTED_FAMILIES:
        raise ValueError("no organic emitter for " + family)
    commit = _miner_commit()
    source_sha256 = _sha(Path(__file__).read_bytes())
    encoded = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    cutoff = _timestamp(as_of)
    if cutoff is None:
        raise ValueError(f"invalid --as-of timestamp: {as_of}")
    provenance = (
        f"# {family} label fixture provenance\n\n"
        f"miner commit: {commit}\n"
        f"miner source sha256: {source_sha256}\n"
        f"log window: {(cutoff - timedelta(days=WINDOW_DAYS)).isoformat()}..{as_of}\n"
        f"command: {command if command is not None else 'UNSPECIFIED (direct API invocation)'}\n"
        f"sha256: {_sha(encoded)}\n"
    )
    destination = target or ROOT / "kit" / "fixtures" / family
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "labels.jsonl").write_text(encoded, encoding="utf-8")
    (destination / "PROVENANCE.md").write_text(provenance, encoding="utf-8")


def _main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", choices=tuple(FAMILY_POINTS))
    parser.add_argument("--rank", action="store_true")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--input", action="append", type=Path, help="explicit JSONL inputs for bounded reproduction")
    parser.add_argument("--budget-seconds", type=_parse_budget_seconds, default=DEFAULT_BUDGET_SECONDS)
    parser.add_argument("--rank-output", type=Path, default=RANK_REPORT, help="report path for --rank")
    parser.add_argument("--rerun-window-calls", type=int, help="explicit shaken-result rerun window K; unknown when omitted")
    args = parser.parse_args(argv)
    if not args.labels and not args.rank:
        parser.error("choose --labels FAMILY or --rank")
    if args.labels is not None and args.labels not in EMITTED_FAMILIES:
        parser.error("no organic emitter for " + args.labels)
    if args.rerun_window_calls is not None and args.rerun_window_calls < 1:
        parser.error("--rerun-window-calls must be positive")
    try:
        _ensure_nice()
    except (OSError, RuntimeError) as error:
        print("miner refused: " + str(error), file=sys.stderr)
        return 2
    cutoff = _timestamp(args.as_of)
    if cutoff is None:
        parser.error("--as-of must be an RFC3339 timestamp")
    paths = args.input or _default_paths(Path.home(), cutoff)
    metrics = Metrics(cutoff - timedelta(days=WINDOW_DAYS), cutoff, rerun_window_calls=args.rerun_window_calls)

    def observe(row: Mapping[str, object], path: str) -> None:
        metrics.process(row, path)

    scan = scan_files(paths, args.as_of, load_average=_load_average, clock=time.monotonic,
                      budget_seconds=args.budget_seconds, on_row=observe)
    if scan.verdict != "COMPLETE":
        payload = {
            "verdict": scan.verdict,
            "files_read": len(scan.files_read),
            "files_not_read": list(scan.files_not_read),
            "partial_counts": dict(scan.counts),
            "complete_counts": None,
        }
        print(json.dumps(payload, sort_keys=True) if args.json else f"{scan.verdict}: {len(scan.files_read)} files read; {len(scan.files_not_read)} unread")
        return 2
    try:
        point_rows = [json.loads(line) for line in PLAN_POINTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError as error:
        raise ValueError(f"cannot read decision-point registry: {PLAN_POINTS}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid decision-point registry JSON at line {error.lineno}") from error
    metrics.finish()
    current = _family_metrics(metrics, point_rows)
    baseline = _baseline_metrics(point_rows)
    if args.labels:
        label_rows = metrics.label_rows(args.labels)
        payload = {"family": args.labels, "as_of": args.as_of, "count": len(label_rows), "labels": label_rows,
                   "family_counts": current, "plan_counts": baseline}
        if args.labels == "result":
            payload["rerun_window_calls"] = metrics.rerun_window_calls
        print(json.dumps(payload, sort_keys=True) if args.json else f"{args.labels}: {len(label_rows)} label rows")
        if os.environ.get("UPDATE_GOLDENS") == "1":
            invocation = list(argv) if argv is not None else sys.argv[1:]
            command = "UPDATE_GOLDENS=1 " + shlex.join([sys.executable, str(Path(__file__)), *invocation])
            _write_labels(label_rows, args.labels, args.as_of, command=command)
    else:
        report = rank_report(current, baseline, args.as_of)
        payload = {
            "verdict": "COMPLETE", "as_of": args.as_of, "families": current,
            "plan_counts": baseline, "reopen": rank_reopen_reasons(current, baseline),
        }
        write_rank_report(report, args.rank_output)
        print(json.dumps(payload, sort_keys=True) if args.json else report)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
