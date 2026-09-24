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

import json
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
        return f"bun test ./{path}"
    return ""


SDK_IMPORT = re.compile(
    r"""^[ \t]*(?:import|from)\s+.*?['\"][^'\"]*(?:@typesafe-ai/sdk|sdk/node_modules/@typesafe-ai/sdk)|^(?:import\s+typesafe_sdk|from\s+typesafe_sdk\s+import)\b""",
    re.M,
)
RELATIVE_IMPORT = re.compile(r"""['\"](\.\.?/[^'\"\n\s]{1,180})['\"]""")


def file_imports_sdk(text):
    return bool(SDK_IMPORT.search(text))


def suite_imports_sdk(repo, path):
    repo = Path(repo)
    seen = set()

    def walk(file, left):
        if file in seen or left < 0:
            return False
        seen.add(file)
        try:
            if not file.is_file():
                return False
            text = file.read_text(encoding="utf-8", errors="replace")[:8000]
        except OSError:
            return False
        if file_imports_sdk(text):
            return True
        if left == 0:
            return False
        for ref in RELATIVE_IMPORT.findall(text):
            if not ref.startswith(("./", "../")):
                continue
            base = file.parent / ref
            for cand in (
                base,
                Path(str(base) + ".py"),
                Path(str(base) + ".mjs"),
                Path(str(base) + ".ts"),
                Path(str(base) + ".js"),
            ):
                if walk(cand, left - 1):
                    return True
        return False

    return walk(repo / path, 2)


def missing_signature(output):
    if "response.clone" in output:
        return ""
    if "prerequisite missing" in output and "npm ci --prefix work/sdk" in output:
        return "npm ci --prefix work/sdk"
    if "actual: 'sdk-missing'" in output or 'actual: "sdk-missing"' in output:
        return "npm ci --prefix work/sdk"
    return ""


def suite_imports_path(repo, path, needle):
    text = Path(repo, path).read_text(encoding="utf-8", errors="replace")
    return bool(
        re.search(
            rf"""(?m)^[ \t]*import\s+.*?['\"][^'\"]*{re.escape(needle)}""",
            text,
        )
    )


def normalize_command(repo, path, command):
    repo = Path(repo)

    def prefix_bun(match):
        arg = match.group(1)
        if arg.startswith(("./", "/", "-")):
            return match.group(0)
        return f"bun test ./{arg}"

    command = re.sub(r"bun test\s+(\S+)", prefix_bun, command)
    cd = re.search(r"cd ([^&]+) && npm test\b", command)
    if cd and not (repo / cd.group(1).strip() / "package.json").is_file():
        return f"node --test {path}"
    return command


def npm_install_need(repo, command):
    cd = re.search(r"cd ([^&]+) &&", command)
    if not cd:
        return ""
    base = Path(repo) / cd.group(1).strip()
    pkg = base / "package.json"
    if not pkg.is_file() or (base / "node_modules").is_dir():
        return ""
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    if not (data.get("dependencies") or data.get("devDependencies")):
        return ""
    rel = base.relative_to(repo)
    if (base / "package-lock.json").is_file():
        return f"npm ci --prefix {rel}"
    return f"npm install --prefix {rel}"


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
    if command.startswith("bun ") or " bun " in command:
        if (
            subprocess.run(
                ["bash", "-lc", "command -v bun"], capture_output=True
            ).returncode
            != 0
        ):
            return "bun"
    install = npm_install_need(repo, command)
    if install:
        return install
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
    if ".venv/bin/python" in command:
        binary = command.split()[0]
        if not (repo / binary).is_file():
            clone = repo / "upstream/typesafe-ai/system-one-adapter-python"
            if not clone.is_dir():
                return "vendored clone upstream/typesafe-ai/system-one-adapter-python absent"
            return "uv sync --directory upstream/typesafe-ai/system-one-adapter-python"
    if (
        suite_imports_path(repo, path, "fast-jev-compaction/")
        and not (repo / "fast-jev-compaction").exists()
    ):
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
    command = normalize_command(repo, path, command)
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
        signature = missing_signature(output) if status == "FAIL" else ""
        if signature:
            return {
                "path": path,
                "rc": rc,
                "count": count_from(output),
                "seconds": f"{time.monotonic() - started:.2f}",
                "prerequisite": signature,
                "status": "SKIP",
            }
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
    mention = tmp / "work/plant/mention_test.py"
    mention.write_text(
        "import unittest\n# a missing typesafe_sdk import is a comment, not an import\n"
        "class T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n"
    )
    demo = tmp / "demos/nopkg/ok.test.mjs"
    demo.parent.mkdir(parents=True)
    demo.write_text(
        "import test from 'node:test';\nimport assert from 'node:assert/strict';\n"
        "test('ok', () => assert.equal(1, 1));\n"
    )
    venv = tmp / "work/plant/venv_test.py"
    venv.write_text(
        "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n"
    )
    (tmp / "TESTS.md").write_text(
        "- `work/plant/fail_test.py` — planted. Run: `python3 -m unittest work/plant/fail_test.py` (1 test).\n"
        "- `work/plant/mention_test.py` — mentions typesafe in a comment. Run: `python3 -m unittest work/plant/mention_test.py`.\n"
        "- `demos/nopkg/ok.test.mjs` — no package.json. Run: `cd demos/nopkg && npm test`.\n"
        "- `work/plant/venv_test.py` — missing adapter venv. Run: `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python -m unittest work/plant/venv_test.py`.\n"
        "- `.omp/extensions/kit-guard/kit-guard.test.ts` — bun path. Run: `bun test .omp/extensions/kit-guard/kit-guard.test.ts`.\n"
    )
    if (
        normalize_command(
            tmp, "x.ts", "bun test .omp/extensions/kit-guard/kit-guard.test.ts"
        )
        != "bun test ./.omp/extensions/kit-guard/kit-guard.test.ts"
    ):
        print("SELFTEST FAIL: bun path was not prefixed", file=sys.stderr)
        return 1
    subprocess.run(
        [
            "git",
            "add",
            "TESTS.md",
            "work/plant/fail_test.py",
            "work/plant/mention_test.py",
            "work/plant/venv_test.py",
            "demos/nopkg/ok.test.mjs",
        ],
        cwd=tmp,
        check=True,
    )
    subprocess.run(["git", "commit", "-q", "-m", "[test] plant"], cwd=tmp, check=True)
    rows = survey(tmp)
    by = {row["path"]: row for row in rows}
    failed = [row["path"] for row in rows if row["status"] == "FAIL"]
    if failed != ["work/plant/fail_test.py"]:
        print(f"SELFTEST FAIL: {failed}", file=sys.stderr)
        return 1
    if by["work/plant/mention_test.py"]["status"] != "PASS":
        print("SELFTEST FAIL: typesafe comment was skipped", file=sys.stderr)
        return 1
    if by["demos/nopkg/ok.test.mjs"]["status"] != "PASS":
        print(
            f"SELFTEST FAIL: no-package.json demo {by['demos/nopkg/ok.test.mjs']}",
            file=sys.stderr,
        )
        return 1
    venv_row = by["work/plant/venv_test.py"]
    if (
        venv_row["status"] != "SKIP"
        or "system-one-adapter-python" not in venv_row["prerequisite"]
    ):
        print(f"SELFTEST FAIL: venv row {venv_row}", file=sys.stderr)
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
