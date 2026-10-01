import json, sys
from csvexp import write_csv

rows = json.load(sys.stdin)
write_csv("/tmp/t09-out.csv", rows)
print(open("/tmp/t09-out.csv", newline="", encoding="utf-8").read(), end="")
