#!/usr/bin/env python3
"""Keyless tests for the shared checkpoint/resume runner."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from kit.experiment.run import run

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "kit" / "experiment" / "run.py"


class SharedRunnerTest(unittest.TestCase):
    def test_appends_fsync_rows_and_skips_completed_ids(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            seen: list[str] = []

            async def fn(item: dict[str, str]) -> dict[str, str]:
                seen.append(item["id"])
                return {"value": item["value"]}

            asyncio.run(
                run([{"id": "a", "value": "A"}, {"id": "b", "value": "B"}], fn, path)
            )
            asyncio.run(
                run([{"id": "a", "value": "A"}, {"id": "b", "value": "B"}], fn, path)
            )

            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([row["id"] for row in rows], ["a", "b"])
            self.assertEqual(seen, ["a", "b"])

    def test_trailing_partial_line_is_dropped_before_resume(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            path.write_text('{"id":"a","value":"A"}\n{"id":"broken"')

            async def fn(item: dict[str, str]) -> dict[str, str]:
                return {"value": item["value"]}

            asyncio.run(
                run([{"id": "a", "value": "A"}, {"id": "b", "value": "B"}], fn, path)
            )
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([row["id"] for row in rows], ["a", "b"])

    def test_interruption_leaves_completed_rows_resumable(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            interrupted = True

            async def stop_once(item: dict[str, str]) -> dict[str, str]:
                nonlocal interrupted
                if item["id"] == "b" and interrupted:
                    interrupted = False
                    raise KeyboardInterrupt
                return {"value": item["value"]}

            with self.assertRaises(KeyboardInterrupt):
                asyncio.run(
                    run(
                        [{"id": "a", "value": "A"}, {"id": "b", "value": "B"}],
                        stop_once,
                        path,
                    )
                )

            async def finish(item: dict[str, str]) -> dict[str, str]:
                return {"value": item["value"]}

            asyncio.run(
                run(
                    [{"id": "a", "value": "A"}, {"id": "b", "value": "B"}], finish, path
                )
            )
            self.assertEqual(
                [json.loads(line)["id"] for line in path.read_text().splitlines()],
                ["a", "b"],
            )

    def test_detached_refuses_omp_child_without_attached_override(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pid_path = root / "runner.pid"
            heartbeat_path = root / "runner.heartbeat"
            env = {**os.environ, "OMP_SESSION_ID": "test-session"}
            refused = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--detach",
                    "--pid-file",
                    str(pid_path),
                    "--heartbeat-file",
                    str(heartbeat_path),
                    "--",
                    sys.executable,
                    "-c",
                    "pass",
                ],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("refusing detached launch from an omp pane", refused.stderr)

    def test_detached_writes_pid_and_heartbeat(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pid_path = root / "runner.pid"
            heartbeat_path = root / "runner.heartbeat"
            command = [
                sys.executable,
                str(RUNNER),
                "--detach",
                "--attached",
                "--pid-file",
                str(pid_path),
                "--heartbeat-file",
                str(heartbeat_path),
                "--",
                sys.executable,
                "-c",
                "import time; time.sleep(0.2)",
            ]
            started = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
            self.assertEqual(started.returncode, 0, started.stderr)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and not heartbeat_path.exists():
                time.sleep(0.01)
            self.assertTrue(pid_path.exists())
            self.assertTrue(heartbeat_path.exists())
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and heartbeat_path.exists():
                if "stopped" in heartbeat_path.read_text():
                    break
                time.sleep(0.02)
            self.assertIn("stopped", heartbeat_path.read_text())


if __name__ == "__main__":
    unittest.main()
