# jev-x5cy: the publish-export scan, its five key-shaped hits and 280 signature lines

Date 2026-10-11. Producer CyanLake. Base: origin/main `0d15436b` (the defect was measured at `d1226888`; nothing in the
files below moved between them). Offline, no key, no model call. Every run happened in a disposable clone inside an owned
scratch directory, so the destructive first step of `publish-export.sh` (`rm -rf ../jev_playground-export`) only ever hit that
clone's own sibling; the real `jev_playground-export` was never run against, read or listed.

Handling rule used throughout (secret-emission discipline, director ruling on `jev-x5cy`): a hit's matched text was never
printed, by me or by the script. Each hit was examined as shape, length, character-class mask, a sha256 prefix of the match,
the line with the match replaced by a marker, and git provenance. Where this file says what a string "is", that came from
those facts, not from reading the string.

## 1. What was wrong

`scripts/publish-export.sh` refused the real tree with only `EXPORT SCAN FAIL (worktree)`.

- The scan ran twice: once silenced, once "to show reasons". Under `set -euo pipefail` the second call died on its first
  statement (`hits=$(grep -r -c ... | awk ...)`; `grep` exits 1 when nothing matches and `pipefail` carries that out), so
  nothing after the heading was ever printed whenever the `/Users/josh` count was zero.
- Had it printed, it would have printed whole matching lines (`printf '%s\n' "$unexplained"`): possible credentials, in one
  case a 443,005-byte line.
- Every `grep ... 2>/dev/null` also hid real grep errors, so an unreadable file read as "no hits".

## 2. What changed in `scripts/publish-export.sh`

| Change | Why |
|---|---|
| Diagnostics are a count plus `path:line` per finding (first 25, then "... and N more"); matched text is never printed in any mode | secret-emission discipline |
| `loc_hits` / `files_with`: grep exit 1 is "no match" (clean), exit >= 2 is a scanner error | the original conflated them in both directions |
| New exit 4 "scanner error", distinct from exit 1 "finding" and 2 "usage"; a malformed exceptions row is also exit 4 | an incomplete scan is never a pass and never reads as a content finding |
| The scan runs once and its report is printed once (`scan_or_exit`) | removes the silent second call |
| Transform 3: a `thinkingSignature` value of 100+ characters of `A-Za-z0-9+/=_-` becomes `THINKING_SIGNATURE_BLOB` in the export copy | the canonical mechanism: the existing content transforms, documented in `docs/PUBLISH-SET.md` |
| Exact exception rows, `docs/publish-key-exceptions.txt`: path + sha256 of the whole exported line + hit count | the director's "exact, narrowly scoped" form; no filename, directory or pattern rows |
| The AWS documentation example now excuses only itself: it is removed from the line and the line is re-tested | the old `grep -v` excused any other key sitting on the same line |
| The redactor source is excused by its exact path `demos/preaction-abstention/src/redact.mjs` | the old `grep -v redact.mjs` excused any line, in any file, that merely mentioned the name |
| `--scan DIR` scans any tree read-only | lets the selftest and a reviewer run the real scan code |

No pattern, count or threshold was loosened: `KEYPAT` and the signature shape are byte-for-byte the original contract. Two
existing excuses were tightened; on the current tree neither tightening changes a verdict (all 17 AWS-example lines have no other
key shape on them, and no hit depended on the `redact.mjs` substring).

## 3. The five unexplained key-shaped lines: individual rulings

Fingerprints are of the exported line (what the scan hashes); "hits" is the key-pattern count on it.

| # | Path:line | Hits | Line sha256 (prefix) | Examined as | Ruling |
|---|---|---|---|---|---|
| 1 | `docs/demos/upstream-repro/issue-1-state-preview-plaintext-credentials.md:48` | 1 | `682c74bc` | the match is the PEM header marker (21 chars); the whole value is header + the literal word `FAKE` + footer, no key body; the sibling lines of the same block are labelled fake (`...FAKE-EXAMPLE-NOT-A-REAL-KEY`); added by `bdd1c9a6` as an upstream defect report | **synthetic, proven by the line's own content. Exact exception row.** |
| 2 | `.omp/hooks/post/jev-gate-observe.test.mjs:235` | 1 | `c4e0c5d8` | the element is the PEM header marker alone, in a unit-test array of secret shapes whose neighbours are generated with `repeat()`; added by `1e16af45` | **synthetic test input, no key material. Exact exception row.** |
| 3 | `work/jev-hqha/hqha.errsample.json:1` | 2 | `f5904f4b` | one 20-char AWS-shaped identifier occurring twice (match sha256 prefix `4ad17f43`) inside a captured error sample quoting a test generator's `SECRETS` list; its first 13 characters equal the AWS documentation example and its last 7 letters differ; occurs nowhere else in the tracked tree; added by `0d2d2beb` | **uncertain: NOT proven synthetic (reviewer `779d84f6` rejected the exemption). REDACT row, no exemption**: the export copy has both matches replaced by `KEY_SHAPE_REDACTED`; the source file is untouched. If the `jev-hqha` owner can show it was ever live it must be rotated; not verifiable offline |
| 4 | `work/jevcache-probe/repro-4-state-preview-credentials.sh:46` | 1 | `b50782ff` | the same FAKE-bodied PEM stub as #1, in the probe that produced it; added by `bdd1c9a6` | **synthetic. Exact exception row.** |
| 5 | `work/gate-question-gap/extract-5-extension.jsonl:895` | 1 | `b07c898a` | the match (17 chars) is a PEM-marker search term inside the `-E` alternation of a `git grep` command in a recorded session command; no key material; added by `f3f544fb` | **search term, not a value. Exact exception row.** |

