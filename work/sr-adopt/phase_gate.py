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
