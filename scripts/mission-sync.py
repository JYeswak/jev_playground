#!/usr/bin/env python3
"""Synchronize mission pillar fields from ROADMAP.md and verify pinned protocol text."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import sys
from pathlib import Path
from typing import Any

PROTOCOL_SHA256 = "229b45bad8c37626d1ba62391cf1a7a9e75bcb346ec4c0ce0df8fad1f1d23672"
COMMANDS = {"classifier", "gh", "grep", "python3"}
MISSION_FIELDS = ("id", "clause", "check", "check_fails_when", "beads")
REQUIRED_COLUMNS = {"pillar", "clause", "check", "owning beads"}


class MissionSyncError(Exception):
    pass


def _markdown_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None

    cells: list[str] = []
    current: list[str] = []
    in_code = False
    for character in stripped[1:-1]:
        if character == "`":
            in_code = not in_code
        if character == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    if in_code:
        raise MissionSyncError("ROADMAP.md has an unmatched inline-code delimiter in a table row")
    cells.append("".join(current).strip())
    return cells


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(
        cell and "-" in cell and set(cell) <= {"-", ":"} for cell in cells
    )


def _plain_markdown(value: str) -> str:
    return value.replace("**", "").replace("`", "").strip()


def _pillar_id(value: str) -> str:
    return "-".join(_plain_markdown(value).lower().split())


def _bead_ids(value: str) -> list[str]:
    found: list[str] = []
    index = 0
    while True:
        start = value.find("jev-", index)
        if start < 0:
            break
        if start and (value[start - 1].isalnum() or value[start - 1] in "_-"):
            index = start + 4
            continue
        end = start + 4
        while end < len(value) and (value[end].isalnum() or value[end] in ".-"):
            end += 1
        if end > start + 4:
            bead = value[start:end]
            if bead not in found:
                found.append(bead)
        index = max(end, start + 4)
    return found


def _inline_code_spans(value: str) -> list[str]:
    spans: list[str] = []
    index = 0
    while index < len(value):
        start = value.find("`", index)
        if start < 0:
            break
        end = value.find("`", start + 1)
        if end < 0:
            raise MissionSyncError("ROADMAP.md check has an unmatched inline-code delimiter")
        spans.append(value[start + 1 : end].strip())
        index = end + 1
    return spans


def _shell_commands(value: str) -> str | None:
    try:
        lexer = shlex.shlex(value, posix=True, punctuation_chars="|&;")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError as error:
        raise MissionSyncError(f"invalid shell quoting in check command: {error}") from error

    if not tokens or tokens[0] not in COMMANDS:
        return None

    segment: list[str] = []
    for token in tokens + ["&&"]:
        if token in {"|", "&&"}:
            if not segment or segment[0] not in COMMANDS or len(segment) < 2:
                raise MissionSyncError(f"check is not an exit-coded command: {value!r}")
            segment = []
        elif token in {";", "||", "&"}:
            raise MissionSyncError(f"check uses a non-failing shell separator: {value!r}")
        else:
            segment.append(token)
    return value.strip()


def _failure_condition(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in (
            "exits non-zero", "exit non-zero", "exits with non-zero",
            "exit with non-zero", "fails when", "fail when",
        )
    )


def _extract_check(cell: str, pillar: str) -> str:
    commands: list[str] = []
    for span in _inline_code_spans(cell):
        command = _shell_commands(span)
        if command is not None:
            commands.append(command)
    if not commands:
        raise MissionSyncError(f"pillar {pillar!r} check has no supported exit-coded command")
    if not _failure_condition(cell):
        raise MissionSyncError(f"pillar {pillar!r} check must state an explicit failure condition")
    return " && ".join(commands)


def read_roadmap(path: Path) -> list[dict[str, Any]]:
    active = False
    indices: dict[str, int] = {}
    pillars: list[dict[str, Any]] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        cells = _markdown_cells(line)
        if cells is None:
            if active:
                active = False
            continue
        normalized = [cell.lower() for cell in cells]
        if not active and REQUIRED_COLUMNS.issubset(set(normalized)):
            indices = {name: normalized.index(name) for name in REQUIRED_COLUMNS}
            active = True
            continue
        if not active or _is_separator(cells):
            continue
        if max(indices.values()) >= len(cells):
            raise MissionSyncError("ROADMAP.md pillar table row has an inconsistent column count")

        name = _pillar_id(cells[indices["pillar"]])
        if not name or name in {"pillar", "---"}:
            continue
        clause = _plain_markdown(cells[indices["clause"]])
        check = _extract_check(cells[indices["check"]], name)
        beads = _bead_ids(cells[indices["owning beads"]])
        if not clause:
            raise MissionSyncError(f"pillar {name!r} has an empty clause")
        if not beads:
            raise MissionSyncError(f"pillar {name!r} has no owning bead ids")
        pillars.append({"id": name, "clause": clause, "check": check, "beads": beads})
    if not pillars:
        raise MissionSyncError("ROADMAP.md pillar table was not found or has no rows")
    ids = [pillar["id"] for pillar in pillars]
    if len(ids) != len(set(ids)):
        raise MissionSyncError("ROADMAP.md contains duplicate pillar ids")
    return pillars


def _table_header(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("[") and stripped.endswith("]")


def _toml_sections(text: str) -> tuple[list[str], list[list[str]]]:
    chunks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines(keepends=True):
        if _table_header(line) and current:
            chunks.append(current)
            current = []
        current.append(line)
    if current:
        chunks.append(current)

    if chunks and not _table_header(chunks[0][0]):
        return chunks[0], chunks[1:]
    return [], chunks


def _pillar_values(section: list[str]) -> dict[str, Any]:
    if not section or section[0].strip() != "[[pillar]]":
        raise MissionSyncError("expected a [[pillar]] table in .omp/mission.toml")

    values: dict[str, Any] = {}
    for line in section[1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw = stripped.split("=", 1)
        key = key.strip()
        if key not in MISSION_FIELDS:
            continue
        if key in values:
            raise MissionSyncError(f"pillar table has duplicate {key!r} field")
        try:
            values[key] = json.loads(raw.strip())
        except json.JSONDecodeError as error:
            raise MissionSyncError(f"pillar {key!r} must use a one-line TOML basic value: {error}") from error

    for field in MISSION_FIELDS:
        if field not in values:
            raise MissionSyncError(f"pillar table is missing required {field!r} field")
    if not isinstance(values["id"], str) or not isinstance(values["clause"], str):
        raise MissionSyncError("pillar id and clause must be strings")
    if not isinstance(values["check"], str) or not isinstance(values["check_fails_when"], str):
        raise MissionSyncError("pillar check and check_fails_when must be strings")
    if not values["check_fails_when"].strip():
        raise MissionSyncError(f"pillar {values['id']!r} has an empty check_fails_when condition")
    if not isinstance(values["beads"], list) or not all(isinstance(item, str) for item in values["beads"]):
        raise MissionSyncError(f"pillar {values['id']!r} beads must be an array of strings")
    return values


def read_mission(path: Path) -> tuple[list[str], list[list[str]], list[dict[str, Any]]]:
    preamble, sections = _toml_sections(path.read_text(encoding="utf-8"))
    pillar_sections = [section for section in sections if section[0].strip() == "[[pillar]]"]
    other_sections = [section for section in sections if section[0].strip() != "[[pillar]]"]
    pillars = [_pillar_values(section) for section in pillar_sections]
    ids = [pillar["id"] for pillar in pillars]
    if len(ids) != len(set(ids)):
        raise MissionSyncError(".omp/mission.toml contains duplicate pillar ids")
    return preamble, pillar_sections + other_sections, pillars


def _toml_value(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return "[" + ", ".join(json.dumps(item, ensure_ascii=False) for item in value) + "]"
    raise MissionSyncError("unsupported value for mission pillar field")


def _set_field(section: list[str], key: str, value: Any) -> list[str]:
    changed = list(section)
    matches: list[int] = []
    for index, line in enumerate(changed):
        if "=" not in line:
            continue
        lhs = line.partition("=")[0]
        if lhs.strip() == key:
            matches.append(index)
    if len(matches) > 1:
        raise MissionSyncError(f"pillar table has duplicate {key!r} field")

    rendered = _toml_value(value)
    if matches:
        index = matches[0]
        lhs = changed[index].partition("=")[0]
        indent = lhs[: len(lhs) - len(lhs.lstrip())]
        changed[index] = f"{indent}{key} = {rendered}\n"
        return changed

    id_index = next(
        (index for index, line in enumerate(changed) if line.partition("=")[0].strip() == "id"),
        None,
    )
    if id_index is None:
        raise MissionSyncError("cannot add a pillar field before its id")
    changed.insert(id_index + 1, f"{key} = {rendered}\n")
    return changed


def _validate_check(value: str, pillar: str) -> None:
    if _shell_commands(value) is None:
        raise MissionSyncError(f"pillar {pillar!r} check is not an exit-coded command: {value!r}")

def _protocol_check(root: Path) -> None:
    path = root / "work" / "plan-20261004" / "MISSION-PROTOCOL.md"
    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise MissionSyncError(f"cannot read pinned protocol file {path}: {error}") from error
    if digest != PROTOCOL_SHA256:
        raise MissionSyncError(
            f"Mission Protocol SHA256 mismatch for {path}: expected {PROTOCOL_SHA256}, got {digest}"
        )


def _mismatch_messages(expected: list[dict[str, Any]], actual: list[dict[str, Any]]) -> list[str]:
    messages: list[str] = []
    expected_by_id = {pillar["id"]: pillar for pillar in expected}
    actual_by_id = {pillar["id"]: pillar for pillar in actual}
    if list(expected_by_id) != list(actual_by_id):
        missing = [pillar_id for pillar_id in expected_by_id if pillar_id not in actual_by_id]
        extra = [pillar_id for pillar_id in actual_by_id if pillar_id not in expected_by_id]
        messages.append(f"pillar ids/order differ: missing={missing}, extra={extra}")

    for pillar_id, source in expected_by_id.items():
        mission = actual_by_id.get(pillar_id)
        if mission is None:
            continue
        for field in ("clause", "check"):
            if mission[field] != source[field]:
                messages.append(f"pillar {pillar_id!r}: {field} differs from ROADMAP.md")
        if mission["beads"] != source["beads"]:
            missing = [bead for bead in source["beads"] if bead not in mission["beads"]]
            extra = [bead for bead in mission["beads"] if bead not in source["beads"]]
            messages.append(f"pillar {pillar_id!r}: beads differ; missing={missing}, extra={extra}")
        try:
            _validate_check(mission["check"], pillar_id)
        except MissionSyncError as error:
            messages.append(str(error))
    return messages


def synchronize(root: Path, write: bool) -> int:
    _protocol_check(root)
    source = read_roadmap(root / "ROADMAP.md")
    mission_path = root / ".omp" / "mission.toml"
    preamble, sections, current = read_mission(mission_path)

    expected_ids = [pillar["id"] for pillar in source]
    current_ids = [pillar["id"] for pillar in current]
    if set(expected_ids) != set(current_ids):
        missing = [pillar_id for pillar_id in expected_ids if pillar_id not in current_ids]
        extra = [pillar_id for pillar_id in current_ids if pillar_id not in expected_ids]
        raise MissionSyncError(
            f"pillar row sets differ; missing mission rows={missing}, extra mission rows={extra}"
        )

    pillar_sections = {
        values["id"]: section
        for section in sections
        if section[0].strip() == "[[pillar]]"
        for values in [_pillar_values(section)]
    }
    other_sections = [section for section in sections if section[0].strip() != "[[pillar]]"]

    if write:
        updated_pillars: list[list[str]] = []
        for source_pillar in source:
            pillar_id = source_pillar["id"]
            section = pillar_sections[pillar_id]
            _validate_check(source_pillar["check"], pillar_id)
            for field in ("clause", "check", "beads"):
                section = _set_field(section, field, source_pillar[field])
            updated_pillars.append(section)
        rendered = "".join(preamble + [line for section in updated_pillars for line in section]
                            + [line for section in other_sections for line in section])
        if rendered != mission_path.read_text(encoding="utf-8"):
            mission_path.write_text(rendered, encoding="utf-8")
            print(f"Updated {mission_path.relative_to(root)} from ROADMAP.md ({len(source)} pillars).")
        else:
            print(f"{mission_path.relative_to(root)} already matches ROADMAP.md ({len(source)} pillars).")
        return 0

    messages = _mismatch_messages(source, current)
    if messages:
        for message in messages:
            print(f"mission-sync: {message}", file=sys.stderr)
        return 1
    print(f"{mission_path.relative_to(root)} matches ROADMAP.md ({len(source)} pillars).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if mission pillar fields differ")
    mode.add_argument("--write", action="store_true", help="sync mission pillar fields from ROADMAP.md")
    args = parser.parse_args(argv)

    try:
        root = Path(__file__).resolve().parents[1]
        return synchronize(root, write=args.write)
    except (MissionSyncError, OSError) as error:
        print(f"mission-sync: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
