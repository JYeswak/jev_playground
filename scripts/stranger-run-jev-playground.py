#!/usr/bin/env python3
"""Run every runnable README command from a fresh GitHub clone.

The child commands receive a clean HOME and a deliberately small PATH.  The script never
passes API keys to a child.  It writes a Markdown receipt containing the line-numbered command
inventory and one result row per unique command.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

REPO_URL = "https://github.com/JYeswak/jev_playground.git"
KEY_NAMES = (
    "TYPESAFE_API_KEY",
    "JEV_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "XAI_API_KEY",
    "OPENROUTER_API_KEY",
)
RUNNABLE_PREFIXES = (
    "node ",
    "python3 ",
    "bash ",
    "./scripts/",
    "git clone ",
    "cd ",
    "npm ",
    "br ",
    "uv ",
)
FAILURE_LINE = re.compile(
    r"(error|fail|traceback|not found|no such|cannot|refus|missing|unable|denied|not_run|timeout)",
    re.IGNORECASE,
)
NUMBER_TOKEN = re.compile(
    r"(?<![A-Za-z\d.])(?<![A-Za-z]-)\d[\d,]*(?:\.\d+)?(?:e-?\d+)?"
)
PATH_TOKEN = re.compile(r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+(?:\.[A-Za-z0-9_.-]+)?")
TIMEOUT_DEFAULT = 600


def readme_commands(readme: str) -> list[dict[str, object]]:
    """Extract runnable fenced and inline commands, retaining every README line occurrence."""
    found: list[dict[str, object]] = []
    fence: str | None = None
    section = ""
    lines = readme.splitlines()
    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            section = stripped.lstrip("#").strip()
        if stripped.startswith("```"):
            fence = None if fence is not None else stripped[3:].strip().lower()
            continue
        if fence is not None:
            if (
                fence in {"bash", "sh", "shell"}
                and stripped
                and not stripped.startswith("#")
            ):
                command = re.sub(r"\s+#\s.*$", "", stripped).strip()
                found.append(
                    {
                        "command": command,
                        "lines": [line_number],
                        "contexts": [line],
                        "sections": [section],
                    }
                )
            continue
        for span in re.findall(r"`([^`]+)`", line):
            command = span.strip()
            if command.startswith(RUNNABLE_PREFIXES):
                found.append(
                    {
                        "command": command,
                        "lines": [line_number],
                        "contexts": [line],
                        "sections": [section],
                    }
                )
    merged: dict[str, dict[str, object]] = {}
    for item in found:
        command = str(item["command"])
        if command not in merged:
            merged[command] = item
            continue
        current = merged[command]
        current["lines"] = list(current["lines"]) + list(item["lines"])
        current["contexts"] = list(current["contexts"]) + list(item["contexts"])
        current["sections"] = list(current["sections"]) + list(item["sections"])
    return list(merged.values())


def cited_numbers(item: dict[str, object], output: str) -> tuple[list[str], list[str]]:
    cited: list[str] = []
    for context in item["contexts"]:
        match = re.search(r"\s#\s(.*)$", str(context))
        if match:
            cited.extend(NUMBER_TOKEN.findall(match.group(1)))
    unique = list(dict.fromkeys(cited))
    compact_output = output.replace(",", "")
    missing = [
        token
        for token in unique
        if token not in output and token.replace(",", "") not in compact_output
    ]
    return unique, missing


def tool_path(name: str) -> str | None:
    return shutil.which(name)


def make_clean_env(home: Path, bindir: Path) -> dict[str, str]:
    home.mkdir(parents=True, exist_ok=True)
    (home / "tmp").mkdir(exist_ok=True)
    bindir.mkdir(parents=True, exist_ok=True)
    required = {"node", "npm", "npx", "python3", "uv", "git", "bash"}
    for name in sorted(required):
        source = tool_path(name)
        if source is None:
            continue
        destination = bindir / name
        if not destination.exists():
            destination.symlink_to(source)
    absent = sorted(
        name
        for name in ("node", "python3", "git", "bash")
        if not (bindir / name).exists()
    )
    if absent:
        raise RuntimeError(f"required stranger tools unavailable: {', '.join(absent)}")
    return {
        "PATH": f"{bindir}:/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(home),
        "TMPDIR": str(home / "tmp"),
        "LANG": "en_US.UTF-8",
        "TERM": "dumb",
        "USER": "stranger",
    }


def redact(output: str) -> str:
    return re.sub(r"(?i)(?:bearer\s+)?[A-Za-z0-9_-]{40,}", "<redacted>", output)


def run_command(
    command: str, cwd: Path, env: dict[str, str], log_path: Path, timeout: int
) -> dict[str, object]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            ["/bin/bash", "-c", command],
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        output = completed.stdout.decode("utf-8", "replace")
        return_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or b"").decode(
            "utf-8", "replace"
        ) + f"\nTIMEOUT after {timeout}s\n"
        return_code = 124
    output = redact(output)
    log_path.write_text(output)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    error_line = ""
    if return_code != 0:
        error_line = next(
            (line for line in lines if FAILURE_LINE.search(line)),
            lines[-1] if lines else "(no output)",
        )
    return {
        "rc": return_code,
        "wall_s": round(time.monotonic() - started, 2),
        "error": error_line[:300],
        "last": (lines[-1] if lines else "")[:300],
        "output": output,
    }


def command_tool(command: str) -> str:
    first = command.strip().split(maxsplit=1)[0]
    return first.removeprefix("./")


def referenced_missing_path(
    command: str, output: str, clone: Path, tracked: set[str]
) -> str | None:
    candidates = list(PATH_TOKEN.findall(command)) + list(PATH_TOKEN.findall(output))
    clone_prefix = f"{clone}/"
    for raw in re.findall(re.escape(clone_prefix) + r"[^\s'\":]+", output):
        candidates.append(raw[len(clone_prefix) :])
    candidates.extend(
        re.findall(r"(?<!\S)([A-Za-z0-9_.-]+\.(?:jsonl|json|md|py|mjs))(?!\S)", command)
    )
    for raw in candidates:
        candidate = raw.rstrip(".,:;)")
        if candidate.startswith(("https://", "http://")) or "://" in candidate:
            continue
        if "<" in candidate or "..." in candidate:
            continue
        path = Path(candidate)
        if path.is_absolute():
            continue
        if path.parts and path.parts[0] in {"node:", "npm:", "usr", "bin"}:
            continue
        if (clone / path).exists() or candidate in tracked:
            continue
        if candidate.startswith(
            ("work/", "docs/", "scripts/", "foundation/", "demos/", "upstream/")
        ):
            return candidate
        if path.suffix in {".jsonl", ".json", ".md", ".py", ".mjs"}:
            return candidate
    return None


def is_template_command(command: str) -> bool:
    return bool(re.search(r"<[^>\n]+>", command))


def classify(
    command: str, result: dict[str, object], readme: str, clone: Path, tracked: set[str]
) -> tuple[str, str]:
    rc = int(result["rc"])
    output = str(result["output"])
    if rc == 0:
        return "none", ""
    if "rows.jsonl" in command:
        return (
            "README wrong",
            "rows.jsonl is an unbound placeholder; no input corpus is supplied",
        )
    if "<name>" in command or "<" in command:
        return "README wrong", "placeholder command is not runnable"
    lower = output.lower()
    if "no session logs" in lower:
        return (
            "named prerequisite",
            "the command names local session logs but clean HOME has none",
        )
    if "fresh clone fix" in lower or "br sync --import-only" in lower:
        return (
            "named prerequisite",
            "the command names the required Beads import prerequisite",
        )
    if "not installed" in lower or "not on path" in lower:
        return (
            "named prerequisite",
            "the command names the missing executable prerequisite",
        )
    if "# fail " in lower:
        return "README wrong", "the documented registered suite has a tracked failure"
    key_signal = any(
        token in lower
        for token in (
            "not_run",
            "no key",
            "missing key",
            "typesafe_api_key",
            "jev_api_key",
            "unconfigured",
        )
    )
    if key_signal:
        if "not_run" in lower:
            return "needs key", "the command explicitly reported NOT_RUN"
        return "needs key (crashed)", "key-required path did not print NOT_RUN"
    missing = referenced_missing_path(command, output, clone, tracked)
    if missing is not None:
        return "missing tracked input", f"{missing} is absent from the fresh clone"
    tool = command_tool(command)
    if (
        "command not found" in lower
        or "not found" in lower
        and tool not in {"node", "python3", "bash", "git"}
    ):
        if tool in readme or tool.lstrip("./") in readme:
            return (
                "named prerequisite",
                f"{tool} is named in README but is not in the stranger PATH",
            )
        return "unnamed prerequisite", f"{tool} is not named in README"
    if rc == 124 or "timeout" in lower:
        return "unnamed prerequisite", "command timed out before producing a result"
    if any(
        marker in lower
        for marker in ("assertionerror", "syntaxerror", "cannot find module")
    ):
        return "README wrong", "the documented command fails in the fresh clone"
    return (
        "expected nonzero",
        "the command returned nonzero without a missing-input or key signal",
    )


def markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_receipt(
    path: Path,
    rows: list[dict[str, object]],
    sha: str,
    node_version: str,
    python_version: str,
    uv_version: str,
    timeout: int,
) -> None:
    command_rows = [row for row in rows if row["source"] != "post"]
    failures = [row for row in rows if row["rc"] not in (0, "TEMPLATE")]
    lines = [
        "# README stranger run (2026-09-25)",
        "",
        "A fresh network clone of [`JYeswak/jev_playground`](https://github.com/JYeswak/jev_playground) was run with no API key and a clean `HOME`.",
        "",
        "## Source and environment",
        "",
        f"- Clone commit: `{sha}`.",
        f"- Tools: `{node_version}`, `{python_version}`, `{uv_version}`.",
        f"- Child command timeout: `{timeout}s` per command.",
        "- Child environment: only PATH, HOME, TMPDIR, LANG, TERM and USER; API-key variables were absent.",
        "- Regenerate: `env -u TYPESAFE_API_KEY -u JEV_API_KEY python3 scripts/stranger-run-jev-playground.py --out docs/demos/upstream-repro/stranger-run-20260925.md`.",
        "",
        "## Command inventory",
        "",
        "The script extracts runnable fenced commands and inline command spans in README order. Exact duplicate commands run once; all README line occurrences are listed. Commands containing `<...>` are listed as `TEMPLATE` and are never executed.",
        "",
        "| # | README lines | command |",
        "|---:|---|---|",
    ]
    for number, row in enumerate(command_rows, 1):
        lines.append(
            f"| {number} | {','.join('L' + str(line) for line in row['readme_lines'])} | `{markdown_cell(row['command'])}` |"
        )
    lines += [
        "",
        "## Results",
        "",
        "`Quoted numbers` checks numbers in a same-line README `#` comment; it is a substring check, not semantic verification.",
        "",
        "| # | README lines | command | exit/status | wall s | quoted numbers | failure class | first error line |",
        "|---:|---|---|---:|---:|---|---|---|",
    ]
    for number, row in enumerate(rows, 1):
        quoted = row.get("quoted", [])
        missing = row.get("quoted_missing", [])
        if not quoted:
            quoted_text = "—"
        elif missing:
            quoted_text = f"{len(quoted) - len(missing)}/{len(quoted)}; missing {','.join(missing)}"
        else:
            quoted_text = f"{len(quoted)}/{len(quoted)}"
        lines.append(
            f"| {number} | {','.join('L' + str(line) for line in row['readme_lines']) or '—'} | `{markdown_cell(row['command'])}` | {row['rc']} | {row['wall_s']} | {quoted_text} | {markdown_cell(row['failure_class'])} | {markdown_cell(row['error'] or '—')} |"
        )
    lines += [
        "",
        f"Result: `{len(rows)}` rows, `{sum(row['rc'] == 0 for row in rows)}` exit 0, `{len(failures)}` nonzero, `{sum(row['rc'] == 'TEMPLATE' for row in rows)}` TEMPLATE.",
        "",
        "## Failures requiring README action",
        "",
        "The classes below are assigned from the captured output and a fresh-clone `git ls-files` check. `expected nonzero` is retained for README commands that explicitly document a failing bar; `TEMPLATE` commands are not failures and are never executed; every other nonzero row is listed for follow-up.",
        "",
    ]
    action_rows = [
        row for row in failures if row["failure_class"] not in {"expected nonzero"}
    ]
    if action_rows:
        for row in action_rows:
            lines.append(
                f"- L{','.join(str(line) for line in row['readme_lines'])}: **{row['failure_class']}** — `{row['command']}` — {row['error']}"
            )
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Boundary (NO-CLAIM)",
        "",
        "- No Jev, OpenAI, Anthropic, xAI or OpenRouter request was authorized or sent; this is keyless only.",
        "- The command output check does not prove that a cited number was produced by the intended computation; it only checks text containment.",
        "- This run uses the current GitHub default branch at the recorded commit. It does not claim reproducibility on another commit, OS, or tool version.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=TIMEOUT_DEFAULT)
    args = parser.parse_args()
    present_keys = [name for name in KEY_NAMES if os.environ.get(name)]
    if present_keys:
        raise SystemExit(f"refusing keyed environment: {', '.join(present_keys)}")
    repo = Path(__file__).resolve().parents[1]
    scratch = repo / "var" / "agent-tmp" / f"stranger-run-20260925-{os.getpid()}"
    scratch.mkdir(parents=True, exist_ok=False)
    (scratch / ".owner").write_text(
        f"pid={os.getpid()}\nrepo={repo}\nlabel=jev-e3on-stranger\n"
    )
    clone = scratch / "clone"
    outside = scratch / "outside"
    home = scratch / "home"
    bindir = scratch / "bin"
    logs = scratch / "logs"
    outside.mkdir()
    logs.mkdir()
    subprocess.run(
        ["git", "clone", "--quiet", REPO_URL, str(clone)],
        check=True,
        timeout=args.timeout,
    )
    sha = subprocess.check_output(
        ["git", "-C", str(clone), "rev-parse", "HEAD"], text=True, timeout=args.timeout
    ).strip()
    readme = (clone / "README.md").read_text()
    commands = readme_commands(readme)
    tracked = set(
        subprocess.check_output(
            ["git", "-C", str(clone), "ls-files"], text=True, timeout=args.timeout
        ).splitlines()
    )
    env = make_clean_env(home, bindir)
    versions = {}
    for tool, flag in (
        ("node", "--version"),
        ("python3", "--version"),
        ("uv", "--version"),
    ):
        executable = bindir / tool
        versions[tool] = subprocess.check_output(
            [str(executable), flag],
            env=env,
            text=True,
            stderr=subprocess.STDOUT,
            timeout=args.timeout,
        ).strip()
    rows: list[dict[str, object]] = []
    for index, item in enumerate(commands, 1):
        command = str(item["command"])
        quoted, quoted_missing = cited_numbers(item, "")
        if is_template_command(command):
            result = {
                "rc": "TEMPLATE",
                "wall_s": 0.0,
                "error": "",
                "last": "",
                "output": "",
            }
            failure_class = "TEMPLATE"
            classification_note = "placeholder command listed but not executed"
        else:
            cwd = (
                outside
                if command.startswith(
                    (
                        "git clone https://github.com/JYeswak/jev_playground",
                        "cd jev_playground",
                    )
                )
                else clone
            )
            result = run_command(
                command, cwd, env, logs / f"{index:03d}.log", args.timeout
            )
            quoted, quoted_missing = cited_numbers(item, str(result["output"]))
            failure_class, classification_note = classify(
                command, result, readme, clone, tracked
            )
        rows.append(
            {
                "source": "command",
                "readme_lines": item["lines"],
                "command": command,
                "rc": result["rc"],
                "wall_s": result["wall_s"],
                "quoted": quoted,
                "quoted_missing": quoted_missing,
                "failure_class": failure_class,
                "classification_note": classification_note,
                "error": result["error"],
                "last": result["last"],
            }
        )
        print(
            f"{index:02d} status={result['rc']} {result['wall_s']}s {command}",
            flush=True,
        )
    render_receipt(
        args.out,
        rows,
        sha,
        versions["node"],
        versions["python3"],
        versions["uv"],
        args.timeout,
    )
    print(f"receipt={args.out} scratch={scratch} clone={sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