Each row binds path + whole-line hash + hit count, so none of them covers another file, an edited line, or a second key
on the same line (arms below). Rows 1, 2, 4 and 5 are EXEMPT rows, proven by the line's own content (the reviewer accepted these
four as structural non-key text). Row 3 is a REDACT row: it grants no permission, it removes the value from the export copy, and a
stale or edited row stops the build (exit 4) instead of being skipped.

## 4. The 280 `thinkingSignature` lines

Two files, both frame captures: `work/jev-claim-check/l3-frames.jsonl` (397 blob values on 201 lines) and
`work/nev-injection/l4-frames.jsonl` (150 values on 79 lines). 547 values on 280 lines; no other file in the tree has one.

- Not approved export content (ruling). Transform 3 replaces each value in the **export copy** with `THINKING_SIGNATURE_BLOB`.
  Measured on the real export: 397 and 150 placeholders, 0 residual blob-shaped values, line counts identical to the sources, the
  JSON shape intact (the key stays, only the value changes). Export size 2,276,561 -> 1,597,960 bytes and 593,800 -> 511,528.
- Original evidence preserved: the source files are not edited; their git blobs are unchanged (`l3-frames.jsonl` blob
  `a916b59bba2a...`); the values were never printed or deleted.
- The scan still refuses any blob-shaped value that survives the transform.

## 5. Evidence

All on disposable clones; the live checkout's `.git/config` sha256 was `8c986e2a6548e039` before and after.

**Real tree, full script, fresh clone of origin/main plus these changes** (`bash scripts/publish-export.sh`, ~66 s each):

| caller environment | rc | caller config / HEAD / reflog / staged entries / index | export |
|---|---|---|---|
| none | 0 | unchanged | `.git` present, 1 commit, 6438 files, `EXPORT SCAN PASS` |
| `GIT_DIR=<clone>/.git` | 0 | unchanged | same |
| `GIT_DIR` + absent `GIT_WORK_TREE` + absent `GIT_INDEX_FILE` | 0 | unchanged | same |
| `GIT_DIR`, with the script's `unset GIT_DIR ...` line deleted (mutant) | 0 | **config, HEAD, reflog, staged entries and index all changed** | RED, the scrub is load-bearing |

This is the full script (archive, transforms, scan, `git init`, commit), not a replay, and it reached `git init`: the item that
was "not exercised" in `jev-90id` is now exercised. The scan summary on the real tree after rework: 21 flagged lines, 17 explained by the
AWS documentation example, 0 in the redactor source, 4 by exact exception rows, 0 unexplained, 0 signature blobs, 0 home paths.

**`scripts/selftest-publish-export-scan.sh`, 48 arms, ~4 s**, run for real (`--scan DIR` over fixtures and the full build inside a
tiny fixture repo whose sibling export is the fixture's): the full fake-key negative (one planted line per key shape, six
shapes, built from parts so the selftest holds no key-shaped literal) is refused with all six `path:line` and none of the planted
text in the output; a no-match tree is clean (the original defect); a planted home path, `encrypted_content` and a signature blob are
refused by location; the exempted line passes at its own path, and fails when edited by one character, moved to another path, given
a second key, or listed with the wrong hit count; the AWS example alone passes and does not excuse another key on its line; an
unreadable file and a malformed row are exit 4; the full build redacts the blob in the export only, keeps the source blob,
and a planted key fails the full build before `git init` with no export repo created.

**Mutation check**, `PES_SUBJECT` pointing at a mutated copy; each mutant must turn at least one arm RED:

