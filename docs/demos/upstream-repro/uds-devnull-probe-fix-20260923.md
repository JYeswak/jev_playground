# uds transport probe — /dev/null fix — 2026-09-23

Joshua authorized the cross-repo fix. Source is `~/Developer/uds/crates/uds/src/main.rs`. The live command was:

```
printf 'fn main() {}' | rustc --crate-name uds_rch_probe --emit=metadata -o /dev/null -
```

at `main.rs:2185` before this edit. Callers `main.rs:3115`, `rch_bundle.rs:742`, `:942`, `:1296` all call `transport_probe`. They do not embed a second rustc command.

## What changed

`transport_probe_command()` is now the only command string. It is:

```
d=$(mktemp -d) && printf 'fn main() {}' | rustc --crate-name uds_rch_probe --emit=metadata --out-dir "$d" - && rm -r "$d"
```

`REMOTE_COMMAND_FINISHED_SUCCESS` is still the pass check. A rustc failure still fails the shell, because `rm` is behind `&&`.

`transport_probe_command_tests::probe_command_never_writes_dev_null` fails if that string contains `-o /dev/null`.

## Other `-o /dev/null`

`control-plane` and `omp-orchestrator` hits are `curl -o /dev/null`. Those do not invoke rustc. Not changed.

`uds/var/agent-tmp/**` contains old copies of `main.rs`. They are not the compiled probe. Not edited. Touching them would rewrite other agents' scratch.

## Commit

Not committed. `git -C ~/Developer/uds diff --stat -- crates/uds/src/main.rs` is 973 insertions and 162 deletions unstaged, and the index already has 88 insertions and 1262 deletions on that file. Committing the path would take other agents' work. Agent Mail reservation failed: mailbox lock busy, pid 98115, age 52h.

## Worker proof

NOT_RUN. The packet says run the probe through RCH only after pane 1 reports the workers repaired. That report has not arrived. Before/after `stat` of `/dev/null` is therefore not measured.

## Draft upstream note — do not file

rust-lang/rust#111157. rustc 1.64+ writes `-o PATH` by creating a temporary file beside `PATH` and renaming it into place. `rustc --emit=metadata -o /dev/null` run as root in `/dev` replaces the `/dev/null` device node with a regular file. Measured here: contabo-2, -3, and -4 have `/dev/null` as mode 0644. contabo-4's file was created 2026-09-19T16:56:36Z, 0.18 s after this probe ran there as root. Reproduction is the command above. The fix on our side is `--out-dir` of a fresh `mktemp -d`, not `-o /dev/null`. This note is a draft. It was not filed.
