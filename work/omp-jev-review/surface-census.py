#!/usr/bin/env python3
"""Which omp-jev-* surfaces are loaded, and which have real decision rows.

Keyless. One row per work/omp-jev-* package. A row counts only after its JSON
line parses. Real work is a session whose path and cwd are not a probe or test
session. The rule is the one jev-cz0 used: /tmp, review-l3, probe, and fixture
sessions are not real work.

    python3 work/omp-jev-review/surface-census.py

Exit 0 when every package has a row. This is a census, not a gate.
"""

import glob
import json
import os
import re
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parents[2]
TYPE_RE = re.compile(r"com\.zeststream\.[A-Za-z0-9_.-]+")
CREDITS_AFTER = "2026-09-24T04:19:00Z"


def packages():
    root = REPO / "work"
    return sorted(
        p.name for p in root.iterdir() if p.is_dir() and p.name.startswith("omp-jev-")
    )


def short_name(package):
    return package.removeprefix("omp-jev-")


def decision_types(package):
    found = set()
    root = REPO / "work" / package
    if not root.is_dir():
        return []
    for path in root.rglob("*"):
        if path.suffix not in {".ts", ".mjs", ".js"} or "node_modules" in path.parts:
            continue
        if "/test/" in str(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in TYPE_RE.findall(text):
            if token.endswith(".decision.v1") or token.endswith(".screen.v1"):
                found.add(token)
    return sorted(found)


def config_files():
    files = [REPO / ".omp" / "config.yml", HOME / ".omp" / "agent" / "config.yml"]
    files.extend(HOME.glob(".omp/profiles/*/agent/config.yml"))
    return [p for p in files if p.is_file()]


def listed_extensions(config_path):
    listed = []
    in_list = False
    for line in config_path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped in {"extensions:", "tools:"}:
            in_list = True
            continue
        if in_list and stripped.startswith("- "):
            listed.append(stripped[2:].strip().strip("\"'"))
            continue
        if in_list and stripped and not stripped.startswith("-"):
            in_list = False
    return listed


def load_sites(package, types):
    name = short_name(package)
    needle = f"omp-jev-{name}"
    sites = []
    for config in config_files():
        for entry in listed_extensions(config):
            target = (
                (config.parent / entry).resolve()
                if not entry.startswith("/")
                else Path(entry)
            )
            blob = entry
            if target.is_file():
                blob += (
                    "\n" + target.read_text(encoding="utf-8", errors="replace")[:4000]
                )
            if needle not in blob and not any(t in blob for t in types):
                continue
            if config == REPO / ".omp" / "config.yml":
                sites.append("project:.omp/config.yml")
            elif config == HOME / ".omp" / "agent" / "config.yml":
                sites.append("agent:default")
            else:
                sites.append(f"profile:{config.parent.parent.name}")
    link_roots = [REPO / ".omp" / "extensions", REPO / ".omp" / "tools"]
    link_roots.append(HOME / ".omp" / "agent" / "extensions")
    link_roots.extend(HOME.glob(".omp/profiles/*/agent/extensions"))
    for root in link_roots:
        if not root.is_dir():
            continue
        for path in root.iterdir():
            if not path.is_symlink():
                continue
            if needle in os.readlink(path) or needle in str(path.resolve()):
                sites.append(f"symlink:{path}")
    return sorted(set(sites))


def session_files():
    roots = [HOME / ".omp" / "agent" / "sessions"]
    roots.extend(HOME.glob(".omp/profiles/*/agent/sessions"))
    files = []
    for root in roots:
        if root.is_dir():
            files.extend(root.rglob("*.jsonl"))
    return roots, files


def session_cwd(path):
    try:
        fh = path.open(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    with fh:
        for i, line in enumerate(fh):
            if i > 40:
                break
            if '"cwd"' not in line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("type") == "session":
                return str(row.get("cwd") or "")
    return ""


def is_probe(path, cwd):
    blob = f"{path}\n{cwd}".lower()
    markers = (
        "/tmp/",
        "/private/tmp/",
        "review-l3",
        "/probe",
        "probe-session",
        "fixture",
    )
    if any(m in blob for m in markers):
        return True
    encoded = path.parent.name.lower()
    if any(m in encoded for m in ("tmp", "probe", "fixture", "review-l3")):
        return True
    if "/test/" in cwd or "/tests/" in cwd or cwd.rstrip("/").endswith("/test"):
        return True
    if "/profiles/omp-test/" in str(path) or "/profiles/jev-scratch" in str(path):
        return True
    return False


def kind_of(data):
    return str(data.get("kind") or data.get("status") or data.get("outcome") or "")


def bucket(kind):
    if kind.endswith("_error") or kind == "error":
        return "error"
    if "_scored" in kind or kind.endswith("scored"):
        return "scored"
    return "other"


def is_credit(data, timestamp):
    if not timestamp or timestamp < CREDITS_AFTER:
        return False
    blob = json.dumps(data)
    return "402" in blob


def main():
    pkgs = packages()
    types_by = {p: decision_types(p) for p in pkgs}
    type_owner = {}
    for package, types in types_by.items():
        for token in types:
            type_owner[token] = package
    roots, files = session_files()
    tallies = {
        p: {
            "real": 0,
            "probe": 0,
            "error": 0,
            "scored": 0,
            "other": 0,
            "last_scored": "",
            "credits": 0,
        }
        for p in pkgs
    }
    for path in files:
        cwd = session_cwd(path)
        probe = is_probe(path, cwd)
        try:
            fh = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if "omp-jev-" not in line and "jev-screen.screen.v1" not in line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                token = row.get("customType")
                if not isinstance(token, str) or token not in type_owner:
                    continue
                package = type_owner[token]
                slot = tallies[package]
                if probe:
                    slot["probe"] += 1
                    continue
                slot["real"] += 1
                data = row.get("data") if isinstance(row.get("data"), dict) else {}
                which = bucket(kind_of(data))
                slot[which] += 1
                timestamp = str(row.get("timestamp") or data.get("timestamp") or "")
                if which == "scored" and timestamp > slot["last_scored"]:
                    slot["last_scored"] = timestamp
                if which == "error" and is_credit(data, timestamp):
                    slot["credits"] += 1
    print(
        "package\tloaded\twhere\ttypes\treal_rows\treal_error\treal_scored\treal_other\tlast_scored\tprobe_rows\tcredits_402"
    )
    credits = 0
    for package in pkgs:
        slot = tallies[package]
        sites = load_sites(package, types_by[package])
        credits += slot["credits"]
        print(
            "\t".join(
                [
                    package,
                    "yes" if sites else "no",
                    ",".join(sites) or "-",
                    ",".join(types_by[package]) or "-",
                    str(slot["real"]),
                    str(slot["error"]),
                    str(slot["scored"]),
                    str(slot["other"]),
                    slot["last_scored"] or "-",
                    str(slot["probe"]),
                    str(slot["credits"]),
                ]
            )
        )
    print(
        f"# packages {len(pkgs)} session_files {len(files)} roots {len([r for r in roots if r.is_dir()])} "
        f"credits_402_since_{CREDITS_AFTER} {credits}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
