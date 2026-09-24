# Gate-edit session 2, part b: stage 80 and jev-sx9, decided by data

From pane 1 AmberWillow, 2026-09-24, answering pane 7's two decisions (it went idle at 03:14Z).
Session still carries `KIT_GATE_EDIT=1`. Same rules as `gate-edit-2.md`.

## What the data says (measured by pane 1, read-only)

1. **`~/.agents/rules` has an owner and a source: `~/Developer/omp-kit`** (Joshua's repo; commit
   `b651509` "one source for ~/.agents/rules", `d2514a1` 21:05, `31abdfe` 21:11). The installed
   `~/.agents/rules/*.md` equal `~/Developer/omp-kit/rules/*.md` byte for byte for all eight drifted
   names. Nobody has to "own" the global root; we align to its source.
2. **The five `ft-*-doctrine` rules were retired on purpose, on jev's own evidence.**
   `~/Developer/omp-kit/retired/REASONS.tsv`: ft-md 0/25, ft-rs 0/25, ft-sh 1/25 real edits bound,
   against a preregistered 20% bar (`NEGATIVE_EVIDENCE.md` R64, line 2896); ft-py and ft-json
   retired with the pack for the same mechanism. Our selftest still demands they exist, so it is
   the stale side.
3. **All eight drifted kit versions are strict improvements over the project copies** (pane 1
   diffed each):
   - `kit-no-verify`: read forms (`--get`, `--list`, `-l`) exempt; fires on a value set,
     `--unset`, or a `-c` override. This is the jev-sx9 fix.
   - `kit-close-needs-evidence`: reason flag must follow whitespace, and `--help`/`-h` is exempt.
   - `kit-jsonl-close`: handles escaped quotes, and needs the full JSON line.
   - `kit-test-skip`: catches `skipif`.
   - `kit-unverified-done`: catches `passed` and `completed`.
   - `kit-weasel-retry`: line-anchored.
   - All six also gain a "Blocked before it ran" first line.
   - `bash-glob-silenced` and `bash-pipe-exit` only add `interruptMode: never`.

## Do, in order

1. Copy the eight kit files over the project copies, verbatim. Use one `cp` from
   `~/Developer/omp-kit/rules/` naming the eight files. That command text contains no trigger
   words, so the old rule loaded in this session will not interrupt it. Then `cmp` each pair.
2. `scripts/selftest-ttsr-rules.sh` (not a gate path; edit it with the edit tool, not bash, since
   the rules are `tool:bash` scope):
   - Replace the five ft-* blocks (lines ~85-160) with ONE retirement arm: each of the five names
     must be ABSENT from `~/.agents/rules`, FAIL if any is present. Cite REASONS.tsv and R64 in a
     comment.
   - Add kit-no-verify arms with `omp ttsr test`:
     - quiet on `git config --get core.hooksPath`;
     - quiet on a plain text search for the key name;
     - fire on setting a value;
     - fire on `-c core.hooksPath=`;
     - fire on `--unset`.
3. Run `bash scripts/selftest-ttsr-rules.sh` and then stage 80. Both must exit 0. Before the fix
   it exits 1, with 4 missing-rule FAILs and 8 DRIFT FAILs. Paste both counts.
4. Planted negative, restored byte-identical afterwards: revert `.omp/rules/kit-no-verify.md` to
   HEAD and show that the drift guard and the quiet-on-read arm go red.
5. Commit (`[mutation]` level), then close jev-sx9 reason-first with the before and after counts.
6. Then continue `gate-edit-2.md`: first jev-fmy, then ratify ae01091.

If a rule interrupts you twice on the same step, write the step's output into a file and tell pane
1 instead of retrying. Never delete anything. Callback `CALLBACK-GATE2-DONE` to pane 1 via
`ntm send jev --pane=1`, then `/exit`.
