#!/usr/bin/env python3
"""Standalone reproduction: jev-align's GEPA objective is flat at F1 = 0.

WHAT THIS SHOWS
---------------
`F1BatchEvaluator.__call__` (src/jev_align/optimizer.py:216) assigns the
BATCH-level score to every row it returns. GEPA's default acceptance criterion
(`strict_improvement`, selected at optimizer.py:369) sums those per-row scores:

    gepa/strategies/acceptance.py:50-53
        old_sum = sum(proposal.subsample_scores_before or [])
        new_sum = sum(proposal.subsample_scores_after or [])
        return new_sum > old_sum

So acceptance collapses to "did batch F1 go up". A child candidate that fixes
rows the parent got wrong -- but does not manufacture a true positive -- keeps
F1 = 0 and is rejected, even though it is strictly more correct on the batch.
The per-row signal that would break the tie (`row_score`, optimizer.py:195-214)
is computed in the same loop and carried only as feedback text
(optimizer.py:244), never as the scalar GEPA climbs.

PREREQUISITES
-------------
  pip install "jev-align==0.1.2"      (pulls gepa[full]>=0.1.4,<0.2)

No API keys. No network. No dataset files. Nothing from any private repo.
The evaluation backend and the reflection LM are both local stubs, so the run
is deterministic and free.

  python3 flat-objective-repro.py

EXIT CODE
---------
0 if the defect reproduced (child rejected, one candidate at the end).
1 if it did NOT reproduce (which would retract the report).
"""

from __future__ import annotations

import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from jev_align.backends import BackendCapabilities
from jev_align.metrics import binary_metrics
from jev_align.models import CandidateSpec, Prediction, Story, TaskSpec
from jev_align.optimizer import F1BatchEvaluator, optimize_candidate

# --- A six-row binary problem with two positives -----------------------------
# Gold: rows 0 and 1 are True; rows 2..5 are False.
GOLD = [True, True, False, False, False, False]

STORIES = {
    f"s{index}": Story(
        id=f"s{index}", row_number=index, fields={"text": f"row {index}"}
    )
    for index in range(len(GOLD))
}

EXAMPLES = [
    {
        "story_id": f"s{index}",
        "label": label,
        "rationale": "fixture label",
        "round_number": 1,
    }
    for index, label in enumerate(GOLD)
]

SEED = CandidateSpec(
    instructions="SEED: decide whether the row is interesting.",
    true_criteria="SEED: the row is interesting.",
    false_criteria="SEED: the row is not interesting.",
)


def predict(candidate: TaskSpec, stories: Sequence[Story]) -> list[Prediction]:
    """Stub backend.

    Seed candidate  -> True on the four negatives, False on the two positives.
                       tp=0 fp=4 fn=2  ->  F1 = 0.0   rows correct = 0/6
    Any mutation    -> False everywhere.
                       tp=0 fp=0 fn=2  ->  F1 = 0.0   rows correct = 4/6

    The mutation is strictly better on four rows and worse on none. Both score
    F1 = 0 because neither produces a true positive.
    """
    is_seed = candidate.as_gepa() == SEED.as_gepa()
    out = []
    for story in stories:
        index = STORIES[story.id].row_number
        if is_seed:
            probability = 0.1 if GOLD[index] else 0.9
        else:
            probability = 0.1
        out.append(Prediction(story_id=story.id, probability=probability))
    return out


class StubBackend:
    backend_id = "stub"
    display_name = "stub"
    model = "stub"
    capabilities = BackendCapabilities(
        task_types=frozenset({"binary"}),
        uncertainty={"binary": "calibrated_probability"},
    )

    def __init__(self) -> None:
        self.calls = 0

    def evaluate_many(
        self, candidate: TaskSpec, stories: Sequence[Story]
    ) -> list[Prediction]:
        self.calls += 1
        return predict(candidate, stories)


def stub_reflection_lm(prompt: str) -> str:
    """Always propose the same improvement. GEPA extracts the fenced block."""
    del prompt
    return "```\nMUTATED: never claim the row is interesting.\n```"


