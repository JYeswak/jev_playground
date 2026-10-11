#!/usr/bin/env bash
# selftest for scripts/publish-export.sh — scan diagnostics, exact exceptions, scanner errors, and the
# thinkingSignature transform (jev-x5cy). Discovered by foundation/gates.d/80 via the scripts/selftest-*.sh glob.
#
# WHY. At 14f31880 the export scan refused the real tree with only "EXPORT SCAN FAIL (worktree)": its second,
# reason-printing call died under `set -euo pipefail` whenever a grep had no match. The reasons it would have
# printed were whole matching lines, i.e. possible credentials. Every arm plants a real condition and requires
# the stated outcome; the planted keys are built from parts so this file never contains a key-shaped literal.
#
# The script is run for real: `--scan DIR` over fixture trees, and the full build inside a tiny fixture repo
# (its ROOT is the fixture, so its sibling export directory is the fixture's too; the real export is never touched).
set -uo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_CONFIG
root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd -P)
cd "$root" || exit 2
S="${PES_SUBJECT:-$root/scripts/publish-export.sh}"   # PES_SUBJECT: a mutated copy, for the mutation check recorded on jev-x5cy
pass=0; fail=0
note() { printf '  %-4s %s\n' "$1" "$2"; }
ok() { note ok "$1"; pass=$((pass + 1)); }
no() { printf '  FAIL %s\n' "$1"; fail=$((fail + 1)); }

mkdir -p "$root/var/agent-tmp" || exit 1
tmp=$(mktemp -d "$root/var/agent-tmp/pes.XXXXXX") || { echo "selftest-publish-export-scan: mktemp failed"; exit 1; }
printf 'pid=%s\nlabel=selftest-publish-export-scan\nrepo=%s\ncreated=%s\n' "$$" "$root" "$(date -u +%FT%TZ)" > "$tmp/.owner"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null

# Planted material, built from parts. Q-runs are the marker the output must never contain.
q16=QQQQQQQQQQQQQQQQ
k_aws="AKIA${q16}"; k_sk="sk-live-${q16}"; k_gh="ghp_${q16}"; k_xox="xoxb-${q16}"; k_bearer="Bearer ey${q16}"
k_pem="-----BEGIN RSA ""PRIVATE KEY-----"
home="/Users/""josh"
sig_blob=$(printf 'Z%.0s' $(seq 1 130))

out=""; rc=0
run_scan() { out=$("${SCAN_SCRIPT:-$S}" --scan "$1" 2>&1); rc=$?; }
has() { printf '%s\n' "$out" | grep -q -F -- "$1"; }
lacks() { ! has "$1"; }
# assert <label> <command...>: ok when the command succeeds
assert() { local label=$1; shift; if "$@"; then ok "$label"; else no "$label"; fi; }
# expect <label> <rc>: the last run must exit with that code
expect() { if [ "$rc" -eq "$2" ]; then ok "$1 (rc=$rc)"; else no "$1: wanted rc=$2 got rc=$rc: $(printf '%s\n' "$out" | tail -1)"; fi; }
has_all_lines() { local n; for n in "$@"; do has "d/keys.txt:$n" || return 1; done; }
lacks_all() { local s; for s in "$@"; do has "$s" && return 1; done; return 0; }

# 1. A tree with no hit at all is clean. This is the original defect: with zero /Users/josh matches the
#    scan died silently under set -e. rc 0 and the PASS line prove it ran to the end.
mkdir -p "$tmp/clean/d"; printf 'nothing to see\n' > "$tmp/clean/d/a.txt"
run_scan "$tmp/clean"; expect "no-match tree is clean" 0
assert "clean tree reaches the PASS line" has "EXPORT SCAN PASS"

# 2. One planted line per key shape: refused, every path:line named, no planted text printed, counted.
mkdir -p "$tmp/keys/d"
{ printf 'a %s z\n' "$k_aws"; printf 'b %s z\n' "$k_sk"; printf 'c %s z\n' "$k_gh"
  printf 'd %s z\n' "$k_xox"; printf 'e %s z\n' "$k_bearer"; printf 'f %s z\n' "$k_pem"; } > "$tmp/keys/d/keys.txt"
