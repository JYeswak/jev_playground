#!/usr/bin/env bash
# pre-push-ci-red-warning.sh — a push to main while main's CI is RED names the red row, and never
# blocks the push.
#
# WHY. 2026-09-24: registered-suites failed on every push to main from cf70e28 (15:19Z) to ff8316d
# (21:10Z), about 55 runs, on one test (work/sr-adopt/test_runner_gates.py), and no agent noticed
# for six hours (bead jev-bfku). scripts/ci-main-status.py names the red row and pane 1's fleet
# check prints it, but the agents who push never run that check. This hook shows the red row to
# the pusher at the moment they add to main (bead jev-rt33).
#
# CONTRACT. git calls a pre-push hook with `<remote> <url>` and one stdin line per ref:
# `<local ref> <local sha> <remote ref> <remote sha>`. Only a push that updates refs/heads/main
# runs scripts/ci-main-status.py, from the checkout that owns this hook (the parent of the
# githooks/ dir git chose, so a push from any cwd finds the same script). Then, on stderr:
#   script exit 1 (red)  `CI on main is RED at <sha7> (run <id>)`, the script's job and row lines
#                        verbatim, then one line: fix the red row or name it in your subject
#   script exit 0        nothing, except a STALE line as one line of context
#   anything else        one line `CI status NOT_RUN: <reason>`: exit 2, any other exit, an exit 1
#                        without a `CI main` line (a traceback is not a red CI), the script or
#                        python3 missing, or the run past the bound (CI_PRE_PUSH_BOUND seconds,
#                        default 45; the script and its gh are killed)
# WARNING ONLY. The hook exits 0 in every case above: a push is never refused because GitHub, gh
# or the network is slow or down, and never because main is red. No model call, no key; gh is
# only read. No `set -e`/`-u` here on purpose: a failing command must not become a refused push.
#
# --selftest: five arms, each a real `git push` from a throwaway repo into a local bare remote
# with this githooks/ dir wired, and a stand-in gh on PATH that serves
# work/ci-main-status/fixtures (no network). An arm that expects silence also requires the
# stand-in to have been called, so a hook that never fired cannot pass it.

HOOKDIR=$(unset CDPATH; cd -- "$(dirname -- "$0")" && pwd)
FIX_LINE='fix the RED row above, or name it in your subject, before pushing more to main (warning only; this push is not blocked)'

notrun() { printf 'CI status NOT_RUN: %s\n' "$1" >&2; }

hook() {
  local rref to_main=0
  while read -r _ _ rref _ || [ -n "$rref" ]; do
    [ "$rref" = refs/heads/main ] && to_main=1
  done
  [ "$to_main" = 1 ] || return 0

  local root script bound dir pid deadline rc first line w1 w2 sha7 runid reason
  local rest=()
  root=$(unset CDPATH; cd -- "$HOOKDIR/.." && pwd)
  script="$root/scripts/ci-main-status.py"
  [ -f "$script" ] || { notrun "scripts/ci-main-status.py missing at $script"; return 0; }
  command -v python3 >/dev/null 2>&1 || { notrun "python3 not on PATH"; return 0; }
  bound=${CI_PRE_PUSH_BOUND:-45}
  case "$bound" in '' | *[!0-9]* | 0) bound=45 ;; esac
  dir=$(mktemp -d "${TMPDIR:-/tmp}/jev-pre-push-ci.XXXXXX") || { notrun "mktemp failed"; return 0; }

  (cd -- "$root" && exec python3 scripts/ci-main-status.py) </dev/null >"$dir/out" 2>"$dir/err" &
  pid=$!
  # Wall clock, not a tick count: a forked `sleep 0.1` measured 0.24 s here (2026-09-24), so 450
  # ticks would have been ~108 s, not 45. SECONDS is whole seconds; -gt means past the bound.
  deadline=$((SECONDS + bound))
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$SECONDS" -gt "$deadline" ]; then
      command -v pkill >/dev/null 2>&1 && pkill -TERM -P "$pid" 2>/dev/null
      kill -TERM "$pid" 2>/dev/null
      { wait "$pid"; } 2>/dev/null
      rm -rf -- "$dir"
      notrun "timed out after ${bound}s"
      return 0
    fi
    sleep 0.1
  done
  { wait "$pid"; } 2>/dev/null
  rc=$?

  first=""
  {
    IFS= read -r first
    while IFS= read -r line || [ -n "$line" ]; do rest+=("$line"); done
  } <"$dir/out"
  if [ -z "$first" ]; then
    first=$(tail -n 1 "$dir/err" 2>/dev/null)
  fi
  rm -rf -- "$dir"

  read -r w1 w2 sha7 _ runid _ <<<"$first"
  if [ "$rc" = 1 ] && [ "$w1 $w2" = "CI main" ] && [ -n "$runid" ] && [ -z "${runid//[0-9]/}" ]; then
    printf 'CI on main is RED at %s (run %s)\n' "$sha7" "$runid" >&2
    for line in "${rest[@]}"; do printf '%s\n' "$line" >&2; done
    printf '%s\n' "$FIX_LINE" >&2
    return 0
  fi
  if [ "$rc" = 0 ]; then
    for line in "${rest[@]}"; do
      case "$line" in STALE*) printf '%s\n' "$line" >&2; return 0 ;; esac
    done
    return 0
  fi
  case "$first" in
    "CI main NOT_RUN "*) reason=${first#CI main NOT_RUN } ;;
    "CI main "*) reason=${first#CI main } ;;
    "") reason="ci-main-status.py exit $rc, no output" ;;
    *) reason="ci-main-status.py exit $rc: $first" ;;
  esac
  [ "$rc" = 2 ] || case "$reason" in ci-main-status.py*) ;; *) reason="ci-main-status.py exit $rc: $reason" ;; esac
  notrun "$reason"
  return 0
}

