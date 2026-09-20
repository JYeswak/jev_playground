# Franken crate / process unused-alpha map — Jev lane

**Date:** 2026-09-19 (America/Denver)  
**Target path (Studio):** `/Users/josh/Developer/jev/docs/demos/upstream-repro/franken-crate-alpha-20260919.md`  
**Public face:** `JYeswak/jev_playground`  
**Executor hostname this dig:** `grok-bot-vm-405183638` (box-scoped subagent)  
**Requested machineId:** `439e8c39-3223-4273-9ce4-4263468cbba7` (`Joshs-Mac-Studio.local`)

## NO-CLAIM (read first)

1. **Hostname:** This executor is **not** `Joshs-Mac-Studio.local`. Do not treat any path under `/Users/josh/Developer/...` in this receipt as live-verified on Studio in this turn.
2. **Live `fh` digs:** **Not run.** Box-scoped subagents do not get `ListMachines` / `Shell.machineId` (host: `isBoxScopedSubagent`). Studio Tailscale SSH from the box timed out (`100.93.84.11:22`). Success criterion "live fh output in the receipt" is **unmet**; parent must re-run the §fh command block on Studio and paste rows.
3. **Live `ripwire` cold maps:** **Not run** for the same reason. Symbol ranks below are from public `redhat-et/ripwire` docs + Jev doctrine that already names ripwire — not from a fresh `--exemplar` / `--for` invocation on Studio mirrors.
4. **Numbers:** No invented counts. Crate lists are from public `Cargo.toml` / trees via `gh api` at dig time. Process→apply rows cite file paths; "Jev uses today?" is from `jev_playground` docs (`GATES.md`, `NEGATIVE_EVIDENCE.md`, `.fh-agents.toml`, `STATUS.tsv`), not from Studio pane observation.
5. **Private mirrors:** `JYeswak/franken-harvest` is **private**; contents were readable via authenticated `gh` as `JYeswak`. Upstream `Dicklesworthstone` has no public `franken-harvest` / `ripwire` repo under that name — Studio `~/Developer/franken-harvest` and `~/Developer/ripwire` remain the live oracles when hostname proves Studio.

---

## Crates inventory

Prefer list from the dig brief. One-line purpose from README / Cargo `description` / module docs. Workspace members abbreviated when large.

### franken-harvest (`JYeswak/franken-harvest`, private; bin `fh` → `/Users/josh/.local/bin/franken-harvest` on Studio per prior transcripts)

| Crate / package | Purpose |
|---|---|
| `franken-harvest` (root package) | Fail-closed, live-mirror evidence harvester (`Cargo.toml` description). |
| `clippy-ratchet` (bin) | Clippy pedantic floor ratchet vs `clippy-pedantic-floor.txt`. |
| `fh-stale-artifact-check` / `fh-collect-check-sync` (bins) | Stale-artifact and collect/check sync gates. |
| Dep: `frankensearch-{core,lexical,fusion,rerank}` | Standing search / suggest ranking (rerank default-features=false — no frankentorch). |
| Dep: `asupersync`, `franken_markdown` | Cancel-correct runtime + markdown receipts. |

**fh command surface** (from prior Studio transcript `fh --help`, not re-run this turn):  
`collect`, `coverage`, `commit-index`, `daily`, `verify`, `mine`, `movement`, `technical-manifest`, `search`, `suggest`, `why`, `how-eval-raw`, `how-eval-grade`, `standards`, `install`, `rollback`, `doctor`/`health`, `repair`, `quickstart`, plus later transcripts also showing `arcs`, `appearance`, `bead-index`, `simultaneity`, `advise`, `agents`.

### franken_engine (`Dicklesworthstone/franken_engine`)

