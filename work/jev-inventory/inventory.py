#!/usr/bin/env python3
"""Jev surface inventory: what is applied to our systems, how it works, what it costs and saves.

Ground truth is LIVE state, read from omp config, hook files, logs and omp session files.
expected.json holds what we CLAIM. Every surface whose live state differs from its claim is a
conformance failure (exit 1). Outputs (default dir var/jev-inventory/):
  inventory.json   live state, 24h usage, cost, verdicts
  inventory.mmd    Mermaid flowchart (validated with frankenmermaid)
  INVENTORY.md     the table

  python3 work/jev-inventory/inventory.py                 # live run, conformance enforced
  python3 work/jev-inventory/inventory.py --structure     # print the deterministic structural
                                                          # diagram (expected.json only; golden)
"""

from __future__ import annotations

import calendar
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HOME = Path.home()
STATE = HOME / ".local" / "state" / "jev"
GROUP_TITLES = {
    "native": "omp native judge (TypeSafe jev-1.13.0)",
    "hook": "project hooks (shadow, log only)",
    "extension": "project extensions",
    "rule": "judged rules",
    "fleet": "fleet",
    "infra": "infrastructure",
}
VERDICT_CLASS = {
    "WORKS": "works",
    "WORKS-NO-BENEFIT-YET": "unproven",
    "UNPROVEN": "unproven",
    "UNMEASURED": "unproven",
    "PARTIAL": "unproven",
    "IDLE-BY-DESIGN": "nobenefit",
    "NO-SIGNAL": "nobenefit",
    "NO-BENEFIT": "nobenefit",
    "OFF-MISROUTES": "off",
    "REFUTED": "off",
    "LOSES-TO-JEV": "off",
}


def load_expected() -> dict:
    return json.loads(
        Path(
            os.environ.get("JEV_INVENTORY_EXPECTED", HERE / "expected.json")
        ).read_text()
    )


def sh(args: list[str], timeout: int = 30) -> str:
    try:
        return subprocess.run(
            args, capture_output=True, text=True, timeout=timeout
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def profile_config(profile: str) -> dict:
    args = (
        ["omp", "config", "list", "--json"]
        if profile == "default"
        else ["omp", "--profile", profile, "config", "list", "--json"]
    )
    try:
        raw = json.loads(sh(args, 60) or "{}")
    except ValueError:
        return {}
    return {k: (v.get("value") if isinstance(v, dict) else v) for k, v in raw.items()}


def session_usage(hours: int = 24) -> tuple[Counter, Counter, int]:
    """Native Jev calls and USD cost by purpose, plus jev-repo sessions started, in the window."""
    cutoff = time.time() - hours * 3600
    roots = [HOME / ".omp" / "agent" / "sessions"] + list(
        (HOME / ".omp" / "profiles").glob("*/agent/sessions")
    )
    calls: Counter = Counter()
    cost: Counter = Counter()  # type: ignore[assignment]  # float values
    jev_sessions = 0
    for root in roots:
        for path in root.glob("*/*.jsonl"):
            try:
                if path.stat().st_mtime < cutoff:
                    continue
            except FileNotFoundError:
                continue
            if path.parent.name == "-Developer-jev" and path.stat().st_ctime >= cutoff:
                jev_sessions += 1
            with path.open(encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    if '"model_usage"' not in line or '"typesafe"' not in line:
                        continue
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    stamp = row.get("timestamp", "")
                    if (
                        stamp
                        and calendar.timegm(
                            time.strptime(stamp[:19], "%Y-%m-%dT%H:%M:%S")
                        )
                        < cutoff
                    ):
                        continue
                    purpose = row.get("purpose", "?")
                    calls[purpose] += 1
                    cost[purpose] += float(
                        ((row.get("usage") or {}).get("cost") or {}).get("total") or 0
                    )
    return calls, cost, jev_sessions


def log_statuses(name: str, hours: int = 24) -> Counter:
    path = STATE / name
    since = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - hours * 3600))
    out: Counter = Counter()
    if not path.exists():
        return out
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if str(row.get("ts", "")) >= since:
                out[str(row.get("status", "?"))] += 1
    return out


def config_extensions() -> list[str]:
    text = (ROOT / ".omp" / "config.yml").read_text()
    block = text.split("\nextensions:", 1)[-1]
    return re.findall(r"^\s+-\s+(\S+)", block, re.M)


def live_state(surface: dict, ctx: dict) -> str:
    kind = surface["group"]
    sid = surface["id"]
    if kind == "native":
        need = {
            "smart-stop": lambda c: c.get("features.unexpectedStopDetection")
            == "smart",
            "auto-thinking": lambda c: c.get("defaultThinkingLevel") == "auto",
        }.get(sid, lambda c: True)
        ok = all(
            str((c.get("modelRoles") or {}).get("judge", "")).startswith("typesafe/")
            and need(c)
            for c in ctx["profiles"].values()
        )
        return "on" if ok and ctx["profiles"] else "off"
    if kind == "hook":
        return "on" if (ROOT / surface["file"]).exists() else "off"
    if kind == "extension":
        return "on" if surface["extension"] in ctx["extensions"] else "off"
    if kind == "rule":
        return (
            "on"
            if (ROOT / ".omp" / "rules" / f"{surface['rule']}.md").exists()
            else "off"
        )
    if kind == "fleet":
        return "on" if sh(["pgrep", "-f", surface["process"]]).strip() else "off"
    if sid == "key-wrapper":
        files = [HOME / ".omp/agent/models.yml"] + [
            HOME / f".omp/profiles/{p}/agent/models.yml"
            for p in ctx["profile_names"]
            if p != "default"
        ]
        return (
            "on"
            if all(f.exists() and "typesafe-key.mjs" in f.read_text() for f in files)
            else "off"
        )
    if sid == "local-sys1":
        declared = "ollama-sys1:" in (HOME / ".omp/agent/models.yml").read_text()
        used = any(
            "ollama-sys1" in json.dumps(c.get("modelRoles") or {})
            for c in ctx["profiles"].values()
        )
        return "inert" if declared and not used else ("on" if used else "off")
    if sid == "agents-trim":
        return (
            "on" if len((ROOT / "AGENTS.md").read_text().splitlines()) <= 600 else "off"
        )
    return "unknown"


