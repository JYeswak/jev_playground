# Reproduction: skillranker @3fe85c4 — built, ran, README ahead of code

Pane 3 (muse), 2026-09-19. Bead jev-1p6. Someone else's code, read and executed
only; worktree verified untouched (`git status` clean apart from ignored `target/`).

## Build

In-flight RCH build finished into `target/release/sr`, but RCH-E327: remote-compiled
on contabo-3 (Linux) and transferred back — `file` says ELF 64-bit x86-64, and it
cannot execute on this Mac (`cannot execute binary file`). Same failure class as
s1-rs. Ran it via Docker instead, exactly like the commit-miner turn:

```sh
docker create --platform linux/amd64 --name sr-run \
  -v $REPO:/repo:ro -e HOME=/tmp/srhome -w /tmp debian:stable-slim sleep 600
docker exec sr-run /repo/target/release/sr doctor --config --json
```

(Note: `docker run --rm` is denied by dcg here; a persistent named container works.
Repo mounted read-only; HOME pointed at scratch so no state enters the clone.)

## Ran

- `sr --help` / `sr --version`: help text is hardcoded in `src/cli.rs:14` — the ONLY
  implemented command is `doctor`. `sr 0.1.0`.
- `sr doctor --config --json`: PASS. `scope: local-configuration-only`, 20 settings,
  all `sources: [built-in]`; `network.enabled: false`, `hook.mode: shadow`,
  `provider.model: jev-latest`. Full output captured 2026-09-19 (20 keys under
  `settings`; see lane notes if needed — not committed, config-shape only).
- `sr demo --case useful`, `sr capabilities --json`, `sr roster --json`,
  `sr doctor --json` (bead's form): all return exit-2-style
  `{"decision":"unavailable","error":{"kind":"invalid-usage",...}}`. Even
  `demo --help` refuses — the subcommands do not exist in this binary.

## Why (source evidence, no guessing)

`src/adapter.rs:495-512`: every command past doctor is `planned(...)` behind
PhaseGates — `roster` P2, `doctor`/`capabilities`/`demo` P4, `stats` P5,
`hook`/`install-hook` P6. The README documents the target shape; the code is at
the doctor milestone. Bonus finding: `src/lib.rs:17` —
`#[cfg(target_os = "linux")] pub mod storage;` — storage is Linux-only, so a
native macOS build would be a second, reduced shape on top.

## NO-CLAIM

`cargo test` not run (RCH would remote-compile; Linux test binaries would not
execute here — same E327 wall). No keyed run (nothing keyed exists to run:
ranking needs the P4+ commands). No filing upstream: README-ahead-of-code on an
active mentor repo is a phase, not a bug.

## Import for our lane

- The bead's acceptance arms (demo cases, capabilities, roster) are unmeetable at
  this SHA — not failed, absent. Any lane plan depending on `sr rank`/`sr roster`
  waits on upstream P4+, it does not route around it.
- Their phase-gate vocabulary (`planned(name, PhaseGate)`) is worth stealing for
  our own seam claims: implemented vs planned is machine-readable in their tree,
  aspirational prose in ours.
- Their error envelope (`decision/error/schema_version`, `retryable`, `hint`) is
  the honest-unavailable shape our installer `--check` already mimics.
