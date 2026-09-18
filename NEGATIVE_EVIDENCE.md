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

## R6 — RETRY CHECKED: `ubs` on first-party TypeScript

**Original measurement:** `ubs AGENTS.md scripts/sync-docs.sh .fh-agents.toml EVAL.md` →
`no supported languages detected … UBS did not run any scanner: nothing was checked (this is NOT a
pass). Exiting 3`.

**So:** citing UBS on a markdown-only change would be citing an empty scan set as a pass — the exact
anti-pattern this lane bans. The Landing-the-Plane checklist scoped UBS to changes that touch
TS/Python/Rust.

**Retry condition:** the lane gains first-party code (`probes/`, a ported demo, or a `.omp/` seam in
TS). UBS applies from that commit onward — and exit 3 still never counts as green.

**Retry check (2026-09-18, jev-publish-redteam-7s0): SATISFIED as a scan-set condition.** `git ls-files`
identified exactly four first-party TypeScript paths: `compaction/src/omp-adapter.ts`,
`compaction/src/omp-hook.ts`, `compaction/src/replay.ts`, and `compaction/ab/run-ab.ts`.
Vendored clones were excluded by scanning this explicit tracked-file list, not a repository-wide
path. UBS scanned 4 files and exited 1: 1 critical, 6 warnings, 27 info. The only critical was
`Possible hardcoded secrets` in `run-ab.ts`; triage found no secret value (only an environment
variable name/receipt provenance string), and `30-no-secrets` passed. The positive-control temp
project containing `eval()` exited 1 with `eval() ALLOWS ARBITRARY CODE EXECUTION`, proving the
scanner fires. Existing async-listener and JSON.parse warnings are documented fail-fast/host-await
shapes, not confirmed defects; no new defect bead was warranted.

Receipt: `docs/demos/duel-1/runs/ubs-r6-20260918T011614Z.json`.

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

## R11 — The A/B's historical relative verdict was a coin flip. Do not pin a threshold to arm B.

**Refuted 2026-09-18** — by a re-run pane 2 was told to report honestly rather than paper over,
and then by a third sample that overturned the obvious explanation for the disagreement.

| Receipt | fixture bytes / sha | armA Jev-prune | armB LLM summary | verdict status |
|---|---|---:|---:|---|
| `compaction/runs/ab-20260917.json` | 214,993 · `20fa1ea0…` | **1/3** | 3/3 | **withheld (n=1)** |
| `compaction/runs/ab-rerun-20260918.json` | 82,214 · `2346451d…` | **1/3** | 1/3 | **withheld (n=1)** |
| `compaction/runs/ab-sample3-20260918.json` | 82,214 · `2346451d…` (**identical**) | **1/3** | 3/3 | **withheld (n=1)** |

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

---

## R12 — Do not grep for the line you expect. It hides the state that produced it.

**Near-miss, 2026-09-18.** Pane 2's probe (`1a4dd77`) found the shared `fleet-idle-monitor` embeds
`FLEET_QUEUE_REPO` and defaults to **another project's repo path**, which neatly explained why it
recommended a bead from that project for a jev pane. I tested the env var like this:

```bash
FLEET_SESSION=jev … fleet-idle-monitor --report-only | grep -E 'ACTIONABLE|bead='   # default: 1 row
FLEET_SESSION=jev FLEET_QUEUE_REPO=…/jev … --report-only | grep -E 'ACTIONABLE|bead='  # with var: NOTHING
```

The `ACTIONABLE` row disappeared, and I was one command away from recording "`FLEET_QUEUE_REPO`
fixes the cross-project recommendation."

**It fixed nothing.** Reading the *full* output showed both runs identical: `UNPROVEN session=jev
pane=%70 reason=capture_gap` plus three WORKING panes and `OK no two-capture idle panes beside
ready work`. The row vanished because a fresh invocation resets `%70` to **UNPROVEN** — the binary
states its own contract in its usage banner, *"true idle requires two captures"* — and the single
`ACTIONABLE` observation came from **cron-accumulated** state (`age=2041s`). The env var was never
exercised.