| Crate | Purpose |
|---|---|
| `franken-engine` | Native Rust runtime for adversarial extension workloads; deterministic replay, crypto decision receipts, fleet containment (repo description). |
| `franken-core` | Shared core types / primitives for the engine workspace. |
| `franken-extension-host` | Extension host surface for sandboxed workloads. |
| `franken-metamorphic` | Metamorphic / property test support. |
| `franken-engine-deterministic-{trait,derive}` | Deterministic replay contracts + derives. |
| `franken-engine-fixed-layout-derive` | Fixed-layout serialization derives. |
| `franken-engine-test-support` / `…-control-plane-integration-tests` | Test + control-plane integration support. |
| `dp` | Workspace member (dp subtree). |

**Process-bearing modules (file cites):**  
`crates/franken-engine/src/promotion_gate_runner.rs` — four-gate self-replacement runner (Equivalence, CapabilityPreservation, PerformanceThreshold, AdversarialSurvival).  
`crates/franken-engine/src/universal_dominance_ratchet.rs` — monotonic supremacy board + frontier-gap ledger (`bd-1lsy.1.6.4`).  
Also: `corpus_promotion.rs`, `law_promotion_lifecycle.rs`, `differential_oracle.rs`, `parser_oracle.rs`, `oracle_release_gate.rs`.

### ripwire (`redhat-et/ripwire` — C++23; Studio mirror `~/Developer/ripwire`)

| Artifact | Purpose |
|---|---|
| `ripwire` binary (CMake `project(ripwire VERSION 0.6.1)`) | Zero-runtime-dep CLI + MCP: ranked call graph, blast radius, tests-to-run, quality deltas (repo description). |
| Verbs (docs/`--help`) | `--for`, `--exemplar`, `--impact`, `--uses`, `--affected`, `--situ`, `--pr-context`, `--callers`, `--expand`, `--doctor`, quality / edit-check surfaces. |

### franken_agent_detection (`Dicklesworthstone/franken_agent_detection`)

| Crate | Purpose |
|---|---|
| `franken-agent-detection` | Local coding-agent installation detection via filesystem probes (`Cargo.toml` description). Optional `connectors` / `chatgpt` / `cursor` features. |

### frankenterm (`Dicklesworthstone/frankenterm`)

Large workspace. Headline crates:

| Crate | Purpose |
|---|---|
| `frankenterm` / `frankenterm-core` | Owned WezTerm-fork terminal + core mux/PTY/state. |
| `frankenterm-core-fleet` | Fleet coordination types. |
| `frankenterm-core-{cass,caut,connector,mcp,policy,replay,telemetry}-types` | Typed seams for CASS/CAUT/connectors/MCP/policy/replay. |
| `frankenterm-flight-recorder` | Session flight recorder. |
| `frankenterm-gui` / `frankenterm-mux-server*` | GUI + mux server. |
| `ft-perf-gate` | Perf gate crate. |
| In-tree `frankenterm/*` (termwiz, pty, mux, …) | Ex-WezTerm owned crates. |

Repo description: terminal hypervisor for AI agent swarms — pane capture, state-machine pattern detection, JSON API.

### frankentui (`Dicklesworthstone/frankentui`)

| Crate | Purpose |
|---|---|
| `ftui` / `ftui-core` / `ftui-runtime` / `ftui-render` / `ftui-widgets` / … | Minimal high-perf TUI kernel (diff rendering, inline mode, RAII cleanup). |
| `doctor_frankentui` | Doctor / health surface for the TUI stack. |

### asupersync (`Dicklesworthstone/asupersync`)

| Crate | Purpose |
|---|---|
| `asupersync` | Spec-first cancel-correct capability-secure async runtime. |
| `asupersync-macros` / `asupersync-tokio-compat` / `asupersync-browser-core` | Macros, tokio compat, browser core. |
| `franken_kernel` | Shared FrankenSuite kernel. |
| `franken_evidence` | Canonical EvidenceLedger schema for decision tracing. |
| `franken_decision` | Decision Contract schema/runtime (Bayesian loss matrix). |
| `frankenlab` / `conformance` | Lab + conformance harnesses. |

### frankensearch (`Dicklesworthstone/frankensearch`)

