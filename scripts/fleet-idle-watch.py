#!/usr/bin/env python3
"""Tell pane 1 when a jev worker pane sits idle.

Worker = tmux pane index >= 2 in the jev session (0 is Joshua's shell, 1 is the conductor).
State  = from process evidence first, screen second (bead jev-6con):
           no-agent  the pane's process tree holds no omp process. Screen text never decides this.
           working   the omp status line shows a spinner, OR omp has a live descendant that is not
                     one of its own long-lived helpers (OMP_HELPERS), i.e. a tool call is running,
                     OR a session .jsonl omp holds open was written in the last SESSION_FRESH s.
           stalled-wait  a wait marker, a session idle for IDLE_STALL_S+, and no CPU-active child
           idle      omp is there and none of the above holds.
         Each state carries the evidence that decided it, e.g. "working (child: docker run ...)".
Alert  = `ntm send jev --pane=1 "IDLE pane N ..."` after POLLS consecutive non-working polls,
         then again every REALERT seconds while it stays that way.
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
                                                 # exit 1 if any worker is not working
  python3 scripts/fleet-idle-watch.py --selftest # classifier on real status lines and trees
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from calendar import timegm
from pathlib import Path
from typing import NamedTuple

SESSION = os.environ.get("JEV_SESSION", "jev")
INTERVAL = int(os.environ.get("IDLE_INTERVAL", "60"))
POLLS = int(os.environ.get("IDLE_POLLS", "2"))
REALERT = int(os.environ.get("IDLE_REALERT", "600"))
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
OMP_HELPERS = (
    "__omp_worker_",  # cli.js __omp_worker_{mnemopi_embed,js_eval_process,daemon_broker}
    "/omp-python-runner/",  # python eval kernel: Python -u $TMPDIR/omp-python-runner/runner-*.py
    "@morphllm/morphmcp",  # MCP server morph: npm exec @morphllm/morphmcp
    "/morph-mcp",  # its node child …/.bin/morph-mcp, or the bin/morph-mcp.sh wrapper
    "franken-harvest serve",  # MCP server franken-harvest
    "typescript-language-server",
    "pyright-langserver",
    "rust-analyzer",
    "gopls",
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
CREATED = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?(Z|\+00:00)$")
# Key exposure paging (bead jev-9ov4): the census's `Key exposure 24h:` line names up to 3 session
# files holding a TypeSafe-shaped key; each path is paged once, persisted like the inbox ids.
KEY_STATE = "~/.local/state/jev/key-exposure-paged.json"
KEY_LINE = "Key exposure 24h: "
KEY_COUNT = re.compile(r"^Key exposure 24h: (\d+) session files hold")
KEY_PATH = re.compile(r"(.+?\.jsonl) \((\d\d:\d\d)Z\)(?:, |$)")


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
        if snap.session_age is not None and snap.session_age < IDLE_STALL_S:
            return (
                "working",
                f"wait marker, session written {snap.session_age:.0f}s ago",
            )
        if snap.session_age is not None:
            return (
                "stalled-wait",
                f"wait marker, session idle {snap.session_age:.0f}s, no CPU descendant",
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
    """Seconds since the newest session .jsonl omp_pid holds open was written; None if none."""
    try:
        out = subprocess.run(
            ["lsof", "-p", str(omp_pid), "-Fn"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    mtimes = []
    for line in out.splitlines():
        if line.startswith("n") and line.endswith(".jsonl"):
            try:
                mtimes.append(os.stat(line[1:]).st_mtime)
            except OSError:
                pass
    return max(0.0, now - max(mtimes)) if mtimes else None


def poll() -> dict[int, tuple[str, str]]:
    """{pane index: (state, "(evidence)  last screen line")} for every watched worker pane."""
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
    table = parse_ps(
        subprocess.run(
            ["ps", "-axo", "pid=,ppid=,pcpu=,command="],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    )
    states = {}
    for row in out.splitlines():
        index, pane_pid, command = (row.split(" ", 2) + ["", ""])[:3]
        if not index.isdigit() or int(index) < 2 or (WATCH and int(index) not in WATCH):
            continue
        screen = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", f"{SESSION}:0.{index}"],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
        omp, tools = (
            omp_processes(table, int(pane_pid)) if pane_pid.isdigit() else (None, [])
        )
        cpu_tools = omp_cpu_tools(table, int(pane_pid)) if pane_pid.isdigit() else []
        snap = Snapshot(
            command=command,
            screen=screen,
            omp=omp is not None,
            tools=tuple(tools),
            cpu_tools=tuple(cpu_tools),
            session_age=session_age(omp, time.time()) if omp is not None else None,
        )
        state, evidence = classify(snap)
        states[int(index)] = (state, f"({evidence})  {last_words(screen)}")
    return states


def send_pane1(message: str) -> bool:
    """`ntm send` one line to the conductor; True only when ntm exited 0."""
    try:
        done = subprocess.run(
            ["ntm", "send", SESSION, "--pane=1", message],
            capture_output=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return done.returncode == 0


def alert(index: int, since: float, words: str) -> None:
    stamp = time.strftime("%H:%MZ", time.gmtime(since))
    message = f"IDLE pane {index} (since {stamp}), last line: {words}"
    send_pane1(message)
    print(f"{time.strftime('%H:%M:%SZ', time.gmtime())} alerted: {message}", flush=True)


def page(message: str) -> bool:
    """The watcher's mail pager: send_pane1 plus a log line saying whether ntm took it."""
    ok = send_pane1(message)
    said = "paged" if ok else "page FAILED"
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