def node_id(sid: str) -> str:
    return sid.replace("-", "_")


def mermaid(expected: dict, live: dict | None) -> str:
    """Flowchart grouped by surface type. live=None gives the deterministic structural diagram."""
    lines = [
        "flowchart LR",
        '  JEV(["TypeSafe API jev-1.13.0"])',
        '  LOCAL(["local Ollama nimble/tev1"])',
    ]
    for group, title in GROUP_TITLES.items():
        members = [s for s in expected["surfaces"] if s["group"] == group]
        if not members:
            continue
        lines.append(f'  subgraph {group}["{title}"]')
        for s in members:
            label = f"{s['name']}<br/>{s['verdict']}<br/>expect {s['expect']}"
            if live is not None:
                row = live[s["id"]]
                label += f"<br/>live {row['state']}" + (
                    f", {row['usage24h']}/24h" if row["usage24h"] is not None else ""
                )
            lines.append(f'    {node_id(s["id"])}["{label}"]')
        lines.append("  end")
    for s in expected["surfaces"]:
        n = node_id(s["id"])
        if s["group"] in ("native", "hook") or s["id"] in ("needs-human",):
            lines.append(f"  JEV --> {n}")
        if s["id"] == "local-sys1":
            lines.append(f"  LOCAL -.-> {n}")
    lines.append(
        "  LOCAL -. cascade jev-8w0h offline 81% fewer paid calls .-> gate_observe"
    )
    lines.append("  key_wrapper --> JEV")
    lines += [
        "  classDef works fill:#d4f7d4,stroke:#2a7a2a",
        "  classDef unproven fill:#fff3c4,stroke:#9a7a00",
        "  classDef nobenefit fill:#ffe0c2,stroke:#a85a00",
        "  classDef off fill:#e6e6e6,stroke:#777,stroke-dasharray:4 3",
    ]
    for cls in sorted(set(VERDICT_CLASS.values())):
        ids = [
            node_id(s["id"])
            for s in expected["surfaces"]
            if VERDICT_CLASS.get(s["verdict"]) == cls
        ]
        if ids:
            lines.append(f"  class {','.join(ids)} {cls}")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    expected = load_expected()
    if "--structure" in argv:
        sys.stdout.write(mermaid(expected, None))
        return 0
    out_dir = Path(os.environ.get("JEV_INVENTORY_OUT", ROOT / "var" / "jev-inventory"))
    out_dir.mkdir(parents=True, exist_ok=True)
    names = expected["profiles"]
    ctx = {
        "profile_names": names,
        "profiles": {p: profile_config(p) for p in names},
        "extensions": config_extensions(),
    }
    calls, cost, jev_sessions = session_usage()
    agents_now = len((ROOT / "AGENTS.md").read_bytes())
    agents_old = len((ROOT / "docs/history/AGENTS-2026-09-30.md").read_bytes())
    live: dict = {}
    failures = []
    for s in expected["surfaces"]:
        state = live_state(s, ctx)
        usage = None
        detail = ""
        if s.get("purpose"):
            usage = calls.get(s["purpose"], 0)
            detail = f"${cost.get(s['purpose'], 0):.4f}/24h"
        elif s.get("log"):
            st = log_statuses(s["log"])
            usage = sum(st.values())
            detail = ", ".join(f"{k} {v}" for k, v in st.most_common(3))
        if s["id"] == "agents-trim":
            saved = (agents_old - agents_now) // 4 * jev_sessions
            detail = f"~{(agents_old - agents_now) // 4:,} tokens/session x {jev_sessions} jev sessions = ~{saved:,} tokens/24h"
        live[s["id"]] = {"state": state, "usage24h": usage, "detail": detail}
        if state != s["expect"]:
            failures.append(f"{s['id']}: claimed {s['expect']}, live {state}")
    total_cost = sum(cost.values())
    report = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "native_calls_24h": sum(calls.values()),
        "native_cost_usd_24h": round(total_cost, 4),
        "surfaces": live,
        "conformance_failures": failures,
    }
    (out_dir / "inventory.json").write_text(json.dumps(report, indent=2) + "\n")
    (out_dir / "inventory.mmd").write_text(mermaid(expected, live))
    rows = [
        "| Surface | How it works | Decision | Claimed | Live | 24h use | Cost / saving | Verdict | Evidence |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in expected["surfaces"]:
        r = live[s["id"]]
        rows.append(
            f"| {s['name']} | {s['how']} | {s['decision']} | {s['expect']} | {r['state']} | {'' if r['usage24h'] is None else r['usage24h']} | {r['detail'] or s['saving']} | {s['verdict']} | {s['evidence']} |"
        )
    (out_dir / "INVENTORY.md").write_text(
        "\n".join(rows)
        + f"\n\nNative Jev: {report['native_calls_24h']:,} calls, ${total_cost:.4f} in the last 24h.\n"
    )
    print(
        f"inventory: {len(live)} surfaces, native {report['native_calls_24h']:,} calls ${total_cost:.4f}/24h, out {out_dir}"
    )
    for f in failures:
        print(f"CONFORMANCE FAIL {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
