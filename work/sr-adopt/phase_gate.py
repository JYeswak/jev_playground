"""One function. An attempt before its phase panics.

Adopted from skillranker@a6f1ff0 src/adapter.rs:569 `planned`, which
composes a command with the PhaseGate it waits for. The negative arm is
the panic in tests/ledger_attempt_rows.rs:136 when the attempt is not Ready.
"""


class AttemptPanic(Exception):
    """The attempt ran before the phase it waits for."""


def composed_phase_gate(earliest, attempt):
    """Return ready, or panic. earliest and attempt are ints, P0 = 0."""
    if attempt < earliest:
        raise AttemptPanic(f"attempt {attempt} before phase {earliest}")
    return "ready"


def require_bar(bar_path, repo="."):
    """Panic unless the bar is tracked, clean, and already committed.

    A dirty or untracked bar is an attempt before the phase. The caller
    must invoke this before the first provider call.
    """
    import subprocess

    tracked = subprocess.run(
        ["git", "-C", repo, "ls-files", "--error-unmatch", "--", bar_path],
        capture_output=True,
    )
    if tracked.returncode != 0:
        raise AttemptPanic(f"bar untracked: {bar_path}")
    dirty = subprocess.run(
        ["git", "-C", repo, "diff", "--quiet", "--", bar_path],
        capture_output=True,
    )
    staged = subprocess.run(
        ["git", "-C", repo, "diff", "--cached", "--quiet", "--", bar_path],
        capture_output=True,
    )
    if dirty.returncode != 0 or staged.returncode != 0:
        raise AttemptPanic(f"bar dirty: {bar_path}")
    committed = subprocess.run(
        ["git", "-C", repo, "log", "-1", "--format=%H", "--", bar_path],
        capture_output=True,
        text=True,
    )
    if committed.returncode != 0 or not committed.stdout.strip():
        raise AttemptPanic(f"bar not committed: {bar_path}")
    return committed.stdout.strip()


def call_after_bar(bar_path, asker, repo="."):
    """The phase gate in front of a provider call. Panic means zero calls."""
    require_bar(bar_path, repo=repo)
    return asker()