| Crate | Purpose |
|---|---|
| `frankensearch-core` / `embed` / `index` / `lexical` / `fusion` / `rerank` | Two-tier hybrid search (BM25 + vectors, RRF). |
| `frankensearch-storage` / `durability` / `fsfs` / `ops` / `quill*` / `tui` | Storage, durability, ops, quill gauntlet, TUI. |

### franken_ocr (`Dicklesworthstone/franken_ocr`)

| Package | Purpose |
|---|---|
| `franken_ocr` / bins `franken_ocr`, `focr` | Pure-Rust CPU-only OCR (DeepSeek-OCR-derived MoE VLM path); no Python/GPU. |

### franken_node (`Dicklesworthstone/franken_node`)

| Crate | Purpose |
|---|---|
| `franken-node` | Trust-native JS/TS runtime platform on franken_engine. |
| `franken-security-macros` | Security macros. |
| `sdk/verifier` | Verifier SDK member. |

### beads-for-frankentui (`Dicklesworthstone/beads-for-frankentui`)

| Artifact | Purpose |
|---|---|
| Dashboard site | Issue tracker dashboard over frankentui beads (not a Rust crate library). |

### Also present in suite (brief)

| Repo | One-liner |
|---|---|
| `frankenjax` | Clean-room JAX transform semantics (jit/grad/vmap) + differential harness. |
| `frankensqlite` / `fsqlite` | Concurrent-writer SQLite reimpl. |
| `skillranker` | Rust CLI powered by Jev — ranks agent skills from live session context (topics include `jev`, `asupersync`, `frankentui`). |

---

## Processes map

For each Franken-encoded **loop** (not just a binary): does the Jev lane use it today? Evidence from public `jev_playground`. One concrete next apply.

| Process (loop) | Encoded where | Jev today? | Evidence | Next apply on `jev_playground` / omp-jev-* |
|---|---|---|---|---|
| **Evidence harvest → suggest → adopt → scaffold** | `franken-harvest` `LOOP.md` Phases 1–2; `fh collect/search/suggest/advise`; `capability-adoptions.tsv` | **Partial** | `.fh-agents.toml` maps nomenclature for `fh agents`; no standing adopt TSV / `fh advise` receipt in-repo | On Studio: `fh advise --repo /Users/josh/Developer/jev` + append one CAP row naming a real Jev caller |
| **Planted-negative / ratchet gates** | harvest `check.d/*` + `clippy-ratchet`; engine `universal_dominance_ratchet.rs` | **Yes (planted-neg)** / **No (dominance ratchet)** | `GATES.md`: `gates.sh --selftest` planted-bad RED; 9 stages. No supremacy-board ratchet | Port **one** harvest-style `check.d` pattern: wire `neg-evidence-gate.sh` the day a tick loop exists (`GATES.md` already argues the refusal) |
| **Promotion gate runner** | `franken_engine` `promotion_gate_runner.rs` (4 gates) | **No** | `STATUS.tsv` rung enum includes `5=promoted` but lane headline is **0 promotions**; no Equivalence/Capability/Perf/Adversarial bundle | Prototype a **doc-only** 4-column promotion checklist for any CLEARED→PROMOTED candidate; refuse PROMOTED without all four |
| **Fail-open host hooks** | harvest + foundry autofix; jev already tracks fail-open | **Aware / partially gated** | `GATES.md` discloses `autofix-precommit.sh` mutates index; exit-code↔verdict rule; `NEGATIVE_EVIDENCE` R1 pane oracle fail-closed | Add a stage that REDs if commit-path actor stages foreign paths (or keep `--only` discipline as measured mitigation) |
| **Bead emit from finding** | harvest `check.d/85-bead-acceptance.sh`; frankentui beads dashboard | **Partial** | `.beads/` present; house gates wrap `close-evidence-gate` / `dag-validate` | `fh mine` / movement → auto-open bead with path:line cite for next CLEARED demo blocked_on |
| **Quality-delta / edit-check / affected tests (ripwire)** | `ripwire --for` / `--situ` / `--impact` / `--affected` | **Doctrine yes, habit unknown** | `.fh-agents.toml` + `AGENTS.md` section "ripwire — Deterministic Code Context"; `NEGATIVE_EVIDENCE` R2–R3 instrument lessons | Before next demo code edit: `ripwire ~/Developer/jev --for="omp compact hook change"` and paste `--situ` test list into the PR |
| **Agent detection / stuck-window oracles** | `franken_agent_detection`; frankenterm pattern detection / memory_pressure | **No / refused** | R1: omp pane oracle REFUTED; fail-closed `PANE_ORACLE_STATE_UNMEASURED` | Do **not** route around with capture-pane; if retry condition met (omp pane→session binding), re-probe — else keep refuse |
| **Held-out retrieval / how-eval oracles** | `fh how-eval-*`, harvest `check.d/20-heldout-v2.sh`, `25-retrieval-quality.sh` | **No** | Jev oracles are TypeSafe schema / system-one-adapter / evals.typesafe.ai (`GATES.md` Oracle table) | Optional: `fh how-eval` only if measuring *mirror doctrine* adoption — not as a Jev product oracle |
| **Decision / evidence ledger schemas** | `franken_evidence`, `franken_decision` (asupersync) | **Parallel, not imported** | Jev has `STATUS.tsv` + receipts + `lane-status.sh`; no EvidenceLedger crate | Map one STATUS row to franken_evidence schema fields as a **compatibility sketch**, no runtime dep until a consumer exists |
| **Simultaneity / co-presence across repos** | `fh simultaneity` (help surface in transcripts) | **No** | Not referenced in jev docs | Use when correlating omp-jev-* + jev_playground + typesafe adapter movement in one window |

