"""PokéJev search policy: pure functions, stdlib only, tested offline in test_policy.py.

Constants are the Stage B preregistration's (docs/demos/upstream-repro/pokejev-stage-b-20260925.md).
"""

from __future__ import annotations

import math

K_PLAYER = 3
K_OPP = 4
OPP_MASS = 0.8
SUM_TOLERANCE = 0.02


def validated(
    probabilities: dict[str, float], display: dict[str, str]
) -> dict[str, float]:
    """Map a Jev distribution back to option keys, or refuse it (jev-ultrafast validate_choice rules).

    Refuses with ValueError, so the decision falls back and nothing Jev said is played, when the labels
    are not exactly the options asked, a value is non-finite or outside [0, 1], or the sum is off by
    SUM_TOLERANCE or more.
    """
    inv = {v: k for k, v in display.items()}
    if set(probabilities) != set(inv):
        raise ValueError(
            "answer labels differ from the options asked; no action from it"
        )
    out = {inv[d]: float(p) for d, p in probabilities.items()}
    if not all(math.isfinite(p) and 0.0 <= p <= 1.0 for p in out.values()):
        raise ValueError("answer has a probability outside [0, 1]; no action from it")
    if abs(sum(out.values()) - 1.0) >= SUM_TOLERANCE:
        raise ValueError("answer probabilities do not sum to 1; no action from it")
    return out


def pick_opponent(
    probs: dict[str, float], mass: float = OPP_MASS, k: int = K_OPP
) -> dict[str, float]:
    """Highest-probability opponent actions until `mass` is covered, at most k, renormalized."""
    out: dict[str, float] = {}
    total = 0.0
    for key, p in sorted(probs.items(), key=lambda kv: (-kv[1], kv[0])):
        if len(out) >= k or (out and total >= mass):
            break
        out[key] = p
        total += p
    z = sum(out.values())
    if z <= 0:
        return {key: 1.0 / len(out) for key in out}
    return {key: p / z for key, p in out.items()}


def pick_player(
    prior: dict[str, float], tool_key: str | None, k: int = K_PLAYER
) -> list[str]:
    """The prior's top k actions, plus PokéChamp's damage-calculator move if it is legal and not already in."""
    ranked = [key for key, _ in sorted(prior.items(), key=lambda kv: (-kv[1], kv[0]))]
    out = ranked[:k]
    if tool_key and tool_key in prior and tool_key not in out:
        out.append(tool_key)
    return out


def expectimax(
    cands: list[str],
    opp: dict[str, float],
    best_given: dict[str, dict[str, float]],
    prior: dict[str, float],
) -> tuple[str, dict[str, float]]:
    """value(a) = sum_o P(o) * P(a best | o); a missing leaf answer counts as 0; the prior breaks ties."""
    values = {
        a: sum(w * best_given.get(o, {}).get(a, 0.0) for o, w in opp.items())
        for a in cands
    }
    best = max(cands, key=lambda a: (round(values[a], 9), prior.get(a, 0.0), a))
    return best, values
