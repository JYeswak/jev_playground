import importlib.util
import subprocess
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("fleet-idle-watch.py")
SPEC = importlib.util.spec_from_file_location("fleet_idle_watch", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"cannot load watcher module from {SCRIPT}")
watch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(watch)


class HookLoadWatchTests(unittest.TestCase):
    def test_failed_load_check_pages_and_reports_failure(self):
        pages = []
        result = subprocess.CompletedProcess([], 1, "HOOK_LOAD_FAIL hooks/post/bad.ts", "")
        note = watch.hook_load_round(
            repo=Path("/repo"),
            home=Path("/home/agent"),
            run=lambda *_args, **_kwargs: result,
            pager=pages.append,
        )
        self.assertEqual(len(pages), 1)
        self.assertIn("HOOK LOAD FAILURE", pages[0])
        self.assertIn("bad.ts", pages[0])
        self.assertIn("FAILURE", note)

    def test_healthy_load_check_is_silent(self):
        pages = []
        result = subprocess.CompletedProcess([], 0, "HOOK_LOAD_OK files=4", "")
        note = watch.hook_load_round(
            repo=Path("/repo"),
            home=Path("/home/agent"),
            run=lambda *_args, **_kwargs: result,
            pager=pages.append,
        )
        self.assertIsNone(note)
        self.assertEqual(pages, [])

    def test_checker_timeout_is_paged(self):
        pages = []

        def timeout(args, **_kwargs):
            raise subprocess.TimeoutExpired(args, 8)

        note = watch.hook_load_round(
            repo=Path("/repo"), home=Path("/home/agent"), run=timeout, pager=pages.append
        )
        self.assertEqual(len(pages), 1)
        self.assertIn("timeout", pages[0].lower())
        self.assertIn("FAILURE", note)


if __name__ == "__main__":
    unittest.main()