run_scan "$tmp/keys"; expect "six planted key shapes are refused" 1
assert "the refusal counts 6 lines" has "6 unexplained key-pattern line(s)"
assert "every planted line is named as path:line" has_all_lines 1 2 3 4 5 6
assert "no planted text appears in the output" lacks_all "$q16" "$k_pem" "BEGIN RSA"

# 3. The other checks print locations and counts, never text.
mkdir -p "$tmp/misc"; printf 'p %s/x q\n' "$home" > "$tmp/misc/h.txt"; printf 'enc encrypted_content here\n' > "$tmp/misc/e.txt"
printf '{"thinkingSignature":"%s"}\n' "$sig_blob" > "$tmp/misc/s.jsonl"
run_scan "$tmp/misc"; expect "home path, encrypted_content and a signature blob are refused" 1
assert "home path named by path:line" has "h.txt:1"
assert "encrypted_content named by path:line" has "e.txt:1"
assert "signature blob named by path:line" has "s.jsonl:1"
assert "no signature text printed" lacks "ZZZZZZZZ"
assert "signature count and file count" has "1 blob-shaped thinkingSignature line(s) in 1 file(s)"

# 4. Exceptions bind path + exact line + hit count. The real exempted line, copied to its own relative path.
doc="docs/demos/upstream-repro/issue-1-state-preview-plaintext-credentials.md"
if [ -f "$root/$doc" ]; then
  mkdir -p "$tmp/exc/$(dirname "$doc")"; cp "$root/$doc" "$tmp/exc/$doc"
  run_scan "$tmp/exc"; expect "the exempted line, at its own path, passes" 0
  assert "it is counted as excepted, not explained away" has "1 by exact exception row(s)"
  mkdir -p "$tmp/exc-edit/$(dirname "$doc")"; sed '48s/FAKE-----/FAKF-----/' "$root/$doc" > "$tmp/exc-edit/$doc"
  run_scan "$tmp/exc-edit"; expect "the same line edited by one character is unexplained again" 1
  assert "and is named as path:line" has "$doc:48"
  mkdir -p "$tmp/exc-move/other"; cp "$root/$doc" "$tmp/exc-move/other/copy.md"
  run_scan "$tmp/exc-move"; expect "the same line at another path is unexplained" 1
  mkdir -p "$tmp/exc-two/$(dirname "$doc")"
  awk -v k="$k_aws" 'NR==48{print $0 " " k; next} {print}' "$root/$doc" > "$tmp/exc-two/$doc"
  run_scan "$tmp/exc-two"; expect "a second key added to the exempted line is unexplained" 1
  assert "no planted text printed for the second-key variant" lacks "$q16"
  # The row's hit count is part of its binding: a row that says 2 for a line that has 1 no longer covers it.
  mkdir -p "$tmp/cnt/scripts" "$tmp/cnt/docs" "$tmp/cnt/tree/$(dirname "$doc")"
  cp -p "$S" "$tmp/cnt/scripts/publish-export.sh"; cp "$root/$doc" "$tmp/cnt/tree/$doc"
  sed "s#^\\(EXEMPT $doc | [0-9a-f]\\{64\\} | \\)1 |#\\12 |#" "$root/docs/publish-key-exceptions.txt" > "$tmp/cnt/docs/publish-key-exceptions.txt"
  if cmp -s "$root/docs/publish-key-exceptions.txt" "$tmp/cnt/docs/publish-key-exceptions.txt"; then no "count arm: the row to edit was not found"
  else SCAN_SCRIPT="$tmp/cnt/scripts/publish-export.sh" run_scan "$tmp/cnt/tree"; expect "a row whose hit count no longer matches does not cover the line" 1; fi
else
  no "exempted document $doc is missing from the tree"
fi

# 4b. The AWS documentation example excuses itself and nothing else on its line.
aws_doc="AKIA""IOSFODNN7""EXAMPLE"
mkdir -p "$tmp/awsonly" "$tmp/awsplus"
printf 'doc example %s here\n' "$aws_doc" > "$tmp/awsonly/a.txt"
printf 'doc example %s and %s here\n' "$aws_doc" "$k_gh" > "$tmp/awsplus/a.txt"
run_scan "$tmp/awsonly"; expect "the AWS documentation example alone is explained" 0
run_scan "$tmp/awsplus"; expect "the AWS example does not excuse a real-shaped key on the same line" 1
assert "and that line is named" has "a.txt:1"
assert "with no planted text printed" lacks "$q16"