def row_correctness(candidate: TaskSpec) -> list[int]:
    predictions = predict(
        candidate, [STORIES[example["story_id"]] for example in EXAMPLES]
    )
    return [
        int((prediction.probability >= 0.5) == bool(example["label"]))
        for prediction, example in zip(predictions, EXAMPLES, strict=True)
    ]


def batch_f1(candidate: TaskSpec) -> float:
    predictions = predict(
        candidate, [STORIES[example["story_id"]] for example in EXAMPLES]
    )
    return binary_metrics(
        [bool(example["label"]) for example in EXAMPLES],
        [prediction.probability >= 0.5 for prediction in predictions],
    ).f1


def main() -> int:
    mutated = CandidateSpec(
        instructions="MUTATED: never claim the row is interesting.",
        true_criteria="MUTATED: never claim the row is interesting.",
        false_criteria="MUTATED: never claim the row is interesting.",
    )

    print("=" * 74)
    print("PART 1  What the evaluator returns per row")
    print("=" * 74)
    evaluator = F1BatchEvaluator(StubBackend(), STORIES, SEED)
    for name, candidate in (("seed", SEED), ("child", mutated)):
        results = evaluator([(candidate.as_gepa(), example) for example in EXAMPLES])
        scores = [round(score, 6) for score, _ in results]
        feedback_rows = [feedback["scores"]["correct"] for _, feedback in results]
        print(f"\n{name}:")
        print(f"  batch F1                       = {batch_f1(candidate):.3f}")
        print(
            f"  rows actually correct          = {row_correctness(candidate)}"
            f"  ({sum(row_correctness(candidate))}/6)"
        )
        print(f"  per-row scores GEPA receives   = {scores}")
        print(
            f"  per-row correctness, feedback  = {feedback_rows}   <- computed, then discarded"
        )

    print()
    print("=" * 74)
    print("PART 2  What GEPA's acceptance criterion does with them")
    print("=" * 74)
    from gepa.strategies.acceptance import StrictImprovementAcceptance

    class Proposal:
        def __init__(self, before, after):
            self.subsample_scores_before = before
            self.subsample_scores_after = after

    acceptance = StrictImprovementAcceptance()
    shipped_before = [
        score for score, _ in evaluator([(SEED.as_gepa(), e) for e in EXAMPLES])
    ]
    shipped_after = [
        score for score, _ in evaluator([(mutated.as_gepa(), e) for e in EXAMPLES])
    ]
    honest_before = [float(v) for v in row_correctness(SEED)]
    honest_after = [float(v) for v in row_correctness(mutated)]

    shipped = acceptance.should_accept(Proposal(shipped_before, shipped_after), None)
    honest = acceptance.should_accept(Proposal(honest_before, honest_after), None)
    print(
        f"  as shipped (batch F1 per row): {sum(shipped_before)} -> {sum(shipped_after)}"
        f"   accept={shipped}"
    )
    print(
        f"  with true per-row correctness: {sum(honest_before)} -> {sum(honest_after)}"
        f"   accept={honest}"
    )

    print()
    print("=" * 74)
    print("PART 3  End to end through jev_align.optimizer.optimize_candidate")
    print("=" * 74)
    backend = StubBackend()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        outcome = optimize_candidate(
            seed_candidate=SEED,
            examples=EXAMPLES,
            stories=STORIES,
            backend=backend,
            reflection_model=stub_reflection_lm,
            metric_budget=120,
            output_dir=root / "out",
            run_dir=root / "run",
            round_number=1,
            concurrency=1,
            seed=0,
        )
    unchanged = outcome.candidate.as_gepa() == SEED.as_gepa()
    print(f"  metric calls spent   : {outcome.total_metric_calls}")
    print(f"  backend batches      : {backend.calls}")
    print(f"  candidates kept      : {outcome.metadata['num_candidates']}")
    print(f"  best score           : {outcome.best_score}")
    print(
        f"  question changed?    : {'NO - byte-identical to the seed' if unchanged else 'yes'}"
    )

    reproduced = (
        shipped is False
        and honest is True
        and unchanged
        and outcome.metadata["num_candidates"] == 1
    )
    print()
    print("REPRODUCED" if reproduced else "DID NOT REPRODUCE")
    return 0 if reproduced else 1


if __name__ == "__main__":
    sys.exit(main())