**Why the grep hid it:** `grep -E 'ACTIONABLE|bead='` over output containing neither pattern
returns empty, and empty was exactly what "fixed" looks like. **A filter tuned to the expected
answer cannot distinguish "the condition changed" from "the condition never occurred."** Same
family as the five earlier instrument errors in this file: `^PASS` versus `name PASS`, "ripwire"
matching `*-skill-tripwire.sh`, a usage banner read as a removed flag, a fixture's own hooks read
as a gate misfire, and "4 questions" reconstructed from `liveCalls: 4`. **Seventh of the family,
and the first one caught before it was written down.**

Attempted reproduction so the claim could be tested honestly: two invocations 3 s apart, with and
without the variable. Both still `reason=capture_gap` — the required interval is longer than 3 s
(fleet doctrine says 30 s is too short and ≥75 s is the working window), so **the env var's effect
is UNMEASURED, not confirmed and not refuted.**

**What was done instead of claiming a fix:** the jev cron row now sets
`FLEET_QUEUE_REPO=<this repo's absolute path>` (one row edited, `crontab -l` grep
confirms 1 occurrence). It is strictly more correct than pointing at another project, it is
reversible in one edit, and **the cron is now the instrument** — the next `ACTIONABLE` row in
`~/.local/state/flywheel/jev-fleet-idle.log` either names a jev bead or it does not.

**Retry condition — FIRED AND RESOLVED, 2026-09-18T01:38Z, ~9 minutes after this entry was
written.** The cron reached the two-capture state that no inline run could, and the row read:

```
IDLE_PROVEN session=jev pane=%70 age=462s timer=prompt
ACTIONABLE  session=jev pane=%70 bead=jev-distinct-lineage-review-substrate-nl9 mode=report-only
```

A **`jev-*` bead**, not the other project's. **`FLEET_QUEUE_REPO` works**, and the queue-source
defect is closed on `jev-demo-loop-a1q.4`. Two things about *how* this was established are the
durable part:

1. **The measurement belonged to the instrument I could not rush.** Two inline attempts 3 s apart
   both returned `reason=capture_gap`; the binary's own banner says *"true idle requires two
   captures"*, and only accumulated cron state satisfies it. Naming the cron as the instrument and
   waiting was faster than any clever local reproduction — and it produced an unambiguous row.
2. **The fix was applied while its effect was still unmeasured, and labelled that way.** That is
   the correct order when a change is strictly-more-correct and reversible in one edit: apply,
   record the uncertainty, name what would settle it. What would have been wrong is the version
   R12 exists to prevent — claiming the fix worked because a grep came back empty.

**A second observation from the same row, recorded because it corrects me:** the binary reported
`%73 reason=spinner_stripped_hash_changed`. So it *does* strip the animated status line before
hashing. My attribution of the false-WORKING defect to "a changing content hash off an animating
spinner" was a **mechanism guess, and this reason string contradicts it.** The false-WORKING
observation at the time carried `reason=timer_changed`, so if anything it came through the timer
path. The defect's *outcome* is measured; its *mechanism* is not, and the bead has been corrected
to say so.

---

## R13 — The identity-locked hero has no available generation path. All three are closed.

**Measured 2026-09-18.** `'/Users/josh/.agents/skills/repo-hero-image/SKILL.md'` prescribes one shippable path and one breadth
path. Pane 3 exhausted the first, and I measured the keys behind both. Every route is closed, and
the three closures have different causes:

| Path | Status | Evidence |
|---|---|---|
| built-in `image_gen__imagegen` via `codex exec` | **UNAVAILABLE in-session** | *"I can't complete this: `image_gen__imagegen` is unavailable in this session, so no image was saved"* ×4 — `visual/hero-gen-attempt-20260918T020500Z.txt`, `45f3aa8` |
| fallback CLI `~/.claude/skills/.system/imagegen/scripts/image_gen.py` | **DEAD KEY** | requires `OPENAI_API_KEY`; fresh probe returns **HTTP 401** on `/v1/models` |
| Grok via `XAI_API_KEY` | **WORKS, but text-only** | fresh probe returns **HTTP 200**; no reference-image support, so candidates score phash 32–41 against a threshold of 70 |

**The diagnostic took three asks and was worth every one.** Pane 3 twice reported `HERO-BLOCKED`
without naming the step. I had three hypotheses from the skill — the 18-minute multi-step hang, the
dead vault key, the network-isolated background subagent — and **all three were wrong.** The real
cause is a fourth mode the skill does not document: the image tool is simply not bound in this
codex session. No amount of retrying the documented remedy would have found that; only the verbatim
output did.

