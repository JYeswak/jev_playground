# NEGATIVE_EVIDENCE — dead-end ledger

> Refuted hypotheses, reverted "wins", NO-SHIP measurements, exhausted veins. Read this BEFORE
> starting any perf/detector/optimization hypothesis. Format + doctrine: the
> `negative-evidence-ledger` skill. **Every row carries a retry condition** — a row without one
> is a grudge, not evidence.
>
> Gate inventory: [`GATES.md`](GATES.md). Acceptance bar: [`AGENTS.md`](AGENTS.md) §4, which
> requires a pass to append here or say why it learned nothing negative.

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

---

## R9 — REJECTED: wiring the reddit MCP into this lane

**Proposal (mine, 2026-09-18):** add grokbot's deployed reddit MCP to `<repo>/.omp/mcp.json` so the
demo loop could read builder-sub threads as external signal alongside `x-cli` and the skillranker
watch.

**Rejected by Joshua, same day: "we dont need to give jev reddit."**

**The capability is real — this is a scope refusal, not a dead end.** Measured live before the
proposal: worker `grokbot-reddit-mcp` (`grokbot/mcp-servers/reddit-mcp/wrangler.jsonc`, keyless, no
bindings) answers at `https://grokbot-reddit-mcp.joshua-68f.workers.dev/mcp` — `GET / → 200`, and
`tools/list` returns `get_subreddit_posts` and `get_post_comments`. A plain `content-type: application/json`
request is refused with `-32000 Not Acceptable`; the client must send
`accept: application/json, text/event-stream`. grokbot also already owns the cadence: a **Reddit
Pulse** bot, weekly Wed 07:00, whose contract is worth stealing verbatim — *"Score and comment
counts are context, never proof"* and *"A complaint with a repro beats a compliment with none."*

**Why the refusal is right, stated so it is not re-litigated:** reddit signal already has an owner,
a schedule, and an evidence contract in the repo where it belongs. Duplicating the surface here
would give this lane a second place to read the same threads, with no second consumer — the
`value-bearing-gates` failure in MCP clothing. This lane's signal is the vendored corpus at pinned
SHAs, `skillranker` as it moves, and X.

**Retry condition:** a demo's acceptance requires reddit thread text as *input* — e.g. a zero-label
classifier fixture whose corpus is builder-sub threads (`USAGE-MAP.md` §9 shape) — **and** grokbot's
Reddit Pulse output is not already reachable as a file we can read. Until both hold, read grokbot's
artifacts instead of adding a server.

---

## R10 — Do not build a jev-local fleet-idle monitor. One is already installed.

**Rejected 2026-09-18.** I wrote `scripts/fleet-idle-monitor.sh` (5,044 bytes) plus
`scripts/selftest-fleet-idle-monitor.sh` (8 arms, all PASS including fires-on-known-bad idle
detection and five fail-closed arms) to fix a real measured gap: the conductor was blind between
20-minute ticks, reported pane 3 as "still working" while all three of its units sat committed in
`git log`, and only a human chase surfaced it.

**Then I read the live crontab.** `$HOME/.local/bin/fleet-idle-monitor` already exists — a
6.98 MB arm64 Mach-O binary, installed 2026-09-04 — invoked by **both** other lanes on identical
rows:

```
8,18,28,38,48,58 * * * * cd <repo> && FLEET_SESSION=<session> timeout 480 \
  $HOME/.local/bin/fleet-idle-monitor --report-only >> <log> 2>&1
```

(The live row spells the path out absolutely, because cron does not expand `$HOME`. Substituted
here so this file carries no operator home directory — the row is otherwise verbatim.)

It ran against jev **unmodified on the first try** (`FLEET_SESSION=jev`), and in cron's exact
environment (`env -i` + the four crontab declarations), emitting per-pane rows with pane ids:
`UNPROVEN session=jev pane=%70 reason=first_capture` / `WORKING … reason=omp_working_marker` /
`OK no two-capture idle panes beside ready work`, exit 0.

**It is strictly better substrate than what I wrote, on the axis that decides correctness.** Its
usage banner states the contract: *"true idle requires two captures; dead means absent from tmux
list-panes -a."* Mine read `safe_to_dispatch` from a **single** capture — and `safe_to_dispatch` is
explicitly not liveness (a pane pending a client restart accepts a packet, parks it, and never
submits). My selftest's 8 green arms proved my detector matched my own fixtures; they could not
prove the detector was asking the right question. **A green selftest against self-authored fixtures
is not evidence that the design is right.**

