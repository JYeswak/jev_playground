from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "close-ref-check.py"


def git(repo: Path, env: dict[str, str], *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        capture_output=True,
        check=True,
        text=True,
        timeout=15,
    )
    return result.stdout.strip()


def commit(repo: Path, env: dict[str, str], message: str) -> None:
    git(
        repo,
        env,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "--quiet",
        "-m",
        message,
    )


def write_issues(repo: Path, issues: list[dict[str, str]]) -> None:
    path = repo / ".beads" / "issues.jsonl"
    path.write_text("".join(json.dumps(issue, sort_keys=True) + "\n" for issue in issues), encoding="utf-8")


def new_repo() -> tuple[Path, dict[str, str], str]:
    scratch_root = ROOT / "var" / "agent-tmp"
    scratch_root.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="jev-c7q7-test.", dir=scratch_root))
    (scratch / ".owner").write_text(
        f"pid={os.getpid()} label=jev-c7q7-test repo={ROOT} created={datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )
    repo = scratch / "repo"
    origin = scratch / "origin.git"
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    env["GIT_TERMINAL_PROMPT"] = "0"

    subprocess.run(["git", "init", "--quiet", "--bare", "--template=", str(origin)], check=True, env=env, timeout=15)
    subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "--quiet", "--template=", str(repo)], check=True, env=env, timeout=15)
    git(repo, env, "config", "user.name", "Test")
    git(repo, env, "config", "user.email", "test@example.invalid")
    git(repo, env, "remote", "add", "origin", str(origin))

    (repo / ".beads").mkdir()
    (repo / "docs").mkdir()
    (repo / "scripts").mkdir()
    (repo / "work" / "plan-20261004" / "convergence" / "r3").mkdir(parents=True)
    (repo / ".gitignore").write_text(
        "work/plan-20261004/convergence/r3/L2-ResearchR3.jsonl\n", encoding="utf-8"
    )
    (repo / "work" / "plan-20261004" / "convergence" / "r3" / "L2-ResearchR3.jsonl").write_text(
        "ignored local plan artifact\n", encoding="utf-8"
    )
    (repo / ".beads" / "issues.jsonl").write_text("", encoding="utf-8")
    (repo / "docs" / "evidence.md").write_text("tracked investigation evidence\n", encoding="utf-8")
    shutil.copy2(CHECKER, repo / "scripts" / "close-ref-check.py")
    git(repo, env, "add", "--", ".gitignore", ".beads/issues.jsonl", "docs/evidence.md", "scripts/close-ref-check.py")
    commit(repo, env, "seed origin/main evidence [test]")
    origin_commit = git(repo, env, "rev-parse", "HEAD")

    write_issues(
        repo,
        [
            {
                "id": "older-close",
                "status": "closed",
                "closed_at": "2026-10-03T23:59:59Z",
                "close_reason": f"commit:{origin_commit} investigation:docs/evidence.md",
            }
        ],
    )
    git(repo, env, "add", "--", ".beads/issues.jsonl")
    commit(repo, env, "add initial closed bead row [test]")
    git(repo, env, "push", "--quiet", "-u", "origin", "main")
    git(repo, env, "fetch", "--quiet", "origin")
    return repo, env, origin_commit


def run_checker(repo: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / "close-ref-check.py"), *args],
        cwd=repo,
        env=env,
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )


def issue(bead_id: str, reason: str, closed_at: str = "2026-10-05T12:00:00Z") -> dict[str, str]:
    return {"id": bead_id, "status": "closed", "closed_at": closed_at, "close_reason": reason}


class CloseReferenceCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo, self.env, self.origin_commit = new_repo()

    def json_result(self, result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
        self.assertTrue(result.stdout.strip(), result.stderr)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"checker output is not valid JSON: {exc}; stdout={result.stdout!r}")
        if not isinstance(payload, dict):
            self.fail(f"checker JSON is not an object: {payload!r}")
        return payload

    def test_origin_main_commit_and_tracked_investigation_path_pass(self) -> None:
        result = run_checker(self.repo, self.env, "--bead", "older-close", "--json")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = self.json_result(result)
        self.assertEqual(payload["status"], "PASS")
        references = payload["results"][0]["references"]
        self.assertEqual([reference["status"] for reference in references], ["PASS", "PASS"])
        self.assertEqual([reference["kind"] for reference in references], ["commit", "investigation"])

    def test_commit_on_local_branch_not_origin_main_is_refused(self) -> None:
        git(self.repo, self.env, "switch", "--quiet", "-c", "local-commit")
        (self.repo / "local-only.txt").write_text("local commit\n", encoding="utf-8")
        git(self.repo, self.env, "add", "--", "local-only.txt")
        commit(self.repo, self.env, "local-only commit [test]")
        local_commit = git(self.repo, self.env, "rev-parse", "HEAD")
        write_issues(self.repo, [issue("local-commit", f"commit:{local_commit} investigation:docs/evidence.md")])

        result = run_checker(self.repo, self.env, "--bead", "local-commit", "--json")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = self.json_result(result)
        self.assertEqual(payload["results"][0]["references"][0]["status"], "REFUSED")
        self.assertIn("not an ancestor of origin/main", payload["results"][0]["reason"])

    def test_bead_id_and_gitignored_investigation_paths_are_refused(self) -> None:
        write_issues(
            self.repo,
            [
                issue("bead-id", f"commit:{self.origin_commit} investigation:jev-vvkr"),
                issue(
                    "ignored-path",
                    f"commit:{self.origin_commit} investigation:work/plan-20261004/convergence/r3/L2-ResearchR3.jsonl",
                ),
            ],
        )
        ignored_path = "work/plan-20261004/convergence/r3/L2-ResearchR3.jsonl"
        self.assertEqual(git(self.repo, self.env, "check-ignore", ignored_path), ignored_path)

        for bead_id in ("bead-id", "ignored-path"):
            with self.subTest(bead_id=bead_id):
                result = run_checker(self.repo, self.env, "--bead", bead_id, "--json")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                payload = self.json_result(result)
                investigation = payload["results"][0]["references"][1]
                self.assertEqual(investigation["status"], "REFUSED")
                self.assertIn("not tracked on origin/main", investigation["reason"])

    def test_investigation_path_tracked_only_on_local_branch_is_refused(self) -> None:
        git(self.repo, self.env, "switch", "--quiet", "-c", "local-evidence")
        (self.repo / "local-evidence.md").write_text("branch-only evidence\n", encoding="utf-8")
        git(self.repo, self.env, "add", "--", "local-evidence.md")
        commit(self.repo, self.env, "add branch-only evidence [test]")
        git(self.repo, self.env, "switch", "--quiet", "main")
        write_issues(self.repo, [issue("branch-path", f"commit:{self.origin_commit} investigation:local-evidence.md")])

        result = run_checker(self.repo, self.env, "--bead", "branch-path", "--json")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        payload = self.json_result(result)
        self.assertEqual(payload["results"][0]["references"][1]["status"], "REFUSED")
        self.assertIn("not tracked on origin/main", payload["results"][0]["reason"])

    def test_since_returns_every_close_strictly_after_the_cutoff(self) -> None:
        write_issues(
            self.repo,
            [
                issue(
                    "older-close",
                    f"commit:{self.origin_commit} investigation:docs/evidence.md",
                    "2026-10-03T23:59:59Z",
                ),
                issue(
                    "newer-close",
                    f"commit:{self.origin_commit} investigation:docs/evidence.md",
                    "2026-10-04T00:00:01Z",
                ),
            ],
        )
        issues_before = (self.repo / ".beads" / "issues.jsonl").read_bytes()

        result = run_checker(self.repo, self.env, "--since", "2026-10-04", "--json")
        self.assertEqual((self.repo / ".beads" / "issues.jsonl").read_bytes(), issues_before)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = self.json_result(result)
        self.assertEqual(payload["summary"], {"checked": 1, "passed": 1, "refused": 0})
        self.assertEqual([row["bead_id"] for row in payload["results"]], ["newer-close"])


if __name__ == "__main__":
    unittest.main()
