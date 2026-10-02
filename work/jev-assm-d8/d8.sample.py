import json, random

items = json.load(open("var/agent-tmp/d8.items.json"))
random.seed(21)
random.shuffle(items)
sel = items[:300]
print(len(sel), "verdicts:", sum(1 for i in sel if i["verdict"] == "verified"))
json.dump(sel, open("var/agent-tmp/d8.live.json", "w"))
