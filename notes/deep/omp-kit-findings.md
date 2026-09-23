# W1 findings

HEAD `33fe6ae`. Installed policy: `.omp/extensions/kit-guard/policy.ts`. Harness: `bun /tmp/jev-rc-p1/w13/run.mjs` importing that file. 12 layout rows. 8 MISMATCH, 4 MATCH. Denominator 12.

## Mismatches

1. `githooks/pre-commit` write expected block, observed pass. Regex: `GATE_PATHS` matches `.githooks/`, not `githooks/`. Planted negative. It came back MISMATCH, so the harness is exercising the installed copy.
2. `rm githooks/commit-msg` expected block, observed pass. Same hole, bash form.
3. `chmod -x githooks/pre-commit` expected block, observed pass. Same hole.
4. `foundation/gates.sh` expected block, observed pass. The added regex covers `foundation/gates.d/[0-9].*.sh`, not the aggregator.
5. `foundation/gates.d/44-native-surface.exemptions` expected block, observed pass. The regex requires a `.sh` suffix.
6. `git config --get core.hooksPath` expected pass, observed block. `core\.hooksPath` has no read exemption. This is the live pane-1 false positive, reproduced on the installed function.
7. `git commit -m "document the -n flag"` expected pass, observed block. `\s-[a-zA-Z]*n` matches ` -n` inside the message.
8. `upstream/typesafe-ai/skills/templates/x.md` expected pass, observed block. `(^|/)templates/` blocks every templates directory, including vendored clones.

## Subdirectory plant

From `jev/notes`, `omp ttsr list` discovered 0 of the 6 project kit rule names and 3 `~/.agents/rules` kit rules. A method that reports 6 project rules from that directory would be blind. This one reported 0.

## Live load

All five running omp processes started before `572e3eb` (2026-09-22 20:07:38 -0600). Pane 2 has no omp child. kit-guard is not loaded in any live pane. Fresh rpc sessions for default, grok, and muse from the repo root did list kit-guard. `omp://ttsr-injection-lifecycle.md` registers rules at session startup and restores eligibility on reload. `omp ttsr list` is a CLI read of the launch directory, not the live session's registered set.

## W1.4

Not overbuilt. Eight mismatches are a path list and a read-versus-write distinction. That is what `.omp/kit-guard.json` was specified to hold (`gatePaths`, `hookDir` from `core.hooksPath`, `readOnlyBashAllow`). A one-line regex patch would miss the next path. The first edit still needs `KIT_GATE_EDIT=1`.

NO-CLAIM: the 8/12 figure is the pure function on 12 strings, not a live pane frame. e2e-live was 0/10 because omp never called the model. The planted-failure arm of that suite was not run.

## Addendum

Census row 2 was wrong. `pgrep -P 1427` missed child `61381`, `omp --profile grok`, started Mon Sep 21 12:18:16. That row is corrected. Models are from `tmux capture-pane` status lines, not titles.

Two more layout mismatches, 10/14 now: `.omp/config.yml` and `.omp/rules/kit-no-verify.md` are not in `GATE_PATHS` (`policy.ts:44-53`). Editing either to disable a kit rule passes the guard.

`.omp/config.yml` lines 79-80 are orphaned comments under the kit-guard list entry. `572e3eb` removed the jev-screen comment anchor. They do not attach to a key.

`scripts/selftest-ttsr-rules.sh` now has hit and miss arms for the six kit rules. Re-run: 105 ok, 0 failed. The old check required exactly 6 project rules; there are 12. The expected count is 12 because the arms exist, not because the check was weakened.

e2e-live root cause: this pane's `OMP_PROFILE=grok` makes omp read the profile models file. The suite writes the default agent models file. `main.ts:2304` exits. Unsetting `OMP_PROFILE`, `PI_PROFILE`, and `PI_CODING_AGENT_DIR` makes the suite 10/10. Planted arm then fails 4/10. omp-continue line 8 fails because the git template commit-msg hook refuses subject `init` (`commit-msg-verification-level.sh:63`), not because identity is unset. With `br` on PATH the script never falls through to JSONL (`omp-continue.sh:30`, `br ready` exit 7). Part B is still paused until the depth callback is sent.
