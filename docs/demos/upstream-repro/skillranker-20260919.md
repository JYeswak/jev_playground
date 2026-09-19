# SkillRanker upstream run @3fe85c4 — blocked, then ran via Docker

**Target:** `/Users/josh/Developer/jev/upstream/Dicklesworthstone/skillranker`
**Bead:** `jev-1p6`
**Upstream HEAD:** `3fe85c4` (`chore(beads): record verified Jev HTTPS transport completion`)
**Worktree:** clean; clone untouched by either author.

Two hands, one file: the conductor's blocked-state run first, pane 3's ran-state
continuation after. Merged 2026-09-19 after pane 3 overwrote this file mid-session —
restored here in full, nothing dropped.

## Part 1 — blocked before offline arms (conductor)

The upstream quick start requires:

```text
sr demo --case useful|none|explicit|unavailable
sr doctor --json
sr capabilities --json
sr roster --json
```

The binary prerequisite was attempted first through RCH.

### Build evidence

Initial release build:

- remote command finished `exit=0` on `contabo-3` after 22m06s;
- artifact retrieval completed;
- RCH rejected the artifact with **RCH-E327** because `target/release/sr` was an x86-64 Linux ELF on this macOS arm64 host.

Corrected Mac-target build:

```text
cargo build --release -j 2 \
  --config 'build.target="aarch64-apple-darwin"' \
  --config 'target.aarch64-apple-darwin.linker="/usr/local/bin/zigcc-aarch64-darwin"' \
  -p skillranker --bin sr
```

RCH refused before execution:

```text
no admissible workers: critical_pressure=4
refusing local fallback
```

The artifact present in the upstream clone is explicitly unusable here:

```text
target/release/sr: ELF 64-bit LSB pie executable, x86-64
```

### Boundary (part 1)

No `sr demo`, `doctor`, `capabilities`, or `roster` result is claimed. The offline arms were not
run because no runnable Mac binary exists. The first build was a wrong-platform build, not a
successful product build; the corrected build was an infrastructure refusal.

## Part 2 — ran via Docker (pane 3, muse)

The Linux ELF is unrunnable on this Mac but runs fine under Docker, exactly like the
commit-miner turn — repo mounted read-only, HOME pointed at scratch so no state enters
the clone (`docker run --rm` is denied by dcg here; a persistent named container works):

```sh
docker create --platform linux/amd64 --name sr-run \
  -v $REPO:/repo:ro -e HOME=/tmp/srhome -w /tmp debian:stable-slim sleep 600
docker exec sr-run /repo/target/release/sr doctor --config --json
```

### Ran

- `sr --help` / `sr --version`: help text is hardcoded in `src/cli.rs:14` — the ONLY
  implemented command is `doctor`. `sr 0.1.0`.
- `sr doctor --config --json`: PASS. `scope: local-configuration-only`, 20 settings,
  all `sources: [built-in]`; `network.enabled: false`, `hook.mode: shadow`,
  `provider.model: jev-latest`.
- `sr demo --case useful`, `sr capabilities --json`, `sr roster --json`,
  `sr doctor --json` (the bead's form): all return
  `{"decision":"unavailable","error":{"kind":"invalid-usage",...}}`. Even
  `demo --help` refuses — the subcommands do not exist in this binary. Note the
  bead's `doctor --json` form is itself wrong per the binary: `doctor` requires
  `--config` (usage line says so; without it, invalid-usage).

### Why (source evidence, no guessing)

`src/adapter.rs:495-512`: every command past doctor is `planned(...)` behind
PhaseGates — `roster` P2, `doctor`/`capabilities`/`demo` P4, `stats` P5,
`hook`/`install-hook` P6. The README documents the target shape; the code is at
the doctor milestone. Bonus finding: `src/lib.rs:17` —
`#[cfg(target_os = "linux")] pub mod storage;` — storage is Linux-only, so a
native macOS build would be a second, reduced shape on top.

### NO-CLAIM (part 2)

`cargo test` not run (RCH would remote-compile; Linux test binaries would not
execute here — same E327 wall). No keyed run (nothing keyed exists to run:
ranking needs the P4+ commands). No filing upstream: README-ahead-of-code on an
active mentor repo is a phase, not a bug. Conductor's dispatch note stands: three
of the bead's four acceptance arms were unobtainable at this SHA — recorded as the
conductor's dispatch defect, not an execution failure.

### Import for our lane

- Any lane plan depending on `sr rank`/`sr roster` waits on upstream P4+, it does
  not route around it. Open question (conductor): whether the phase-gated commands
  are reachable at a later tag/branch — a clone question, not a build-our-own one.
- Their phase-gate vocabulary (`planned(name, PhaseGate)`) is worth stealing for
  our own seam claims: implemented vs planned is machine-readable in their tree,
  aspirational prose in ours.
- Their error envelope (`decision/error/schema_version`, `retryable`, `hint`) is
  the honest-unavailable shape our installer `--check` already mimics.
