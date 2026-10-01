import json
from collections import Counter


def count_calls(path):
    counts = Counter()
    with open(path) as f:
        for line in f:
            try:
                row = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if not isinstance(row, dict):
                continue
            msg = row.get("message", {})
            if not isinstance(msg, dict):
                continue
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "toolCall":
                    continue
                name = item.get("name")
                if not isinstance(name, str):
                    continue
                counts[name] += 1
    return dict(counts)
