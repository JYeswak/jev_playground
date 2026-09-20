#!/usr/bin/env bash
# Standalone reproduction: jev-align prints "The unlabeled pool is exhausted."
# while rows in the pool have never been offered for labeling.
#
# WHAT THIS SHOWS
# ---------------
# src/jev_align/cli.py:2477-2497 treats a remainder smaller than one batch as
# exhaustion:
#
#     remaining = session.unlabeled_stories()
#     if not remaining or (
#         session.capture_pool is None and len(remaining) < state.batch_size
#     ):
#         ...
#         console.print(... else "The unlabeled pool is exhausted.")
#         return
#
# The guard is deliberate -- a short final batch would distort batch-level F1.
# The sentence it prints is not true. With --pool-size 11 --batch-size 6 the run
# offers 6 rows and then reports the pool exhausted with 5 rows never shown.
#
# PREREQUISITES
# -------------
#   pip install "jev-align==0.1.2"
#   TYPESAFE_API_KEY   set   (the pool evaluation is a real backend call: 11 rows)
#   ANTHROPIC_API_KEY  set   (or OPENAI_API_KEY / GEMINI_API_KEY; jev-align
#                             refuses to start without some reflection key, even
#                             on the path below, which never reaches GEPA)
#
# The dataset is the one bundled inside the jev-align wheel. Nothing from any
# private repo is used.
#
# Labels are supplied as blank lines on stdin. jev-align falls back to
# line-oriented input when stdin is not a TTY (cli.py:1449) and an empty line
# accepts the highlighted default, so all six labels land in the same class.
# That is deliberate: it keeps the run deterministic, and it means the run never
# reaches GEPA, so this reproduction costs 11 backend calls and no reflection
# calls at all.
#
# USAGE
#   ./false-exhaustion-repro.sh                         # uses `jeva`/`python3` on PATH
#   JEVA=/venv/bin/jeva PYTHON=/venv/bin/python ./false-exhaustion-repro.sh
set -uo pipefail

JEVA="${JEVA:-jeva}"
PYTHON="${PYTHON:-python3}"
POOL_SIZE=11
BATCH_SIZE=6

SAMPLE="${SAMPLE:-$("$PYTHON" - <<'PY'
import importlib.util, pathlib
spec = importlib.util.find_spec("jev_align")
print(pathlib.Path(spec.origin).parent / "sample_data" / "support-tickets.csv" if spec else "")
PY
)}"
if [ ! -f "$SAMPLE" ]; then
  echo "could not locate the bundled support-tickets.csv; jev_align must be" \
       "importable from \$PYTHON ($PYTHON), or set SAMPLE by hand" >&2
  exit 2
fi

WORKDIR="$(mktemp -d)"
cd "$WORKDIR" || exit 2
echo "workdir: $WORKDIR"
echo "dataset: $SAMPLE"
echo

# 6 rows x (label prompt + rationale prompt) = 12 lines; send extra for slack.
for _ in $(seq 1 40); do echo; done | "$JEVA" optimize "$SAMPLE" \
  --question "Is this ticket about billing?" \
  --column instruction \
  --pool-size "$POOL_SIZE" \
  --batch-size "$BATCH_SIZE" \
  --max-metric-calls 20 \
  --seed 0 2>&1 | tee transcript.txt
echo "jeva rc=${PIPESTATUS[1]}"

echo
echo "--- accounting -------------------------------------------------------"
LABELS="$(find .jev-align/runs -name labels.jsonl -print -quit)"
if [ -n "$LABELS" ]; then
  OFFERED="$(wc -l < "$LABELS" | tr -d ' ')"
else
  OFFERED=0
fi
echo "pool size            : $POOL_SIZE"
echo "rows ever offered    : $OFFERED"
echo "rows NEVER offered   : $(( POOL_SIZE - OFFERED ))"
if grep -q "The unlabeled pool is exhausted." transcript.txt \
   && [ "$(( POOL_SIZE - OFFERED ))" -gt 0 ]; then
  echo "REPRODUCED: printed \"exhausted\" with $(( POOL_SIZE - OFFERED )) rows never offered"
  exit 0
fi
echo "DID NOT REPRODUCE"
exit 1
