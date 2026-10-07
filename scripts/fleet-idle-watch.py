#!/usr/bin/env python3
"""Tell pane 1 when a jev worker pane sits idle.

Worker = tmux pane index >= 2 in the jev session (0 is Joshua's shell, 1 is the conductor).
State  = from process evidence first, screen second (bead jev-6con):
           no-agent  the pane's process tree holds no omp process. Screen text never decides this.
           working   the omp status line shows a spinner, OR omp has a live descendant that is not
                     one of its own long-lived helpers (OMP_HELPERS), i.e. a tool call is running,
                     OR a session .jsonl omp holds open was written in the last SESSION_FRESH s.
           stalled-wait  a wait marker, a session idle for IDLE_STALL_S+, and no live non-helper
                     descendant. A child alive at 0% CPU counts as working (bead jev-oxdq: a paced
                     API client sleeps between requests). Known limit: a hung child at 0% CPU is
                     no longer paged; only a wait with nothing left under omp is.
           idle      omp is there and none of the above holds.
         Each state carries the evidence that decided it, e.g. "working (child: docker run ...)".
Route  = a pane idle for POLLS polls gets work before pane 1 hears of it (bead jev-ara9): first an
         in_progress bead labelled needs-verify that its agent did not write (oldest first), else
         the highest-priority unassigned bead in br ready, claimed for the agent with br's atomic
         --claim and --if-unchanged compare-and-set. br's close policy (.beads/policy.yaml) refuses a
         self-close, so a misrouted verification cannot close anything. One routed item per pane
         per ROUTE_COOLDOWN_S; a verification goes to another verifier after VERIFY_REROUTE_S, never
         to the same one twice. Agents are resolved each round from tmux pane ids through Agent
         Mail's per-pane identity bindings (pane_agents), never from a stored name map, so a
         restarted pane is routed under its new name; the router is off (the watcher behaves as
         before) while no pane has a binding or while ~/.local/state/jev/fleet-router.off exists.
         Why: 2026-10-02 panes sat idle ~7 h (07:54-15:01Z) waiting on manual dispatch.
Alert  = after POLLS idle polls, page pane 1 only when no route was accepted. If pane 1 has a
         spinner in its last four lines, queue via literal `tmux send-keys -l` then `C-q`, never
         Enter. Busy pages coalesce and flush at most once per 600 s; when idle use `ntm send`.
         Re-alert gaps still double from REALERT to REALERT_MAX (measured 2026-10-01: a fixed
         600 s re-page sent pane 1 300 pages for 56 idle episodes).
Mail   = every round, each urgent/high Agent Mail message in the conductor's archive inbox that
         was never paged goes to pane 1 once as `MAIL <importance> from <from>: <subject> (id <id>,
         <HH:MM>Z)` (bead jev-lqfm). Paged ids persist in JEV_WATCH_INBOX_STATE, so a restart
         does not re-page; with no state file, mail created before start - 15 min is history,
         recorded and never paged. One `Inbox:` line per round; `Inbox: NOT_RUN <reason>` when
         the inbox or the state file cannot be read. Why: 2026-09-25 an urgent key-leak report
         to AmberWillow sat unread 42 minutes, because pane 1 does not poll Agent Mail.
Key    = every round, the census's `Key exposure 24h:` line (surface-census.py --fleet-line) is
         printed, and each session file it names as holding a TypeSafe-shaped key goes to pane 1
         once as `KEY EXPOSURE: <path> holds a TypeSafe-shaped key (modified <HH:MM>Z); ...`
         (bead jev-9ov4). Paged paths persist in JEV_WATCH_KEY_STATE, so a restart does not
         re-page; a first run pages every named path. Paths only, never the key. Why: 2026-09-25
         05:57Z a pane printed the live key into a tool result and nobody saw it for 50 minutes.
Stranger = every round, the `README stranger nightly:` lines from ci-main-status.py are printed,
         and each new failed or stale failed run goes to pane 1 once as `README STRANGER FAILURE: ...`.
         Paged run ids persist in JEV_WATCH_STRANGER_STATE, so a restart does not re-page the same run.
         Why: 2026-09-25 the README nightly gate failed twice before its green dispatch was visible.

Why: 2026-09-24, 4 of 6 worker panes sat at their prompts for most of an hour and the
conductor only looked when a callback arrived. Joshua: "dont let that happen again."
Why process evidence: 2026-09-25 the screen-only reading said panes 2 and 5 were 'no-agent'
while each had omp mid-task (a diff view or todo panel hid the status line), and said pane 2
was 'idle' while its omp had a docker run live under a bash tool call.

  python3 scripts/fleet-idle-watch.py            # run forever (start it under hub)
  python3 scripts/fleet-idle-watch.py --once     # one poll, then the CI-on-main line from
                                                 # scripts/ci-main-status.py, the Jev judge
                                                 # line from surface-census.py --fleet-line
                                                 # (both informational) and one mail round;
                                                 # exit 1 if any worker is not working; 2 if ps is NOT_RUN
  python3 scripts/fleet-idle-watch.py --selftest # classifier on real status lines and trees
  python3 scripts/fleet-idle-watch.py --route-plan  # what the router would send idle panes now;
                                                 # reads br and tmux only, writes nothing
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
from calendar import timegm
from pathlib import Path
from typing import NamedTuple

WATCHER_DIR = str(Path(__file__).resolve().parent)
if WATCHER_DIR not in sys.path:
    sys.path.insert(0, WATCHER_DIR)

import fleet_surface_heartbeat as surface_heartbeat  # noqa: E402

SESSION = os.environ.get("JEV_SESSION", "jev")
# A pane status line can contain private session state. The env flag alone is
# not owner approval for TypeSafe export; keep background scoring disabled.
SHADOW_ENABLED = False
SHADOW_ONLY = os.environ.get("JEV_FLEET_SHADOW_ONLY") == "1"
SURFACE_OBSERVE_ONLY = os.environ.get("JEV_FLEET_SURFACE_OBSERVE_ONLY") == "1"
SHADOW_MAX_INFLIGHT = int(os.environ.get("JEV_FLEET_SHADOW_MAX_INFLIGHT", "16"))
SHADOW_LOG = Path(
    os.environ.get("JEV_FLEET_SHADOW_LOG", "~/.local/state/jev/fleet-jev-shadow.jsonl")
).expanduser()
SHADOW_HELPER = Path(__file__).with_name("fleet-jev-shadow.mjs")
INTERVAL = int(os.environ.get("IDLE_INTERVAL", "60"))
POLLS = int(os.environ.get("IDLE_POLLS", "2"))
REALERT = int(os.environ.get("IDLE_REALERT", "600"))
REALERT_MAX = int(os.environ.get("IDLE_REALERT_MAX", "7200"))
HOOK_LOAD_INTERVAL = 600
HEARTBEAT_INTERVAL = 3600
SURFACE_REGISTRY = Path(
    os.environ.get(
        "JEV_SURFACE_REGISTRY",
        str(Path(__file__).resolve().parents[1] / "work/blast-radius/surfaces.json"),
    )
).expanduser()


SPINNER = re.compile(r"^\s*[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]")
WAIT_MARKER = re.compile(
    r"(?:^\s*[⌛⏳]|^\s*Wait\b|\bwaiting on \d+ jobs?\b)",
    re.I | re.M,
)
# Comma list of pane indexes to watch; empty = every worker (index >= 2). Set it when some panes
# are down for a known reason (2026-09-24: the five Muse panes hit a quota that resets 09-28).
WATCH = {
    int(p)
    for p in os.environ.get("JEV_WATCH_PANES", "").split(",")
    if p.strip().isdigit()
}
STATUS = re.compile(r"[◒◕]")  # the omp status line carries the model marker
# An omp main process: `omp ...`, `bun /…/bin/omp ...`, or bun running the package's cli.js.
OMP = re.compile(r"(^|[\s/])omp(\s|$)|pi-coding-agent/dist/cli\.js(?!\s+__omp_worker_)")
# omp's own long-lived children, present under every live omp whether or not it is mid-task
# (ps under jev panes 1-5, 2026-09-25). A match is not tool work, but its descendants are still
# walked: a subprocess started from the python or js eval kernel is a running tool.
# MCP and language servers match by generic name markers, not by server name: a named list went
# stale the day the math MCPs were installed (2026-10-05: infisical, mathlas, z3, sympy, wolfram
# and vscode-json servers made every pane read 'working', so no idle alert or steering nudge fired).
# Tradeoff: a tool call whose command line itself carries one of these markers reads as a helper.
OMP_HELPERS = (
    "__omp_worker_",  # cli.js __omp_worker_{mnemopi_embed,js_eval_process,daemon_broker}
    "/omp-python-runner/",  # python eval kernel: Python -u $TMPDIR/omp-python-runner/runner-*.py
    "@morphllm/morphmcp",  # MCP server morph: npm exec @morphllm/morphmcp
    "franken-harvest serve",  # MCP server franken-harvest
    # MCP servers: @infisical/mcp/dist, mcp-z3-prover, sympy-mcp / mcp[cli] / server.mcp.run(),
    # mathlas-mcp, wolfram_llm_mcp.py, morph-mcp
    "/mcp/",
    "mcp-",
    "-mcp",
    "_mcp",
    "mcp[cli]",
    ".mcp.run(",
    # language servers: typescript-, vscode-json-language-server, pyright-langserver, ...
    "language-server",
    "langserver",
    "rust-analyzer",
    "gopls",
    "marksman server",  # markdown language server (pane 6, 2026-10-05T16:15Z)
    # a zombie (ps shows "<defunct>") is no work in progress (pane 5, 2026-10-05T16:15Z)
    "<defunct>",
)
SESSION_FRESH = int(os.environ.get("IDLE_SESSION_FRESH", "60"))
IDLE_STALL_S = int(os.environ.get("IDLE_STALL_S", "600"))
# Agent Mail paging (bead jev-lqfm). Paths are read from the env each round, not at import, so a
# test that points HOME or these at a temp tree never reads or writes the real ones.
INBOX_ROOT = (
    "~/.local/share/mcp-agent-mail-rust-live/projects/users-josh-developer-jev/agents"
)
INBOX_STATE = "~/.local/state/jev/inbox-paged.json"
PAGE_IMPORTANCE = ("urgent", "high")
INBOX_LOOKBACK = (
    15 * 60
)  # with no state file, mail created before start - this is history
# Agent Mail's canonical per-pane identity bindings; the watcher resolves names from pane ids here.
IDENTITY_ROOT = "~/.config/agent-mail/identity"
CONDUCTOR_PANE = 1
CREATED = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?(Z|\+00:00)$")
# Key exposure paging (bead jev-9ov4): the census's `Key exposure 24h:` line names up to 3 session
# files holding a TypeSafe-shaped key; each path is paged once, persisted like the inbox ids.
KEY_STATE = "~/.local/state/jev/key-exposure-paged.json"
STRANGER_STATE = "~/.local/state/jev/stranger-paged.json"
STRANGER_LINE = "README stranger nightly: "
STRANGER_FAILURE = re.compile(
    r"^README stranger nightly: (?:STALE )?failure (\d+) (.+)$"
)

KEY_LINE = "Key exposure 24h: "
KEY_COUNT = re.compile(r"^Key exposure 24h: (\d+) session files hold")
KEY_PATH = re.compile(r"(.+?\.jsonl) \((\d\d:\d\d)Z\)(?:, |$)")


NEEDS_HUMAN_THRESHOLD = float(os.environ.get("JEV_NEEDS_HUMAN_THRESHOLD", "0.7"))
NEEDS_HUMAN_DAILY_CAP = int(os.environ.get("JEV_NEEDS_HUMAN_DAILY_CAP", "20"))
NEEDS_HUMAN_HELPER = Path(__file__).with_name("fleet-needs-human.mjs")
NEEDS_HUMAN_MODEL = "jev-1.13.0"
NEEDS_HUMAN_CALL_LOG = "~/.local/state/jev/fleet-needs-human-calls.jsonl"
NEEDS_HUMAN_PAGED_STATE = "~/.local/state/jev/needs-human-paged.json"
NEEDS_HUMAN_DAY_STATE = "~/.local/state/jev/needs-human-day.json"
NEEDS_HUMAN_TAIL_BYTES = 2_000_000
NEEDS_HUMAN_MAX_CHARS = 2000
KEY_SHAPE = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{16,}|apikey_[A-Za-z0-9_-]{20,}|Bearer\s+\S{20,})", re.I
)


class Snapshot(NamedTuple):
    """What one poll saw of one pane; classify() reads nothing else, so tests need no tmux."""

    command: str  # tmux pane_current_command
    screen: str  # tmux capture-pane text
    omp: bool  # an omp process is in the pane's process tree
    tools: tuple[str, ...] = ()  # non-helper descendants of omp, preorder
    cpu_tools: tuple[str, ...] = ()  # non-helper descendants with ps %CPU > 0
    session_age: float | None = (
        None  # seconds since omp's open session .jsonl was written
    )


def short(command: str, width: int = 90) -> str:
    """argv0 cut to its basename, the whole thing cut to width."""
    head, _, rest = command.partition(" ")
    text = f"{os.path.basename(head)} {rest}".strip()
    return text if len(text) <= width else text[: width - 3] + "..."


def classify(snap: Snapshot) -> tuple[str, str]:
    """(working | stalled-wait | idle | no-agent, the deciding evidence)."""
    if not snap.omp:
        return (
            "no-agent",
            f"no omp in the pane's process tree; foreground {snap.command}",
        )
    wait = WAIT_MARKER.search(snap.screen)
    if wait:
        if snap.cpu_tools:
            more = (
                f" (+{len(snap.cpu_tools) - 1} more)" if len(snap.cpu_tools) > 1 else ""
            )
            return (
                "working",
                f"wait marker, child using CPU: {short(snap.cpu_tools[-1])}{more}",
            )
        if snap.tools:
            return (
                "working",
                f"wait marker, child alive, idle CPU: {short(snap.tools[-1])}",
            )
        if snap.session_age is not None and snap.session_age < IDLE_STALL_S:
            return (
                "working",
                f"wait marker, session written {snap.session_age:.0f}s ago",
            )
        if snap.session_age is not None:
            return (
                "stalled-wait",
                f"wait marker, session idle {snap.session_age:.0f}s, no live child",
            )
    lines = [line for line in snap.screen.splitlines() if STATUS.search(line)]
    if lines and SPINNER.match(lines[-1]):
        return "working", "spinner on the status line"
    if snap.tools:
        more = f" (+{len(snap.tools) - 1} more)" if len(snap.tools) > 1 else ""
        return "working", f"child: {short(snap.tools[-1])}{more}"
    if snap.session_age is not None and snap.session_age < SESSION_FRESH:
        return "working", f"session written {snap.session_age:.0f}s ago"
    seen = "no status line on screen" if not lines else "no spinner"
    age = (
        "no open session file"
        if snap.session_age is None
        else f"session written {snap.session_age:.0f}s ago"
    )
    return "idle", f"{seen}, no tool child, {age}"


def composer_text(screen: str) -> str:
    """Text typed but unsent in the composer box open at the screen bottom.

    A composer is a ╭…╮/╰…╯ box whose ╰ sits within the last 6 screen lines,
    whose nearest ╭ above is within 40 lines, and whose every interior line
    is bordered or blank. Anything else (stale transcript boxes mid-screen,
    a dangling ╰ under borderless transcript like pane 2's right-aligned
    session title at 08:58Z, the ❯ prompt form whose echoes are
    indistinguishable from unsent text) reads as "".
    """
    lines = screen.splitlines()
    if not lines:
        return ""
    closers = [i for i, line in enumerate(lines) if "╰" in line]
    bottom = [i for i in closers if i >= len(lines) - 6]
    if not bottom:
        return ""
    close = bottom[-1]
    top = None
    for i in range(close - 1, max(-1, close - 40), -1):
        if "╭" in lines[i]:
            top = i
            break
    if top is None:
        return ""
    parts = []
    for line in lines[top + 1 : close]:
        cell = line.strip()
        if not cell:
            continue
        if not cell.startswith("│"):
            return ""
        cell = cell[1:]
        if cell.endswith("│"):
            cell = cell[:-1]
        cell = cell.strip(" ─")
        if cell:
            parts.append(cell)
    return " ".join(parts)[:500]


STEERING = re.compile(r"^\s*Steering · (\d+)\s*$")


def steering_text(screen: str) -> str:
    """First queued steering message near the screen bottom, or "" (bead jev-of3b).

    omp shows "Steering · N" then "1. <text>" when a message waits for the next turn; an idle
    pane never takes that turn by itself (pane 4, 2026-10-03 11:18Z and 11:25Z).
    """
    lines = screen.splitlines()[-15:]
    for i, line in enumerate(lines):
        if STEERING.match(line):
            for nxt in lines[i + 1 : i + 3]:
                cell = nxt.strip()
                if cell[:2].rstrip(".").isdigit() or cell.startswith("1."):
                    return cell.split(".", 1)[-1].strip()[:200]
            return "queued"
    return ""


def steering_due(state, index, text, composer, done) -> bool:
    """Nudge once per queued message, only from an idle empty-composer snapshot."""
    return (
        state == "idle"
        and not composer
        and bool(text)
        and (index, text) not in done
    )


def nudge_steering(
    index: int, *, state: str, composer: str, queued_steer: str
) -> bool:
    """Start queued steering only after a fresh idle, empty-composer snapshot."""
    if state != "idle" or composer or not queued_steer:
        return False
    states = poll()
    reading = states.get(index) if states is not None else None
    if reading is None or len(reading) < 6:
        return False
    fresh_state, _, _, _, fresh_composer, fresh_steer = reading[:6]
    if (
        fresh_state != "idle"
        or fresh_composer
        or fresh_steer != queued_steer
    ):
        return False
    target = f"{SESSION}:0.{index}"
    try:
        typed = subprocess.run(
            ["tmux", "send-keys", "-l", "-t", target, "."],
            capture_output=True,
            timeout=10,
        )
        if typed.returncode != 0:
            return False
        return submit_enter(index)
    except (OSError, subprocess.TimeoutExpired):
        return False


def unsubmitted_ready(state, index, composer, last_text, same_count, done):
    """(submit_now, new_same_count) for one idle poll of one pane.

    The same non-empty composer on 2 consecutive idle polls submits once per
    (pane, text): a stuck paste is static across polls, active typing is not.
    """
    if state != "idle" or not composer:
        return False, 0
    same = same_count + 1 if composer == last_text else 1
    if same >= 2 and (index, composer) not in done:
        return True, same
    return False, same


def last_words(screen: str) -> str:
    stripped = [
        line.strip(" │╰╭─") for line in screen.splitlines() if not STATUS.search(line)
    ]
    keep = [line for line in stripped if line]
    return keep[-1][:140] if keep else ""


def parse_ps(text: str) -> dict[int, tuple]:
    """`ps -axo pid=,ppid=,pcpu=,command=` → {pid: (ppid, cpu, command)}."""
    table = {}
    for row in text.splitlines():
        parts = row.split(None, 3)
        if len(parts) == 4 and parts[0].isdigit() and parts[1].isdigit():
            try:
                cpu = float(parts[2])
            except ValueError:
                table[int(parts[0])] = (int(parts[1]), 0.0, f"{parts[2]} {parts[3]}")
            else:
                table[int(parts[0])] = (int(parts[1]), cpu, parts[3])
        elif len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            table[int(parts[0])] = (int(parts[1]), 0.0, parts[2])
    return table


def _parent_command(row: tuple) -> tuple[int, str]:
    return int(row[0]), str(row[-1])


def _cpu(row: tuple) -> float:
    try:
        return float(row[1]) if len(row) >= 3 else 0.0
    except (TypeError, ValueError):
        return 0.0


def _process_children(table: dict[int, tuple]) -> dict[int, list[int]]:
    children: dict[int, list[int]] = {}
    for pid, row in table.items():
        ppid, _ = _parent_command(row)
        children.setdefault(ppid, []).append(pid)
    return children


def _find_omp(
    table: dict[int, tuple], pane_pid: int, children: dict[int, list[int]]
) -> int | None:
    queue = [pane_pid]
    while queue:
        pid = queue.pop(0)
        if pid in table and OMP.search(_parent_command(table[pid])[1]):
            return pid
        queue.extend(sorted(children.get(pid, [])))
    return None


def omp_processes(
    table: dict[int, tuple], pane_pid: int
) -> tuple[int | None, list[str]]:
    """(the first omp pid at or under pane_pid, all non-helper descendants)."""
    children = _process_children(table)
    omp = _find_omp(table, pane_pid, children)
    if omp is None:
        return None, []
    tools = []
    stack = sorted(children.get(omp, []), reverse=True)
    while stack:
        pid = stack.pop()
        command = _parent_command(table[pid])[1]
        if not any(helper in command for helper in OMP_HELPERS):
            tools.append(command)
        stack.extend(sorted(children.get(pid, []), reverse=True))
    return omp, tools


def omp_cpu_tools(table: dict[int, tuple], pane_pid: int) -> list[str]:
    """Return non-helper omp descendants whose ps %CPU is positive."""
    children = _process_children(table)
    omp = _find_omp(table, pane_pid, children)
    if omp is None:
        return []
    tools = []
    stack = sorted(children.get(omp, []), reverse=True)
    while stack:
        pid = stack.pop()
        command = _parent_command(table[pid])[1]
        if (
            not any(helper in command for helper in OMP_HELPERS)
            and _cpu(table[pid]) > 0
        ):
            tools.append(command)
        stack.extend(sorted(children.get(pid, []), reverse=True))
    return tools


def session_age(omp_pid: int, now: float) -> float | None:
    """Seconds since the newest session .jsonl omp_pid holds open; None if none."""
    try:
        out = subprocess.run(
            ["lsof", "-p", str(omp_pid), "-Fn"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except OSError:
        return None
    mtimes = []
    for line in out.splitlines():
        if line.startswith("n") and line.endswith(".jsonl"):
            try:
                mtimes.append(os.stat(line[1:]).st_mtime)
            except OSError:
                pass
    return max(0.0, now - max(mtimes)) if mtimes else None


def newest_session_file(omp_pid: int):
    """Newest session .jsonl omp_pid holds open, or None. Metadata only; never reads text."""
    try:
        out = subprocess.run(
            ["lsof", "-p", str(omp_pid), "-Fn"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    best = None
    for line in out.splitlines():
        if not line.startswith("n") or not line.endswith(".jsonl"):
            continue
        path = Path(line[1:])
        try:
            if "sessions" not in path.parts or not path.is_file():
                continue
            mtime = path.stat().st_mtime_ns
        except OSError:
            continue
        if best is None or mtime > best[0]:
            best = (mtime, path)
    return best[1] if best else None


def assistant_text_of(row) -> str:
    """Visible assistant text of one session row; toolCall/thinking-only rows yield ''."""
    message = (
        row.get("message")
        if isinstance(row, dict) and isinstance(row.get("message"), dict)
        else row
    )
    if not isinstance(message, dict) or message.get("role") != "assistant":
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "text"
                and isinstance(block.get("text"), str)
            ):
                parts.append(block["text"])
        return "".join(parts).strip()
    return ""


def last_assistant_message(path: Path, tail_bytes: int = NEEDS_HUMAN_TAIL_BYTES):
    """Newest non-empty assistant text with stopReason stop (or unset). Returns dict or None."""
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            handle.seek(max(0, size - tail_bytes))
            lines = handle.read().splitlines()
        total = None
        try:
            with path.open("rb") as handle:
                total = sum(1 for _ in handle)
        except OSError:
            total = None
        offset = (total - len(lines)) if total is not None else None
    except OSError:
        return None
    for reverse_index, line in enumerate(reversed(lines)):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        text = assistant_text_of(row)
        if not text:
            continue
        message = (
            row.get("message")
            if isinstance(row, dict) and isinstance(row.get("message"), dict)
            else row
        )
        stop = message.get("stopReason") if isinstance(message, dict) else None
        if stop is not None and stop != "stop":
            continue
        line_no = (offset + len(lines) - reverse_index) if offset is not None else None
        return {
            "text": text,
            "line": line_no,
            "row_id": row.get("id"),
            "timestamp": message.get("timestamp")
            if isinstance(message, dict)
            else None,
        }
    return None


def needs_human_paths():
    """(paged state, day state, call log) honoring test overrides; real paths by default."""
    paged = Path(
        os.environ.get("JEV_WATCH_NEEDS_HUMAN_PAGED") or NEEDS_HUMAN_PAGED_STATE
    ).expanduser()
    day = Path(
        os.environ.get("JEV_WATCH_NEEDS_HUMAN_DAY") or NEEDS_HUMAN_DAY_STATE
    ).expanduser()
    log = Path(
        os.environ.get("JEV_WATCH_NEEDS_HUMAN_LOG") or NEEDS_HUMAN_CALL_LOG
    ).expanduser()
    return paged, day, log


def load_needs_human_marks(paged: Path) -> set:
    try:
        saved = json.loads(paged.read_text()) if paged.exists() else {}
        return set(saved.get("paged", []))
    except (OSError, ValueError, AttributeError):
        return set()


def save_needs_human_marks(paged: Path, marks: set) -> None:
    try:
        paged.parent.mkdir(parents=True, exist_ok=True)
        tmp = paged.with_name(f"{paged.name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps({"paged": sorted(marks)}) + "\n")
        os.replace(tmp, paged)
    except OSError:
        pass


def load_needs_human_day(day: Path):
    today = time.strftime("%Y-%m-%d", time.gmtime())
    try:
        saved = json.loads(day.read_text()) if day.exists() else {}
    except (OSError, ValueError, AttributeError):
        saved = {}
    if saved.get("date") != today:
        return {"date": today, "count": 0, "auth_stop": False}
    return {
        "date": today,
        "count": int(saved.get("count", 0)),
        "auth_stop": bool(saved.get("auth_stop", False)),
    }


def save_needs_human_day(day: Path, state: dict) -> None:
    try:
        day.parent.mkdir(parents=True, exist_ok=True)
        tmp = day.with_name(f"{day.name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps(state) + "\n")
        os.replace(tmp, day)
    except OSError:
        pass


def ask_needs_human(text: str, timeout: int = 25):
    """Call the bounded node helper once. Never raises; failures are data."""
    try:
        done = subprocess.run(
            ["node", "--experimental-strip-types", str(NEEDS_HUMAN_HELPER)],
            input=(json.dumps({"message": text}) + "\n"),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as err:
        return {
            "ok": False,
            "reason": "transport",
            "error": f"helper {type(err).__name__}",
            "model": NEEDS_HUMAN_MODEL,
            "latencyMs": 0,
        }
    try:
        return json.loads(done.stdout or "{}")
    except ValueError:
        return {
            "ok": False,
            "reason": "non-json",
            "error": (done.stderr or "")[:200] or "helper printed no JSON",
            "model": NEEDS_HUMAN_MODEL,
            "latencyMs": 0,
        }


def append_needs_human_call(log: Path, row: dict) -> None:
    try:
        log.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a") as handle:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    except OSError:
        pass


def check_idle_needs_human(
    index: int,
    omp_pid: int,
    now: float,
    send=None,
    asker=ask_needs_human,
    session_file=None,
    cap: int = NEEDS_HUMAN_DAILY_CAP,
    threshold: float = NEEDS_HUMAN_THRESHOLD,
) -> bool:
    """Page pane 1 when an idle pane's last session message waits on a human. True when paged."""
    if send is None:
        send = page
    paged_path, day_path, log_path = needs_human_paths()
    marks = load_needs_human_marks(paged_path)
    day = load_needs_human_day(day_path)
    if day.get("auth_stop"):
        return False
    if day.get("count", 0) >= cap:
        return False
    path = session_file or newest_session_file(omp_pid)
    if path is None:
        return False
    found = last_assistant_message(path)
    if not found or not found.get("text"):
        return False
    text = found["text"]
    if KEY_SHAPE.search(text):
        return False
    if len(text) > NEEDS_HUMAN_MAX_CHARS:
        text = text[:NEEDS_HUMAN_MAX_CHARS]
    import hashlib as _hashlib

    mark = f"{index}:{_hashlib.sha256(text.encode()).hexdigest()[:16]}"
    if mark in marks:
        return False
    result = asker(text)
    day["count"] = day.get("count", 0) + 1
    status = "ok" if result.get("ok") else str(result.get("reason", "unknown"))
    if (
        not result.get("ok")
        and result.get("reason") == "http"
        and re.search(r"\b401\b|\b402\b|\b403\b", str(result.get("error", "")))
    ):
        day["auth_stop"] = True
    save_needs_human_day(day_path, day)
    append_needs_human_call(
        log_path,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "pane": index,
            "mark": mark,
            "status": status,
            "score": result.get("score") if result.get("ok") else None,
            "model": result.get("model", NEEDS_HUMAN_MODEL),
            "input_tokens": (result.get("usage") or {}).get("input_tokens")
            if isinstance(result.get("usage"), dict)
            else None,
            "output_tokens": (result.get("usage") or {}).get("output_tokens")
            if isinstance(result.get("usage"), dict)
            else None,
            "latencyMs": result.get("latencyMs", 0),
            "chars": len(text),
        },
    )
    marks.add(mark)
    save_needs_human_marks(paged_path, marks)
    if (
        result.get("ok")
        and isinstance(result.get("score"), (int, float))
        and result["score"] >= threshold
    ):
        one_line = " ".join(text.split()).strip()
        if len(one_line) > 140:
            one_line = one_line[:137] + "..."
        send(f"NEEDS-HUMAN pane {index}: {one_line}")
        return True
    return False


