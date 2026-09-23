# Depth directive — all wave-1 panes (2–6), from pane 1 AmberWillow

Joshua, 2026-09-22, verbatim, after reading the first callbacks:

> your agents are marking things uncited easily - they need to be going deeper … with agents of their own

This supersedes the "DEFER / BLOCKED / NOT_RUN are real outcomes" line in your packet §5 **for Part A**.
Those labels are still legal. They are no longer cheap.

## The rule, effective now

1. **Part B waits.** Do not start (or continue) your planning review until Part A has zero unearned
   labels. If you already started Part B, pause it and say so in your next callback.
2. **An UNMEASURED / NOT_RUN / ABSENT / BLOCKED / "not diagnosed" cell is earned only when it carries
   all four:** (a) the exact command, (b) the verbatim failing output line, (c) a root cause located
   in code or config with `file:line`, and (d) at least **two independent routes** tried (a different
   command, a different data source, a different process). Anything missing one of the four is a
   defect in your artifact, and you reopen it.
3. **An infrastructure failure is a finding to root-cause, not a stopping point.** If a suite or tool
   fails before doing its job, rerun it with its temp dirs kept and its stderr unredirected, read the
   script at the failing line, fix the *environment* (never the upstream code), and rerun until it
   either does its job or you can name the exact line that prevents it.
4. **Use agents of your own.** Fan your reopen list out to your own subagents (`task` tool with
   `tasks[]`, or an eval `workpool`). One subagent per independent question. Give each a
   self-contained brief. Read-only research goes to `scout`. You integrate and verify their claims
   before they reach your artifact. A subagent's "done" is not evidence; re-run its decisive command.
5. **Self-consistency check before callback:** a pane cannot report its own process as absent; a
   live-pane setting cannot be reported from a fresh session; a count must be recounted, not copied.

## Your reopen list

### Pane 2 — RedMaple (W1.1–1.3, `jev-deep-kit-8q7.1`, commit cead414)

- **Census row 2 is you, and it is wrong.** `pgrep -P 1427` returns `61381` right now; `ps` shows
  `61381 1427 Mon Sep 21 12:18:16 2026 bun /Users/josh/.bun/bin/omp --profile grok`. Redo the row.
- **`model` is UNMEASURED in 6/6 rows.** Every pane prints its model on the status line
  (`tmux capture-pane -p -t jev:0.N | tail -3`). Measure all six.
- **Live vs fresh is conflated.** `ttsr_repeatMode after-gap / 0` is the *fresh-session* value. Per
  https://omp.sh/docs/ttsr, settings and rules load at session start, so a pane started before
  `572e3eb` runs the settings it loaded then. Split every such column into `_fresh` and `_live`, and
  derive `_live` from the config that existed at that pane's start (`git show <commit-before-start>:.omp/config.yml`,
  the profile config mtime, the global config).
- **e2e-live 0/10 "omp never called the model" has no root cause.** Rerun with `KEEP=1`
  (`tests/e2e-live.sh:10`), then read `$T/out*.txt` and `$LOG`. Check: does `mock-model.mjs` bind
  `PORT=18777` (is the port free)? Does `HOME="$H" omp --version` print (`:36`)? Does omp 18.2.10
  read `$H/.omp/agent/models.yml` (`:23`) for `--model mock/mock` (`:52`)? Does `-p --no-session`
  exist in 18.2.10 (`omp --help`)? Does `init.sh` (`:43`) succeed — its output is discarded?
- **omp-continue "initial commit failed" has no root cause.** The kit README says an unset git
  identity makes the first commit fail. Under an isolated HOME there is no `~/.gitconfig`. Rerun the
  failing step with stderr visible and name the cause. Then set the identity in the test's
  environment (not in the kit code) and run all 11 scenarios.
- **Then run the planted-failure arm** (README: one rule removed + guard block disabled → 4/10 fail).
  A clean suite that cannot call the model never made that arm impossible. Fixing the environment
  did.
- Suggested subagents: e2e-live root cause; omp-continue root cause; census re-measure (models, live
  settings); `omp ttsr scan` of each kit rule over the tree (addendum item 2).

### Pane 3 — TopazRaven (W4.1–4.2, `jev-deep-kit-8q7.2`)

- **"Transcript invocation counts unmeasured (scope block)" is a misread of scope.** Your packet
  allows the jev panes' own session transcripts. They live in
  `~/.omp/profiles/<profile>/agent/sessions/-Developer-jev/` and `~/.omp/agent/sessions/-Developer-jev/`
  (session dirs are named for the launch cwd). Count franken-derived binary invocations (`fh`, `ft`,
  `ftts`, `fsqlite`, `fmd`, `fsw`, and any other you find) in bash tool calls there. Name each
  binary's source repo from evidence (`--version`, `cargo install --list`, the binary's own help).
- **"8 not-assessed origins"**: for each, say why no packet covers it, and whether it is a franken
  repo at all. Name all eight.
- Suggested subagents: one per profile's jev session corpus; one to map binaries to repos.

### Pane 4 — MistyTurtle (W3.1, `jev-deep-kit-8q7.3`)

- Before callback: every row with `executes=unknown` gets its execution command run, or the four
  earned-label fields. Five source lists means five subagents, one per list, each running the
  `--selftest` or command behind every HAVE it scores. Note: `foundation/gates.sh` at `33fe6ae` has
  **3 RED stages** (70, 80, 97). Any mechanism routed through those stages does not execute today.

### Pane 5 — SunnyTiger (W5.1, `jev-deep-kit-8q7.4`, commit 8b09086)

- **gates.sh at the pin is 14 PASS / 3 RED**, not "97 RED". Stage 70: `TESTS.md` does not name
  `work/omp-jev-observer/test/screen-log.test.mjs`. Stage 80: `selftest-ttsr-rules.sh` (12 project
  rules, 6 tested), `selftest-ttsr-assert-disabled.sh`, and `selftest-pin-liveness.sh` fail. Stage 97:
  `num_word()` spells only 8–15 and `gates.d` holds 17. Re-derive the suite result yourself and put
  all three in §4.5 and §4.12, each with its diagnosis.
- **"Calibration runner not re-executed"**: run `cd foundation && python3 run_calibration.py`
  if it is keyless. If it needs a key, the key is in Infisical (`jev-key-canonical-source` rule).
  The receipt is either reproduced or you name why not, with all four fields.
- Re-run more than 5 of the 12 claims. Every keyless command behind a claim gets run.
- Suggested subagents: one per RED stage diagnosis; one re-running all keyless README commands;
  one on the calibration receipt.

### Pane 6 — QuietHarbor (W2.1, `jev-deep-kit-8q7.5`)

- No callback yet. Apply the rule before you send one. The pin-liveness addendum stands: the
  instrument W2.1(c) depends on is RED, so diagnose it before you use it.
- Suggested subagents: B13 census; B12 claim coverage; B11 with the pin-liveness diagnosis.

## Callback

Same channel and shape as your packet §7, tagged `CALLBACK-P<N>-DEPTH-DONE`, listing every reopened
cell with before → after, and every label still standing with its four fields.
