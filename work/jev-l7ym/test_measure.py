#!/usr/bin/env python3
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("measure.py")
spec = importlib.util.spec_from_file_location("jev_l7ym_measure", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load measurement module")
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)


def row(message):
    return {"type": "message", "message": message}


def tool_call(name, call_id, arguments):
    return row(
        {
            "role": "assistant",
            "content": [
                {
                    "type": "toolCall",
                    "name": name,
                    "id": call_id,
                    "arguments": arguments,
                }
            ],
        }
    )


def tool_result(tool_name, call_id, details):
    return row(
        {
            "role": "toolResult",
            "toolName": tool_name,
            "toolCallId": call_id,
            "details": details,
        }
    )


def test_actual_rank_is_taken_from_the_used_returned_path():
    rows = [
        tool_call("find", "find-1", {"query": "needle"}),
        tool_result(
            "find",
            "find-1",
            {
                "cwd": "/repo",
                "hits": [
                    {"rel": "zeta-longest.md"},
                    {"rel": "alpha.md"},
                    {"rel": "beta-long.md"},
                ],
            },
        ),
        tool_call("read", "read-1", {"path": "alpha.md"}),
    ]

    report = measure.analyze_rows(rows)

    assert report["windowed_calls"] == 1
    assert report["actual"]["top1"]["hits"] == 0
    assert report["actual"]["top3"]["hits"] == 1
    assert report["baseline"]["top1"]["hits"] == 1
    assert report["baseline"]["top3"]["hits"] == 1


def test_unknown_tool_and_unreturned_path_do_not_count_as_use():
    rows = [
        tool_call("find", "find-1", {"query": "needle"}),
        tool_result("find", "find-1", {"cwd": "/repo", "hits": [{"rel": "one.md"}]}),
        tool_call("grep", "grep-1", {"path": "one.md"}),
        tool_call("read", "read-1", {"path": "other.md"}),
    ]

    report = measure.analyze_rows(rows)

    assert report["ranked_calls"] == 1
    assert report["windowed_calls"] == 0
    assert report["no_returned_file_used"] == 1


def test_foreign_rows_are_ignored():
    rows = [
        {"type": "heartbeat", "payload": "metadata"},
        tool_call("find", "find-1", {"query": "needle"}),
    ]
    assert measure.analyze_rows(rows)["find_calls"] == 1


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_"):
            value()
    print("3 tests passed")
