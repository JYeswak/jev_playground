# Gate-edit session 7 (`KIT_GATE_EDIT=1`) - apply the omp-kit guard-completion patch

From pane 1 AmberWillow, 2026-09-25. Joshua approved this kind of session ("approval on all",
2026-09-24). The flag lets you edit kit gate paths (`.omp/kit-guard.json` gatePaths, which include
`.omp/extensions/kit-guard/*` and `.omp/rules/kit-*.md`). Do the one item below, then exit.

## 1. Mission

Validate Jev, build tools from what survives, liven an omp surface, dogfood it, keep the README a
stranger can run. kit-guard is the omp surface that refuses hook bypasses and gate-file edits in
every jev session; this unit lands a stricter version built and tested in the omp-test session.

## 2. What was already checked (pane 1, /tmp/vkg clone at b88b863-era main)

- The patch and hashes: `/Users/josh/Developer/omp-test/var/agent-tmp/guard-completion/`
  `jev-kit-guard.patch` (sha256 `4146b1a09b6f89c4a3d09f1810ff354f72e7dae50f69a9c8fc6852a611d0a519`)
  and `jev-kit-guard-hashes.json` (base and new sha256 per file). jev's current files equal the
  base hashes; the patch applies cleanly and yields the new hashes.
- `bun test ./.omp/extensions/kit-guard/kit-guard.test.ts` on the patched tree: 134 pass, 0 fail.
- jev's OLD suite (the current kit-guard.test.ts, 79 tests) against the patched code: 79 pass.
- 2,395 distinct real fleet bash commands replayed: 1 newly blocked (a gate-file write in a /tmp
  clone, done by a flagged session), 0 newly allowed.
- `bash foundation/gates.sh --portable` on the patched tree: ALL GREEN.

## 3. The item

1. Register with Agent Mail under a fresh name. Reserve `.omp/extensions/kit-guard/policy.ts`,
   `.omp/extensions/kit-guard/index.ts`, `.omp/extensions/kit-guard/kit-guard.test.ts`,
   `.omp/rules/kit-no-verify.md`, `.omp/rules/kit-close-needs-evidence.md`,
   `.omp/rules/kit-jsonl-close.md` and `TESTS.md`, reason `gate-edit-7`.
2. Verify the three base hashes again on the live tree (stop and report if any differs), then
   `git apply` the patch pane 1 names in the dispatch message (the revised one, with its sha256).
   Check the new hashes the dispatch message gives.
3. Rule shadows: copy only the three that exist in jev, byte for byte, from
   `/Users/josh/Developer/omp-kit/rules/{kit-no-verify,kit-close-needs-evidence,kit-jsonl-close}.md`
   (omp-kit commit `1033ab0`). Their sha256 must equal
   `34c5e3e8e062344aa22e4a0272a203f6e8a09dec2f5f5d12804d65bb79a4e312`,
   `b48eb52d4534b15e691033ca5369bccc2c01ddd6ee95388e17c9af65dbea66ed`,
   `a8bdcd79c987ce5a88a6df35a64412f839ad8a737b5d308ae68dda635c535f37`. Create no other rule file.
4. TESTS.md: update the kit-guard.test.ts row (its counts and what it covers, from the new file),
   with its `Run:` command in the path form the runner matches. No second suite: the patch author
   (omp-test pane %15) is folding the behavioral checks the old file had (session_start root,
   agent_end re-read, session_compact re-anchor, path globs, missingPatterns, layout rows) into
   kit-guard.test.ts itself, and sends a revised test-only patch and hash before this session runs.
5. Verify, and paste each result: `bun test ./.omp/extensions/kit-guard/kit-guard.test.ts`; jev's
   previous suite (`git show HEAD:.omp/extensions/kit-guard/kit-guard.test.ts` saved under /tmp)
   against the patched code; `bash scripts/selftest-ttsr-rules.sh` and `bash
   scripts/selftest-ttsr-assert-disabled.sh` (the rule shadows changed);
   `python3 scripts/run-registered-suites.py` reads 0 fail; `bash foundation/gates.sh --portable`
   and `--selftest --portable` exit 0 (stage 80 is slow under load; do not time it out, and record
   a timeout as a timeout, never a pass). Planted mutations of your own that the new tests must
   catch, each restored byte for byte: `bashVerdict` ignoring `core.hookspath` in lower case; the
   agent_end handler never re-reading AGENTS.md; the session_compact handler not queueing the
   re-anchor.
6. Commit path-limited, subject `[mutation] gate-edit-7: omp-kit guard completion (1033ab0) ...`,
   push, confirm `python3 scripts/ci-main-status.py` goes green on the push run.

## 4. Rules

- No deletes, no amend, never skip a hook. No model call, no key. Touch only the reserved paths.
- If any hash differs from what is written here, stop and report instead of applying.

## 5. Close

Comment the results on bead `jev-5b8d` (pane 1 files it with this packet), leave it open for pane
1's non-author check, callback `CALLBACK-GATE7-DONE` to pane 1 via `ntm send jev --pane=1`, then
`/exit`.
