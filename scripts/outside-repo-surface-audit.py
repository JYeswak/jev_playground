#!/usr/bin/env python3
"""Audit installed Jev-capable omp hooks and extensions against a registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

Surface = dict[str, object]


def roots(home: Path) -> list[Path]:
    return [
        home / ".omp" / "agent",
        *sorted((home / ".omp" / "profiles").glob("*/agent")),
    ]


def installed(home: Path) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for root in roots(home):
        for kind in ("hooks/pre", "hooks/post", "extensions"):
            directory = root / kind
            if not directory.is_dir():
                continue
            for path in sorted(directory.iterdir()):
                if path.is_file() and (
                    path.name.startswith("jev-")
                    or path.name.startswith("omp-jev-")
                    or path.name in {"guard-rule.ts", "omp-harm-rule.ts"}
                ):
                    found[str(path)] = {
                        "path": str(path),
                        "name": path.name,
                        "loaded_from": str(path.resolve()),
                    }
        config = root / "config.yml"
        if config.is_file():
            for line in config.read_text(encoding="utf-8").splitlines():
                value = line.strip().removeprefix("-").strip().strip("'\"")
                if "jev" in value.lower() and value.endswith((".ts", ".js", ".mjs")):
                    path = Path(value).expanduser()
                    if path.is_file() and path.parent != root / "extensions":
                        installed_path = f"{config}::{value}"
                        found[installed_path] = {
                            "path": installed_path,
                            "physical_path": str(path),
                            "name": path.name,
                            "loaded_from": str(path.resolve()),
                            "configured_at": str(config),
                        }
    return sorted(
        found.values(),
        key=lambda row: (
            row["name"],
            row.get("configured_at", row["path"]),
            row["path"],
        ),
    )


def audit(registry: dict[str, object], rows: list[dict[str, str]]) -> dict[str, object]:
    entries = registry.get("surfaces")
    errors: list[dict[str, str]] = []
    if not isinstance(entries, list):
        entries = []
        errors.append({"kind": "invalid_registry", "detail": "surfaces must be a list"})
    by_path: dict[str, Surface] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(
                {
                    "kind": "invalid_entry",
                    "detail": f"surfaces[{index}] must be an object",
                }
            )
            continue
        name = str(entry.get("id", f"surfaces[{index}]"))
        paths = entry.get("installed_paths")
        if not isinstance(paths, list) or not paths:
            errors.append({"kind": "missing_installed_paths", "surface": name})
            paths = []
        for path in paths:
            if not isinstance(path, str):
                errors.append({"kind": "invalid_installed_path", "surface": name})
                continue
            if path in by_path:
                errors.append(
                    {"kind": "duplicate_registry_path", "surface": name, "path": path}
                )
            by_path[path] = entry
        budget = entry.get("latency_budget_ms")
        if (
            not isinstance(budget, int)
            or isinstance(budget, bool)
            or budget <= 0
            or budget >= 30000
        ):
            errors.append({"kind": "invalid_latency_budget", "surface": name})
        if (
            not isinstance(entry.get("fail_open_test"), str)
            or not entry["fail_open_test"].strip()
        ):
            errors.append({"kind": "missing_fail_open_test", "surface": name})
        switch = entry.get("off_switch")
        if (
            not isinstance(switch, dict)
            or not switch.get("path")
            or switch.get("polarity") not in {"presence-OFF", "presence-ON"}
        ):
            errors.append({"kind": "missing_or_invalid_off_switch", "surface": name})
        if (
            not isinstance(entry.get("safe_side"), str)
            or not entry["safe_side"].strip()
        ):
            errors.append({"kind": "missing_safe_side", "surface": name})
        if not isinstance(entry.get("owner"), str) or not entry["owner"].strip():
            errors.append({"kind": "missing_owner", "surface": name})
        if (
            not isinstance(entry.get("loaded_from"), str)
            or not entry["loaded_from"].strip()
        ):
            errors.append({"kind": "missing_loaded_from", "surface": name})
        if entry.get("outside_repo") is not True:
            errors.append({"kind": "outside_repo_not_true", "surface": name})
    observed = {row["path"] for row in rows}
    for path, entry in by_path.items():
        if path not in observed:
            errors.append(
                {
                    "kind": "registry_path_not_installed",
                    "surface": str(entry.get("id", "unknown")),
                    "path": path,
                }
            )
    for row in rows:
        if row["path"] not in by_path:
            errors.append(
                {
                    "kind": "installed_surface_unregistered",
                    "path": row["path"],
                    "name": row["name"],
                }
            )
    return {
        "status": "RED" if errors else "GREEN",
        "installed_count": len(rows),
        "registered_path_count": len(by_path),
        "installed": rows,
        "errors": errors,
    }


def main(argv: Optional[list[str]] = None) -> int:  # noqa: UP045 -- Python 3.9 runtime compatibility
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json", action="store_true", help="emit the complete audit report as JSON"
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="home root to inspect (test seam)",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "work/blast-radius/surfaces.json",
    )
    parser.add_argument(
        "--write-report", type=Path, help="write the complete report JSON to this path"
    )
    args = parser.parse_args(argv)
    try:
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        if not isinstance(registry, dict):
            raise TypeError("registry root must be an object")
        report = audit(registry, installed(args.home))
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        report = {
            "status": "RED",
            "installed_count": 0,
            "registered_path_count": 0,
            "installed": [],
            "errors": [{"kind": "audit_input_error", "detail": str(exc)}],
        }
    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(report, indent=2, sort_keys=True)
        if args.json
        else f"{report['status']}: {len(report['installed'])} installed surfaces; {len(report['errors'])} findings"
    )
    return 1 if report["status"] != "GREEN" else 0


if __name__ == "__main__":
    raise SystemExit(main())
