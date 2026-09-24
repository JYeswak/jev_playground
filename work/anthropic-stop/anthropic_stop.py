"""No Anthropic API spend on comparisons (bead jev-sybt).

Every Haiku or other Anthropic-API comparator arm calls refuse_anthropic_comparator() at its
entry, before any provider or client is constructed. It always raises: there is no override,
no environment variable and no flag. Jev arms, grok and OpenRouter arms, and the keyless scorers
never call it.

The rule is AGENTS.md "No Anthropic API spend on comparisons" (ed8ef13). Results already committed
stand; an Anthropic pairing that never ran is reported as "not run (Anthropic spend stopped)".
"""

DIRECTIVE = (
    'Joshua, 2026-09-24: "i want us to stop using haiku api credits to compare our systems, '
    "i've been charged $100 from anthropic since yesterday\""
)


class AnthropicSpendStopped(SystemExit):
    """Raised at the entry of an Anthropic-API comparator arm.

    A SystemExit, so a runner's per-row `except Exception` cannot swallow it, and the process
    exits non-zero with the message instead of a traceback.
    """


def refuse_anthropic_comparator(arm):
    """Refuse the Anthropic-API comparator arm `arm`. Always raises; there is no override."""
    raise AnthropicSpendStopped(
        f"REFUSED: {arm} is an Anthropic API comparator arm and no longer runs. {DIRECTIVE}. "
        "AGENTS.md 'No Anthropic API spend on comparisons'; report this pairing as "
        "'not run (Anthropic spend stopped)'. There is no override."
    )
