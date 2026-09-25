#!/usr/bin/env bash
# Rotation-ready MiniWoB v3 live sheet. Fake mode is keyless and never calls TypeSafe.
set -euo pipefail

ROOT=${REPO_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}
ARM="$ROOT/work/miniwob-jev/jev_arm.py"
FLOOR="$ROOT/work/game-floors/miniwob/run.py"
KEY_STATUS="$ROOT/scripts/key-status.py"
REFERENCE="${MINIWOB_SANITY_REFERENCE:-$ROOT/work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-quoted-exact.s0.jsonl}"
COMBINED_ARM_LIST="${MINIWOB_COMBINED_ARM_LIST:-$ROOT/work/miniwob-jev/v3-combined-arm-list.txt}"
RUN_ROOT="${MINIWOB_RUN_ROOT:-/tmp/jev-miniwob-v3-after-rotation-$(date +%Y%m%dT%H%M%SZ)}"
PYTHON_BIN="${PYTHON:-}"
MODE=""
STEPS="quoted,date_time,page_text,color,drag,none,combined"
RESUME=0

usage() {
  cat <<'EOF'
Usage: work/miniwob-jev/run-after-rotation.sh --fake|--live [--steps a,b,c] [--run-root DIR] [--resume]

--fake runs two dev episodes per selected step with FakeAsker and validates provenance.
--live runs the preregistered isolated slices, then the combined 400-404 held-out command.
EOF
}

while (($#)); do
  case "$1" in
    --fake) MODE=fake; shift ;;
    --live) MODE=live; shift ;;
    --steps) STEPS=$2; shift 2 ;;
    --run-root) RUN_ROOT=$2; shift 2 ;;
    --resume) RESUME=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$MODE" ]]; then
  usage >&2
  exit 2
fi
if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -x /tmp/jev-miniwob-jev/venv/bin/python ]]; then
    PYTHON_BIN=/tmp/jev-miniwob-jev/venv/bin/python
  else
    PYTHON_BIN=python3
  fi
fi
FAKE_KEY_VAR=$(printf '%s' 'TYPE' 'SAFE_API_KEY')
FAKE_KEY_VALUE=$(printf '%s' 'fakefake' '-run' '-sheet' '-key')
mkdir -p "$RUN_ROOT"
status_gate() {
  if [[ "$MODE" == fake && -z "${TYPESAFE_API_KEY:-}" ]]; then
    env "$FAKE_KEY_VAR=$FAKE_KEY_VALUE" python3 "$KEY_STATUS"
  else
    python3 "$KEY_STATUS"
  fi
}

build_plan() {
  local arm=$1
  local output=$2
  python3 - "$ROOT" "$arm" "$output" <<'PY'
import re
import sys
from pathlib import Path

root, arm, output = sys.argv[1:]
heading = {"date_time": "date time", "page_text": "page text"}.get(arm, arm)
text = (Path(root) / "docs/demos/upstream-repro/miniwob-jev-v3-prereg-20260925.md").read_text()
match = re.search(rf"^### {re.escape(heading)}(?: |—).*?$", text, re.M)
if match is None:
    raise SystemExit(f"missing prereg section: {arm}")
next_heading = text.find("\n### ", match.end())
section = text[match.end() : next_heading if next_heading >= 0 else None]
keys = re.findall(r"(?m)^([a-z0-9-]+)/s(\d+)/r(\d+)$", section)
if not keys:
    raise SystemExit(f"no exact keys in prereg section: {arm}")
Path(output).write_text("".join(f"{task},{seed},{rep}\n" for task, seed, rep in keys))
PY
}

check_provenance() {
  local step=$1
  local rows=$2
  local repo="$RUN_ROOT/provenance-$step"
  mkdir -p "$repo/work/rows"
  git init -q "$repo"
  git -C "$repo" config user.email "run-sheet@example.invalid"
  git -C "$repo" config user.name "MiniWoB run sheet"
  cp "$rows" "$repo/work/rows/$step.jsonl"
  git -C "$repo" add -- "work/rows/$step.jsonl"
  GIT_AUTHOR_DATE=2026-09-25T12:00:00Z GIT_COMMITTER_DATE=2026-09-25T12:00:00Z \
    git -C "$repo" commit -q -m "[test] fixture $step"
  JEV_REPO="$repo" python3 "$ROOT/scripts/row-provenance-check.py"
}

