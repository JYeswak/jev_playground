# Upstream report: `loop-kit/commit-evidence-lint.sh --selftest` is host-config dependent

**Target:** `~/Developer/foundry/loop-kit/commit-evidence-lint.sh`
**Found by:** pane 2 (`WindyJaguar`) claiming `jev-foundry-selftest-git-template-coc`
**Independently reproduced by:** pane 1 (conductor), commands below
**Status:** reported, not patched. The upstream worktree carries unrelated uncommitted changes, so no
edit or commit was made there.

## Reproduction

```bash
cd ~/Developer/foundry/loop-kit
./commit-evidence-lint.sh --selftest                              # rc=1
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
  ./commit-evidence-lint.sh --selftest                            # rc=0
```

Both run back to back on the same bytes. The only difference is whether the host's git configuration
is visible to the selftest.

## Mechanism

The selftest builds a fixture repository and commits into it with a subject of `init`. The host's
global git config installs a `commit-msg` hook that requires a verification level in the subject, the
hook fires inside the fixture, `init` has no level, and the commit is rejected. The selftest reads
that rejection as its own failure.

So the selftest does not isolate git configuration from the environment it runs in. Its result
depends on the machine rather than on the code under test, in both directions: it fails on a host
that enforces commit subjects, and it would pass on a host that enforces nothing even if the lint
itself were broken.

## Why this is worth a patch rather than a workaround

**A selftest whose green is host-dependent is not a selftest.** This is the same defect class this
lane measured in itself on the same day: `foundation/gates.sh` reported `ALL GREEN` in a developed
checkout while two of its nine stages could not pass from a bare clone, because they depended on
untracked local state. The fix there was to pin the run
(`scripts/verify-frozen.sh`) and state the gap. The fix here is one line of isolation.

Suggested shape, not a submitted patch: export `GIT_CONFIG_GLOBAL=/dev/null` and
`GIT_CONFIG_SYSTEM=/dev/null` around the fixture commit, or pass
`-c core.hooksPath=/dev/null` to the fixture `git commit`. Either makes the selftest's answer a
function of the code.

## Scope and non-claims

- The lint's production behaviour is **not** implicated. The defect is in the selftest's
  environment handling, and the ambient failure is a false negative caused by a host hook.
- No claim about other `loop-kit` selftests; only this one was run.
- No edit, commit, or push was made in `foundry`. The worktree there was dirty with unrelated
  changes, and patching around someone else's in-flight work is how attribution gets lost.
- This lane invokes `autofix-precommit.sh` from the same directory on every commit. That path was
  not implicated by this finding and was not tested for the same defect.
