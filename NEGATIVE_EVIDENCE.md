# NEGATIVE_EVIDENCE.md — the jev lane

Refuted hypotheses, retracted claims, rejected designs, and measured "do not build this" results.
**Every row carries a retry condition.** A row with no retry condition is a grudge, not evidence.

Read this before starting a hypothesis in this lane: the cheapest experiment is the one someone
already ran and wrote down.

---

## R1 — REFUTED: "omp can be asked for the live state of a pane"

**Claim:** an orchestrator can read a running pane-agent's state (working vs idle, current model,
last message) from omp.

**Measured (2026-09-17, omp/18.2.4, and earlier in `skill://omp-integration` wave 7):** three
independent paths, all refuted.

- `omp --mode=rpc` **spawns a new session** on every invocation — two runs return two session ids.
  It never attaches to a pane.
- `~/.omp/profiles/<p>/agent/terminal-sessions/tmux-%N` yields the **last session opened**, not the
  live one. A pane a monitor called WORKING and a pane it called IDLE both projected `idle`.
- `get_last_assistant_text` returns `success=true, data={}` — **no text field** — on both fresh and
  resumed sessions.

**Consequence adopted:** a pane oracle must fail closed (`PANE_ORACLE_STATE_UNMEASURED`) and refuse
to authorize dispatch. Do not route around it with spinner/braille parsing of `capture-pane`.

**Retry condition:** omp ships a documented pane→session binding (a tmux-pane-keyed handle in
`get_state`, or an `omp ps`-style surface that maps panes to live session ids). Re-probe
`omp://rpc.md` for a `pane` field on any frame.

---

## R2 — RETRACTED (instrument error): "install.sh wired a ripwire hook into Claude Code"

**Claim, published then withdrawn within the same session:** the ripwire 0.6.1 install registered a
hook in `~/.claude/settings.json`.

**Refutation:** the three matches were `yaml-config-serializer-skill-tripwire.sh`,
`runtime-ddl-skill-tripwire.sh`, `process-compose-skill-tripwire.sh` — **"tripwire" contains
"ripwire"**. `settings.json` mtime was unchanged (2026-09-16, the install ran 2026-09-17).

**Lesson, general:** a substring needle over a filename namespace is not a detector. Match on the
basename with anchors (`^ripwire[-.]`), or on the file the entry points at.

**Retry condition:** none — the claim was false. The *instrument* rule stands permanently.

---

## R3 — REFUTED: "ripwire 0.6.1 dropped `--doctor`"

**Claim:** `--doctor` was removed, because `ripwire --doctor` printed a usage banner.

**Refutation:** `<dir>` is ripwire's one required argument. `ripwire . --doctor` works —
`checks="9" passed="9"` measured on `jev-review`.

**Lesson:** a usage banner is the tool telling you the *invocation* is wrong, never that the
*feature* is gone. Read the banner before writing the obituary.

**Retry condition:** none.

---

## R4 — RETRACTED (instrument error): "stamp-check produces zero rows for this lane"

**Claim:** `stamp-check.sh --repo jev` exited 0 with 0 PASS and 0 FAIL — an empty scan set.

**Refutation:** the counting grep was `^PASS`; stamp-check emits `<item-name><spaces>PASS`. The run
had produced **32 PASS / 20 FAIL / 2 PARTIAL / 10 N-A** all along.

**Lesson:** before reporting an empty scan set — which this lane treats as an ERROR — confirm the
*reader*, not the tool. Two of the four negative results in this file are reader defects.

**Retry condition:** none.

---

## R5 — REJECTED design: commit the mirrored documentation bytes

**Proposal:** track `docs-mirror/**` (111 TypeSafe doc pages, `llms-full.txt`, ripwire docs, ~5 MB)
so a fresh clone has the corpus with no network.

**Rejected because:** (1) it redistributes third-party documentation from our history, (2) every
`sync-docs.sh` run would rewrite ~5 MB and bury real diffs, (3) the guarantee it buys is already
bought — `docs-mirror/MANIFEST.tsv` is tracked and `sync-docs.sh --check` proves byte identity by
sha256 (`CHECK PASS 114 mirrored files`).

**Retry condition:** the lane needs to run air-gapped (no network at clone time) **or** upstream
removes pages we cite, making the mirror irreproducible. The second is detectable: `--check`
reports `DRIFT`/`MISSING` instead of PASS.

---

## R6 — NOT ADOPTED as a gate: `ubs` on doc-only changes

**Measured:** `ubs AGENTS.md scripts/sync-docs.sh .fh-agents.toml EVAL.md` →
`no supported languages detected … UBS did not run any scanner: nothing was checked (this is NOT a
pass). Exiting 3`.

**So:** `ubs` is correct and honest here, and citing it on a markdown-only change would be citing an
empty scan set as a pass — the exact anti-pattern this lane bans. The Landing-the-Plane checklist
therefore scopes `ubs` to changes that touch TS/Python/Rust.

**Retry condition:** the lane gains first-party code (`probes/`, a ported demo, a `.omp/` seam in
TS). `ubs` applies from that commit onward — and exit 3 still never counts as green.

---

## R7 — MEASURED, do not design on it: `abort_bash` acknowledges without cancelling

**Measured upstream (`skill://omp-integration` wave 3):** `abort_bash` against a running
`bash sleep 10` returned `success=true`, and the bash call later reported
`exitCode=0, cancelled=false`.

**So:** a `success=true` acknowledgement from an omp RPC handler is **not** evidence of the effect.
Treat `success=true` with empty or null `data` as `NO_PAYLOAD`.

**Retry condition:** `omp://rpc.md` documents cancellation semantics for `abort_bash`, or a probe
shows a non-zero `cancelled=true` on a live long-running call.

---

## R8 — NOT A REGRESSION: `ripwire-opt-remarks` disappeared from the skill store

**Observed:** after the 0.6.1 install, 16 of 17 shipped `ripwire-*` skills were linked into
`~/.claude/skills/`; `ripwire-opt-remarks` was pruned.

**Explanation, from the upstream activator itself** (`~/.local/share/ripwire/skills/install.sh`,
lines 314-320): its frontmatter is `audience: contributor` — it is about working *on* ripwire's C++ —
and the activator deliberately prunes contributor-only skills unless `--contributor` is passed, so a
checkout that stops being a contributor setup does not keep one forever.

**Retry condition:** we start editing ripwire's own C++. Then run the activator with
`--contributor`.