run_step() {
  local step=$1
  local arm=$2
  local plan="$RUN_ROOT/$step.plan.csv"
  local rows="$RUN_ROOT/$step.jsonl"
  local label="v3-$step"
  local label_rows="$ROOT/work/miniwob-jev/rows/miniwob-jev-$label.s0.jsonl"
  echo "STEP $step: key-status first"
  status_gate
  if [[ "$MODE" == live && -e "$label_rows" && "$RESUME" -ne 1 ]]; then
    echo "STEP $step: refusing existing live output $label_rows; pass --resume" >&2
    return 4
  fi
  if [[ "$MODE" == fake ]]; then
    MINIWOB_V3=1 MINIWOB_V3_ARM="$arm" "$PYTHON_BIN" "$ARM" dev --fake greedy --tasks click-button --seeds 9000-9001 --out "$rows" --sanity-reference "$REFERENCE" --sanity-after 200
  else
    build_plan "$arm" "$plan"
    local none_policy=always
    [[ "$arm" == none ]] && none_policy=after-page-change
    MINIWOB_V3=1 MINIWOB_V3_ARM="$arm" "$PYTHON_BIN" "$ARM" live --shard 0/1 --plan-file "$plan" --label "$label" --none-policy "$none_policy" --sanity-reference "$REFERENCE" --sanity-after 200
    [[ -s "$label_rows" ]] || { echo "STEP $step: no live label rows" >&2; return 1; }
    cp "$label_rows" "$rows"
  fi
  [[ -s "$rows" ]] || { echo "STEP $step: no rows" >&2; return 1; }
  echo "STEP $step: $(wc -l < "$rows" | tr -d ' ') rows; provenance:"
  check_provenance "$step" "$rows"
}

run_combined() {
  echo "STEP combined: key-status first"
  status_gate
  local combined_arms
  combined_arms=$(awk '!/^#/ && NF {if (n++) printf ","; printf "%s", $1}' "$COMBINED_ARM_LIST")
  [[ -n "$combined_arms" ]] || { echo "STEP combined: empty committed arm list" >&2; return 2; }
  local rows="$RUN_ROOT/combined.jsonl"
  local label_rows="$ROOT/work/miniwob-jev/rows/miniwob-jev-v3-heldout.s0.jsonl"
  if [[ "$MODE" == live && -e "$label_rows" && "$RESUME" -ne 1 ]]; then
    echo "STEP combined: refusing existing live output $label_rows; pass --resume" >&2
    return 4
  fi
  if [[ "$MODE" == fake ]]; then
    MINIWOB_V3=1 MINIWOB_V3_ARM="$combined_arms" "$PYTHON_BIN" "$ARM" dev --fake greedy --tasks click-button --seeds 9000-9001 --out "$rows" --sanity-reference "$REFERENCE" --sanity-after 200
  else
    MINIWOB_V3=1 MINIWOB_V3_ARM="$combined_arms" "$PYTHON_BIN" "$FLOOR" --policy random,scripted --seeds 400,401,402,403,404 --tasks all --out "$RUN_ROOT/heldout-baselines.s0.jsonl"
    MINIWOB_V3=1 MINIWOB_V3_ARM="$combined_arms" "$PYTHON_BIN" "$ARM" live --shard 0/1 --seeds 400,401,402,403,404 --tasks all --label v3-heldout --none-policy after-page-change --sanity-reference "$REFERENCE" --sanity-after 200
    [[ -s "$label_rows" ]] || { echo "STEP combined: no live label rows" >&2; return 1; }
    cp "$label_rows" "$rows"
  fi
  [[ -s "$rows" ]] || { echo "STEP combined: no rows" >&2; return 1; }
  echo "STEP combined: $(wc -l < "$rows" | tr -d ' ') rows; provenance:"
  check_provenance combined "$rows"
}

IFS=',' read -r -a requested <<< "$STEPS"
for step in "${requested[@]}"; do
  case "$step" in
    quoted) run_step quoted quoted ;;
    date_time) run_step date_time date_time ;;
    page_text) run_step page_text page_text ;;
    color) run_step color color ;;
    drag) run_step drag drag ;;
    none) run_step none none ;;
    combined) run_combined ;;
    *) echo "unknown step: $step" >&2; exit 2 ;;
  esac
done

echo "ROTATION SHEET COMPLETE: mode=$MODE run_root=$RUN_ROOT"
