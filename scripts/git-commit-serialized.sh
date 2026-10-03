#!/usr/bin/env bash
# Compatibility entry point for the shared-checkout single Git writer.
# Raw Git remains available for read-only commands; index mutation must use
# this request path until every live pane has the guarded Git dispatcher.
set -u

repo="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "git-commit-serialized: not in a git repo" >&2
  exit 2
}
script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
verb=commit
if [ "${1:-}" = add ] || [ "${1:-}" = commit ]; then
  verb=$1
  shift
fi

exec python3 "$script_dir/git-commitd.py" client --repo "$repo" "$verb" "$@"
