# jev-90id: residual fixture builders under the inherited-`GIT_DIR` sentinel

Date 2026-10-11. Producer CyanLake. Source under test: origin/main `d1226888` (a fresh `git clone` of
`JYeswak/jev_playground`, disposable, nothing run against the live checkout). Lane: offline, no model call, no key.
Fixes already landed for this bead: `93e33e0b` (hook selftest, miniwob fixture, publish-export) and `e6b9186f`
(`run-registered-suites.py`). This file records the sentinel runs they were checked with.

## Sentinel

A subject is run from the clone's root with the clone itself exported as the caller's repo. Before and after, five
fingerprints of that clone are compared: sha256 of `.git/config`, `HEAD`, reflog line count, sha256 of
`git ls-files -s`, sha256 of `.git/index`. Any difference means the subject wrote through the inherited environment.

| shape | exported |
|---|---|
| `none` | nothing (clean-env control) |
| `dir` | `GIT_DIR=<clone>/.git` |
| `full` | `GIT_DIR=<clone>/.git`, `GIT_WORK_TREE=<absent dir>`, `GIT_INDEX_FILE=<absent file>` (the 2026-10-06 incident shape) |

Clone baseline for the table: config sha256 `738f79c458f48511…`, HEAD `d1226888`, reflog 1, staged-entries sha256
`cfb5644c1a30030d…`.

## Results

| subject | none | dir | full | fingerprints changed |
|---|---|---|---|---|
| `scripts/run-registered-suites.py --selftest` (as shipped, `e6b9186f`) | rc 0, 1.6 s | rc 0, 1.3 s | rc 0, 1.4 s | none in all three |
| same file at `93e33e0b` (before the scrub) | rc 0 | rc 0 | rc 1 (git refuses the absent work tree) | `dir`: config, HEAD, reflog, staged entries and index all changed; config gained `[user] email = test@example.com name = test` |
| `work/x7-gate-rules/test_replay.py` | rc 1, 0.1 s | rc 1, 0.1 s | rc 1, 0.1 s | none in all three |
| `scripts/publish-export.sh`, full script | rc 1, 32.3 s | rc 1, 31.3 s | rc 1, 31.9 s | none in all three |

The pre-fix row is the evidence that the sentinel can see this builder: the same subject, same clone, same environment,
RED before the scrub and unchanged after it.

## x7 `test_replay.py`: not a leak

rc 1 is identical in all three shapes and the caller is untouched. All 3 tests fail with
`AssertionError: replay.py must implement isolated X7 command replay`: they are red-first tests for a module,
`work/x7-gate-rules/replay.py`, that does not exist in the tree (`ls` of the directory: no `replay.py`). Nothing was
changed there: the failure is independent of the environment and belongs to that lane.

## publish-export.sh: the pre-`init` refusal, exactly

`git init` is not reachable at `d1226888`. The script's worktree scan (line 92, before the `unset` and `git init`)
refuses, so the export directory never gains a `.git`: `EXPORT SCAN FAIL (worktree)`, exit 1, in all three shapes, and the
caller fingerprints are unchanged. The scan was not bypassed and no diagnostics were printed from it. The failing checks, measured by running
the script's own `scan_export` function on the disposable export tree with matched text masked (paths and counts only):

- `/Users/josh` hits: 0. `encrypted_content` files: 0.
- Key-pattern hits: 23 in total, 18 on the known-benign list, **5 unexplained**:
  `docs/demos/upstream-repro/issue-1-state-preview-plaintext-credentials.md:48`,
  `.omp/hooks/post/jev-gate-observe.test.mjs:235`, `work/jev-hqha/hqha.errsample.json:1`,
  `work/jevcache-probe/repro-4-state-preview-credentials.sh:46`, `work/gate-question-gap/extract-5-extension.jsonl:895`.
- Blob-shaped `thinkingSignature` lines: **280** in 2 files, `work/jev-claim-check/l3-frames.jsonl` and
  `work/nev-injection/l4-frames.jsonl`.

The script then calls `scan_export` a second time to print the reasons, and that call dies silently: under `set -euo pipefail`
the first statement of the function (`hits=$(grep -r -c "/Users/josh" … | awk …)`) exits non-zero when there are zero
matches, so nothing after "EXPORT SCAN FAIL (worktree)" is ever printed. Reproduced by running the extracted function under the
same `set` flags: the line printed after the second call is never reached. Not fixed here: a working diagnostic would print the
matching key lines.

The script's first act is `rm -rf "$ROOT/../jev_playground-export"`. It was only ever run from a clone inside an owned scratch
directory, so that sibling was the clone's own; the real `/Users/josh/Developer/jev_playground-export` was never run against or read.

**Not exercised versus proven.** The full script's scrub is NOT exercised (it cannot reach `git init`). What is proven is a
replay: `scripts/selftest-fixture-isolation.sh` extracts the script's post-scan block (`unset GIT_DIR …` through the `commit -qm`
line) verbatim and runs it against an owned export directory with a decoy exported as the caller. As shipped the decoy is
unchanged; with the `unset` line deleted the decoy changes (its config gains `core.hooksPath` and the identity). A replay is
not a full run, and if the block or its `unset` line is removed or renamed in the script the arm fails loudly.

## miniwob `run-after-rotation.sh`, hook selftest

`check_provenance` is replayed the same way (extracted from the script, run with the decoy as the caller): unchanged as shipped,
changed with its `unset` line deleted. The script itself was not run end to end (it needs a run sheet). The commit-msg hook
`--selftest` arms were already in `selftest-fixture-isolation.sh` (`93e33e0b`).

## Regression gate

`scripts/selftest-fixture-isolation.sh` now has 15 arms (was 9), 10-11 s, all pass; live `.git/config` sha256
`8c986e2a6548e039…` before and after. New arms: `run-registered-suites --selftest` as shipped and with its scrub turned into
`pass` (the decoy changes), the publish-export replay pair, the miniwob replay pair.

## Not done

- Installed `.git/hooks/commit-msg-verification-level.sh` differs from the source (source sha256 `af35e790…`, installed
  `9a83563e…`). Activating the repaired copy is the guarded live-restoration step of `jev-n3lx`; nothing was copied through the guard.
- publish-export's silent second scan and its 5 unexplained key hits and 280 blob lines are filed, not fixed (`jev-x5cy`).

## No-claim

One environment family was exercised (`GIT_DIR`, with and without `GIT_WORK_TREE`/`GIT_INDEX_FILE`), not every way a caller
can steer git. A clean sentinel says the writes went nowhere else for those runs; it does not say the builders are otherwise correct.
