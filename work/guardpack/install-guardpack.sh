#!/usr/bin/env bash
# guardpack — install this lane's measured guards into ANY repo, in one command.
#
# WHY THIS EXISTS (Joshua, 2026-09-20): "every single project I start has this multi-day effort
# of making the same mistakes over and over again before the system is hardened." True, and the
# reason is that everything we hardened tonight is REPO-LOCAL. The guards work; they just do not
# travel. Doctrine files travel and do not work — this repo carries a 200-line tick file that
# warned about the selector defect in three places while it recurred 26 times.
#
# WHAT TRAVELS, measured over one session of 21 recorded defects:
#
#   detection point          instances  mechanism
#   ---------------------------------------------------------------------------
#   before the command runs      7      PreToolUse hook reading the bash string
#   from the command's result    8      wrapper tools (vgrep, pinned-denominator)
#   from repo state at commit    6      gate stages + selftests
#
# So the pack ships all three tiers. Tier 1 is the new part: dcg proves a PreToolUse-class hook
# sees bash strings before execution (it blocks recursive rm in this environment), so the seven
# string-detectable defects can be caught at the moment they are typed rather than in review.
#
# CREATION GATE:
#   1. CONSUMER  — any repo that installs it; the hook is read by the agent harness, the wrappers
#                  by whoever greps for proof, the gates by that repo's CI.
#   2. GATE      — nothing; this is an INSTALLER, and it says so. The things it installs gate.
#   3. DEFECT    — observed: 21 defects in one session, of which the 14 covered by tiers 1-2 had
#                  no mechanism in a fresh repo. Re-earned per project, every project.
#   4. RETIREMENT — when these guards live in a shared harness that every repo inherits, an
#                  installer is redundant. Delete it then.
#
# Usage:
#   work/guardpack/install-guardpack.sh --check <target-repo>   # report, change nothing
#   work/guardpack/install-guardpack.sh <target-repo>           # install (idempotent)
set -uo pipefail
src=$(CDPATH='' cd -- "$(dirname "$0")/../.." && pwd -P)

check_only=0
[ "${1:-}" = "--check" ] && { check_only=1; shift; }
target="${1:-}"
[ -n "$target" ] || { echo "guardpack: usage: $0 [--check] <target-repo>" >&2; exit 2; }
[ -d "$target/.git" ] || { echo "guardpack: $target is not a git repo — refusing" >&2; exit 2; }
target=$(CDPATH='' cd -- "$target" && pwd -P)
[ "$target" = "$src" ] && { echo "guardpack: target is the source repo — nothing to do" >&2; exit 2; }

# TIER 2: result-detectable. These are the two that caught their own author seven times tonight.
WRAPPERS="scripts/vgrep.sh scripts/pinned-denominator.sh"
# TIER 3: repo-state. pin-liveness only matters where pinned digests exist; installed but inert
# until the target has a STATUS-like file, and it says so rather than failing.
GATES="scripts/pin-liveness.sh"

missing=0
for f in $WRAPPERS $GATES; do
  [ -f "$src/$f" ] || { echo "guardpack: source missing $f" >&2; missing=1; }
done
[ "$missing" -eq 0 ] || exit 2

echo "guardpack: source $src"
echo "guardpack: target $target"
for f in $WRAPPERS $GATES; do
  dest="$target/$f"
  if [ -f "$dest" ] && cmp -s "$src/$f" "$dest"; then
    echo "  same     $f"
  elif [ -f "$dest" ]; then
    echo "  DIFFERS  $f (target has its own copy — NOT overwritten)"
  else
    echo "  install  $f"
    [ "$check_only" -eq 1 ] || { mkdir -p "$(dirname "$dest")"; cp "$src/$f" "$dest"; chmod +x "$dest"; }
  fi
done

# TIER 1: the hook. Advisory by default — it WARNS and never blocks, because the pipe-to-head
# pattern is correct almost always and a blocking rule would be the gate-that-fires-on-everything
# this lane refuses (see NEGATIVE_EVIDENCE R48).
hook="$target/.guardpack/pretooluse-advise.sh"
if [ "$check_only" -eq 1 ]; then
  [ -f "$hook" ] && echo "  same     .guardpack/pretooluse-advise.sh" || echo "  install  .guardpack/pretooluse-advise.sh"
else
  mkdir -p "$target/.guardpack"
  cat > "$hook" <<'HOOK'
#!/usr/bin/env bash
# PreToolUse advisory. Reads a bash command string on stdin (or $1) and prints warnings for the
# defect classes that are detectable BEFORE execution. Exit 0 always: advisory, never blocking.
# Measured basis: 7 of 21 defects in one session were visible in the command string itself.
cmd="${1:-$(cat)}"
warn() { printf 'guardpack: %s\n' "$1" >&2; }
case "$cmd" in
  *"| head"*|*"| tail"*)
    warn "pipeline exit status is head/tail's, NOT the command's — 4 false reads measured. Re-run unpiped if you will report an rc." ;;
esac
case "$cmd" in
  *"git add -A"*|*"git add ."*)
    warn "git add -A stages a shared tree you do not own — use explicit paths with git commit --only." ;;
esac
case "$cmd" in
  *"git commit"*-m*'`'*)
    warn "backticks inside an inline -m are COMMAND SUBSTITUTION and have executed code from a commit message here. Use -F <file>." ;;
esac
case "$cmd" in
  *"grep -c"*|*"grep -q"*)
    warn "grep used as proof: zero matches exits 1 and reads as clean. Prefer scripts/vgrep.sh, which exits 3 on zero hits." ;;
esac
exit 0
HOOK
  chmod +x "$hook"
  echo "  install  .guardpack/pretooluse-advise.sh"
fi

echo
echo "guardpack: wire tier 1 by pointing your harness's PreToolUse bash hook at"
echo "  $target/.guardpack/pretooluse-advise.sh"
echo "It is ADVISORY and exits 0 always. It does not block, because every pattern it warns about"
echo "is correct most of the time — a blocking version would be a gate that fires on everything."
[ "$check_only" -eq 1 ] && echo "guardpack: --check, nothing written."
exit 0