**A fail-open worth recording separately:** the attempt exited **`exit=0`** while producing no
image. A harness that trusts codex's exit code cannot distinguish "generated" from "politely
declined". Any future hero automation must assert the output file exists, not that the command
succeeded.

**The lead that did not pan out, and why it looked good.** The same verbatim output revealed the
fallback CLI — *"`scripts/image_gen.py`: fallback-only CLI implementation"* — which
`repo-hero-image` never mentions. That is a genuine skill gap worth reporting upstream. But it
needs the same OpenAI key that returns 401, so discovering it did not unblock anything.

**Not attempted, deliberately:** a Grok hero. Grok authenticates and would produce a good scene,
but `repo-hero-image` says **do not ship a `reject`/`marginal`**, and a text-only generator cannot
hold the canonical face — the documented tell is eyebrows the canonical does not have. Shipping a
Yuzu that is not the Yuzu, then recording an honest failing grade beside it, would satisfy the
letter of the grading rule while defeating its purpose. **That is a taste call, not an engineering
one, so it is escalated rather than decided here.**

**Current state is honest, not broken:** `README.md:5` references `visual/hero.jpg`, which does not
exist. Nothing renders broken to anyone because nothing is pushed — publishing is already gated
behind `jev-publish-playground-hog.1` (tip scrubs cannot satisfy the acceptance while history
publishes unrewritten). The hero is a publish-blocker, not a live defect.

**Retry condition — any ONE of these, and the pipeline runs unchanged:**
1. A working OpenAI key (vault or otherwise) — then the fallback CLI path opens immediately, and
   it also restores the grader's vision leg, which currently under-scores every candidate.
2. `image_gen__imagegen` becomes available in a `codex exec` session — re-probe with one
   single-step call; the anchor sha `52fb1b09…` is verified and the spec at
   `visual/HERO-PROMPT.md` is complete, so only generation is missing.
3. A ruling that a non-identity-locked hero is acceptable — then Grok ships it today, with the
   phash distance recorded and `identity_pass` explicitly **false**.

---

## R14 — MU-H1 TODO-judge: refuted by a marker census, for one hour's work

**Refuted 2026-09-18** by the cheapest half of its own falsification design, run by a non-author.

`docs/demos/duel-2/runs/muh1-marker-census-20260918T034820Z.json` (`6a09e86`):

| | |
|---|---:|
| pinned repositories | 16 |
| total code | **283,786 KLOC** |
| TODO/FIXME/HACK/XXX markers found | **17** |
| repositories with zero | 13 |
| median per repo | **0** |
| density | **0.0599 markers/KLOC** |
| concentration | `skillranker` alone = 12, **70.6% of all markers** |
| shortfall vs the 200-marker labelled study | **183** |