selftest() {
  local tmp root fix git commit fails=0 c p shim
  # A selftest run from inside another git hook must not inherit that repo's GIT_DIR/index.
  # shellcheck disable=SC2046
  unset $(git rev-parse --local-env-vars 2>/dev/null)
  tmp=$(mktemp -d "${TMPDIR:-/tmp}/pre-push-selftest.XXXXXX") || { echo "selftest: FAIL — mktemp"; exit 1; }
  trap 'rm -rf -- "$tmp"' EXIT
  root=$(unset CDPATH; cd -- "$HOOKDIR/.." && pwd)
  fix="$root/work/ci-main-status/fixtures"
  git=$(command -v git) || { echo "selftest: FAIL — git not on PATH"; exit 1; }
  [ -x "$HOOKDIR/pre-push" ] || { echo "selftest: FAIL — $HOOKDIR/pre-push missing or not executable"; exit 1; }
  for c in list-red.json list-green.json view-36059723283.json log-36059723283.txt; do
    [ -f "$fix/$c" ] || { echo "selftest: FAIL — fixture $fix/$c missing"; exit 1; }
  done

  # One throwaway repo, one commit made with plumbing (no commit hook runs), then this githooks/
  # dir wired as its hook path so `git push` runs the real wrapper and impl.
  export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
  "$git" init -q "$tmp/work" || { echo "selftest: FAIL — git init"; exit 1; }
  printf 'x\n' >"$tmp/work/f"
  if ! { "$git" -C "$tmp/work" add f &&
    commit=$("$git" -C "$tmp/work" commit-tree "$("$git" -C "$tmp/work" write-tree)" -m x) &&
    "$git" -C "$tmp/work" update-ref refs/heads/main "$commit" &&
    "$git" -C "$tmp/work" config core.hooksPath "$HOOKDIR"; }; then
    echo "selftest: FAIL — could not build the throwaway repo"; exit 1
  fi

  standin() { # standin <arm> <red|green|sleep>: a gh that serves fixtures and logs each call
    mkdir -p "$tmp/$1.bin"
    cat >"$tmp/$1.bin/gh" <<EOF
#!/bin/sh
printf '%s\n' "\$*" >>"$tmp/$1.calls"
[ "$2" = sleep ] && exec sleep 30
case "\$1 \$2" in
  "run list") cat "$fix/list-$2.json" ;;
  "run view") case "\$*" in *--log-failed*) cat "$fix/log-\$3.txt" ;; *) cat "$fix/view-\$3.json" ;; esac ;;
  *) echo "stand-in gh: unexpected: \$*" >&2; exit 9 ;;
