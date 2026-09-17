#!/usr/bin/env bash
# Refuse a path-limited commit when Git dropped a staged deletion while the file
# still exists in the working tree. Git gives this hook the prospective index in
# GIT_INDEX_FILE; the real index is the comparison baseline.

set -euo pipefail

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  printf 'STAGED_DELETION_REFUSED reason=git-dir-unresolvable\n' >&2
  exit 1
fi

real_index=$(env -u GIT_INDEX_FILE git rev-parse --git-path index 2>/dev/null) || {
  printf 'STAGED_DELETION_REFUSED reason=real-index-unresolvable\n' >&2
  exit 1
}

candidate_index=${GIT_INDEX_FILE:-$real_index}
if [ ! -f "$candidate_index" ] || [ ! -f "$real_index" ]; then
  printf 'STAGED_DELETION_REFUSED reason=index-unreadable candidate=%s real=%s\n' \
    "$candidate_index" "$real_index" >&2
  exit 1
fi

candidate_deletions=$(GIT_INDEX_FILE="$candidate_index" git diff --cached --name-only --diff-filter=D --)
real_deletions=$(GIT_INDEX_FILE="$real_index" git diff --cached --name-only --diff-filter=D --)

while IFS= read -r path; do
  [ -n "$path" ] || continue
  if ! printf '%s\n' "$candidate_deletions" | grep -F -x -q -- "$path"; then
    printf 'STAGED_DELETION_REFUSED dropped-staged-deletion path=%s\n' "$path" >&2
    printf '%s\n' \
      'The path-limited commit re-resolved this path from the working tree and dropped its staged deletion.' \
      'Fix: rerun the commit without a path list, or use git commit --include -- <paths>.' \
      "Surviving-blob check: git ls-files --stage -- $path" >&2
    exit 1
  fi
done <<< "$real_deletions"

exit 0
