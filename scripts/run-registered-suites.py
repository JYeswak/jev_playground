#!/usr/bin/env python3
"""Run every first-party suite TESTS.md names, with that row's command.

  python3 scripts/run-registered-suites.py
  python3 scripts/run-registered-suites.py --selftest

Prints one TSV row per suite: path, rc, count, seconds, prerequisite, status.
A missing prerequisite is SKIP, never a pass. Exit 0 only when every row is
PASS or SKIP. --selftest plants a failing assertion in /tmp and requires the
command to exit nonzero and name that file.

Does not edit a gate. The stage to extend is 70-tests-registry-sync.
"""

import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKED = re.compile(
    r"(^|/)(test|tests)/|\.test\.[cm]?[tj]s$|\.spec\.[cm]?[tj]s$|_test\.py$|test_.*\.py$|probe.*\.mts$",
    re.I,
)
TIMEOUT = 180


def tracked_tests(repo):
    out = subprocess.run(
        ["git", "-C", repo, "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in out.stdout.splitlines() if TRACKED.search(line)]


def run_command_for(registry, path):
    text = Path(registry).read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r"Run: `([^`]+)`", text):
        if path in match.group(1):
            return match.group(1)
    idx = text.find(f"`{path}`")
    if idx >= 0:
        match = re.search(r"Run: `([^`]+)`", text[idx : idx + 800])
        if match:
            return match.group(1)
    for block in re.split(r"\n(?=- )", text):
        if f"`{path}`" not in block[:400]:
            continue
        match = re.search(r"Run: `([^`]+)`", block)
        if match:
            return match.group(1)
    if path.endswith(".py"):
        return f"python3 -m unittest {path}"
    if path.endswith((".mjs", ".js", ".cjs")):
        return f"node --test {path}"
    if path.endswith(".mts"):
        return f"npx tsx {path}"
    if path.endswith(".ts"):
        return f"bun test {path}"
    return ""


def node_major():
    try:
        out = subprocess.run(["node", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        return None
    match = re.match(r"v(\d+)", out.stdout.strip())
    return int(match.group(1)) if match else None


def prerequisite(repo, path, command):
    repo = Path(repo)
    if path.endswith(".ts") and node_major() is not None and node_major() < 22:
        return "Node 22.18+ (README.md:26); this node is older"
    if path.startswith("compaction/") or "bootstrap-compaction" in command:
        if (
            not (repo / "compaction/node_modules").is_dir()
            and not (repo / "compaction/dist").is_dir()
        ):
            return "./scripts/bootstrap-compaction.sh"
    head = Path(repo, path).read_text(encoding="utf-8", errors="replace")[:4000].lower()
    if "work/sdk" in path or "work/sdk" in command or "typesafe" in head:
        if not (repo / "work/sdk/node_modules").is_dir():
            return "npm ci --prefix work/sdk"
    if command.startswith("bun ") or " bun " in command:
        if (
            subprocess.run(
                ["bash", "-lc", "command -v bun"], capture_output=True
            ).returncode
            != 0
        ):
            return "bun"
    if "npm " in command:
        cd = re.search(r"cd ([^&]+) &&", command)
        base = repo / cd.group(1).strip() if cd else repo / Path(path).parent
        if not (base / "node_modules").is_dir():
            rel = base.relative_to(repo) if str(base).startswith(str(repo)) else base
            return f"npm ci in {rel}"
    if (command.startswith("node") or " node " in command) and node_major() is None:
        return "node"
    if command.startswith("python"):
        if (
            subprocess.run(
                ["bash", "-lc", "command -v python3"], capture_output=True
            ).returncode
            != 0
        ):
            return "python3"
    if "fast-jev-compaction" in head and not (repo / "fast-jev-compaction").exists():
        return "vendored clone fast-jev-compaction (not in a fresh clone)"
    return ""


def count_from(output):
    for pattern in (
        r"# tests (\d+)",
        r"# pass (\d+)",
        r"Ran (\d+) tests",
        r"(\d+) passing",
    ):
        found = re.findall(pattern, output)
        if found:
            return found[-1]
    return ""


def run_one(repo, path, command):
    started = time.monotonic()
    need = prerequisite(repo, path, command)
    if need or not command:
        return {
            "path": path,
            "rc": "",
            "count": "",
            "seconds": f"{time.monotonic() - started:.2f}",
            "prerequisite": need or "no Run: command in TESTS.md",
            "status": "SKIP",
        }
    try:
        proc = subprocess.run(
            command,
            cwd=repo,
            shell=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        output = proc.stdout + proc.stderr
        status = "PASS" if proc.returncode == 0 else "FAIL"
        rc = str(proc.returncode)
    except subprocess.TimeoutExpired:
        output = ""
        status = "FAIL"
        rc = "124"
    return {
        "path": path,
        "rc": rc,
        "count": count_from(output),
        "seconds": f"{time.monotonic() - started:.2f}",
        "prerequisite": "",
        "status": status,
    }


def survey(repo):
    registry = Path(repo) / "TESTS.md"
    return [
        run_one(repo, path, run_command_for(registry, path))
        for path in tracked_tests(repo)
        if (Path(repo) / path).exists()
    ]


def emit(rows):
    print("path\trc\tcount\tseconds\tprerequisite\tstatus")
    failed = []
    for row in rows:
        print(
            "\t".join(
                [
                    row["path"],
                    row["rc"],
                    row["count"],
                    row["seconds"],
                    row["prerequisite"],
                    row["status"],
                ]
            )
        )
        if row["status"] == "FAIL":
            failed.append(row["path"])
    print(
        f"# {sum(1 for r in rows if r['status']=='PASS')} pass, "
        f"{sum(1 for r in rows if r['status']=='SKIP')} skip, "
        f"{len(failed)} fail",
        file=sys.stderr,
    )
    return failed


def selftest():
    tmp = Path(tempfile.mkdtemp(prefix="suites-", dir="/tmp"))
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=tmp, check=True
    )
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp, check=True)
    suite = tmp / "work/plant/fail_test.py"
    suite.parent.mkdir(parents=True)
    suite.write_text(
        "import unittest\nclass T(unittest.TestCase):\n"
        "    def test_planted(self):\n        self.fail('planted')\n"
    )
    (tmp / "TESTS.md").write_text(
        "- `work/plant/fail_test.py` — planted. Run: `python3 -m unittest work/plant/fail_test.py` (1 test).\n"
    )
    subprocess.run(
        ["git", "add", "TESTS.md", "work/plant/fail_test.py"], cwd=tmp, check=True
    )
    subprocess.run(["git", "commit", "-q", "-m", "[test] plant"], cwd=tmp, check=True)
    failed = [row["path"] for row in survey(tmp) if row["status"] == "FAIL"]
    if failed != ["work/plant/fail_test.py"]:
        print(f"SELFTEST FAIL: {failed}", file=sys.stderr)
        return 1
    print("SELFTEST PASS planted failing assertion named work/plant/fail_test.py")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    repo = ROOT
    for arg in argv[1:]:
        if not arg.startswith("-"):
            repo = Path(arg)
    rows = survey(repo)
    if not rows:
        print(
            "ERROR: zero tracked test files — an empty scan set is not a pass",
            file=sys.stderr,
        )
        return 3
    return 1 if emit(rows) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