**The idea was good and the world does not supply its input.** MU-H1 proposed judging whether a TODO
marker is still *true* — a genuinely novel capability, with the strongest rung-2 mechanism argument
anyone wrote this session (*"calibrated batch judgment with a receipt over hundreds of markers, not
one clever answer"*). It cleared rung 1 at 820 non-author and rung 2 on structure. **Then the
premise failed arithmetically: batch judgment over hundreds of markers requires hundreds of
markers, and our reachable corpus has seventeen.**

**What makes this entry worth writing is the cost.** Under the ordering that existed an hour
earlier, MU-H1 was the leading rung-3 candidate — first to carry a non-author pass at both rungs.
It would have received a CLI, fixtures, RED arms, a receipt, an install script and clean-clone
verification, taking days, and *then* the labelled study would have demanded 200 markers that do
not exist. **`PLAN.md` §3k — estimate rung 4 before paying for rung 3 — was written after demo-1
died that exact way, and its first application killed the very next candidate to reach that point,
for an hour and zero dollars.**

**Retry condition, deliberately narrow because the sample is biased.** The 16 repositories are our
**vendored corpus**: modern, curated, actively maintained, mostly small — close to the *least*
marker-dense population in software. Legacy code is where marker debt accrues, and this census says
nothing about it. **If ≥5 large legacy repositories (≥100 KLOC each, ≥5 years old, ≥20 contributors)
show density ≥1.0 markers/KLOC — roughly 17× what we measured — MU-H1 re-opens with that corpus as
its charter.**

**What was refuted, precisely:** *"there is a judgeable marker population in the code we can
reach."* **Not** *"no such population exists anywhere."* The density figure is a ratio over a corpus
we selected; it is the right number for deciding whether **we** can run the study and the wrong
number for any claim about software at large.

---

## R15 — COD-H3 price-drift auditor: real pain, no Jev-necessary stage

**Refuted 2026-09-18** by its non-author, in `docs/demos/duel-2/RUNG2_COD-H3_resolved_MU.md`
(`51c2bb1`), resolving the structural question its rung-2 pass had left open.

**The demand was never the charge and is reaffirmed.** LiteLLM #38064 is verified independently,
carries a runnable repro and a measured **262% excess**, and has a deep buyer. COD-H3's rung-1 score
of **890 stands.** What failed is the mechanism.

**Stage decomposition — 4 of 5 stages need no judgment model:**

| Stage | Needs Jev? |
|---|---|
| Parse price manifests + usage logs | No |
| Detect drift (manifest vs observed) | No |
| Attribute effective cost per route/provider | No |
| Refuse unverifiable rows | No |
| Counterfactual tier comparison | **the only filed Jev role — claimed, unproven** |

**And 100% of the verified pain lives in the deterministic four.** #38064 is a ranking-arithmetic
bug — cache-read price unread, plus a stable-sort tie-break — with **no judgment anywhere in its
causal chain.** The single Jev stage classifies request complexity so a counterfactual can name a
tier, but tier assignment for operator-owned model sets is served today by **fixed capability
tables** (model → tier, committed, versioned) that a FinOps operator already maintains. The
candidate never exhibits a request the table misclassifies, a tier the table cannot name, or a
dollar figure that moves on the difference.

**The fork it cannot avoid.** Push on that one stage and it becomes exactly one of two other things:
**Fork A**, the counterfactual genuinely needs judgment — then it is *shadow routing*, a realer
product that competes head-on with RouteLLM, Martian and LiteLLM's own cost routing, which the
candidate filed as *neighbours rather than rivals* with no wedge and audit-shaped pricing. **Fork
B**, it does not — then the table classifies tiers, the deterministic core does the rest, and **the
shipped artifact contains zero Jev calls**, which is precisely demo-1's shape. *"H3-as-filed sits
between the forks: too router-shaped to be pure audit, too audit-shaped to face routers, with one
Jev call mediating a question a table answers. That is not a third position. It is the absence of
one."*

**Two executable retry tracks, neither of them taste:**
- **T1 — deterministic auditor, outside this lane.** Build Fork B as lane tooling with the #38064
  repro as fixture one. Predeclared success: catches the tie-break misroute plus one novel drift
  class on real manifests. No Jev call, no demo slot, no rung. If it works, every future routing
  discussion in this lane cites its numbers.
- **T2 — counterfactual router, inside the lane.** Re-file Fork A with a named wedge against
  RouteLLM/Martian on operator-owned traffic (e.g. calibration they cannot emit: per-decision
  probabilities with withhold on novel requests), plus the head-to-head fixture where fixed-tier
  rules misclassify at material cost. **That fixture is the price of re-entry; without it the Jev
  call is garnish.**

**Why this kill matters beyond one candidate.** It is the first time the demo-1 lesson was applied
*before* a build rather than after one. demo-1 shipped, then turned out to make zero Jev calls;
COD-H3 was caught wearing one unproven Jev call over a deterministic core **at rung 2, for the cost
of a decomposition table.** As the ruling puts it: a backlog that keeps a valuable non-Jev tool
wearing a single unproven Jev call *"will eventually ship the demo-1 shape again — valuable,
Jev-free, mislabeled."*

**Untouched:** the #38064 pain, the auditor-not-router positioning insight, and the
confidence-interval and refuse-unverifiable discipline in H3's receipt plan — all of it transfers
verbatim into T1. **The two retries keep everything valuable; they refuse to keep it in one
artifact.**

---

## R16 — the 32.5-point "signals beat verdicts" delta is **not** a transferable method gain

**Refuted 2026-09-18** by `docs/demos/duel-2/FALSIFY_demo7_MU.md` (`8757b07`), label-free half
executed at $0, read-only, against the vendored pinned source `jev-phishing-bench@1d56e8c`.

**The lane quoted "verdict-only 62.6% → 95.1%, a 32.5-point delta" from the demand duel onward — in
demo-7's contract, in `PLAN.md` §3m, and in my own commit messages. The delta is real and the
attribution was wrong.**

The source **ships its own no-AI control** (`bench/heuristics.py` Control 1, `report.md:113-119`):
**two regex features, no fitting, no labels → 91.6%** [90.4, 92.8], FPR 0.2%.

```text
verdict-only ............ 62.6%
+ dataset knowledge ..... 91.6%  (+29.0)   regex floor, NO AI
+ Jev signals + fitting . 95.1%  (+3.5)    the method
```

**89% of the advertised delta is the gap between knowing the dataset and not knowing it.** CIs are
disjoint at each step, so the **3.5 points are real** — and so is the conclusion that the other 29
are not method. The source states it directly (`report.md:162-165`): the five questions were written
*after* reading the dataset's URL-evasion taxonomy and *"target the way this dataset was built."*

**What was refuted, precisely:** *"asking signals instead of verdicts buys ~32 points."* **Not**
*"signals are worthless"* — the marginal method gain is 3.5 points with disjoint CIs, plus
calibration machinery (ECE 0.027, AUROC 0.988) that no regex emits. **demo-7 was repriced, not
killed**; a kill here would have been this session's fourth over-kill.

**Retry / decision condition — predeclared, and it is a gate rather than a hope.** On any new
labelled corpus, run three arms (verdict-only, regex floor encoding the builder's own knowledge,
fitted signals+head) under identical stratified splits and compute
`method_gain = acc_fitted − acc_regexfloor`:

- `method_gain < 0.05`, or overlapping 95% CIs, or either arm under N=200 → **HELD / UNASKABLE**:
  ship the regex and the calibration report format, **not the template.**
- `method_gain ≥ 0.05` with disjoint CIs → proceed to calibration measurement on held-out data.
- Builder claims no domain knowledge, so no regex floor is buildable → **UNASKABLE.** Do not grade a
  template against a missing baseline.

**Pane 3's own note on the base rate:** the failing branch is *"the common case by the base rate of
the current evidence (one corpus in, dataset-knowledge dominant)."*

**Second, cheaper falsifier still unrun and worth $0:** committed full-fit weights show
free-hosting **+9.27** and generic-sender **+12.24** (`report.md:107`). If one weight dominates, the
"five signals" story is *"one signal plus decoration"* → HELD for scope-narrowing. **Check the
weights before building anything.**

**Methodological note this entry exists to preserve:** the lane repeated a headline number for a
full session without opening the source's own control arm. The control was committed, documented,
and one file away. **A number quoted from a report's abstract is not evidence until someone reads
the report's controls.**

## R17 — my own gate carried the defect I ruled a candidate UNASKABLE over (2026-09-18)

**Claim retired:** that `scripts/audit-score-lineage.sh` as first committed (`44ed719`) was a sound
gate.

**Two defects, self-found within one tick of shipping it.**

**1. A self-satisfiable escape branch.** The trip condition read
`SCORE_RECEIPT.search(msg) or <changed-row receipts>`. **A gate that can be satisfied by typing
`RUNG2_` into your own commit message is not a gate** — and the party writing those messages is the
conductor, the party this gate exists to constrain. **I built myself an escape hatch and shipped it
with a `[selftest]` verification level.** Removed; the row-receipt branch is now the only branch, and
**ARM G** proves it (a legal shape whose changed-row receipt is not a scoring artifact must TRIP).

Measured before removing it: `7622790` passed via **both** branches; `1bb9a4b` and `1ccddf9` passed
on **row receipts alone**. **So removing it changes no historical verdict** — `7 changes, 0 upward,
3 coincidences, 0 trips` is byte-identical after the fix. The hole was live but never load-bearing.

**2. `SCORE_RECEIPT` is a pattern rule over filenames — still.** It matches **17 of the 48**
top-level `duel-2` documents. **That is the same label-defining-regex defect this lane ruled COD-H2's
rung 4 `UNASKABLE` over** (*"labels = pattern rule, fixed by the rubric"*), now sitting inside one of
the lane's own gates.

**Direction matters and is stated:** the regex is **permissive**, so it **under-fires** — missed
trips, never false accusations. And all three historical passes cite receipts that are genuinely
scoring artifacts (`HUNT_SCORES_COD_ON_MU.md`, `HUNT_SCORES_MU_ON_COD.md`, `RUNG2_demo9_MU.md`), so
**the clean result stands on the merits while the gate stays weaker than it looks.**

**RETRY CONDITION:** replace the regex with a **declared receipt type in `STATUS.tsv`**, so *"is this
a score receipt"* is **stated by the row rather than inferred from its filename.** Until then this
gate's `0 trips` carries a weaker claim than its output suggests, and the script says so in its own
source.

**And the measurement error inside the diagnosis, recorded because it is the pattern:** my first
attempt to size the regex counted **all 17 rows' receipts** (14/14/12 matching) when the gate only
ever reads the **changed** rows' receipts. **Wrong control, caught mid-measurement before any claim
was published** — the first time in this session that the loop closed before the number left my
hands.

### R17 CORRECTION (2026-09-18, pane 2 `965005a`) — the direction claim was false in its load-bearing half

**R17 above says:** *"the direction is permissive — it under-fires (missed trips), it never falsely
accuses."* **That is wrong, and pane 2 found it in a non-author audit of my instruments:**

> **"`b2eaf6f` claim `regex under-fires but never false-accuses` is FALSE generally: a real score
> receipt with nonmatching filename triggers rc5."**

**The regex is used NEGATED** — `if not any(SCORE_RECEIPT.search(r)): trip` — so:

| filename lies... | consequence |
|---|---|
| a **non-score** receipt **matches** the pattern | no trip → **false GREEN** (what R17 described) |
| a **genuine score** receipt **misses** the pattern | trip → **false RED on honest work** |

**And a false RED is the failure mode I myself called worse**, because it trains everyone to ignore
the gate. **I asserted the safe direction and shipped the unsafe one alongside it.**

**Measured exposure, both directions live in the current file:**

```text
unique receipts in STATUS.tsv ....... 16
matching SCORE_RECEIPT .............. 6
NOT matching ........................ 10   <- false-RED exposure, the MAJORITY
```

And the false-GREEN half is concrete too: **`docs/demos/duel-2/HELD_demo2_demand_COD.md` matches** —
because `demand_` satisfies `DEMAND_` under `re.I`. **A hold receipt passing as a score receipt.**

**No arm caught this, and that is why I believed the wrong direction.** Pane 2: *"score selftest has
no genuine score receipt whose filename misses `SCORE_RECEIPT`, so the R17 false-red hole remains."*
**`ARM G` tests a non-score receipt tripping correctly; nothing tested a score receipt tripping
wrongly.**

**RESOLUTION — not a regex patch.** Pane 2's Q19 ruling (`RULE_receipt_type_COD.md`, `fe63347`)
replaces inference with a **declared** `receipt_type` enum read as a field, fail-closed on
empty/unknown/out-of-enum, **never filename-backfilled.** That **removes the defect class** rather
than tuning a pattern, so both error directions go together. Patching the regex would have kept a
label-defining rule alive with better constants.

**And the measurement error inside this correction, recorded because the pattern is the point:** my
first attempt to size the exposure ran a **case-sensitive `grep -E`** against a **`re.I`** regex, and
reported 12 nonmatching. Wrong control; corrected to 10 before publishing. **Eighth instance, second
consecutive one caught before the number left my hands.**

---

## R18 — a receipt that contradicts ITSELF is real, and a gate for it is refused (2026-09-18)

**Not a gap I closed. A mechanism a pane refused to let me build, with the trigger that would
change the answer.**

Pane 3 (`docs/demos/duel-2/runs/internal-consistency-ruling-20260918T133055Z.json`, `2c2519b`) found
**three values for one share** inside a single cited receipt,
`docs/demos/duel-2/runs/demo7-weights-20260918T041352Z.json`:

```text
0.7624955689471817   stored fraction      = 76.2496%
76.22                stored INTERPRETATION TEXT   <- neither the fraction rounded nor explained
76.25                cited in STATUS.tsv  = the fraction, correctly rounded
```

`scripts/verify-reason-numerals.sh` cannot see this. It checks **STATUS → receipt** literals and
**never receipt ↔ receipt**. The defect lives entirely inside one file, in the half no instrument
reads.

**The ruling was BOTH, and the split is the finding.** Pane 3: *"Conceding either half loses
something: calling it only a receipt defect leaves the blind spot unnamed; calling it only a gate gap
demands machinery for one observation."*

**Why no gate — and this is the reasoning worth keeping, not the verdict.** *"A general
internal-consistency gate is UNDECIDABLE WITHOUT PER-SCHEMA DERIVATION RULES: any two numbers
coexisting in one file are usually DIFFERENT QUANTITIES (91.6 vs 3.5 in FALSIFY_demo7 sit side by
side legitimately), so a mechanical pair-check FALSE-POSITIVES BY CONSTRUCTION."* The only honest
narrow form — author-declared `assert_equal` pairs — is new machinery for one observed case, and the
lane's own family rule forbids it: **the tautology breaker waited for FOUR instances.**

It labelled its own answer to stop it reading as evasion: **`NONE NOW — stated as a finding, not a
dodge.`**

**RETRY CONDITION (the part that makes a refusal usable):** a **SECOND** observed receipt-internal
contradiction triggers a schema-level rule. Until then this row is the ledger entry that future
recurrence is measured against — one observation is an instance, two is a class.

**Remedy for the instance, not the class:** its owner explains or corrects the `76.22`, a
**0.03-point unexplained gap inside a cited receipt.** Pane 3: *"No new gate, no guidance prose. The
receipt's fraction and interpretation must agree or the disagreement must be explained in the receipt
itself."* Assigned to pane 2 as the receipt's author; I did not edit another pane's receipt.

**Why this row exists at all.** My instinct on being handed a blind spot was to extend the
instrument, and I asked for a mechanism to be specified rather than invent one. The pane's answer was
that the right size is zero — and a refusal with a trigger is worth more here than a gate that fires
on every legitimately-adjacent pair of numbers in the corpus.

---

## R19 — read-triage with calibrated withhold: incumbent ships the surface, wedge gaps immaterial (2026-09-18)

**Candidate (pane 3's, killed by its author-pane's own ruling):** a pre-read gate — Jev Choice per
candidate chunk (read/skip) with calibrated probability, withhold routing to reading — aimed at the
measured ~99% retransmission lever. Ruling: `docs/demos/duel-2/runs/wedge-ruling-20260918T145151Z.json`.

**Why it dies:** the named wedge was calibration-plus-withhold against BorisLeMeec/jev's find/read-hook.
On their published evidence both halves fail as a *product* wedge: (1) calibration is asserted
without measurement, but their bimodal scores (true 0.92–0.99 vs false 0.02–0.13, "the threshold
barely matters") leave no material room where calibration changes a decision — an unmeasured gap with
no demonstrated materiality is a hypothesis, not a wedge; (2) fail-open is stated ("every gate fails
toward doing nothing") without a refusal-path arm, but their 50/50 recall vs 28% chance already covers
the underlying fear (hidden code) the accounting would serve. Real narrow gaps, audit-trail grade.

**What stands (not retracted):** different levers / under-scoped rung-4 (EXT-U1 ruling) — the kill
is of this candidate's wedge, not of the lever analysis that motivated it.

**RETRY CONDITION (two independent tracks, either re-opens):**
1. **Materiality:** evidence that mid-range (non-bimodal) triage scores occur materially in practice —
   then calibration has something to fix and the wedge re-opens as a head-to-head on paired-agent cost.
2. **Tester-to-subject bench:** a withhold-behavior bench for triage tools (theirs and any successor)
   measuring refusal necessity — declined-vs-necessary refusals — in the COD-H5 mold: it benchmarks the
   thing that ships rather than rivaling it.

**Fairness recorded (from the ruling):** labels by agents forbidden from self-grading, 6/6 negative
controls read correctly, fitted-and-overridable thresholds disclosed, leverage-vs-saving distinguished
against their own headline. Killed on the wedge, not on the shop.
