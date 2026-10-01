import json
from collections import Counter


def count_calls(path):
    counts = Counter()
    for line in open(path):
        row = json.loads(line)
        msg = row.get("message", {})
        for item in msg.get("content", []):
            if item.get("type") == "toolCall":
                counts[item.get("name")] += 1
    return dict(counts)