# 5. A scanner error is not a result. An unreadable file makes grep exit 2: exit 4, never a pass, never a finding.
mkdir -p "$tmp/unread"; printf 'x\n' > "$tmp/unread/u.txt"; chmod 000 "$tmp/unread/u.txt"
run_scan "$tmp/unread"; chmod 644 "$tmp/unread/u.txt"
expect "an unreadable file is a scanner error" 4
assert "reported as SCAN ERROR" has "SCAN ERROR"
assert "never as a PASS" lacks "EXPORT SCAN PASS"

# Tiny fixture repo whose ROOT is the fixture: the script's sibling export lands beside it. mini <name> [exceptions-file]
mini() {
  local d="$tmp/$1/root"; mkdir -p "$d/scripts" "$d/docs" "$d/data"
  cp -p "$S" "$d/scripts/publish-export.sh"
  if [ -n "${2-}" ]; then cp "$2" "$d/docs/publish-key-exceptions.txt"; else printf '# none\n' > "$d/docs/publish-key-exceptions.txt"; fi
  printf '{"a":1,"thinkingSignature":"%s","b":2}\n{"thinkingSignature":"short"}\n' "$sig_blob" > "$d/data/frames.jsonl"
  printf 'home %s/x\n' "$home" > "$d/data/path.txt"
  printf 'prose: thinkingSignature blobs are public in history, said the note\n' > "$d/data/prose.txt"
  git init -q -b main "$d" && git -C "$d" add -A \
    && git -C "$d" -c user.name=pes -c user.email=pes@example.invalid commit -q -m 'fixture [test]' || return 1
  printf '%s' "$d"
}

# 6. Malformed exceptions row: the scan refuses to run (exit 4), it does not skip the row.
printf '# bad\nEXEMPT only-two | fields\n' > "$tmp/bad-exc.txt"
if d=$(mini bad "$tmp/bad-exc.txt"); then
  SCAN_SCRIPT="$d/scripts/publish-export.sh" run_scan "$d/data"
  expect "a malformed exceptions row stops the scan" 4
  assert "and says why" has "malformed"
else no "fixture repo build failed"; fi

# 7. Full build in the fixture repo: the blob is redacted in the export only, the committed source keeps it.
if d=$(mini full); then
  out=$(bash "$d/scripts/publish-export.sh" 2>&1); rc=$?
  expect "the full script builds, scans, inits and commits in the fixture" 0
  e="$tmp/full/jev_playground-export"
  frames_ok() { grep -q THINKING_SIGNATURE_BLOB "$e/data/frames.jsonl" && ! grep -q "$sig_blob" "$e/data/frames.jsonl"; }
  assert "export value redacted" frames_ok
  assert "short value left alone" grep -q -F '"thinkingSignature":"short"' "$e/data/frames.jsonl"
  assert "prose that merely names thinkingSignature is left alone" grep -q -F 'prose: thinkingSignature blobs are public' "$e/data/prose.txt"
  source_keeps() { git -C "$d" show HEAD:data/frames.jsonl | grep -q "$sig_blob"; }
  assert "committed source still holds the original blob" source_keeps
  one_commit() { [ "$(git -C "$e" rev-list --count HEAD 2>/dev/null)" = 1 ]; }
  assert "export is one commit" one_commit
  tilde=$(printf '\176')   # a literal ~, built without shell tilde-expansion ambiguity
  assert "home path transform still applies" grep -q -F "${tilde}/x" "$e/data/path.txt"
else no "fixture repo build failed"; fi

# 8. Full build with a planted key in a tracked file: refused before init, nothing printed, no export repo.
if d=$(mini planted); then
  printf 'x %s y\n' "$k_gh" > "$d/data/key.txt"
  git -C "$d" add data/key.txt && git -C "$d" -c user.name=pes -c user.email=pes@example.invalid commit -q -m 'plant [test]'
  out=$(bash "$d/scripts/publish-export.sh" 2>&1); rc=$?
  expect "a planted key in the tree fails the full build" 1
  assert "named as path:line" has "data/key.txt:1"
  assert "planted text not printed" lacks "$q16"
  no_export_repo() { [ ! -d "$tmp/planted/jev_playground-export/.git" ]; }
  assert "refused before git init" no_export_repo
else no "fixture repo build failed"; fi

printf 'selftest-publish-export-scan: pass=%d fail=%d\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
