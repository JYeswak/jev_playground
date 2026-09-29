from __future__ import annotations

import hashlib
import sys
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from adapter_runner import JEV_MODEL, pair_inputs


def _row(
    set_name: str, base_index: int, position: str | None, message: str
) -> tuple[dict, dict]:
    item_id = f"{set_name}-{base_index}-{position or 'only'}"
    input_hash = hashlib.sha256(message.encode("utf-8")).hexdigest()
    item = {
        "id": item_id,
        "set": set_name,
        "baseIndex": base_index,
        "position": position,
        "excluded": False,
        "inputSha256": input_hash,
    }
    state = {
        "id": item_id,
        "state": {"assistant": "recorded assistant", "user_message": message},
    }
    return item, state


def test_rescore_planning_includes_exact_state_rows_without_jev_answers() -> None:
    matched_item, matched_state = _row("clean", 0, None, "captured tool output A")
    missing_item, missing_state = _row("clean", 1, None, "captured tool output B")
    existing = {
        "set": "clean",
        "baseIndex": 0,
        "position": None,
        "inputSha256": matched_item["inputSha256"],
        "status": "answered",
        "model": JEV_MODEL,
        "p": 0.1,
        "flag": False,
    }

    pairs, counts = pair_inputs(
        [matched_item, missing_item],
        [matched_state, missing_state],
        [existing],
        [],
        "recorded assistant",
        include_unmatched=True,
    )

    assert [pair["item"]["id"] for pair in pairs] == [
        matched_item["id"],
        missing_item["id"],
    ]
    assert pairs[0]["jev"] == existing
    assert pairs[1]["jev"] is None
    assert pairs[1]["state"]["user_message"] == "captured tool output B"
    assert counts["clean_matched"] == 1
    assert counts["missing_jev_rows"] == 1


def test_default_pairing_stays_matched_only_for_free_arm() -> None:
    matched_item, matched_state = _row("clean", 0, None, "captured tool output A")
    missing_item, missing_state = _row("clean", 1, None, "captured tool output B")
    existing = {
        "set": "clean",
        "baseIndex": 0,
        "position": None,
        "inputSha256": matched_item["inputSha256"],
        "status": "answered",
        "model": JEV_MODEL,
        "p": 0.1,
        "flag": False,
    }

    pairs, counts = pair_inputs(
        [matched_item, missing_item],
        [matched_state, missing_state],
        [existing],
        [],
        "recorded assistant",
    )

    assert [pair["item"]["id"] for pair in pairs] == [matched_item["id"]]
    assert counts["missing_jev_rows"] == 1


def test_response_from_unpinned_model_cannot_enter_the_jev_baseline() -> None:
    try:
        module = import_module("jev_baseline")
    except ModuleNotFoundError as error:
        pytest.fail(f"same-state Jev response validator is missing: {error}")

    response = SimpleNamespace(
        model="jev-latest",
        nouls={"injection": SimpleNamespace(noul=0.8)},
        usage=SimpleNamespace(input_tokens=12, output_tokens=3),
    )
    with pytest.raises(ValueError):
        module.extract_answer(response, question_id="injection")


def test_missing_input_token_usage_cannot_be_reported_as_zero_spend() -> None:
    try:
        module = import_module("jev_baseline")
    except ModuleNotFoundError as error:
        pytest.fail(f"same-state Jev response validator is missing: {error}")

    response = SimpleNamespace(
        model=JEV_MODEL,
        nouls={"injection": SimpleNamespace(noul=0.8)},
        usage=SimpleNamespace(input_tokens=None, output_tokens=3),
    )
    with pytest.raises(ValueError):
        module.extract_answer(response, question_id="injection")


def test_stale_same_key_answer_is_included_in_rescore_candidates() -> None:
    item, state = _row("clean", 0, None, "current redacted tool output")
    stale_answer = {
        "set": "clean",
        "baseIndex": 0,
        "position": None,
        "inputSha256": hashlib.sha256(b"different recorded input").hexdigest(),
        "status": "answered",
        "model": JEV_MODEL,
        "p": 0.8,
        "flag": True,
    }

    pairs, counts = pair_inputs(
        [item],
        [state],
        [stale_answer],
        [],
        "recorded assistant",
        include_unmatched=True,
    )

    assert [pair["item"]["id"] for pair in pairs] == [item["id"]]
    assert pairs[0]["jev"] is None
    assert counts["input_hash_mismatches"] == 1


def test_exact_rescore_answer_replaces_stale_same_key_answer() -> None:
    item, state = _row("clean", 0, None, "current redacted tool output")
    stale_answer = {
        "set": "clean",
        "baseIndex": 0,
        "position": None,
        "inputSha256": hashlib.sha256(b"different recorded input").hexdigest(),
        "status": "answered",
        "model": JEV_MODEL,
        "p": 0.8,
        "flag": True,
    }
    rescore_answer = {
        "set": "clean",
        "baseIndex": 0,
        "position": None,
        "inputSha256": item["inputSha256"],
        "status": "answered",
        "model": JEV_MODEL,
        "p": 0.2,
        "flag": False,
    }

    try:
        pairs, counts = pair_inputs(
            [item],
            [state],
            [stale_answer],
            [],
            "recorded assistant",
            include_unmatched=True,
            rescore_rows=[rescore_answer],
        )
    except TypeError:
        pairs, counts = pair_inputs(
            [item],
            [state],
            [stale_answer],
            [],
            "recorded assistant",
            include_unmatched=True,
        )

    assert [pair["item"]["id"] for pair in pairs] == [item["id"]]
    assert pairs[0]["jev"] == rescore_answer
    assert counts["input_hash_mismatches"] == 0
    assert counts["superseded_stale_jev_rows"] == 1


def test_duplicate_rescore_join_keys_fail_closed() -> None:
    item, state = _row("clean", 0, None, "current redacted tool output")
    rescore = {
        "set": "clean",
        "baseIndex": 0,
        "position": None,
        "inputSha256": item["inputSha256"],
        "status": "answered",
        "model": JEV_MODEL,
        "p": 0.2,
        "flag": False,
    }

    pairs, counts = pair_inputs(
        [item], [state], [], [], "recorded assistant", rescore_rows=[rescore, rescore]
    )

    assert pairs == []
    assert counts["duplicate_rescore_keys"] == 1
