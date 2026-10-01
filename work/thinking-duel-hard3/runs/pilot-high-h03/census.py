import json
from collections import Counter


def summarize(path):
    counts = Counter()
    think = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "\x00" in line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if not isinstance(row, dict):
                continue
            msg = row.get("message")
            if isinstance(msg, dict):
                role = msg["role"] if "role" in msg else row.get("role")
                content = msg["content"] if "content" in msg else row.get("content")
                mthink = msg.get("thinking")
                rthink = row.get("thinking") if msg is not row else None
            else:
                msg = row
                role = row.get("role")
                content = row.get("content")
                mthink = row.get("thinking")
                rthink = None
            if role != "assistant":
                continue
            if isinstance(mthink, str):
                think += len(mthink)
            if isinstance(rthink, str):
                think += len(rthink)
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "toolCall":
                    name = item.get("name")
                    if isinstance(name, str):
                        counts[name] += 1
                t = item.get("thinking")
                if isinstance(t, str):
                    think += len(t)
    return {"calls": dict(counts), "think_chars": think}