def inbox_paths() -> tuple[Path, Path]:
    """(the conductor's archive inbox dir, the paged-ids state file)."""
    root = Path(os.environ.get("JEV_WATCH_INBOX_ROOT") or INBOX_ROOT).expanduser()
    agent = os.environ.get("JEV_WATCH_INBOX_AGENT") or "AmberWillow"
    state = Path(os.environ.get("JEV_WATCH_INBOX_STATE") or INBOX_STATE).expanduser()
    return root / agent / "inbox", state


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


def save_state(state: Path, paged: set[int], history: set[int]) -> None:
    """Write the state file atomically: a sibling temp file, then os.replace."""
    state.parent.mkdir(parents=True, exist_ok=True)
    tmp = state.with_name(f"{state.name}.{os.getpid()}.tmp")
    tmp.write_text(
        json.dumps({"paged": sorted(paged), "history": sorted(history)}) + "\n"
    )
    os.replace(tmp, state)


def inbox_round(inbox: Path, state: Path, started: float, send) -> str:
    """Page every urgent/high message not paged before; return this round's `Inbox:` line.
    `send(message) -> bool`; a False leaves the id unrecorded so the next round retries it.
    State: {"paged": ids sent, "history": urgent/high ids older than the first-run cutoff}."""
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
    cutoff = started - INBOX_LOOKBACK if first_run else None
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
        save_state(state, paged, history)
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
        for head in ("Jev judge 24h:", "Skills 24h:", KEY_LINE.rstrip())
    ]


def judge_lines() -> list[str]:
    """surface-census.py --fleet-line: the Jev judge-role line (jev-xpk1), the skills line
    (jev-yy7f) and the key exposure line (jev-9ov4). Informational: never sets our exit code.
    The census prints every line it has; a dead census is NOT_RUN for all three."""
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


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    if "--once" in sys.argv:
        states = poll()
        for index, reading in sorted(states.items()):
            state, words = reading[:2]
            print(f"pane {index}: {state} {words}")
        for line in ci_lines():
            print(line)
        census = judge_lines()
        for line in census:
            print(line)
        note = key_round(census, key_state_path(), page)
        if note:
            print(note)
        print(inbox_round(*inbox_paths(), time.time(), page), flush=True)
        return 1 if any(reading[0] != "working" for reading in states.values()) else 0
    streak: dict[int, int] = {}
    idle_since: dict[int, float] = {}
    alerted_at: dict[int, float] = {}
    stalled_since: dict[int, float] = {}
    stalled_alerted: set[int] = set()
    print(f"watching {SESSION} worker panes every {INTERVAL}s", flush=True)
    started = time.time()
    while True:
        now = time.time()
        for index, reading in poll().items():
            state, words = reading[:2]
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
                continue
            streak[index] = streak.get(index, 0) + 1
            idle_since.setdefault(index, now)
            due = now - alerted_at.get(index, 0) >= REALERT
            if streak[index] >= POLLS and due:
                alert(index, idle_since[index], f"[{state}] {words}")
                alerted_at[index] = now
        inbox_line = inbox_round(*inbox_paths(), started, page)
        stamp = time.strftime("%H:%M:%SZ", time.gmtime())
        print(f"{stamp} {inbox_line}", flush=True)
        # The census each round (about 2 s on 2026-09-25), so a printed key pages within one round.
        census = judge_lines()
        for line in census:
            if line.startswith(KEY_LINE):
                print(f"{stamp} {line}", flush=True)
        note = key_round(census, key_state_path(), page)
        if note:
            print(f"{stamp} {note}", flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
