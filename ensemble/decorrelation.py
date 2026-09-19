"""Does averaging two scorers pay? Measure the thing that decides it.

RECIPES.md recipe 4 says averaging a zero-label judgment with a trained classifier beat both
(98.57% / 98.57% -> 99.83% on Ling-Spam), and states its own falsifier: *"stops being true when the
two are correlated."* Upstream computes the average in one line
(upstream/bitnovus/jev-spam-eval/tfidf_baseline.py:128) and never measures the correlation, so the
recipe is currently "it worked once" rather than a rule you can apply in advance.

This measures the predicate. Given two scorers' probabilities and the truth, it reports:

  * each scorer's errors, and the SHAPE of them (false negatives vs false positives);
  * the phi coefficient between their error indicator vectors -- are they wrong on the same items?
  * the averaged scorer's accuracy, and the gain over the better input;
  * the disagreement rate, which is the budget the average has to work with.

The claim under test is mechanistic: the average pays BECAUSE the errors are decorrelated and
oppositely shaped. If phi is high, averaging should buy nothing -- and that is the planted negative
in the tests, where a scorer is averaged with itself.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScorerErrors:
    name: str
    accuracy: float
    false_negatives: int
    false_positives: int

    @property
    def errors(self) -> int:
        return self.false_negatives + self.false_positives


@dataclass(frozen=True)
class EnsembleReport:
    a: ScorerErrors
    b: ScorerErrors
    averaged: ScorerErrors
    phi: float
    disagreement_rate: float
    gain_over_best_input: float

    @property
    def verdict(self) -> str:
        """The recipe's own rule, applied. Thresholds are stated, not hidden in prose."""
        if self.gain_over_best_input <= 0:
            return "AVERAGE_DID_NOT_PAY"
        if self.phi >= 0.5:
            return "AVERAGE_PAID_DESPITE_CORRELATION"  # recipe 4 does not predict this
        return "AVERAGE_PAID_AS_PREDICTED"


def _errors(
    name: str, scores: list[float], truth: list[bool], threshold: float
) -> ScorerErrors:
    fn = sum(1 for s, t in zip(scores, truth) if t and s < threshold)
    fp = sum(1 for s, t in zip(scores, truth) if not t and s >= threshold)
    n = len(truth)
    return ScorerErrors(name, (n - fn - fp) / n if n else 0.0, fn, fp)


def _phi(x: list[bool], y: list[bool]) -> float:
    """Phi (Matthews) between two boolean vectors. 0.0 when either is constant.

    A constant vector has no variance, so correlation is undefined; returning 0.0 says "this tells
    you nothing about shared failure", which is the honest reading for a scorer that never errs.
    """
    n11 = sum(1 for a, b in zip(x, y) if a and b)
    n10 = sum(1 for a, b in zip(x, y) if a and not b)
    n01 = sum(1 for a, b in zip(x, y) if not a and b)
    n00 = sum(1 for a, b in zip(x, y) if not a and not b)
    denom = (n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00)
    if denom == 0:
        return 0.0
    return (n11 * n00 - n10 * n01) / (denom**0.5)


def analyze(
    a_scores: list[float],
    b_scores: list[float],
    truth: list[bool],
    *,
    a_name: str = "a",
    b_name: str = "b",
    threshold: float = 0.5,
) -> EnsembleReport:
    if not (len(a_scores) == len(b_scores) == len(truth)):
        raise ValueError(
            f"length mismatch: {a_name}={len(a_scores)} {b_name}={len(b_scores)} truth={len(truth)}"
        )
    if not truth:
        raise ValueError("no items to analyze")

    a = _errors(a_name, a_scores, truth, threshold)
    b = _errors(b_name, b_scores, truth, threshold)
    avg_scores = [(x + y) / 2 for x, y in zip(a_scores, b_scores)]
    averaged = _errors("averaged", avg_scores, truth, threshold)

    a_wrong = [(s >= threshold) != t for s, t in zip(a_scores, truth)]
    b_wrong = [(s >= threshold) != t for s, t in zip(b_scores, truth)]
    disagree = sum(
        1 for x, y in zip(a_scores, b_scores) if (x >= threshold) != (y >= threshold)
    ) / len(truth)

    return EnsembleReport(
        a=a,
        b=b,
        averaged=averaged,
        phi=_phi(a_wrong, b_wrong),
        disagreement_rate=disagree,
        gain_over_best_input=averaged.accuracy - max(a.accuracy, b.accuracy),
    )