| mutant | arms RED |
|---|---|
| matched text added to the printed locations | 13 |
| grep error treated as clean | 3 |
| exception matched by path only (hash ignored) | 2 |
| signature transform removed | 3 |
| exception ignores the hit count | 1 |
| AWS example excuses the whole line | 2 |

`scripts/selftest-fixture-isolation.sh` (15 arms) now runs the full `publish-export.sh` in a fixture repo that is its own
caller: untouched as shipped, changed with the `unset` line deleted. Fresh clone, clean environment, `foundation/gates.sh`:
stages 10-20, 40-97 PASS (stage 70 registry, stage 80 including both new selftests, stage 97); `test_git_optional_locks.py` OK.

## 6. Not done, not claimed

- **Stage 30 `30-no-secrets` is RED on origin/main independently of this change**: `work/x7-gate-rules/test_replay.py:136`,
  `TYPESAFE_API_KEY value (value withheld)`, present at `d1226888` and in a clone without these files. Not touched; belongs to the x7 lane
  (the same file whose three tests fail for the missing `replay.py`).
- Passing the scan is not proof the export is free of secrets; it is the existing allowlist of shapes plus four proven-synthetic
  lines. The hqha line is redacted, not excused (rework). The scan's history leg still checks only `/Users/josh` and `encrypted_content`
  (unchanged from before).
- The real `jev_playground-export` was not rebuilt or scanned; building and publishing it is the owner's act.
- The installed commit-msg hook copy still differs from source (`jev-n3lx` live restoration, guarded).
- One environment family was exercised for the caller sentinel (`GIT_DIR`, with and without work tree and index).

## 7. Regex notes (regex-engineering)

- Engines: macOS `grep -E` and BSD `sed -E` over a trusted tree (our own tracked files, not external input); no backreference
  in any pattern, so there is no backtracking-class risk to bound. Largest single line scanned: 443,005 bytes; the run is 66 s end to end.
- `KEYPAT` and the scan's signature shape are the original contract, byte for byte. The one new pattern is the `sed` substitution
  for transform 3: a literal-anchored prefix (`"thinkingSignature"`, optional spaces, `:`, optional spaces, a quote), then
  `[A-Za-z0-9+/=_-]{100,}`. The repeated class excludes `"`, which is what follows a value, so each value is owned by exactly one
  attempt; it is the same class and bound the scan refuses, so a value the transform leaves is a value the scan reports (no
  third state). The placeholder is 24 characters, under the 100 bound, so a second pass changes nothing.
- Semantics preserved on purpose: a value shorter than 100 characters and the prose "thinkingSignature" are untouched (arms:
  short value left alone; prose is not a value). `/Users/josh` and `encrypted_content` matches switched from regex to fixed-string
  (`-F`); neither pattern had a metacharacter, so the match set is identical.
- Not covered: BSD `sed -E` and `grep -E` only; no GNU or Windows behaviour is claimed. Quote-escaped signature values inside an
  embedded JSON string (`\"thinkingSignature\":`) are not the refused shape and are unchanged, as before.

## 8. Rework after reviewer FAIL `779d84f6`

Finding: the exemption for row 3 labelled an unproven AWS-shaped identifier benign. Accepted. The four structural non-key rows stay.

- `docs/publish-key-exceptions.txt`: row 3 is now `REDACT`, not `EXEMPT`; no permission remains for it. `publish-export.sh` gained
  `redact_rows`: for each REDACT row it finds the exported line by sha256 (after the existing transforms), checks the hit count, and
  replaces every key-shaped match on it with `KEY_SHAPE_REDACTED` in the export copy only. A missing file, a hit-count mismatch or a
  line that no longer matches stops the build (exit 4): a stale row is never skipped.
- Real tree, fresh clone, full script: export line redacted (2 markers, 0 residual key shapes, line count equal to the source);
  the source blob is unchanged; scan summary 21 flagged, 17 AWS example, 4 exact rows, 0 unexplained. Full run rc 0 in 65-66 s under
  no env, `GIT_DIR`, and `GIT_DIR` + absent work tree + index; caller config/HEAD/reflog/staged/index unchanged each time; with the
  `unset GIT_DIR ...` line deleted all five change.
- New selftest arms (40 -> 48): a REDACT row redacts the planted uncertain line in the export and leaves no key text; the source keeps
  it; the same row is not an exemption (`--scan` of the unredacted line fails with path:line); an edited line makes the row stale (exit 4).
  Mutants (arms RED): the original six 14/3/2/4/1/2, plus redact_rows doing nothing 2, a REDACT row that also exempts 2, a redaction that
  leaves the key text 2.
