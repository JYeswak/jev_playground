#!/usr/bin/env python3
"""Tell pane 1 when a jev worker pane sits idle.

Worker = tmux pane index >= 2 in the jev session (0 is Joshua's shell, 1 is the conductor).
State  = from process evidence first, screen second (bead jev-6con):
           no-agent  the pane's process tree holds no omp process. Screen text never decides this.
           working   the omp status line shows a spinner, OR omp has a live descendant that is not
                     one of its own long-lived helpers (OMP_HELPERS), i.e. a tool call is running,
                     OR a session .jsonl omp holds open was written in the last SESSION_FRESH s.
           idle      omp is there and none of the above holds.
         Each state carries the evidence that decided it, e.g. "working (child: docker run ...)".
Alert  = `ntm send jev --pane=1 "IDLE pane N ..."` after POLLS consecutive non-working polls,
         then again every REALERT seconds while it stays that way.

Why: 2026-09-24, 4 of 6 worker panes sat at their prompts for most of an hour and the
conductor only looked when a callback arrived. Joshua: "dont let that happen again."
Why process evidence: 2026-09-25 the screen-only reading said panes 2 and 5 were 'no-agent'
while each had omp mid-task (a diff view or todo panel hid the status line), and said pane 2
was 'idle' while its omp had a docker run live under a bash tool call.

  python3 scripts/fleet-idle-watch.py            # run forever (start it under hub)
  python3 scripts/fleet-idle-watch.py --once     # one poll, then the CI-on-main line from
                                                 # scripts/ci-main-status.py and the Jev judge
                                                 # line from surface-census.py --fleet-line
                                                 # (both informational); exit 1 if any worker
                                                 # is not working
  python3 scripts/fleet-idle-watch.py --selftest # classifier on real status lines and trees
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from typing import NamedTuple

SESSION = os.environ.get("JEV_SESSION", "jev")
INTERVAL = int(os.environ.get("IDLE_INTERVAL", "60"))
POLLS = int(os.environ.get("IDLE_POLLS", "2"))
REALERT = int(os.environ.get("IDLE_REALERT", "600"))
SPINNER = re.compile(r"^\s*[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]")
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
)
SESSION_FRESH = int(os.environ.get("IDLE_SESSION_FRESH", "60"))


class Snapshot(NamedTuple):
    """What one poll saw of one pane; classify() reads nothing else, so tests need no tmux."""

    command: str  # tmux pane_current_command
    screen: str  # tmux capture-pane text
    omp: bool  # an omp process is in the pane's process tree
    tools: tuple[str, ...] = ()  # non-helper descendants of omp, preorder
    session_age: float | None = (
        None  # seconds since omp's open session .jsonl was written
    )


def short(command: str, width: int = 90) -> str:
    """argv0 cut to its basename, the whole thing cut to width."""
    head, _, rest = command.partition(" ")
    text = f"{os.path.basename(head)} {rest}".strip()
    return text if len(text) <= width else text[: width - 3] + "..."


def classify(snap: Snapshot) -> tuple[str, str]:
    """(working | idle | no-agent, the evidence that decided it)."""
    if not snap.omp:
        return (
            "no-agent",
            f"no omp in the pane's process tree; foreground {snap.command}",
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


def parse_ps(text: str) -> dict[int, tuple[int, str]]:
    """`ps -axo pid=,ppid=,command=` → {pid: (ppid, command)}."""
    table = {}
    for row in text.splitlines():
        parts = row.split(None, 2)
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            table[int(parts[0])] = (int(parts[1]), parts[2])
    return table


def omp_processes(
    table: dict[int, tuple[int, str]], pane_pid: int
) -> tuple[int | None, list[str]]:
    """(the first omp pid at or under pane_pid, the commands of its non-helper descendants)."""
    children: dict[int, list[int]] = {}
    for pid, (ppid, _) in table.items():
        children.setdefault(ppid, []).append(pid)
    queue = [pane_pid]
    omp = None
    while queue:
        pid = queue.pop(0)
        if pid in table and OMP.search(table[pid][1]):
            omp = pid
            break
        queue.extend(sorted(children.get(pid, [])))
    if omp is None:
        return None, []
    tools = []
    stack = sorted(children.get(omp, []), reverse=True)
    while stack:
        pid = stack.pop()
        command = table[pid][1]
        if not any(helper in command for helper in OMP_HELPERS):
            tools.append(command)
        stack.extend(sorted(children.get(pid, []), reverse=True))
    return omp, tools


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
            ["ps", "-axo", "pid=,ppid=,command="],
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
        snap = Snapshot(
            command=command,
            screen=screen,
            omp=omp is not None,
            tools=tuple(tools),
            session_age=session_age(omp, time.time()) if omp is not None else None,
        )
        state, evidence = classify(snap)
        states[int(index)] = (state, f"({evidence})  {last_words(screen)}")
    return states


def alert(index: int, since: float, words: str) -> None:
    stamp = time.strftime("%H:%MZ", time.gmtime(since))
    message = f"IDLE pane {index} (since {stamp}), last line: {words}"
    subprocess.run(
        ["ntm", "send", SESSION, "--pane=1", message], capture_output=True, timeout=60
    )
    print(f"{time.strftime('%H:%M:%SZ', time.gmtime())} alerted: {message}", flush=True)


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


def judge_lines() -> list[str]:
    """The Jev judge-role line (bead jev-xpk1). Informational: never sets our exit code."""
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
        return [
            "Jev judge 24h: NOT_RUN surface-census.py --fleet-line timed out after 60s"
        ]
    lines = done.stdout.splitlines()
    return lines or [
        f"Jev judge 24h: NOT_RUN surface-census.py printed nothing (exit {done.returncode})"
    ]


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
        for index, (state, words) in sorted(states.items()):
            print(f"pane {index}: {state} {words}")
        for line in ci_lines():
            print(line)
        for line in judge_lines():
            print(line)
        return 1 if any(state != "working" for state, _ in states.values()) else 0
    streak: dict[int, int] = {}
    idle_since: dict[int, float] = {}
    alerted_at: dict[int, float] = {}
    print(f"watching {SESSION} worker panes every {INTERVAL}s", flush=True)
    while True:
        now = time.time()
        for index, (state, words) in poll().items():
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
        time.sleep(INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
