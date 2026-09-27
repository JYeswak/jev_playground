#!/usr/bin/env python3
import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("audit_sources.py")
spec = importlib.util.spec_from_file_location("jev_l7ym_audit", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load source audit module")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def row(message):
    return {"type": "message", "message": message}


def call(name, call_id, arguments):
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


def result(call_id, details):
    return row(
        {
            "role": "toolResult",
            "toolName": "find",
            "toolCallId": call_id,
            "details": details,
        }
    )


def test_broad_path_touch_is_secondary_to_narrow_match():
    rows = [
        call("find", "f", {}),
        result(
            "f",
            {
                "hits": [
                    {"rel": "zeta-longest.md"},
                    {"rel": "alpha.md"},
                    {"rel": "beta-long.md"},
                ]
            },
        ),
        call("grep", "g", {"path": "alpha.md", "pattern": "needle"}),
    ]
    calls = audit._tool_calls(rows)
    results = audit._find_results(rows)
    candidates = audit._hits(results["f"][1])
    next_call = calls[1][1]
    assert audit._used_rank(next_call, candidates, audit.WINDOW_TOOLS) is None
    assert audit._used_rank(next_call, candidates, audit.BROAD_TOOLS) == 2


def test_exact_mcnemar_and_wilson_are_deterministic():
    assert audit.exact_mcnemar_p(20, 4) == audit.exact_mcnemar_p(4, 20)
    assert audit._wilson(28, 42)["hits"] == 28
    assert audit._wilson(0, 0)["rate"] is None


def test_usage_parent_source_follows_find_chain():
    rows = [
        {
            "id": "start",
            "type": "custom",
            "customType": "tool_execution_start",
            "data": {"toolName": "find"},
        },
        {"id": "usage", "type": "model_usage", "purpose": "find", "parentId": "middle"},
        {"id": "middle", "type": "model_usage", "purpose": "find", "parentId": "start"},
    ]
    assert audit._usage_parent_source(rows, rows[1]) == "find"


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_"):
            value()
    print("3 tests passed")