**What the lane was actually missing was one crontab row, not a script.** jev had the `*/20` tick
row and no 10-minute monitor row, while omp-orchestrator and cfsios each had both. Installed:
diff +1/−0, jev now carries 2 rows, matching the live convention exactly.

**Both scripts withdrawn** (uncommitted, never in git history — removing my own unlanded work, not
deleting anything of Joshua's).

**The rule, and it generalizes past this instance:** before writing lane infrastructure, grep
`crontab -l` and `~/.local/bin` for the capability. Two other lanes doing the same thing by an
identical row is the signal that the substrate exists and is parameterized. `ompo`
(omp-orchestrator) is where general fleet orchestration is being built and is **not finished** — so
a jev-local conductor would have become a competing implementation of an in-progress system, the
"five competing conductors" failure the ntm-fleet-monitor skill names.

**Retry condition:** the installed binary cannot express something jev specifically needs — e.g. it
cannot report a **dry queue** (a pane that is idle *because its packet ran out of units*, which is a
packet defect, not a pane state). If that need becomes concrete, the fix is a flag or an upstream
bead against the shared binary, **never** a jev-local fork.

---

## R11 — The A/B's "B wins" was a coin flip. Do not pin a threshold to arm B.

**Refuted 2026-09-18** — by a re-run pane 2 was told to report honestly rather than paper over,
and then by a third sample that overturned the obvious explanation for the disagreement.

| Receipt | fixture bytes / sha | armA Jev-prune | armB LLM summary | verdict |
|---|---|---:|---:|---|
| `compaction/runs/ab-20260917.json` | 214,993 · `20fa1ea0…` | **1/3** | 3/3 | "B wins" |
| `compaction/runs/ab-rerun-20260918.json` | 82,214 · `2346451d…` | **1/3** | 1/3 | "tie" |
| `compaction/runs/ab-sample3-20260918.json` | 82,214 · `2346451d…` (**identical**) | **1/3** | 3/3 | "B wins" |

**The wrong explanation, which I held for about ten minutes and which the data supported.** Rows 1
and 2 disagreed, and the fixture had changed between them: `a6e1353` removed 76 `thinkingSignature`
blobs — roughly 133 KB of base64 — shrinking the corpus 62% and moving its sha. Corpus change was
the obvious cause, and I wrote it into `EVAL.md` as "unattributed between corpus change and
generator variance" with a named separating experiment.

**Row 3 ran that experiment and exonerated the corpus.** Same fixture bytes as row 2, and arm B
came back 3/3. Arm B is produced by a live `runOmp` summarization call with **no temperature pin**,
so it scores **3, 1, 3 on identical input**. The disagreement is generator variance, and the
corpus scrub was innocent.

**What this refutes:** "Jev-pruning loses to generic summarization, 1/3 vs 3/3." That was **n=1 on
a stochastic arm** — a coin flip reported as a measurement. It propagated into 17 tracked files
before anything tested it twice.

**What survives, and it is the more useful half:** **armA (Jev-prune) scored 1/3 in all three runs,
across two different corpora.** Pruning really does drop answer-bearing facts. That is robust, and
it is exactly the premise the fact-ledger demo (duel CC-1) rests on — so the demo's motivation is
*strengthened* by the same evidence that killed its comparison.

**The design defect this exposed, which is the durable lesson:** CC-1's satisfying arm read
*"score ≥ arm B's 3/3"*. Against a 2-point-variance baseline, that threshold is unfalsifiable in
both directions — a demo could pass by standing still on a bad roll, or fail on a good one. **A
stochastic baseline is not a threshold.** Corrected to an absolute 3/3.

**Retry condition:** a *relative* claim about pruning versus summarization becomes available only
with a pinned generator (fixed model, fixed temperature, fixed seed if the provider exposes one)
**or** a reported distribution — n≥10 per arm with the spread published, not a single verdict
string. Until then the harness may report arm A absolutely and must not emit a `verdict` field at
all; a one-word verdict over a stochastic arm is the defect, not the presentation.