esac
EOF
    chmod +x "$tmp/$1.bin/gh"
  }
  push() { # push <arm> <PATH> <refspec> <bound>: sets RC, SECS, ERR, REMOTE
    REMOTE="$tmp/$1.git"
    ERR="$tmp/$1.err"
    "$git" init -q --bare "$REMOTE"
    local start=$SECONDS
    (cd "$tmp/work" && PATH="$2" CI_PRE_PUSH_BOUND="$4" CI_MAIN_STATUS_TIMEOUT=60 \
      "$git" push -q "$REMOTE" "$3") </dev/null >"$tmp/$1.out" 2>"$ERR"
    RC=$?
    SECS=$((SECONDS - start))
  }
  landed() { [ "$("$git" -C "$REMOTE" rev-parse -q --verify "$1" 2>/dev/null)" = "$commit" ]; }
  arm() { # arm <label> <failure or empty>
    if [ -z "$2" ]; then echo "  PASS $1"; else
      echo "  FAIL $1: $2"; sed 's/^/    stderr| /' "$ERR"; fails=$((fails + 1))
    fi
  }
  local why

  # 1. RED: the push lands, and stderr names the red row and the fix-or-say-why line, in order.
  standin red red
  push red "$tmp/red.bin:$PATH" main:main 45
  why=""
  [ "$RC" = 0 ] || why="exit $RC (the warning blocked the push)"
  [ -z "$why" ] && ! landed refs/heads/main && why="remote main not updated"
  [ -z "$why" ] && [ "$(sed -n 1p "$ERR")" != "CI on main is RED at ff8316d (run 36059723283)" ] &&
    why="first stderr line is not 'CI on main is RED at ff8316d (run 36059723283)'"
  [ -z "$why" ] && ! grep -qF 'work/sr-adopt/test_runner_gates.py' "$ERR" && why="red row work/sr-adopt/test_runner_gates.py not named"
  [ -z "$why" ] && ! tail -n 1 "$ERR" | grep -qF 'fix the RED row above, or name it in your subject' &&
    why="last stderr line is not the fix-or-say-why line"
  arm "arm 1 red CI: push landed, stderr names work/sr-adopt/test_runner_gates.py then the fix line" "$why"

  # 2. GREEN: the push lands and the hook says nothing, but only after it really asked gh.
  standin green green
  push green "$tmp/green.bin:$PATH" main:main 45
  why=""
  [ "$RC" = 0 ] || why="exit $RC"
  [ -z "$why" ] && ! landed refs/heads/main && why="remote main not updated"
  [ -z "$why" ] && [ -s "$ERR" ] && why="stderr not empty on green"
  [ -z "$why" ] && ! grep -q '^run list' "$tmp/green.calls" 2>/dev/null && why="stand-in gh never called (hook did not fire)"
  arm "arm 2 green CI: push landed, stderr empty, stand-in gh was called" "$why"

  # 3. gh ABSENT: PATH holds only the tools the hook and git need, no gh. One NOT_RUN line.
  shim="$tmp/nogh.bin"
  mkdir -p "$shim"
  for c in bash dirname python3 mktemp sleep rm tail pkill git; do
    p=$(command -v "$c") && ln -s "$p" "$shim/$c"
  done
  push nogh "$shim" main:main 45
  why=""
  [ "$RC" = 0 ] || why="exit $RC"
  [ -z "$why" ] && ! landed refs/heads/main && why="remote main not updated"
  [ -z "$why" ] && [ "$(grep -c '' "$ERR")" != 1 ] && why="expected exactly one stderr line"
  [ -z "$why" ] && ! grep -q '^CI status NOT_RUN: gh not installed' "$ERR" &&
    why="stderr line does not start with 'CI status NOT_RUN: gh not installed'"
  [ -z "$why" ] && grep -qF -e 'CI on main is RED' -e 'success' "$ERR" &&
    why="stderr line carries a red or green status ('CI on main is RED' or 'success')"
  arm "arm 3 gh absent: push landed, one line starting 'CI status NOT_RUN: gh not installed', no red or green line" "$why"

  # 4. NOT MAIN: a push to refs/heads/topic lands and never runs the script (gh never called).
  standin topic red
  push topic "$tmp/topic.bin:$PATH" main:refs/heads/topic 45
  why=""
  [ "$RC" = 0 ] || why="exit $RC"
  [ -z "$why" ] && ! landed refs/heads/topic && why="remote topic not updated"
  [ -z "$why" ] && [ -s "$ERR" ] && why="stderr not empty on a non-main push"
  [ -z "$why" ] && [ -e "$tmp/topic.calls" ] && why="script ran on a non-main push (stand-in gh was called)"
  arm "arm 4 push to refs/heads/topic: push landed, script not run, stderr empty" "$why"

  # 5. HANG: a gh that sleeps 30 s against a 2 s bound. The push lands within the bound + 5 s.
  standin hang sleep
  push hang "$tmp/hang.bin:$PATH" main:main 2
  why=""
  [ "$RC" = 0 ] || why="exit $RC"
  [ -z "$why" ] && ! landed refs/heads/main && why="remote main not updated"
  [ -z "$why" ] && [ "$(cat "$ERR")" != "CI status NOT_RUN: timed out after 2s" ] &&
    why="stderr is not the one line 'CI status NOT_RUN: timed out after 2s'"
  [ -z "$why" ] && [ ! -e "$tmp/hang.calls" ] && why="stand-in gh never called (hook did not fire)"
  [ -z "$why" ] && [ "$SECS" -gt 7 ] && why="push took ${SECS}s, past the 2 s bound + 5 s"
  arm "arm 5 gh hangs past a 2 s bound: push landed in ${SECS}s, 'CI status NOT_RUN: timed out after 2s'" "$why"

  if [ "$fails" -eq 0 ]; then
    echo "# pass 5"
    echo "selftest: PASS 5/5 arms (red names the row and the fix line; green silent; gh absent NOT_RUN; non-main push skips the script; hang bounded), every push landed"
    exit 0
  fi
  echo "selftest: FAIL ($fails of 5 arms)"
  exit 1
}

case "${1:-}" in
  --selftest) selftest ;;
  *) hook; exit 0 ;;
esac
