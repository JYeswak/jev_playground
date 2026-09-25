#!/usr/bin/env python3
"""Keyless tests for the post-rotation MiniWoB v3 run sheet."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / "work/miniwob-jev/run-after-rotation.sh"
FAKE_KEY = f"{'fake'}-{'run'}-{'sheet'}-{'key'}"


class RotationSheetTests(unittest.TestCase):
    def run_sheet(
        self,
        root: Path,
        *args: str,
        revoked: Path | None = None,
        mode: str = "fake",
        extra_env: dict[str, str] | None = None,
    ):
        env = os.environ.copy()
        env["TYPESAFE_API_KEY"] = FAKE_KEY
        default_venv = (
            Path(os.sep) / "tmp" / "jev-miniwob-jev" / "venv" / "bin" / "python"
        )
        candidate_value = os.environ.get("MINIWOB_TEST_VENV")
        candidate = Path(candidate_value) if candidate_value else default_venv
        env["PYTHON"] = str(candidate) if candidate.exists() else sys.executable
        if revoked is not None:
            env["KEY_STATUS_REVOKED_FILE"] = str(revoked)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ["bash", str(SHEET), f"--{mode}", "--run-root", str(root), *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_fake_sheet_runs_two_episodes_per_step(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = self.run_sheet(root, "--steps", "quoted,date_time")
            if (
                result.returncode != 0
                and "No module named 'gymnasium'" in result.stderr
            ):
                self.skipTest("prerequisite: gymnasium unavailable for rotation sheet")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout.count("KEY: OK"), 2)
            for step in ("quoted", "date_time"):
                rows = root.joinpath(f"{step}.jsonl").read_text().splitlines()
                self.assertEqual(len(rows), 2, step)
                self.assertIn("code_sha256", rows[0])
                self.assertIn("started_utc", rows[0])

    def test_revoked_fake_key_stops_at_step_one_before_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            revoked = root / "revoked.tsv"
            fingerprint = hashlib.sha256(FAKE_KEY.encode()).hexdigest()[:16]
            revoked.write_text(f"{fingerprint}\t2026-09-25\ttest revoked\n")
            result = self.run_sheet(
                root, "--steps", "quoted,date_time", revoked=revoked
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("KEY: REVOKED", result.stdout + result.stderr)
            self.assertFalse(root.joinpath("quoted.jsonl").exists())

    def test_live_sheet_all_steps_with_stub_runner(self):
        import shutil

        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            sandbox = temp_root / "repo"
            (sandbox / "scripts").mkdir(parents=True)
            (sandbox / "docs/demos/upstream-repro").mkdir(parents=True)
            shutil.copy2(
                ROOT / "scripts/key-status.py", sandbox / "scripts/key-status.py"
            )
            shutil.copy2(
                ROOT / "scripts/row-provenance-check.py",
                sandbox / "scripts/row-provenance-check.py",
            )
            shutil.copy2(
                ROOT / "docs/demos/upstream-repro/miniwob-jev-v3-prereg-20260925.md",
                sandbox / "docs/demos/upstream-repro/miniwob-jev-v3-prereg-20260925.md",
            )
            revoked = sandbox / "revoked.tsv"
            revoked.write_text("")
            stub = temp_root / "python-stub"
            stub.write_text(
                "#!/usr/bin/env python3\n"
                "import json, pathlib, sys, os\n"
                "args=sys.argv[1:]\n"
                "if '--out' in args:\n"
                "    out=pathlib.Path(args[args.index('--out')+1])\n"
                "else:\n"
                "    label=args[args.index('--label')+1]\n"
                "    out=pathlib.Path(os.environ['REPO_ROOT']) / ('work/miniwob-jev/rows/miniwob-jev-'+label+'.s0.jsonl')\n"
                "out.parent.mkdir(parents=True, exist_ok=True)\n"
                "out.write_text(json.dumps({'task':'stub','seed':1,'rep':0,'success':1.0,'run_py_sha256':'a'*64,'started_utc':'2026-09-25T12:00:00Z','finished_utc':'2026-09-25T12:00:01Z'})+'\\n')\n"
            )
            stub.chmod(0o755)
            result = self.run_sheet(
                sandbox / "run",
                "--steps",
                "quoted,date_time,page_text,color,drag,none,combined",
                mode="live",
                extra_env={
                    "REPO_ROOT": str(sandbox),
                    "PYTHON": str(stub),
                    "KEY_STATUS_REVOKED_FILE": str(revoked),
                },
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ROTATION SHEET COMPLETE", result.stdout)
        self.assertEqual(result.stdout.count("KEY: OK"), 7)
        self.assertEqual(result.stdout.count("provenance:"), 7)

    def test_live_stale_label_requires_resume(self):
        import shutil

        with tempfile.TemporaryDirectory() as temp:
            sandbox = Path(temp) / "repo"
            (sandbox / "scripts").mkdir(parents=True)
            shutil.copy2(
                ROOT / "scripts/key-status.py", sandbox / "scripts/key-status.py"
            )
            revoked = sandbox / "revoked.tsv"
            revoked.write_text("")
            label = sandbox / "work/miniwob-jev/rows/miniwob-jev-v3-quoted.s0.jsonl"
            label.parent.mkdir(parents=True)
            label.write_text("stale\n")
            result = self.run_sheet(
                sandbox / "run",
                "--steps",
                "quoted",
                mode="live",
                extra_env={
                    "REPO_ROOT": str(sandbox),
                    "PYTHON": "/bin/false",
                    "KEY_STATUS_REVOKED_FILE": str(revoked),
                },
            )
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        self.assertIn("refusing existing live output", result.stderr)

    def test_live_stale_heldout_requires_resume(self):
        import shutil

        with tempfile.TemporaryDirectory() as temp:
            sandbox = Path(temp) / "repo"
            (sandbox / "scripts").mkdir(parents=True)
            shutil.copy2(
                ROOT / "scripts/key-status.py", sandbox / "scripts/key-status.py"
            )
            revoked = sandbox / "revoked.tsv"
            revoked.write_text("")
            label = sandbox / "work/miniwob-jev/rows/miniwob-jev-v3-heldout.s0.jsonl"
            label.parent.mkdir(parents=True)
            label.write_text("stale\n")
            result = self.run_sheet(
                sandbox / "run",
                "--steps",
                "combined",
                mode="live",
                extra_env={
                    "REPO_ROOT": str(sandbox),
                    "PYTHON": "/bin/false",
                    "KEY_STATUS_REVOKED_FILE": str(revoked),
                },
            )
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        self.assertIn("refusing existing live output", result.stderr)


if __name__ == "__main__":
    unittest.main()
