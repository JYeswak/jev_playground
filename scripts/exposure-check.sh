#!/usr/bin/env bash
# exposure-check.sh — "what is our exposure to this gap" in one screen.
#
# WHY: with 651 skills and a 221-repo mirror, the binding constraint is not
# discovery or delivery but EXPOSURE: a rule/skill pays only when we hit the
# gap it guards. Three narrow-corpus numbers died here in one day, all of
# them a count without its denominator. This tool prints every denominator.
#
# Usage:
#   scripts/exposure-check.sh --pattern REGEX [--not REGEX]
#       [--path-pattern REGEX] [--label NAME]
#   env: EXPOSURE_CORPUS_DIR (default ~/.omp), EXPOSURE_HARVEST
#        (default work/toolcall-judge-v3/real-allowed.json)
#
# A call counts when --pattern matches its args blob AND --path-pattern
# (if given) matches its path. --not excludes blobs matching a second
# regex: raw count vs real count is the whole point (the 818-class error
# counted forbid(unsafe_code) churn as danger).
#
PATTERN=""; NOT=""; PATHPAT=""; LABEL="pattern"; TEXTMODE=0
usage() {
  sed -n '2,18p' "$0"
  echo "Flags: --pattern REGEX [--not REGEX] [--path-pattern REGEX]"
  echo "       [--label NAME] [--text] [--help]"
  echo "  --text matches assistant text turns instead of tool args."
}
while [ $# -gt 0 ]; do
  case "$1" in
    --pattern) PATTERN="$2"; shift 2 ;;
    --not) NOT="$2"; shift 2 ;;
    --path-pattern) PATHPAT="$2"; shift 2 ;;
    --label) LABEL="$2"; shift 2 ;;
    --text) TEXTMODE=1; shift ;;
    --help|-h) usage; exit 0 ;;
    --*) echo "REFUSE_USAGE: unknown flag $1" >&2; usage >&2; exit 2 ;;
    *) echo "REFUSE_USAGE: did you mean --pattern $1" >&2; usage >&2; exit 2 ;;
  esac
done
[ -n "$PATTERN" ] || { echo "REFUSE_USAGE: --pattern required" >&2; usage >&2; exit 2; }

CORPUS="${EXPOSURE_CORPUS_DIR:-$HOME/.omp}"
HARVEST="${EXPOSURE_HARVEST:-work/toolcall-judge-v3/real-allowed.json}"

export EXPOSURE_PATTERN="$PATTERN" EXPOSURE_NOT="$NOT"
export EXPOSURE_PATHPAT="$PATHPAT" EXPOSURE_CORPUS="$CORPUS"
export EXPOSURE_HARVEST_F="$HARVEST" EXPOSURE_LABEL="$LABEL"
export EXPOSURE_TEXT="$TEXTMODE"

python3 - <<'PY'
import fnmatch
import json
import os
import re
import sys
from collections import Counter

label = os.environ["EXPOSURE_LABEL"]
pat = os.environ["EXPOSURE_PATTERN"]
notpat = os.environ["EXPOSURE_NOT"]
pathpat = os.environ["EXPOSURE_PATHPAT"]
corpus = os.environ["EXPOSURE_CORPUS"]
harvest = os.environ["EXPOSURE_HARVEST_F"]

try:
    rx = re.compile(pat)
except re.error as e:
    print(f"REFUSE_BAD_PATTERN: {e}")
    sys.exit(2)
notrx = None
if notpat:
    try:
        notrx = re.compile(notpat)
    except re.error as e:
        print(f"REFUSE_BAD_PATTERN: --not: {e}")
        sys.exit(2)
pathrx = re.compile(pathpat) if pathpat else None
textmode = os.environ.get("EXPOSURE_TEXT") == "1"
unit = "text turns" if textmode else "edit-write payloads"

# --- bash harvest ---
try:
    with open(harvest, encoding="utf-8") as fh:
        data = json.load(fh)
    records = data["records"] if isinstance(data, dict) else data
except (OSError, ValueError, KeyError) as e:
    print(f"REFUSE_EMPTY_CORPUS: harvest unreadable: {e}")
    sys.exit(2)
bash_hits = sum(1 for r in records
                if rx.search(json.dumps(r, sort_keys=True)))
bash_n = len(records)

# --- session corpus ---
files = []
if os.path.isdir(corpus):
    for dirpath, _d, filenames in os.walk(corpus):
        for fn in filenames:
            if fn.endswith(".jsonl"):
                files.append(os.path.join(dirpath, fn))
if not files:
    print("REFUSE_EMPTY_CORPUS: no session files")
    sys.exit(2)

sessions_any = 0
payload_n = 0
raw_hits = 0
real_hits = 0
fire_sessions = set()
per_session = Counter()
for fp in sorted(files):
    try:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            seen_any = False
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") != "message":
                    continue
                msg = obj.get("message") or {}
                if msg.get("role") != "assistant":
                    continue
                if textmode:
                    texts = [c.get("text", "") for c in (msg.get("content") or [])
                             if isinstance(c, dict) and c.get("type") == "text"]
                    if not texts:
                        continue
                    seen_any = True
                    blob = "\n".join(texts)
                    payload_n += 1
                    if not rx.search(blob):
                        continue
                    raw_hits += 1
                    if notrx and notrx.search(blob):
                        continue
                    real_hits += 1
                    fire_sessions.add(fp)
                    per_session[fp] += 1
                    continue
                for c in msg.get("content") or []:
                    if not isinstance(c, dict) or c.get("type") != "toolCall":
                        continue
                    name = str(c.get("name") or "").lower()
                    if not name:
                        continue
                    seen_any = True
                    if name not in ("edit", "write"):
                        continue
                    args = c.get("arguments") or {}
                    path = args.get("path") or args.get("file") or ""
                    if not isinstance(path, str) or not path:
                        continue
                    blob = json.dumps(args, sort_keys=True)
                    payload_n += 1
                    if pathrx and not pathrx.search(path):
                        continue
                    if not rx.search(blob):
                        continue
                    raw_hits += 1
                    if notrx and notrx.search(blob):
                        continue
                    real_hits += 1
                    fire_sessions.add(fp)
                    per_session[fp] += 1
    except OSError:
        continue
    if seen_any:
        sessions_any += 1

if not sessions_any or not payload_n:
    print("REFUSE_EMPTY_CORPUS: no calls to evaluate")
    sys.exit(2)
if not raw_hits and not bash_hits:
    print(f"REFUSE_NO_SIGNAL: pattern matched nothing in {bash_n} harvest "
          f"records or {payload_n} payloads")
    sys.exit(2)

sess_n = len(fire_sessions)
sess_pct = sess_n / sessions_any * 100
top1 = (per_session.most_common(1)[0][1] / real_hits) if real_hits else 0.0

print(f"EXPOSURE {label}")
print(f"bash: {bash_hits}/{bash_n} harvest commands match")
print(f"payloads: {real_hits}/{payload_n} {unit} match "
      f"(raw {raw_hits}, {raw_hits - real_hits} excluded by --not)")
print(f"sessions: {sess_n}/{sessions_any} sessions-with-calls touch it "
      f"({sess_pct:.2f}%)")
print(f"concentration top1: {top1 * 100:.1f}% of real hits")
if real_hits < 50:
    print("VERDICT: TOO_RARE")
    sys.exit(1)
if sess_pct > 5:
    print("VERDICT: WALLPAPER")
    sys.exit(1)
if top1 >= 0.5:
    print("VERDICT: ONE_HABIT")
    sys.exit(1)
print("VERDICT: MEASURE")
PY
