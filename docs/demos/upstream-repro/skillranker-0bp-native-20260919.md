# `jev-0bp` native SkillRanker build boundary

**Target:** clean `origin/main` export at `4ed4c9b7a57cd1a110e1a0c5f42e111a3f60177f`
**Vendored clone:** untouched.

## Evidence

The suggested path was checked:

```text
~/.rustup/toolchains/1.95.0-aarch64-apple-darwin/bin/cargo
cargo 1.95.0
```

But that path is a managed RCH launcher, not an unshimmed native Cargo binary. It delegates to:

```text
~/.rustup/toolchains/1.95.0-aarch64-apple-darwin/bin/cargo-rch-real
```

That path is also a managed hard-deny dispatcher. For `build`, it returns:

```text
LOCAL RUST BUILD DENIED BY CONSTRUCTION — CONTABO OR BUST
The real compiler is not reachable from any local path.
```

The first in-flight build produced an artifact, but verification showed:

```text
target/release/sr: ELF 64-bit LSB pie executable, x86-64
```

RCH rejected it as `RCH-E327`; it is not runnable on this macOS arm64 host.

A corrected `aarch64-apple-darwin` RCH build was attempted and refused before execution with:

```text
no admissible workers: critical_pressure=4
```

## No-claim

- No `sr demo` offline arm ran.
- No `sr doctor`, `sr capabilities`, or `sr roster` result is claimed.
- No native Mac binary was produced.
- The conductor tip's absolute path is not unshimmed in the current installation; both Cargo layers terminate in the local-build hard deny.
