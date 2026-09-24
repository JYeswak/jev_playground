"""No paid comparisons (beads jev-sybt, jev-lbgk).

Every paid comparator arm calls refuse_paid_comparator() at its
entry, before any provider or client is constructed: an Anthropic model (Haiku or other), an xAI
model (grok-*, XAI_API_KEY, api.x.ai), or an OpenRouter model id without ':free'.
It always raises: there is no override, no environment variable and no flag. An OpenRouter arm
whose model id is data calls
require_free_comparator(model, arm), which returns for a ':free' id and refuses any other id.
Jev arms (the system under test), ':free' OpenRouter arms, and the keyless scorers never refuse.

The rule is AGENTS.md "No paid comparisons" (1cc7876). Results already committed stand; a paid
pairing that never ran is reported as "not run (paid comparisons stopped 2026-09-24)".
"""

DIRECTIVE = (
    'Joshua, 2026-09-24: "i want us to stop using haiku api credits to compare our systems, '
    "i've been charged $100 from anthropic since yesterday\", then \"we're not going to use any "
    'of the paid comparisons"'
)


class PaidComparisonStopped(SystemExit):
    """Raised at the entry of a paid comparator arm.

    A SystemExit, so a runner's per-row `except Exception` cannot swallow it, and the process
    exits non-zero with the message instead of a traceback.
    """


def refuse_paid_comparator(arm):
    """Refuse the paid comparator arm `arm`. Always raises; there is no override."""
    raise PaidComparisonStopped(
        f"REFUSED: {arm} is a paid comparator arm and no longer runs. {DIRECTIVE}. "
        "AGENTS.md 'No paid comparisons': a comparator is a free OpenRouter model (a ':free' id) "
        "or nothing. Report this pairing as 'not run (paid comparisons stopped 2026-09-24)'. "
        "There is no override."
    )


def require_free_comparator(model, arm):
    """Return if `model` is a ':free' OpenRouter id; refuse the arm otherwise."""
    if not model.endswith(":free"):
        refuse_paid_comparator(f"{arm} ({model})")
