# SkillRanker upstream run — blocked before offline arms

**Target:** `/Users/josh/Developer/jev/upstream/Dicklesworthstone/skillranker`
**Bead:** `jev-1p6`
**Upstream HEAD:** `3fe85c4` (`chore(beads): record verified Jev HTTPS transport completion`)
**Worktree:** clean; clone untouched.

## Attempted path

The upstream quick start requires:

```text
sr demo --case useful|none|explicit|unavailable
sr doctor --json
sr capabilities --json
sr roster --json
```

The binary prerequisite was attempted first through RCH.

## Build evidence

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

## Boundary

No `sr demo`, `doctor`, `capabilities`, or `roster` result is claimed. The offline arms were not
run because no runnable Mac binary exists. The first build was a wrong-platform build, not a
successful product build; the corrected build was an infrastructure refusal.
