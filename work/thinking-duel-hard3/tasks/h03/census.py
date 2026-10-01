import json
from collections import Counter


def summarize(path):
    counts = Counter()
    think = 0
    for line in open(path):
        row = json.loads(line)
        for item in row["message"]["content"]:
            if item.get("type") == "toolCall":
                counts[item.get("name")] += 1
            think += len(item.get("thinking", ""))
    return {"calls": dict(counts), "think_chars": think}
