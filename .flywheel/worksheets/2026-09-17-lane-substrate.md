# Worksheet — jev lane substrate, 2026-09-17

Handoff for the next agent in this lane. This session mutated substrate, so the things below are
**not discoverable from the code** — they are config, machine state, and refusals.

---

## WHAT

Turned this repo from a loose directory of vendored clones into a governed lane:

1. **`AGENTS.md`** authored against the mirror-derived canonical shape (`fh agents` skeleton
   `content_id=095decf2…`, `source_rev=bb59539…`), with `§0` (the non-negotiables index, which is
   also the convention contract) and `§4 Definition of Done`. `.fh-agents.toml` declares the
   synonym map so every canonical row is measured: **zero UNMEASURED**, remaining ABSENT argued.
2. **Primary sources vendored** — `scripts/sync-docs.sh` mirrors 111 TypeSafe doc pages +
   `llms-full.txt` + ripwire's manual, pins `upstream/typesafe-ai/{typesafe-sdk-python@420ef4f,
   typesafe-sdk-js@66880cc, system-one-adapter-python@0bb819b, skills@65a39f3}`, and writes sha256
   manifests. `--check` → `CHECK PASS 114`.
3. **`git init`** (authorized) with an **allowlist** `.gitignore`, plus `GATES.md`,
   `NEGATIVE_EVIDENCE.md`, `TESTS.md`.
4. **ripwire upgraded** 0.4.0 → **0.6.1** (`built_from=f45087a77`), still exactly one binary at
   `~/.local/bin/ripwire`.
5. **Gates**: `50-house-gates.sh` (wraps three foundry house gates) and
   `60-staged-deletion-lane.sh` (1 trigger + 5 satisfying witnesses) added to `foundation/gates.sh`.
6. **`stamp-check --repo .`: 32 PASS / 20 FAIL → 47 PASS / 5 FAIL / 1 PARTIAL** (of 64).

## STATE

**Substrate you must know about before you touch anything:**

- **`core.hooksPath` is this clone's ABSOLUTE `githooks/`** (re-derive: `git config
  core.hooksPath`). A relative value
  resolves per-worktree and every worker lane would commit unhooked. Two hooks live there:
  `commit-msg` (refuses a subject with no verification level: `pending|selftest|test|mutation|
  oracle|live`) and `pre-commit` → `pre-commit-staged-deletion-survives.sh`. Both byte-identical to
  their upstream sources; **editing either is a re-certification, not an edit.**
- **`dcg` denies whole-tree staging here** (`zeststream.shared_worktree:git-add-whole-tree`). Stage
  explicit paths. This is correct: three agents share this worktree.
- **`init.templateDir = ~/.git-templates` is machine-wide** and installs the `commit-msg` hook into
  every newly created repo — so **any** selftest that builds a throwaway git fixture must run with
  `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`. Both of this lane's gate wrappers
  already do; your new one will not unless you copy that.
- **The clone census grows every session; never hardcode it.** `AGENTS.md § The census` has the
  one-liner. ~20 clones at handoff time.
- **`docs-mirror/` and `upstream/` are gitignored except their manifests.** A fresh clone needs
  `./scripts/sync-docs.sh` before it can read a primary source.
- **Beads:** 7 in `.beads/` (prefix `jev`), 4 filed this session — two routed to franken-harvest
  (`route-standards-manifest-6yq`, `route-jev-oracle-row-7ou`) and two upstream foundry bugs
  (`foundry-selftest-git-template-coc`, `stampcheck-vendored-false-positives-lfn`).
- **Sibling work in flight, do not touch:** `compaction/` (omp transcript adapter, `omp-hook.ts`,
  the A/B run) belongs to another pane and is tracked by `jev-compact-hook-hbs` /
  `jev-compact-ab-l6f`. They are building the omp compaction seam.

**Verification at handoff:** `foundation/gates.sh` and `--selftest` ALL GREEN across six stages ·
`sync-docs.sh --check` CHECK PASS 114 · `probes/fast-jev-probe.mts` 8/8 offline ·
`fh agents --repo .` nomenclature VALID.

**Refusals that are decisions, not gaps** (argued in `GATES.md` § *Not wired yet*):
`neg-evidence-gate.sh` unwired (no tick loop ⇒ no consumer) · `p6-cross-lineage` not adopted ·
`p5-autofix` / `rc0-declared-path` / `p10-commit-sweep` false positives on vendored clones ·
`p12-loop-integrity` N/A.

## NEXT

1. **Do not duplicate the compaction seam** — a sibling owns it. If you want an omp seam, take the
   unclaimed one: the `tool_call` safety gate (seam #1 in `AGENTS.md § Jev × omp Integration`), in
   `<repo>/.omp/hooks/pre/`. Everything omp-side is at **L0**: designed and cited, nothing wired.
2. **Get one seam to L3** — it fires in a real omp session AND a known-bad input makes it refuse,
   with the frame pasted. That is the lane's actual product bar; nothing has reached it.
3. **Chase the two routed beads** — until `fh standards check` returns PASS this repo is unstamped,
   and until `fh oracles --domain jev` returns a row every claim cites its oracle inline.
4. **Read `NEGATIVE_EVIDENCE.md` first.** Four of the eight rows are instrument errors, three of
   them mine from this session. Same traps are waiting for you.