---

## fh top rows (live)

### Status: BLOCKED this turn

Required Studio commands (re-run on `Joshs-Mac-Studio.local`, paste raw stdout under this heading):

```bash
hostname   # must print Joshs-Mac-Studio.local
fh suggest "agent dig moves"
fh suggest "promotion gate"
fh suggest "planted negative gate"
fh suggest "jev judgment oracle"   # or: fh oracles / fh agents --repo .
fh rejected | head -40
fh techniques | head -40   # or fh rigor — whichever exists
fh search "ratchet"
fh search "co-presence"
fh search "fail-open"
# then for best 5–8 row ids:
fh why <ROW_ID>
```

### Surrogate (prior Studio transcripts only — NOT live 2026-09-19)

From agent-transcript mines (hostname proven `Joshs-Mac-Studio.local` in those sessions):

- `fh` → `/Users/josh/.local/bin/franken-harvest` (symlink).
- Help identity: *"Fail-closed evidence harvesting from the live FrankenSuite mirror"*.
- Example `fh suggest "SwiftUI cockpit…"` returned ranked TECH/WHY/DOC rows (frankenterm memory_pressure, beads, …) — pattern only; **not** the dig queries above.
- `fh suggest` = search alias with default limit 5; `fh advise` = adopted-vs-next for a repo HEAD.

**Do not treat surrogate rows as 2026-09-19 dig evidence.**

---

## Unused alpha ranked for Jev

Rank = value to Jev lane × tractability × underuse today. Not a score invented from thin air — ordered by process gap × existing Jev surface that can consume it.

