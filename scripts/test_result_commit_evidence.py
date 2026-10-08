from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "result_commit_evidence.py"
TMP_ROOT = Path(os.environ["TMPDIR"])


def new_repo() -> tuple[Path, dict[str, str]]:
    repo = Path(tempfile.mkdtemp(prefix="jev-oh7c-test.", dir=TMP_ROOT))
    (repo / ".owner").write_text(
        f"pid={os.getpid()}\nlabel=jev-oh7c-test\nrepo={ROOT}\ncreated={datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    subprocess.run(["git", "init", "--quiet", "--template=", str(repo)], check=True, env=env, timeout=10)
    return repo, env


def git(repo: Path, env: dict[str, str], *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True, timeout=10)


def stage(repo: Path, env: dict[str, str], *paths: str) -> None:
    git(repo, env, "add", "--", *paths)


def evidence_files(
    repo: Path, rows_path: str = "work/sample/rows.jsonl"
) -> tuple[str, str, str, str]:
    scorer_path = "work/sample/score.py"
    split_path = "work/sample/PREREG.md"
    rows = (
        json.dumps(
            {
                "n": 0,
                "label": "ign",
                "status": "ok",
                "noul": 0.5,
                "pred": "ign",
                "valid": True,
                "input_tokens": 1,
                "latency_ms": 1,
            },
            sort_keys=True,
        )
        + "\n"
    )
    scorer = "def score(row):\n    return row['pred'] == row['label']\n"
    split = "Split: held-out=1. Seed: 47.\n"
    files = ((rows_path, rows), (scorer_path, scorer), (split_path, split))
    for path, content in files:
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    hashes = [hashlib.sha256(content.encode("utf-8")).hexdigest() for _, content in files]
    manifest = (
        f"Evidence: per-call rows: `{rows_path}`@{hashes[0]}; "
        f"scorer: `{scorer_path}`@{hashes[1]}; "
        f"split/seed: `{split_path}`@{hashes[2]}"
    )
    return rows_path, scorer_path, split_path, manifest

def result_metadata(
    repo: Path, *, include_timestamp: bool = True, include_bar_hash: bool = True
) -> tuple[str, str]:
    bar_path = "work/sample/BAR.md"
    content = "# Frozen bar\nAccuracy >= 0.9.\n"
    target = repo / bar_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    fields = []
    if include_timestamp:
        fields.append("ts=2026-10-06T20:00:00Z")
    if include_bar_hash:
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        fields.append(f"bar file: `{bar_path}`@{digest}")
    return f"Measurement: {'; '.join(fields)}", bar_path



def commit(repo: Path, env: dict[str, str], message: str) -> None:
    git(
        repo,
        env,
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "--quiet",
        "-m",
        message,
    )


def run_checker(
    repo: Path, env: dict[str, str], commit_ref: str | None = None
) -> subprocess.CompletedProcess[str]:
    mode = ["--staged"] if commit_ref is None else ["--commit", commit_ref]
    return subprocess.run(
        [sys.executable, str(CHECKER), *mode],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )


class ResultCommitEvidenceTests(unittest.TestCase):
    def test_result_row_without_sources_is_refused_by_category(self) -> None:
        repo, env = new_repo()
        (repo / "EVAL.md").write_text(
            "## 2026-10-03 sample\n\n- **Result:** accuracy 4/10; FAIL.\n",
            encoding="utf-8",
        )
        stage(repo, env, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing=per-call rows,scorer,split/seed", result.stderr)

    def test_result_row_with_committed_hashed_sources_passes(self) -> None:
        repo, env = new_repo()
        metadata, bar_path = result_metadata(repo)
        rows, scorer, split, manifest = evidence_files(
            repo, "work/sample/labels-50.jsonl"
        )
        (repo / "EVAL.md").write_text(
            f"## 2026-10-03 sample\n\n- **Result:** accuracy 1/1; PASS.\n- {manifest}\n- {metadata}\n",
            encoding="utf-8",
        )
        stage(repo, env, rows, scorer, split, bar_path, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("result-commit-evidence PASS", result.stdout)

    def test_result_row_without_timestamp_is_refused(self) -> None:
        repo, env = new_repo()
        rows, scorer, split, manifest = evidence_files(repo)
        metadata, bar_path = result_metadata(repo, include_timestamp=False)
        (repo / "EVAL.md").write_text(
            f"## 2026-10-03 sample\n\n- **Result:** accuracy 1/1; PASS.\n- {manifest}\n- {metadata}\n",
            encoding="utf-8",
        )
        stage(repo, env, rows, scorer, split, bar_path, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing=timestamp", result.stderr)

    def test_result_row_without_bar_hash_is_refused(self) -> None:
        repo, env = new_repo()
        rows, scorer, split, manifest = evidence_files(repo)
        metadata, bar_path = result_metadata(repo, include_bar_hash=False)
        (repo / "EVAL.md").write_text(
            f"## 2026-10-03 sample\n\n- **Result:** accuracy 1/1; PASS.\n- {manifest}\n- {metadata}\n",
            encoding="utf-8",
        )
        stage(repo, env, rows, scorer, split, bar_path, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing=bar file", result.stderr)

    def test_committed_sources_can_be_referenced_from_a_later_result_commit(self) -> None:
        repo, env = new_repo()
        rows, scorer, split, manifest = evidence_files(repo)
        metadata, bar_path = result_metadata(repo)
        stage(repo, env, rows, scorer, split, bar_path)
        commit(repo, env, "evidence sources [test]")
        (repo / "EVAL.md").write_text(
            f"## 2026-10-03 sample\n\n- **Result:** accuracy 1/1; PASS.\n- {manifest}\n- {metadata}\n",
            encoding="utf-8",
        )
        stage(repo, env, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_historical_commit_replay_uses_committed_tree(self) -> None:
        repo, env = new_repo()
        (repo / "README.md").write_text("baseline\n", encoding="utf-8")
        stage(repo, env, "README.md")
        commit(repo, env, "baseline [test]")
        (repo / "EVAL.md").write_text(
            "## 2026-10-03 sample\n\n- **Result:** accuracy 4/10; FAIL.\n",
            encoding="utf-8",
        )
        stage(repo, env, "EVAL.md")
        commit(repo, env, "record result [receipt]")

        result = run_checker(repo, env, "HEAD")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing=per-call rows,scorer,split/seed", result.stderr)

    def test_labels_result_file_without_evidence_is_refused(self) -> None:
        repo, env = new_repo()
        rows_path, _, _, _ = evidence_files(repo, "work/sample/labels-50.jsonl")
        stage(repo, env, rows_path)

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing=per-call rows,scorer,split/seed", result.stderr)

    def test_live_result_rows_and_done_manifest_pass_as_one_commit(self) -> None:
        repo, env = new_repo()
        rows_path = "work/sample/labels-50.jsonl"
        _, scorer_path, split_path, manifest = evidence_files(repo, rows_path)
        metadata, bar_path = result_metadata(repo)
        done = repo / "work" / "sample" / "DONE.md"
        done.write_text(
            f"# DONE\n\nResult: accuracy 1/1 PASS.\n{manifest}\n{metadata}\n",
            encoding="utf-8",
        )
        stage(repo, env, rows_path, scorer_path, split_path, bar_path, "work/sample/DONE.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unlabelled_eval_metric_is_still_a_result_change(self) -> None:
        repo, env = new_repo()
        (repo / "EVAL.md").write_text(
            "## 2026-10-03 census\n\n- Census: 1,239 files / 139,018 turns; top-3 identical.\n",
            encoding="utf-8",
        )
        stage(repo, env, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_done_python_file_is_not_a_result(self) -> None:
        repo, env = new_repo()
        source = repo / "work" / "sample" / "done.py"
        source.parent.mkdir(parents=True)
        source.write_text("def done():\n    return None\n", encoding="utf-8")
        stage(repo, env, "work/sample/done.py")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_docs_only_eval_heading_without_numbers_passes(self) -> None:
        repo, env = new_repo()
        (repo / "EVAL.md").write_text(
            "## Clarification about the PASS label\n\n"
            "This note explains the boundary of the existing evaluation.\n",
            encoding="utf-8",
        )
        stage(repo, env, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no-result-changes", result.stdout)


    def test_hashed_malformed_row_data_is_refused(self) -> None:
        repo, env = new_repo()
        rows, scorer, split, manifest = evidence_files(repo)
        rows_file = repo / rows
        old_hash = hashlib.sha256(rows_file.read_bytes()).hexdigest()
        invalid_rows = b'{"call_id":\n'
        rows_file.write_bytes(invalid_rows)
        manifest = manifest.replace(
            old_hash, hashlib.sha256(invalid_rows).hexdigest(), 1
        )
        (repo / "EVAL.md").write_text(
            f"## 2026-10-03 sample\n\n- **Result:** 1/1 PASS.\n- {manifest}\n",
            encoding="utf-8",
        )
        stage(repo, env, rows, scorer, split, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("per-call rows:not-row-data", result.stderr)

    def test_wrong_source_hash_is_refused(self) -> None:
        repo, env = new_repo()
        rows, scorer, split, manifest = evidence_files(repo)
        bad_hash = "0" * 64
        manifest = manifest.replace(manifest.split("@")[1].split(";")[0], bad_hash, 1)
        (repo / "EVAL.md").write_text(
            f"## 2026-10-03 sample\n\n- **Result:** 1/1 PASS.\n- {manifest}\n",
            encoding="utf-8",
        )
        stage(repo, env, rows, scorer, split, "EVAL.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("sha256-mismatch", result.stderr)

    def test_done_result_file_without_sources_is_refused(self) -> None:
        repo, env = new_repo()
        target = repo / "work" / "sample" / "DONE.md"
        target.parent.mkdir(parents=True)
        target.write_text("# DONE\n\nResult: 9/10 PASS.\n", encoding="utf-8")
        stage(repo, env, "work/sample/DONE.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("work/sample/DONE.md", result.stderr)

    def test_negative_evidence_result_requires_sources(self) -> None:
        repo, env = new_repo()
        (repo / "NEGATIVE_EVIDENCE.md").write_text(
            "## R999 — FAIL: planted result\n\n**Result:** accuracy 0/10.\n",
            encoding="utf-8",
        )
        stage(repo, env, "NEGATIVE_EVIDENCE.md")

        result = run_checker(repo, env)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("NEGATIVE_EVIDENCE.md", result.stderr)


if __name__ == "__main__":
    unittest.main()
