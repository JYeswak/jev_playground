# Skillranker at origin/main (ba5da08): builds, reads corpus, keyed rank blocked (2026-09-19)

## Checkout

Existing clone moved 54705d4 → ba5da08 (217 commits, `feat(p5): sr replay and
--save-case on sr rank`). Tree clean before and after; nothing committed inside the
clone. Bead jev-0bp claimed in_progress before starting.

## Build: remote Linux OK, macOS native BLOCKED (verbatim, in order)

1. `cargo build --locked --release --bin sr` via rch → remote compile on contabo-1
   SUCCEEDED but artifacts are ELF: "RCH-E327 ... targets aarch64-apple-darwin and the
   retrieved artifact(s) are ELF ... exit 102" (21 min).
2. Local build refused by operator order, not by toolchain: the toolchain `cargo` is a
   wrapper terminating in "⛔ LOCAL RUST BUILD DENIED BY CONSTRUCTION — CONTABO OR BUST
   ... Joshua, 2026-09-07 ... no rust builds" (lanes registry: "i do not want any rust
   builds to happen locally - zero - none"; both Mac workers `enabled = false`).
   I did not circumvent it; the real binary it guards was left alone.
3. Sanctioned cross path (`--config build.target="aarch64-apple-darwin"` on worker)
   fails in `ring-0.17.14`: Linux `cc` rejects `-arch arm64 -mmacosx-version-min=11.0`
   (exit 101, 33s). No mac SDK on workers.
4. Net: no runnable macOS `sr` exists. The Linux ELF binary (20MB, retrieved) runs on
   workers: `sr 0.1.0`.

## Corpus-blindness: REFUTED (source + behavior, not the conductor's grep)

- Source: `src/pipeline/cass_source.rs:41,45` calls cass `.sessions()`; `src/context/cass.rs`
  lists/parses archive sessions (276, 588–637); `src/context/discovery.rs:193` discovers
  workspace sessions. The old "src never reads the corpus" no longer describes this tree.
- Behavior, keyless, on the worker: `rank --context ctx-X.json --dry-run --json` from a
  scratch workspace (2 skills) embeds corpus-derived state in the provider request —
  `latest_user_request`, `recent_messages`, `project_signals`, `candidates: 2` from disk
  roster. Context A (rust-test request) vs B (birthday poem): payloads differ (3650 vs
  3603 bytes, `provider_request` + `disclosure` differ; B's request contains the poem).
  A pipeline that never read the corpus could not do this. Full keyed rank still needed
  for quality; blindness is dead.

## Re-score vs gate: BLOCKED

No keyed rank is runnable: no mac binary exists, and TYPESAFE_API_KEY does not leave
this machine for a worker job (stated refusal, not an oversight). The old frozen gate
has no runnable equivalent at main — `tests/eval/` fixtures are contract artifacts
whose README says they "are not benchmark results" and contain no live responses.
`sr demo`, `doctor`, `capabilities`, and `--dry-run` all work keyless on the worker;
none of them is a rank.

## Scratch left in the clone (diagnostic, reported, not committed)

`skillranker/sr-linux-amd64` (retrieved ELF, 20MB), `skillranker/scratch-ho/` (2-skill
workspace + 2 contexts for the variance test). Awaiting deletion approval per RULE 1.

## NO-CLAIM

One machine, one toolchain, Linux-only execution; dry-run proves input-dependence of
the pipeline, not rank quality; the 0.90 gate is the old tree's policy, not ground
truth, and unrun here. Bead jev-0bp updated with this receipt.