def shadow_features(words: str) -> list[str]:
    """Reduce watcher evidence to safe categorical features; never send screen text."""
    low = words.lower()
    features: list[str] = []
    if "no omp in" in low:
        features.append("omp_absent")
    if "wait marker" in low:
        features.append("wait_marker")
    if "spinner on the status line" in low:
        features.append("spinner")
    if "child using cpu" in low:
        features.append("child_cpu")
    elif "child alive" in low or "child:" in low:
        features.append("child_alive")
    if "session written" in low:
        features.append("session_fresh_or_stale")
    if "no tool child" in low:
        features.append("no_tool_child")
    return features or ["unclassified_evidence"]


def redacted_status_line(screen: str) -> str:
    """Keep only the status line, with path and prompt text replaced before Jev sees it."""
    lines = [line.strip() for line in screen.splitlines() if STATUS.search(line)]
    if not lines:
        return ""
    line = lines[-1]
    line = re.sub(r"📁[^│·]+", "📁[path]", line)
    line = re.sub(r"❯.*$", "❯[prompt]", line)
    return line[:200]


class ShadowDispatcher:
    def __init__(self) -> None:
        self.children: list[tuple[subprocess.Popen, io.BufferedWriter]] = []

    def reap(self) -> None:
        live = []
        for child, stream in self.children:
            if child.poll() is None:
                live.append((child, stream))
            else:
                child.wait()
                stream.close()
        self.children = live

    def submit(self, payload: dict) -> None:
        if not SHADOW_ENABLED:
            return
        self.reap()
        if len(self.children) >= SHADOW_MAX_INFLIGHT:
            return
        stream = None
        try:
            SHADOW_LOG.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd = os.open(SHADOW_LOG, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            stream = os.fdopen(fd, "wb")
            child = subprocess.Popen(
                ["node", "--experimental-strip-types", str(SHADOW_HELPER)],
                stdin=subprocess.PIPE,
                stdout=stream,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            assert child.stdin is not None
            child.stdin.write(
                (json.dumps(payload, separators=(",", ":")) + "\n").encode()
            )
            child.stdin.close()
            self.children.append((child, stream))
        except (OSError, BrokenPipeError):
            if stream is not None:
                stream.close()


SHADOW_DISPATCHER = ShadowDispatcher()


def submit_shadow(states: dict[int, tuple[str, str, str]]) -> None:
    if not SHADOW_ENABLED:
        return
    worker_count = len(states)
    for pane_index, reading in states.items():
        incumbent, evidence = reading[:2]
        status_line = reading[2] if len(reading) > 2 else ""
        SHADOW_DISPATCHER.submit(
            {
                "pane_index": pane_index,
                "worker_panes": worker_count,
                "incumbent": incumbent,
                "evidence_features": shadow_features(evidence),
                "status_line": status_line,
            }
        )


def poll() -> dict[int, tuple] | None:
    """Read one complete pane snapshot, or return None if any process probe times out."""
    try:
        out = subprocess.run(
            [
                "tmux",
                "list-panes",
                "-t",
                SESSION,
                "-F",
                "#{pane_index} #{pane_pid} #{pane_current_command}",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except subprocess.TimeoutExpired:
        print(
            "NOT_RUN fleet-idle-watch poll: tmux list-panes timed out after 10s",
            flush=True,
        )
        return None
    try:
        processes = subprocess.run(
            ["ps", "-axo", "pid=,ppid=,pcpu=,command="],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        print("NOT_RUN fleet-idle-watch poll: ps timed out after 10s", flush=True)
        return None
    table = parse_ps(processes.stdout)
    states = {}
    for row in out.splitlines():
        index, pane_pid, command = (row.split(" ", 2) + ["", ""])[:3]
        if not index.isdigit() or int(index) < 2 or (WATCH and int(index) not in WATCH):
            continue
        try:
            screen = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", f"{SESSION}:0.{index}"],
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout
        except subprocess.TimeoutExpired:
            print(
                f"NOT_RUN fleet-idle-watch poll: tmux capture-pane pane {index} timed out after 10s",
                flush=True,
            )
            return None
        omp, tools = (
            omp_processes(table, int(pane_pid)) if pane_pid.isdigit() else (None, [])
        )
        cpu_tools = omp_cpu_tools(table, int(pane_pid)) if pane_pid.isdigit() else []
        try:
            age = session_age(omp, time.time()) if omp is not None else None
        except subprocess.TimeoutExpired:
            print(
                "NOT_RUN fleet-idle-watch poll: lsof session probe timed out after 10s",
                flush=True,
            )
            return None
        snap = Snapshot(
            command=command,
            screen=screen,
            omp=omp is not None,
            tools=tuple(tools),
            cpu_tools=tuple(cpu_tools),
            session_age=age,
        )
        state, evidence = classify(snap)
        states[int(index)] = (
            state,
            f"({evidence})  {last_words(screen)}",
            redacted_status_line(screen),
            omp,
            composer_text(screen),
            steering_text(screen),
        )
    return states


def submit_enter(index: int) -> bool:
    """Press Enter in the pane's composer once; True only when tmux took it."""
    try:
        done = subprocess.run(
            ["tmux", "send-keys", "-t", f"{SESSION}:0.{index}", "Enter"],
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return done.returncode == 0


PAGE_BATCH_INTERVAL = 600.0
PAGE_BUSY_LAST_SENT: float | None = None
PAGE_BUSY_PENDING: list[str] = []
PAGE_SEND_ACTION = "sent"


def _capture_pane1_screen() -> str | None:
    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", f"{SESSION}:0.1"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def _pane1_is_busy(screen: str) -> bool:
    # OMP's status bar includes a border before the spinner; strip it before matching.
    return any(SPINNER.match(line.lstrip("╭─ ")) for line in screen.splitlines()[-4:])


def _combine_page_messages(messages: list[str]) -> str:
    return "; ".join(dict.fromkeys(message for message in messages if message))


def _send_busy_page1(message: str) -> bool:
    """Queue literal text in pane 1 without submitting or interrupting its active turn."""
    target = f"{SESSION}:0.1"
    try:
        typed = subprocess.run(
            ["tmux", "send-keys", "-l", "-t", target, message],
            capture_output=True,
            timeout=10,
        )
        if typed.returncode != 0:
            return False
        queued = subprocess.run(
            ["tmux", "send-keys", "-t", target, "C-q"],
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return queued.returncode == 0


def _send_idle_page1(message: str) -> bool:
    try:
        done = subprocess.run(
            ["ntm", "send", SESSION, "--pane=1", message],
            capture_output=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return done.returncode == 0


def send_pane1(message: str) -> bool:
    """Send when pane 1 is idle; queue/coalesce without Enter while its spinner is visible."""
    global PAGE_BUSY_LAST_SENT, PAGE_SEND_ACTION
    if surface_heartbeat.record_dry_run_send(message, pane=1):
        PAGE_SEND_ACTION = "dry-run"
        return True
    screen = _capture_pane1_screen()
    if screen is None:
        PAGE_SEND_ACTION = "failed"
        return False
    busy = _pane1_is_busy(screen)
    now = time.monotonic()
    messages = [*PAGE_BUSY_PENDING, message]
    payload = _combine_page_messages(messages)
    if (
        busy
        and PAGE_BUSY_LAST_SENT is not None
        and now - PAGE_BUSY_LAST_SENT < PAGE_BATCH_INTERVAL
    ):
        if message and message not in PAGE_BUSY_PENDING:
            PAGE_BUSY_PENDING.append(message)
        PAGE_SEND_ACTION = "batched"
        return True
    sent = _send_busy_page1(payload) if busy else _send_idle_page1(payload)
    if not sent:
        # A failed send may have typed part of the payload into the composer.
        # Do not retry it automatically: that could duplicate or submit stale text.
        PAGE_BUSY_PENDING.clear()
        PAGE_SEND_ACTION = "failed"
        return False
    PAGE_BUSY_PENDING.clear()
    PAGE_BUSY_LAST_SENT = now if busy else None
    PAGE_SEND_ACTION = "queued" if busy else "sent"
    return True


def flush_pending_page1(now: float | None = None) -> bool:
    """Deliver a coalesced busy-pane batch after its ten-minute cooldown."""
    global PAGE_BUSY_LAST_SENT, PAGE_SEND_ACTION
    if not PAGE_BUSY_PENDING or PAGE_BUSY_LAST_SENT is None:
        return False
    now = time.monotonic() if now is None else now
    if now - PAGE_BUSY_LAST_SENT < PAGE_BATCH_INTERVAL:
        return False
    screen = _capture_pane1_screen()
    if screen is None:
        PAGE_SEND_ACTION = "failed"
        return False
    payload = _combine_page_messages(PAGE_BUSY_PENDING)
    busy = _pane1_is_busy(screen)
    sent = _send_busy_page1(payload) if busy else _send_idle_page1(payload)
    if not sent:
        # The batch may already be in the composer; retrying could duplicate it.
        PAGE_BUSY_PENDING.clear()
        PAGE_BUSY_LAST_SENT = None
        PAGE_SEND_ACTION = "failed"
        return False
    PAGE_BUSY_PENDING.clear()
    PAGE_BUSY_LAST_SENT = now if busy else None
    PAGE_SEND_ACTION = "queued" if busy else "sent"
    return True


def realert_due(now: float, last: float | None, count: int) -> bool:
    """First page of an idle episode is due at once; each re-page waits twice as long as the last."""
    if last is None:
        return True
    return now - last >= min(REALERT * (2 ** max(count - 1, 0)), REALERT_MAX)


def alert(index: int, since: float, words: str) -> None:
    stamp = time.strftime("%H:%MZ", time.gmtime(since))
    message = f"IDLE pane {index} (since {stamp}), last line: {words}"
    ok = send_pane1(message)
    if surface_heartbeat.DRY_RUN and ok:
        result = "would alert"
    elif not ok:
        result = "alert FAILED"
    elif PAGE_SEND_ACTION == "batched":
        result = "batched"
    elif PAGE_SEND_ACTION == "queued":
        result = "queued"
    else:
        result = "alerted"
    print(
        f"{time.strftime('%H:%M:%SZ', time.gmtime())} {result}: {message}", flush=True
    )


def page(message: str) -> bool:
    """Page pane 1, or record the attempt in dry-run mode."""
    ok = send_pane1(message)
    if surface_heartbeat.DRY_RUN and ok:
        said = "would page"
    elif not ok:
        said = "page FAILED"
    elif PAGE_SEND_ACTION == "batched":
        said = "page batched"
    elif PAGE_SEND_ACTION == "queued":
        said = "page queued"
    else:
        said = "paged"
    print(f"{time.strftime('%H:%M:%SZ', time.gmtime())} {said}: {message}", flush=True)
    return ok


def page_stalled_once(
    index: int,
    now: float,
    session_age: float,
    last_line: str,
    stalled_since: dict[int, float],
    alerted: set[int],
    send=page,
) -> bool:
    """Page one stalled-wait episode once, even when ntm itself is unavailable."""
    if index in alerted:
        return False
    stalled_since.setdefault(index, now - session_age)
    waiting_s = max(0.0, now - stalled_since[index])
    message = (
        f"STALLED pane {index}: waiting {waiting_s / 60:.0f} min, "
        f"session idle {session_age / 60:.0f} min, last line: {last_line}"
    )
    send(message)
    alerted.add(index)
    return True


def agent_mail_project_dir(repo: Path) -> str:
    """Agent Mail's identity directory name for a repo: sha1 of its path, first 12 hex (observed:
    /Users/josh/Developer/jev -> 0427e59174bf). Naming only, not a security hash."""
    return hashlib.sha1(str(repo).encode(), usedforsecurity=False).hexdigest()[:12]


def pane_agents(run=subprocess.run) -> dict[int, str]:
    """{pane index: Agent Mail name} for SESSION, resolved live on every call.

    Pinned to tmux pane ids, never to names: each pane id is looked up in Agent Mail's own
    per-pane binding (<root>/<sha1(repo)[:12]>/<pane id without %>, JSON {"name": ...} or a bare
    name), so a restarted pane is followed under whatever name its new session registered. A pane
    with no readable binding is absent. Why: 2026-10-04 a hand-kept index->name map still named
    three ended sessions, so routes would have claimed beads for agents that no longer exist."""
    root = Path(os.environ.get("JEV_WATCH_IDENTITY_ROOT") or IDENTITY_ROOT).expanduser()
    project = root / agent_mail_project_dir(REPO_ROOT)
    try:
        out = run(
            ["tmux", "list-panes", "-t", SESSION, "-F", "#{pane_index} #{pane_id}"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {}
    agents = {}
    for row in (out or "").splitlines():
        index, _, pane_id = row.strip().partition(" ")
        if not index.isdigit() or not pane_id.startswith("%"):
            continue
        try:
            text = (project / pane_id[1:]).read_text(encoding="utf-8").strip()
            name = json.loads(text).get("name") if text.startswith("{") else text
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(name, str) and name.strip():
            agents[int(index)] = name.strip()
    return agents


def inbox_paths() -> tuple[Path, Path]:
    """(the conductor's archive inbox dir, the paged-ids state file). The conductor is whoever
    holds pane CONDUCTOR_PANE right now; JEV_WATCH_INBOX_AGENT overrides (tests)."""
    root = Path(os.environ.get("JEV_WATCH_INBOX_ROOT") or INBOX_ROOT).expanduser()
    agent = os.environ.get("JEV_WATCH_INBOX_AGENT") or pane_agents().get(CONDUCTOR_PANE)
    state = Path(os.environ.get("JEV_WATCH_INBOX_STATE") or INBOX_STATE).expanduser()
    return root / (
        agent or f"no-agent-mail-identity-for-pane-{CONDUCTOR_PANE}"
    ) / "inbox", state


def read_mail(path: Path) -> dict:
    """An archive file's JSON front matter (between `---json` and `---`), with `created` as epoch
    seconds. Raises ValueError/KeyError/TypeError for any file not in that shape."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---json\n"):
        raise ValueError("no ---json line")
    head, closed, _ = text[len("---json\n") :].partition("\n---\n")
    if not closed:
        raise ValueError("no closing ---")
    front = json.loads(head)
    stamp = CREATED.match(front["created"])
    if not stamp or not isinstance(front["id"], int):
        raise ValueError("bad created or id")
    return {
        "id": front["id"],
        "from": str(front["from"]),
        "subject": str(front["subject"]),
        "importance": str(front["importance"]),
        "created": timegm(time.strptime(stamp.group(1), "%Y-%m-%dT%H:%M:%S")),
        "hhmm": stamp.group(1)[11:16],
    }


def save_state(
    state: Path, paged: set[int], history: set[int], agent: str = ""
) -> None:
    """Write the state file atomically: a sibling temp file, then os.replace."""
    state.parent.mkdir(parents=True, exist_ok=True)
    tmp = state.with_name(f"{state.name}.{os.getpid()}.tmp")
    tmp.write_text(
        json.dumps({"agent": agent, "paged": sorted(paged), "history": sorted(history)})
        + "\n"
    )
    os.replace(tmp, state)


def inbox_round(inbox: Path, state: Path, started: float, send) -> str:
    """Page every urgent/high message not paged before; return this round's `Inbox:` line.
    `send(message) -> bool`; a False leaves the id unrecorded so the next round retries it.
    State: {"agent": inbox owner, "paged": ids sent, "history": urgent/high ids older than the
    first-run cutoff}. When pane 1 restarts under a new name, the new owner's existing backlog is
    history, exactly like a first run (2026-10-04: a rename paged 3 resolved day-old mails)."""
    agent = inbox.parent.name
    if not inbox.is_dir():
        return f"Inbox: NOT_RUN no inbox dir {inbox}"
    first_run = not state.exists()
    try:
        saved = {} if first_run else json.loads(state.read_text())
        paged, history = set(saved.get("paged", [])), set(saved.get("history", []))
    except (OSError, ValueError, AttributeError, TypeError) as err:
        return f"Inbox: NOT_RUN state file {state} unreadable ({type(err).__name__}: {err})"
    try:
        files = sorted(inbox.glob("*/*/*.md"))
    except OSError as err:
        return f"Inbox: NOT_RUN cannot list {inbox} ({err})"
    mails, malformed = [], []
    for path in files:
        try:
            mails.append(read_mail(path))
        except (OSError, ValueError, KeyError, TypeError):
            malformed.append(path.name)
    renamed = bool(saved.get("agent")) and saved.get("agent") != agent
    if first_run:
        cutoff = started - INBOX_LOOKBACK
    elif renamed:
        cutoff = time.time() - INBOX_LOOKBACK
    else:
        cutoff = None
    sent = failed = 0
    for mail in sorted(mails, key=lambda m: m["created"]):
        if mail["importance"] not in PAGE_IMPORTANCE or mail["id"] in paged | history:
            continue
        if cutoff is not None and mail["created"] < cutoff:
            history.add(mail["id"])
            continue
        message = (
            f"MAIL {mail['importance']} from {mail['from']}: {mail['subject']}"
            f" (id {mail['id']}, {mail['hhmm']}Z)"
        )
        if send(message):
            paged.add(mail["id"])
            sent += 1
        else:
            failed += 1
    notes = [inbox.parent.name, f"{len(files)} messages"]
    try:
        save_state(state, paged, history, agent)
    except OSError as err:
        notes.append(f"state NOT saved, next round re-pages ({err})")
    if malformed:
        notes.append(f"{len(malformed)} malformed: {', '.join(malformed)}")
    if failed:
        notes.append(f"{failed} send failed, retried next round")
    return (
        f"Inbox: {sent} urgent/high paged this round, {len(paged)} paged total"
        f" ({'; '.join(notes)})"
    )


def key_state_path() -> Path:
    """The paged-paths state file for key exposure pages."""
    return Path(os.environ.get("JEV_WATCH_KEY_STATE") or KEY_STATE).expanduser()


def key_round(lines: list[str], state: Path, send) -> str | None:
    """Page each session file the census's `Key exposure 24h:` line names, once ever.

    None, with nothing paged and no state written, when the line is absent, NOT_RUN or 0. The
    line names the newest 3 paths; each page carries the count, so a 4th file new in the same
    round is still visible as a number. `send(message) -> bool`; a False leaves the path
    unrecorded so the next round retries it. State: save_state's shape, paths in "paged"."""
    line = next((text for text in lines if text.startswith(KEY_LINE)), "")
    count = KEY_COUNT.match(line)
    if not count or count.group(1) == "0":
        return None
    try:
        saved = json.loads(state.read_text()) if state.exists() else {}
        paged = set(saved.get("paged", []))
    except (OSError, ValueError, AttributeError, TypeError) as err:
        return f"Key page: NOT_RUN state file {state} unreadable ({type(err).__name__}: {err})"
    sent = failed = 0
    for match in KEY_PATH.finditer(line.partition("; newest: ")[2]):
        path, hhmm = match.groups()
        if path in paged:
            continue
        message = (
            f"KEY EXPOSURE: {path} holds a TypeSafe-shaped key (modified {hhmm}Z); "
            f"{count.group(1)} session files in 24h. Rotate the key; never open that file"
            " into a pane."
        )
        if send(message):
            paged.add(path)
            sent += 1
        else:
            failed += 1
    notes = []
    try:
        save_state(state, paged, set())
    except OSError as err:
        notes.append(f"state NOT saved, next round re-pages ({err})")
    if failed:
        notes.append(f"{failed} send failed, retried next round")
    tail = f" ({'; '.join(notes)})" if notes else ""
    return (
        f"Key page: {sent} new paths paged this round, {len(paged)} paged total{tail}"
    )


def stranger_state_path() -> Path:
    """The paged-run state file for README stranger failures."""
    return Path(
        os.environ.get("JEV_WATCH_STRANGER_STATE") or STRANGER_STATE
    ).expanduser()


def stranger_round(lines: list[str], state: Path, send) -> str | None:
    """Page each new failed README stranger run once.

    `send(message) -> bool`; a False leaves the run id unrecorded so the next round retries it.
    The status script emits the mismatch on the following line, which is included in the page.
    """
    status = next((line for line in lines if line.startswith(STRANGER_LINE)), "")
    match = STRANGER_FAILURE.match(status)
    if not match:
        return None
    run_id, age = match.groups()
    try:
        saved = json.loads(state.read_text()) if state.exists() else {}
        paged = {str(item) for item in saved.get("paged", [])}
    except (OSError, ValueError, AttributeError, TypeError) as err:
        return f"Stranger page: NOT_RUN state file {state} unreadable ({type(err).__name__}: {err})"
    if run_id in paged:
        return (
            f"Stranger page: 0 new failures paged this round, {len(paged)} paged total"
        )
    mismatch = next(
        (
            line.removeprefix("  FIRST MISMATCH ")
            for line in lines
            if line.startswith("  FIRST MISMATCH ")
        ),
        "not named in failed log",
    )
    message = f"README STRANGER FAILURE: run {run_id} {age}; {mismatch}"
    sent = 1 if send(message) else 0
    failed = 0 if sent else 1
    if sent:
        paged.add(run_id)
    notes = [f"{failed} send failed, retried next round"] if failed else []
    try:
        save_state(state, paged, set())
    except OSError as err:
        notes.append(f"state NOT saved, next round re-pages ({err})")
    tail = f" ({'; '.join(notes)})" if notes else ""
    return (
        f"Stranger page: {sent} new failures paged this round, {len(paged)} paged total"
        f"{tail}"
    )


def ci_lines() -> list[str]:
    """scripts/ci-main-status.py's output (bead jev-bfku). Informational: never sets our exit code."""
    script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ci-main-status.py"
    )
    try:
        done = subprocess.run(
            [sys.executable, script], capture_output=True, text=True, timeout=90
        )
    except subprocess.TimeoutExpired:
        return ["CI main NOT_RUN scripts/ci-main-status.py timed out after 90s"]
    lines = done.stdout.splitlines()
    return lines or [
        f"CI main NOT_RUN scripts/ci-main-status.py printed nothing (exit {done.returncode})"
    ]


def census_not_run(why: str) -> list[str]:
    return [
        f"{head} NOT_RUN {why}"
        for head in (
            "Jev judge 24h:",
            "Skills 24h:",
            KEY_LINE.rstrip(),
            "Jev tools 24h:",
        )
    ]


def judge_lines() -> list[str]:
    """surface-census.py --fleet-line: the Jev judge-role line (jev-xpk1), the skills line
    (jev-yy7f), the key exposure line (jev-9ov4) and the Jev tools line (jev-x28o).
    Informational: never sets our exit code. The census prints every line it has; a dead census
    is NOT_RUN for all four."""
    script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "work",
        "omp-jev-review",
        "surface-census.py",
    )
    try:
        done = subprocess.run(
            [sys.executable, script, "--fleet-line"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return census_not_run("surface-census.py --fleet-line timed out after 60s")
    lines = done.stdout.splitlines()
    return lines or census_not_run(
        f"surface-census.py printed nothing (exit {done.returncode})"
    )


def selftest() -> int:
    # Status lines captured from the jev session, 2026-09-24T02:0xZ, each on a pane whose tree
    # holds omp with no tool child and a session file 10 min old, so only the screen can decide.
    # Process evidence is covered by work/fleet-idle-watch/test_fleet_idle_watch.py.
    cases = [
        (" π > ◒ Grok 4.7 > 📁 …/jev > ⑂ main *9 ?121 > S30.63", "idle"),
        (" π · ◕ Muse Spark 1.3 · 📁 …/jev · ⑂ main *13 ?122 · ◫ 67.2%/1M ⟲", "idle"),
        (" ⠋ 14m > ◒ Muse Spark 1.3 Contributor > 📁 …/jev", "working"),
        (" ⠇ 8m · ◕ Muse Spark 1.3 · 📁 ~/Developer/jev", "working"),
        # no status line on screen is not 'no-agent' when omp is in the tree (jev-6con)
        ("loading...", "idle"),
        # the spinner line wins over an older idle line higher on the screen
        (" π · ◕ Muse Spark 1.3\n some output\n ⠙ 2s · ◕ Muse Spark 1.3", "working"),
    ]
    snaps = [
        (Snapshot("bun", screen, omp=True, session_age=600.0), want)
        for screen, want in cases
    ]
    # a shell pane with no omp under it, whatever its screen says
    snaps.append((Snapshot("zsh", " ⠋ 14m > ◒ Grok 4.7", omp=False), "no-agent"))
    bad = [(s, want, classify(s)) for s, want in snaps if classify(s)[0] != want]
    for case in bad:
        print("FAIL", case)
    print(f"selftest: {len(snaps) - len(bad)}/{len(snaps)} classifications correct")
    return 1 if bad else 0


# Stale index lock recovery. 2026-10-01 between 03:16Z and 04:12Z, four `git commit` runs killed
# mid-hook under load each left an empty .git/index.lock behind, and every pane's commit failed
# until the conductor moved it by hand. Stale means: empty, at least LOCK_STALE_S old, and no git
# process whose cwd is inside this repository. The lock is renamed into var/agent-tmp, never
# deleted; any failed probe leaves it in place.
REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_STALE_S = int(os.environ.get("JEV_LOCK_STALE_S", "120"))


def hook_load_round(
    repo: Path = REPO_ROOT,
    home: Path = Path.home(),
    run=subprocess.run,
    pager=page,
):
    """Validate installed hooks/extensions and page pane 1 on parse or resolution failures."""
    command = [
        "bun",
        str(repo / "scripts" / "check-hook-loads.mjs"),
        "--repo",
        str(repo),
        "--home",
        str(home),
    ]
    try:
        result = run(command, capture_output=True, text=True, timeout=8, cwd=repo)
    except subprocess.TimeoutExpired:
        note = "HOOK LOAD FAILURE reason=checker-timeout after=8s"
    except OSError as err:
        note = f"HOOK LOAD FAILURE reason=checker-unavailable type={type(err).__name__}"
    else:
        if result.returncode == 0:
            return None
        details = " ".join((result.stdout + " " + result.stderr).split())[:1200]
        note = f"HOOK LOAD FAILURE exit={result.returncode} {details}".rstrip()
    pager(note)
    return note


def live_git_in_repo(repo: Path):
    """PIDs of git processes whose cwd is inside `repo`, or None when a probe fails."""
    try:
        found = subprocess.run(
            ["pgrep", "-f", "(^|/)git( |$)"], capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if found.returncode not in (0, 1):
        return None
    root = str(repo)
    live = []
    for pid in found.stdout.split():
        try:
            cwd = subprocess.run(
                ["lsof", "-a", "-p", pid, "-d", "cwd", "-Fn"],
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout
        except (OSError, subprocess.TimeoutExpired):
            return None
        for line in cwd.splitlines():
            path = line[1:]
            if line.startswith("n") and (
                path == root or path.startswith(root + os.sep)
            ):
                live.append(int(pid))
    return live


def stale_lock_round(
    repo: Path, now: float, send, live_git=live_git_in_repo, park_dir=None
):
    """Move a stale .git/index.lock aside and page once; return a log line or None."""
    lock = repo / ".git" / "index.lock"
    try:
        info = lock.stat()
    except FileNotFoundError:
        return None
    age = int(now - info.st_mtime)
    if info.st_size != 0 or age < LOCK_STALE_S:
        return None
    holders = live_git(repo)
    if holders is None:
        return f"Stale lock: NOT_RUN process probe failed; {lock} ({age}s old) left in place"
    if holders:
        return None
    park = Path(park_dir) if park_dir is not None else repo / "var" / "agent-tmp"
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now))
    dest = park / f"git-index.lock.stale-{stamp}"
    try:
        park.mkdir(parents=True, exist_ok=True)
        lock.rename(dest)
    except OSError as err:
        return f"Stale lock: move FAILED ({type(err).__name__}); {lock} left in place"
    send(
        f"STALE LOCK moved: {lock} (0 bytes, {age}s old, no git process in the repo) -> {dest}; "
        "retry any commit that failed on index.lock"
    )
    return f"Stale lock: moved to {dest} ({age}s old)"


LOCK_CREATOR_LOG_REL = "state/jev/index-lock-creators.jsonl"
LOCK_WATCH_STATE_REL = "state/jev/index-lock-watch.json"


def _read_watch_state(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def _write_watch_state(path, ident):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(ident))
    except OSError:
        pass


def _proc_field(pid, field):
    try:
        out = subprocess.run(
            ["ps", "-o", field + "=", "-p", str(pid)],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        return out[:300] or None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _pane_for_pids(pids):
    """Best-effort tmux pane owning one of the pids; None when unavailable."""
    try:
        out = subprocess.run(
            ["tmux", "list-panes", "-s", "-F", "#{pane_pid} #{pane_id}"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    table = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            table[parts[0]] = parts[1]
    for pid in pids:
        if str(pid) in table:
            return table[str(pid)]
    return None


def _holders_of(lock, run):
    """PIDs with the lock file open. Targeted first: every known creator is
    git, and a full `lsof -t` scan stalls 10 s+ under fleet load. Falls back
    to the full scan so a non-git holder is still found when it answers."""
    try:
        gitpids = run(
            ["pgrep", "-f", "(^|/)git( |$)"], capture_output=True, text=True, timeout=10
        ).stdout.split()
    except Exception:
        gitpids = []
    found = []
    for pid in gitpids[:50]:
        try:
            out = run(
                ["lsof", "-p", str(pid)], capture_output=True, text=True, timeout=10
            ).stdout
        except Exception:
            continue
        if str(lock) in out:
            found.append(str(pid))
    if found:
        return found
    try:
        return run(
            ["lsof", "-t", str(lock)], capture_output=True, text=True, timeout=10
        ).stdout.split()
    except Exception:
        return []


def capture_lock_creator(repo, now, log_path=None, state_path=None, run=subprocess.run):
    """Log the creating process the first time .git/index.lock is seen.

    jev-5hw1: the stale sweeper only sees abandoned locks. This runs beside it
    and captures a fresh lock's holder (pid, argv, parent chain, tmux pane)
    into a private 0600 log. Read-only: it never moves or deletes the lock.
    Capture-once per lock identity; a lock that vanishes resets the state so
    the next appearance captures again. Returns the row on first sight, else
    None. Never throws past the caller.
    """
    try:
        lock = Path(repo) / ".git" / "index.lock"
        home = Path.home()
        log = Path(log_path) if log_path else home / ".local" / LOCK_CREATOR_LOG_REL
        state = state_path if state_path else home / ".local" / LOCK_WATCH_STATE_REL
        try:
            info = lock.stat()
        except FileNotFoundError:
            _write_watch_state(state, None)
            return None
        ident = [info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size]
        if _read_watch_state(state) == ident:
            return None
        pids = _holders_of(lock, run)
        chain = []
        seen = set()
        for pid in pids:
            if pid in seen:
                continue
            seen.add(pid)
            argv = _proc_field(pid, "command")
            ancestors = []
            at, depth = pid, 0
            while depth < 5:
                ppid = _proc_field(at, "ppid")
                if not ppid or not ppid.strip().isdigit() or ppid.strip() == "1":
                    break
                at = ppid.strip()
                ancestors.append({"pid": at, "argv": _proc_field(at, "command")})
                depth += 1
            chain.append({"pid": pid, "argv": argv, "parents": ancestors})
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "lock": str(lock),
            "size": info.st_size,
            "holders": chain,
            "pane": _pane_for_pids(
                [p for p in pids] + [a["pid"] for h in chain for a in h["parents"]]
            ),
        }
        try:
            log.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(str(log), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "a") as fh:
                fh.write(json.dumps(row) + "\n")
        except OSError:
            pass
        _write_watch_state(state, ident)
        return row
    except Exception:
        return None


ROUTER_OFF = "~/.local/state/jev/fleet-router.off"
ROUTER_STATE = "~/.local/state/jev/fleet-router-state.json"
ROUTER_LOG = "~/.local/state/jev/fleet-router.jsonl"
ROUTE_COOLDOWN_S = int(os.environ.get("JEV_ROUTE_COOLDOWN_S", "1800"))
VERIFY_REROUTE_S = int(os.environ.get("JEV_VERIFY_REROUTE_S", "3600"))
VERIFY_LABEL = "needs-verify"
ROUTER_ACTOR = "FleetRouter"


def plan_routes(ripe, agents, ready, verify, state, now):
    """[(pane, agent, kind, bead)] with kind 'verify' or 'claim'; pure, so tests need no br.

    ripe: [(pane, idle_since)], longest idle served first; agents: {pane: agent name};
    ready: unassigned ready beads; verify: in_progress beads labelled needs-verify;
    state: {"pane": {pane: [bead, ts]}, "verify": {bead: [verifier, ts]}}.
    A bead goes to one pane per round; a verification never to its assignee (the author), never
    twice to the same verifier, and to another only after VERIFY_REROUTE_S; a pane gets one
    routed item per ROUTE_COOLDOWN_S, so a pane that ignores its packet is paged, not re-fed."""
    plans, taken = [], set()
    for pane, _since in sorted(ripe, key=lambda item: item[1]):
        agent = agents.get(pane)
        last = state.get("pane", {}).get(str(pane))
        if not agent or (last and now - last[1] < ROUTE_COOLDOWN_S):
            continue
        pick = None
        for bead in sorted(verify, key=lambda b: b.get("updated_at") or ""):
            routed = state.get("verify", {}).get(bead["id"])
            if (
                bead["id"] in taken
                or bead.get("assignee") in (None, "", agent)
                or (
                    routed
                    and (routed[0] == agent or now - routed[1] < VERIFY_REROUTE_S)
                )
            ):
                continue
            pick = ("verify", bead)
            break
        if pick is None:
            for bead in sorted(
                ready, key=lambda b: (b.get("priority", 9), b.get("created_at") or "")
            ):
                if (
                    bead["id"] in taken
                    or bead.get("assignee")
                    or bead.get("issue_type") == "epic"
                ):
                    continue
                pick = ("claim", bead)
                break
        if pick:
            taken.add(pick[1]["id"])
            plans.append((pane, agent, pick[0], pick[1]))
    return plans


def _cut(text: str, width: int = 100) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= width else text[: width - 3] + "..."


def route_packet(pane: int, agent: str, kind: str, bead: dict) -> str:
    """The ntm message for one routed item; ends with the callback line every dispatch carries."""
    bid = bead["id"]
    if kind == "claim":
        return (
            f"FLEET ROUTER to {agent} (pane {pane}): you were idle and {bid} "
            f"(P{bead.get('priority')}) was unassigned in br ready; it is now claimed for you. "
            f"{_cut(bead.get('title', ''))}. Start with br show {bid} and follow its ACCEPTANCE. "
            f"When done: comment the evidence with commit:<sha>, then br --actor {agent} update "
            f"{bid} --add-label {VERIFY_LABEL}; another pane closes it (br refuses a self-close). "
            f'CALLBACK REQUIRED: ntm send jev --pane=1 "DONE {bid} <sha> <one-line evidence>".'
        )
    return (
        f"FLEET ROUTER to {agent} (pane {pane}): verify {bid} (author {bead.get('assignee')}; "
        f"you did not write it). {_cut(bead.get('title', ''))}. Read br show {bid} and its last "
        f"comments, then recompute the claim from the committed rows and scorer (no provider "
        f"calls unless the bead requires them). Holds: br --actor {agent} close {bid} --reason "
        f'"verified <numbers> commit:<sha>". Differs: br --actor {agent} update {bid} '
        f"--remove-label {VERIFY_LABEL} and comment the exact diff. CALLBACK REQUIRED: ntm send "
        f'jev --pane=1 "DONE verify {bid} <holds|differs> <numbers>".'
    )


def send_pane(pane: int, message: str) -> bool:
    """`ntm send` one message to a worker pane; True only when ntm exited 0."""
    if surface_heartbeat.record_dry_run_send(message, pane=pane):
        return True
    try:
        done = subprocess.run(
            [
                "ntm",
                "send",
                SESSION,
                f"--pane={pane}",
                "--no-cass-check",
                "--force-non-interactive",
                message,
            ],
            capture_output=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return done.returncode == 0


def _issues(text: str) -> list[dict] | None:
    """br --json stdout as a list of issues (br list wraps them in {"issues": ...}); None if unparseable."""
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return None
    if isinstance(data, dict):
        data = data.get("issues")
    return data if isinstance(data, list) else None


class Router:
    """One routing round per poll; every side effect goes through run, send and page."""

    def __init__(self, run=subprocess.run, send=send_pane, pager=None):
        self.run, self.send, self.pager = run, send, pager or page
        self.said = None

    def _say(self, note: str) -> None:
        if note != self.said:
            print(f"{time.strftime('%H:%M:%SZ', time.gmtime())} {note}", flush=True)
        self.said = note

    def br(self, *args: str) -> tuple[int | None, str]:
        try:
            done = self.run(
                ["br", *args],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=REPO_ROOT,
                env=dict(os.environ, RUST_LOG="off"),
            )
        except (OSError, subprocess.TimeoutExpired):
            return None, ""
        return done.returncode, done.stdout or ""

    def inputs(self):
        """(agents, ready, verify), or None with the reason printed once."""
        if (
            os.environ.get("JEV_FLEET_ROUTER") == "0"
            or Path(ROUTER_OFF).expanduser().exists()
        ):
            self._say("router off (switch)")
            return None
        agents = pane_agents(self.run)
        if not agents:
            self._say(
                f"NOT_RUN router: no {SESSION} pane has an Agent Mail identity binding"
            )
            return None
        rc_ready, ready = self.br("ready", "--unassigned", "--json")
        rc_verify, verify = self.br(
            "list", "--status", "in_progress", "--label", VERIFY_LABEL, "--json"
        )
        ready, verify = _issues(ready), _issues(verify)
        if rc_ready != 0 or rc_verify != 0 or ready is None or verify is None:
            self._say(
                f"NOT_RUN router: br ready/list failed (rc {rc_ready}/{rc_verify})"
            )
            return None
        self._say("router on")
        return agents, ready, verify

    def round(self, ripe: list[tuple[int, float]], now: float) -> set[int]:
        """Route work to ripe idle panes; return the panes that got a packet."""
        if not ripe:
            return set()
        loaded = self.inputs()
        if loaded is None:
            return set()
        state_path = Path(ROUTER_STATE).expanduser()
        try:
            state = json.loads(state_path.read_text())
        except (OSError, ValueError):
            state = {}
        state = {
            kind: {k: v for k, v in state.get(kind, {}).items() if now - v[1] < 86400}
            for kind in ("pane", "verify")
        }
        routed = set()
        for pane, agent, kind, bead in plan_routes(ripe, *loaded, state, now):
            row = {
                "ts": now,
                "pane": pane,
                "agent": agent,
                "kind": kind,
                "bead": bead["id"],
            }
            if kind == "claim":
                rc, _ = self.br(
                    "update",
                    bead["id"],
                    "--claim",
                    "--if-unchanged",
                    bead.get("updated_at", ""),
                    "--actor",
                    agent,
                )
                if rc != 0:
                    self._log({**row, "result": f"claim-refused rc {rc}"})
                    continue
            sent = self.send(pane, route_packet(pane, agent, kind, bead))
            self._log({**row, "result": "sent" if sent else "send-failed"})
            if not sent:
                if kind == "claim":
                    self.pager(
                        f"ROUTER: {bead['id']} claimed for {agent} but the packet to pane {pane} failed"
                    )
                continue
            state["pane"][str(pane)] = [bead["id"], now]
            if kind == "verify":
                state["verify"][bead["id"]] = [agent, now]
            self.br(
                "comments",
                "add",
                bead["id"],
                f"fleet router: {kind} routed to {agent} (pane {pane})",
                "--actor",
                ROUTER_ACTOR,
            )
            routed.add(pane)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state))
        return routed

    def _log(self, row: dict) -> None:
        path = Path(ROUTER_LOG).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as handle:
            handle.write(json.dumps(row) + "\n")
        print(
            f"{time.strftime('%H:%M:%SZ', time.gmtime())} routed {row['kind']} {row['bead']} "
            f"-> {row['agent']} (pane {row['pane']}): {row['result']}",
            flush=True,
        )


ROUTER = Router()


def route_plan() -> int:
    """--route-plan: print what the router would send every idle pane now; writes nothing."""
    states = poll()
    if states is None:
        return 2
    now = time.time()
    ripe = [
        (index, now)
        for index, reading in sorted(states.items())
        if reading[0] == "idle"
    ]
    loaded = Router().inputs()
    if loaded is None:
        return 2
    try:
        state = json.loads(Path(ROUTER_STATE).expanduser().read_text())
    except (OSError, ValueError):
        state = {}
    print(f"idle panes: {[index for index, _ in ripe]}")
    for pane, agent, kind, bead in plan_routes(ripe, *loaded, state, now):
        print(
            f"pane {pane} {agent}: {kind} {bead['id']} P{bead.get('priority')} "
            f"{_cut(bead.get('title', ''), 70)}"
        )
    return 0


def _surface_heartbeat_round(now: float) -> int:
    state_dir = surface_heartbeat.resolve_state_dir()
    try:
        assessments = surface_heartbeat.monitor(
            SURFACE_REGISTRY,
            state_dir,
            now=now,
            omp_root=surface_heartbeat.real_omp_root(),
            send=page,
            observe_only=SHADOW_ONLY or SURFACE_OBSERVE_ONLY,
        )
    except (OSError, ValueError) as error:
        reason = type(error).__name__
        print(f"surface heartbeat NOT_RUN: {reason}", flush=True)
        page(f"SURFACE HEARTBEAT NOT_RUN: {reason}")
        return 2
    for assessment in assessments:
        print(
            f"surface {assessment.surface_id}: {assessment.state} "
            f"events={assessment.host_events} rows={assessment.rows} errors={assessment.errors}",
            flush=True,
        )
    return 0


def _record_liveness(now: float, status: str) -> None:
    try:
        surface_heartbeat.append_liveness(
            surface_heartbeat.resolve_state_dir(), now=now, status=status
        )
    except (OSError, ValueError) as error:
        print(f"watcher liveness NOT_RUN: {type(error).__name__}", flush=True)


def main() -> int:
    args = sys.argv[1:]
    if "--selftest" in args:
        return selftest()
    if "--route-plan" in args:
        if "--dry-run" in args:
            print("--dry-run supports --once or --probe-start", file=sys.stderr)
            return 2
        return route_plan()
    dry_run = "--dry-run" in args
    surface_heartbeat.DRY_RUN = dry_run
    surface_heartbeat.DRY_RUN_SENDS.clear()
    if dry_run:
        state_dir = surface_heartbeat.resolve_state_dir()
        if not surface_heartbeat.dry_run_targets_are_isolated(
            SURFACE_REGISTRY, state_dir
        ):
            print(
                "--dry-run requires telemetry, switch, and state paths under HOME inside TMPDIR",
                file=sys.stderr,
            )
            return 2
        if "--once" not in args and "--probe-start" not in args:
            print("--dry-run supports --once or --probe-start", file=sys.stderr)
            return 2
    if "--probe-start" in args:
        if "--once" in args or "--hours" not in args:
            print("usage: --probe-start SURFACE_ID --hours N", file=sys.stderr)
            return 2
        try:
            surface_id = args[args.index("--probe-start") + 1]
            duration = int(
                float(args[args.index("--hours") + 1]) * surface_heartbeat.HOUR
            )
            surface = next(
                item
                for item in surface_heartbeat.load_registry(SURFACE_REGISTRY)
                if item.id == surface_id
            )
            surface_heartbeat.start_restore_probe(
                surface,
                surface_heartbeat.resolve_state_dir(),
                now=time.time(),
                duration_seconds=duration,
            )
        except (IndexError, StopIteration, OSError, ValueError, OverflowError) as error:
            print(f"restore probe refused: {type(error).__name__}", file=sys.stderr)
            return 2
        print(
            f"{surface_id}: log-only probe registered; keep the surface in shadow mode "
            "for the stated window"
        )
        return 0
    if "--once" in args:
        states = poll()
        if states is None:
            _record_liveness(time.time(), "poll-unavailable")
            return 2
        submit_shadow(states)
        heartbeat_rc = _surface_heartbeat_round(time.time())
        _record_liveness(time.time(), "ok" if heartbeat_rc == 0 else "heartbeat-error")
        for index, reading in sorted(states.items()):
            state, words = reading[:2]
            print(f"pane {index}: {state} {words}")
        ci = ci_lines()
        for line in ci:
            print(line)
        note = stranger_round(ci, stranger_state_path(), page)
        if note:
            print(note)
        census = judge_lines()
        for line in census:
            print(line)
        note = key_round(census, key_state_path(), page)
        if note:
            print(note)
        print(inbox_round(*inbox_paths(), time.time(), page), flush=True)
        note = stale_lock_round(REPO_ROOT, time.time(), page)
        if note:
            print(note, flush=True)
        row = capture_lock_creator(REPO_ROOT, time.time())
        if row:
            print(
                f"{time.strftime('%H:%M:%SZ', time.gmtime())} lock-creator: {row['lock']} holders={[h['pid'] for h in row['holders']]}",
                flush=True,
            )
        if dry_run:
            print(
                f"dry-run: recorded {len(surface_heartbeat.DRY_RUN_SENDS)} pane sends; "
                "ntm subprocess sends=0",
                flush=True,
            )
        if heartbeat_rc:
            return 2
        return 1 if any(reading[0] != "working" for reading in states.values()) else 0
    composer_last: dict[int, str] = {}
    composer_same: dict[int, int] = {}
    composer_done: set = set()
    steering_done: set = set()
    streak: dict[int, int] = {}
    idle_since: dict[int, float] = {}
    alerted_at: dict[int, float] = {}
    alert_count: dict[int, int] = {}
    stalled_since: dict[int, float] = {}
    stalled_alerted: set[int] = set()
    print(f"watching {SESSION} worker panes every {INTERVAL}s", flush=True)
    next_hook_load = 0.0
    next_heartbeat = 0.0
    started = time.time()  # Stable first-run cutoff, even if the inbox appears later.
    while True:
        now = time.time()
        monotonic_now = time.monotonic()
        if monotonic_now >= next_hook_load:
            next_hook_load = monotonic_now + HOOK_LOAD_INTERVAL
            hook_note = hook_load_round()
            if hook_note:
                print(hook_note, flush=True)
        states = poll()
        if states is None:
            _record_liveness(now, "poll-unavailable")
            time.sleep(INTERVAL)
            continue
        submit_shadow(states)
        heartbeat_status = "checked"
        if monotonic_now >= next_heartbeat:
            next_heartbeat = monotonic_now + HEARTBEAT_INTERVAL
            heartbeat_status = (
                "checked" if _surface_heartbeat_round(now) == 0 else "heartbeat-error"
            )
        _record_liveness(now, heartbeat_status)
        if flush_pending_page1():
            print(
                f"{time.strftime('%H:%M:%SZ', time.gmtime())} "
                f"page batch {PAGE_SEND_ACTION}",
                flush=True,
            )
        if SHADOW_ONLY:
            time.sleep(INTERVAL)
            continue
        due: list[tuple[int, str, str]] = []
        for index, reading in states.items():
            state, words = reading[:2]
            omp_pid = reading[3] if len(reading) > 3 else None
            if state == "stalled-wait":
                match = re.search(r"session idle ([0-9.]+)s", words)
                if match:
                    last_line = words.rsplit(")  ", 1)[-1]
                    page_stalled_once(
                        index,
                        now,
                        float(match.group(1)),
                        last_line,
                        stalled_since,
                        stalled_alerted,
                    )
                continue
            stalled_since.pop(index, None)
            stalled_alerted.discard(index)
            if state == "working":
                streak.pop(index, None)
                idle_since.pop(index, None)
                alerted_at.pop(index, None)
                alert_count.pop(index, None)
                continue
            if state == "idle" and omp_pid is not None:
                try:
                    check_idle_needs_human(index, omp_pid, now)
                except Exception as err:
                    print(
                        f"needs-human check failed pane {index}: {type(err).__name__}",
                        flush=True,
                    )
            if state == "idle":
                composer = reading[4] if len(reading) > 4 else ""
                submit, composer_same[index] = unsubmitted_ready(
                    state,
                    index,
                    composer,
                    composer_last.get(index, ""),
                    composer_same.get(index, 0),
                    composer_done,
                )
                if composer:
                    composer_last[index] = composer
                else:
                    composer_last.pop(index, None)
                    composer_same.pop(index, None)
                    composer_done = {
                        (i, text) for i, text in composer_done if i != index
                    }
                steer = reading[5] if len(reading) > 5 else ""
                if not steer:
                    steering_done = {(i, t) for i, t in steering_done if i != index}
                elif steering_due(state, index, steer, composer, steering_done):
                    ok = nudge_steering(
                        index,
                        state=state,
                        composer=composer,
                        queued_steer=steer,
                    )
                    steering_done.add((index, steer))
                    print(
                        f"{time.strftime('%H:%M:%SZ', time.gmtime())} "
                        f"steering pane {index} nudge {'sent' if ok else 'FAILED'}",
                        flush=True,
                    )
                if submit:
                    ok = submit_enter(index)
                    composer_done.add((index, composer))
                    print(
                        f"{time.strftime('%H:%M:%SZ', time.gmtime())} "
                        f"unsubmitted pane {index} Enter {'sent' if ok else 'FAILED'}",
                        flush=True,
                    )
                    if ok:
                        page(f"UNSUBMITTED pane {index} submitted")
            else:
                composer_last.pop(index, None)
                composer_same.pop(index, None)
            streak[index] = streak.get(index, 0) + 1
            idle_since.setdefault(index, now)
            if streak[index] >= POLLS and realert_due(
                now, alerted_at.get(index), alert_count.get(index, 0)
            ):
                due.append((index, state, words))
        try:
            routed = ROUTER.round(
                [
                    (index, idle_since[index])
                    for index, state, _ in due
                    if state == "idle"
                ],
                now,
            )
        except Exception as err:  # the router must never stop the idle pages
            print(f"router failed: {type(err).__name__}", flush=True)
            routed = set()
        for index, state, words in due:
            if index not in routed:
                alert(index, idle_since[index], f"[{state}] {words}")
            alerted_at[index] = now
            alert_count[index] = alert_count.get(index, 0) + 1
        stamp = time.strftime("%H:%M:%SZ", time.gmtime())
        ci = ci_lines()
        for line in ci:
            print(f"{stamp} {line}", flush=True)
        note = stranger_round(ci, stranger_state_path(), page)
        if note:
            print(f"{stamp} {note}", flush=True)
        inbox_line = inbox_round(*inbox_paths(), started, page)
        print(f"{stamp} {inbox_line}", flush=True)
        # The census each round (about 2 s on 2026-09-25), so a printed key pages within one round.
        census = judge_lines()
        for line in census:
            if line.startswith(KEY_LINE):
                print(f"{stamp} {line}", flush=True)
        note = key_round(census, key_state_path(), page)
        if note:
            print(f"{stamp} {note}", flush=True)
        note = stale_lock_round(REPO_ROOT, time.time(), page)
        if note:
            print(f"{stamp} {note}", flush=True)
        row = capture_lock_creator(REPO_ROOT, time.time())
        if row:
            print(
                f"{stamp} lock-creator: {row['lock']} holders={[h['pid'] for h in row['holders']]}",
                flush=True,
            )
        time.sleep(INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