| Rank | Unused alpha | Why it sits on the table | First consumer in Jev |
|---:|---|---|---|
| 1 | **Promotion gate runner pattern** (4 mandatory gates) | Lane has rung-5 `PROMOTED` vocabulary and 0 promotions; engine already defines Equivalence/Capability/Perf/Adversarial | Any CLEARED candidate before PROMOTED |
| 2 | **`fh advise` / capability-adoptions.tsv loop** | `.fh-agents.toml` proves fh agents awareness; no adopt ledger | `fh advise --repo .` → one CAP row |
| 3 | **ripwire `--for` / `--situ` / `--affected` before edit** | Doctrine present; NEGATIVE_EVIDENCE already fixed instrument mistakes — usage not wired to PR template | Next compaction / demo code PR |
| 4 | **Harvest `check.d/70-negative-evidence.sh` + tick-driven `neg-evidence-gate`** | Explicitly unwired in `GATES.md` until loop driver exists | Day `p12-loop-integrity` leaves N/A |
| 5 | **`universal_dominance_ratchet` / frontier-gap ledger** | Jev STATUS is a flat TSV; no monotonic cell board against regressions | Optional meta-ledger for "CLEARED must not silently become HELD without digest" |
| 6 | **`franken_evidence` / `franken_decision` schemas** | Parallel evidence vocabulary; skillranker already bridges Jev↔FrankenSuite | Schema map doc, not a dep |
| 7 | **`fh simultaneity` / co-presence** | Multi-repo omp-jev + playground + adapter | Weekly movement digest |
| 8 | **frankenterm stuck-window / pattern detection** | Pane truth still UNMEASURED (R1) | Only after omp pane binding exists |
| 9 | **`franken-agent-detection` probes** | Useful for "which agents have ripwire/fh skills activated" census | Machine-wide install audit, not product |
| 10 | **frankensearch quill / held-out how-eval** | Harvest retrieval kernel is FH's product; Jev's oracle is TypeSafe | Keep separate — do not self-oracle Jev with FH retrieval |

### Top 5 crates / packages to adopt first (process patterns, not cargo deps)

1. **`promotion_gate_runner` pattern** from `franken_engine` (copy contract, don't link the engine).  
2. **`franken-harvest` / `fh advise` + `capability-adoptions.tsv` shape**.  
3. **`ripwire` quality verbs** (`--for`, `--situ`, `--affected`) as mandatory pre-edit.  
4. **`franken_evidence` schema** (fields only) aligned to `STATUS.tsv` receipts.  
5. **Harvest `check.d/75-gate-verdict-contract.sh` + planted-neg discipline** (already close; close the unwired neg-evidence loop).

Avoid as first adopts for Jev: frankentorch/OCR/TTS stacks, franken_node runtime, full frankenterm GUI — wrong product boundary (`LOOP.md`: FH is not the orchestrator).

---

## Next 5 adopts (`fh adopt` / copy pattern)

1. **Studio live fh dig** — run the blocked command block; paste into this file under "fh top rows (live)"; `fh why` the best 5–8.  
2. **`fh advise --repo /Users/josh/Developer/jev`** — land one capability row or typed refusal.  
3. **Promotion checklist** — add `docs/demos/PROMOTION-GATES.md` mirroring the four `GateKind`s; refuse `verdict=PROMOTED` in `lane-status` until filled.  
4. **ripwire cold map on next edit** — `ripwire . --for="…"` + `--situ` attached to PR body.  
5. **Wire or schedule `neg-evidence-gate`** — only when a tick loop exists; until then keep the argued refusal in `GATES.md` and append RED ticks by hand.

---

## ripwire cold maps (intended; not executed)

```bash
# On Studio only:
ripwire ~/Developer/franken_engine --exemplar="promotion gate"
ripwire ~/Developer/ripwire --for="blast radius before edit"
ripwire ~/Developer/franken-harvest --for="evidence harvest search"
```

Expected unused-looking symbols for Jev (hypothesis from public sources, **unverified ranks**):  
`promotion_gate_runner::GateKind`, `UniversalDominanceRatchet`, harvest `check.d/75-gate-verdict-contract`, ripwire `--situ` / quality-ack paths. Replace with live ranked XML when Studio run lands.

---

## Method / sources

- `gh api` / authenticated reads: `Dicklesworthstone/{franken_engine,frankenterm,frankentui,franken_agent_detection,frankensearch,franken_ocr,franken_node,asupersync,beads-for-frankentui}`, `redhat-et/ripwire`, `JYeswak/{jev_playground,franken-harvest}`.
- Prior Studio agent transcripts under `/home/box/agent-data/agent-transcripts` for `fh --help` / suggest shape only.
- Host note: sand-host `isBoxScopedSubagent` strips machine-routed Shell — parent with `machineId` must finish live fh/ripwire.

