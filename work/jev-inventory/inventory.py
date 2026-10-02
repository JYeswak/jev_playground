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
import hashlib
import hmac
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
    "global": "machine-wide shadow screens (5 profiles)",
    "extension": "project extensions",
    "rule": "judged rules",
    "fleet": "fleet",
    "infra": "infrastructure",
}


def global_hook_state(surface: dict, ctx: dict) -> str:
    """A global screen is on only while every profile copy is the repo file.

    Git and most editors replace on write (rename), which breaks the hardlink:
    either a differing inode or a differing sha256 means drift. Both are
    checked so a byte-identical rewrite still fails closed (re-link to fix).
    """
    try:
        repo = ROOT / surface["repo"]
        rstat = repo.stat()
        rhash = hashlib.sha256(repo.read_bytes()).hexdigest()
    except OSError:
        return "off"
    for p in ctx.get("profile_names", []):
        base = HOME / (".omp/agent" if p == "default" else f".omp/profiles/{p}/agent")
        target = base / "hooks" / "post" / surface["hookfile"]
        try:
            tstat = target.stat()
            tbytes = target.read_bytes()
        except OSError:
            return "off"
        if (tstat.st_dev, tstat.st_ino) != (rstat.st_dev, rstat.st_ino):
            return "off"
        if not hmac.compare_digest(hashlib.sha256(tbytes).hexdigest(), rhash):
            return "off"
    return "on"


VERDICT_CLASS = {
    "WORKS": "works",
    "WORKS-NO-BENEFIT-YET": "unproven",
    "UNPROVEN": "unproven",
    "UNMEASURED": "unproven",
    "PARTIAL": "unproven",
    "SHADOW": "unproven",
    "IDLE-BY-DESIGN": "nobenefit",
    "NO-SIGNAL": "nobenefit",
    "NO-BENEFIT": "nobenefit",
    "NO-WIN-EASY": "nobenefit",
    "ENFORCING": "works",
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
        if sid == "websearch-rerank":
            # Factory default OFF since jev-ib1h (VERIFIED+CLOSED): the file
            # exists but subscribes nothing unless enabled, so file presence
            # mis-reports live-on. When enabled it fires on every web_search
            # (fleet volume guarantees rows within minutes); 3h silence = off.
            # Rows re-appear the moment anyone enables it, failing conformance.
            return "on" if sum(log_statuses("websearch-rerank.jsonl", 3).values()) else "off"
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
    if sid in ("webscreen-global", "injection-global"):
        return global_hook_state(surface, ctx)
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
        if s["group"] in ("native", "hook", "global") or s["id"] in ("needs-human",):
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


# Joshua, 2026-10-01: "anything unproven should automatically tell us - hey lets go create proper
# dag tasks and go prove - it blanket approval / requirement to do so". A surface needs proof when
# its verdict is not a measured outcome, or when it is ON and its saving was never measured.
PROVEN_VERDICTS = {
    "WORKS",
    "ENFORCING",
    "NO-SIGNAL",
    "NO-BENEFIT",
    "IDLE-BY-DESIGN",
    "OFF-MISROUTES",
    "REFUTED",
    "LOSES-TO-JEV",
}
UNMEASURED_SAVING = (
    "none measured",
    "not quantified",
    "no token saving measured",
    "logged",
    "not live",
)


def needs_proof(surface: dict) -> str | None:
    """Why this surface still needs a proof task, or None when it has a measured outcome."""
    if surface["expect"] == "off":
        return None
    if surface["verdict"] not in PROVEN_VERDICTS:
        return f"verdict {surface['verdict']} is not a measured outcome"
    saving = surface.get("saving", "").lower()
    if surface["expect"] == "on" and any(mark in saving for mark in UNMEASURED_SAVING):
        return f"ON but its saving is unmeasured ({surface['saving']})"
    return None


def proof_bead_text(surface: dict, why: str) -> tuple[str, str]:
    title = f"Prove {surface['name']}: {surface['decision']}"
    body = (
        f"AUTO-FILED by work/jev-inventory/inventory.py --file-beads ({why}). Standing order (Joshua 2026-10-01): "
        "every unproven surface gets a proof task; blanket approval for bounded live calls.\n"
        f"SURFACE: {surface['id']} - {surface['how']}. Current evidence: {surface['evidence']}.\n"
        "WHAT: produce a measured outcome for this surface on real traffic or a controlled live experiment you build "
        "(fresh omp sessions, real prompts or commands cut from session files). If the data does not exist, create it. "
        "UNMEASURED / NOT_RUN is never an acceptable close.\n"
        "ACCEPTANCE: (1) a bar committed in a bead comment BEFORE outcome data is read; (2) the number with its "
        "denominator and a 95% interval where it is a rate; (3) spend stated; (4) a planted negative; (5) on a FAIL, "
        "LOSS DEPTH (autopsy, 3 one-variable hypotheses, dev replay, one held-out retest) before parking; (6) update "
        "work/jev-inventory/expected.json with the new verdict and re-bless the golden. A non-author verifies and closes.\n"
        "NO-CLAIM: whatever the bar does not cover."
    )
    return title, body


def file_proof_beads(expected: dict, run=subprocess.run) -> list[str]:
    """Create one open proof bead per surface that needs proof and has none open; return created ids."""
    env = dict(os.environ, RUST_LOG="error")
    created = []
    for surface in expected["surfaces"]:
        why = needs_proof(surface)
        if why is None:
            continue
        label = f"prove-{surface['id']}"
        listed = run(
            [
                "br",
                "list",
                "--label",
                label,
                "--status",
                "open",
                "--status",
                "in_progress",
                "--status",
                "blocked",
                "--json",
            ],
            capture_output=True,
            text=True,
            env=env,
            cwd=ROOT,
        )
        try:
            rows = json.loads(listed.stdout or "[]")
        except ValueError:
            rows = None
        if rows is None or listed.returncode != 0:
            print(f"NOT_RUN prove {surface['id']}: br list failed")
            continue
        if rows if isinstance(rows, list) else rows.get("issues", []):
            continue
        title, body = proof_bead_text(surface, why)
        made = run(
            [
                "br",
                "create",
                "--actor",
                "jev-inventory",
                "--title",
                title,
                "--type",
                "task",
                "--priority",
                "1",
                "--labels",
                f"{label},prove,reality-check",
                "--description",
                body,
                "--json",
            ],
            capture_output=True,
            text=True,
            env=env,
            cwd=ROOT,
        )
        try:
            bead = json.loads(made.stdout)
            created.append((bead[0] if isinstance(bead, list) else bead)["id"])
        except (ValueError, KeyError, IndexError):
            print(f"NOT_RUN prove {surface['id']}: br create failed")
    return created


def main(argv: list[str]) -> int:
    expected = load_expected()
    if "--structure" in argv:
        sys.stdout.write(mermaid(expected, None))
        return 0
    if "--file-beads" in argv:
        made = file_proof_beads(expected)
        print(f"proof beads created: {len(made)} {' '.join(made)}")
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
